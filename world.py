"""
world.py — Geração otimizada para 60 FPS.
Melhorias:
  - Mundo menor (20x20) com VIEW_RADIUS de 10 blocos
  - Menos árvores (TREE_CHANCE reduzido)
  - Culling por distância: esconde blocos longe do jogador
  - Chunks: apenas blocos dentro do raio são entidades ativas
"""

import json
import math
import os
import random

from ursina import *
from block import Block, BLOCK_TYPES

WORLD_WIDTH  = 20
WORLD_DEPTH  = 20
BASE_HEIGHT  = 4
MAX_HEIGHT   = 9
TREE_CHANCE  = 0.025          # menos árvores = menos entidades
VIEW_RADIUS  = 10             # raio em blocos para mostrar entidades

FACE_DIRS = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
SAVE_FILE = 'savegame.json'


def smooth_noise(x, z, seed=0):
    s = seed * 0.1
    val = (
        math.sin((x + s) * 0.25) * 0.40 +
        math.cos((z + s) * 0.25) * 0.40 +
        math.sin((x + z + s) * 0.15) * 0.25 +
        math.cos((x - z + s) * 0.18) * 0.20 +
        math.sin((x * 1.7 + s) * 0.10) * 0.10 +
        math.cos((z * 1.5 + s) * 0.10) * 0.10
    )
    return (val + 1.45) / 2.90


class World:
    def __init__(self, width=WORLD_WIDTH, depth=WORLD_DEPTH, seed=None):
        self.width  = width
        self.depth  = depth
        self.seed   = seed if seed is not None else random.randint(0, 9999)
        self.blocks = {}
        self._plan  = {}
        self._ox    = width  // 2
        self._oz    = depth  // 2
        print(f"[World] Seed: {self.seed} | Tamanho: {width}x{depth}")

    def _get_height(self, x, z):
        n = smooth_noise(x, z, self.seed)
        return max(BASE_HEIGHT, min(int(n * (MAX_HEIGHT - BASE_HEIGHT)) + BASE_HEIGHT, MAX_HEIGHT))

    # ── Geração ───────────────────────────────────────────────────────────
    def generate(self):
        print("[World] Planejando terreno...")
        self._plan = {}
        tree_positions = []

        for bx in range(self.width):
            for bz in range(self.depth):
                wx = bx - self._ox
                wz = bz - self._oz
                height = self._get_height(bx, bz)

                for wy in range(height):
                    if wy == height - 1:
                        btype = 'grass'
                    elif wy >= height - 3:
                        btype = 'dirt'
                    else:
                        btype = 'stone'
                    self._plan[(wx, wy, wz)] = btype

                edge = 3
                if (edge < bx < self.width - edge and
                        edge < bz < self.depth - edge and
                        random.random() < TREE_CHANCE):
                    tree_positions.append((wx, height, wz))

        for pos in tree_positions:
            self._plan_tree(pos)

        print(f"[World] Blocos planejados: {len(self._plan)}")

        created = 0
        for pos, btype in self._plan.items():
            if self._is_exposed(pos):
                block = Block(position=pos, block_type=btype)
                self.blocks[pos] = block
                created += 1

        print(f"[World] Entidades criadas: {created}")

    def _is_exposed(self, pos):
        x, y, z = pos
        for dx, dy, dz in FACE_DIRS:
            if (x+dx, y+dy, z+dz) not in self._plan:
                return True
        return False

    def _plan_tree(self, base):
        bx, by, bz = base
        trunk_height = random.randint(3, 5)
        for dy in range(trunk_height):
            self._plan[(bx, by + dy, bz)] = 'wood'
        top = by + trunk_height
        for dx in range(-2, 3):
            for dy in range(-1, 3):
                for dz in range(-2, 3):
                    dist = math.sqrt(dx**2 + (dy * 0.8)**2 + dz**2)
                    if dist <= 2.2:
                        pos = (bx + dx, top + dy, bz + dz)
                        if pos not in self._plan:
                            self._plan[pos] = 'leaves'

    # ── Culling por distância ─────────────────────────────────────────────
    def update_visibility(self, player_pos):
        """
        Ativa/desativa entidades baseado na distância XZ do jogador.
        Chamado a cada N frames no main.py para não sobrecarregar o update.
        """
        px, _, pz = player_pos
        r2 = VIEW_RADIUS * VIEW_RADIUS
        for pos, block in self.blocks.items():
            dx = pos[0] - px
            dz = pos[2] - pz
            block.enabled = (dx*dx + dz*dz) <= r2

    # ── Modificação ───────────────────────────────────────────────────────
    def add_block(self, position, block_type='grass'):
        pos = (int(position[0]), int(position[1]), int(position[2]))
        if pos in self.blocks or pos in self._plan:
            return None
        self._plan[pos] = block_type
        block = Block(position=pos, block_type=block_type)
        self.blocks[pos] = block
        self._reveal_neighbors(pos)
        return block

    def remove_block(self, position):
        pos = (int(position[0]), int(position[1]), int(position[2]))
        if pos not in self.blocks:
            return False
        destroy(self.blocks[pos])
        del self.blocks[pos]
        del self._plan[pos]
        self._reveal_neighbors(pos)
        return True

    def _reveal_neighbors(self, pos):
        x, y, z = pos
        for dx, dy, dz in FACE_DIRS:
            npos = (x+dx, y+dy, z+dz)
            if npos in self._plan and npos not in self.blocks:
                block = Block(position=npos, block_type=self._plan[npos])
                self.blocks[npos] = block

    # ── Save / Load ───────────────────────────────────────────────────────
    def save(self, filename=SAVE_FILE):
        data = {
            'seed':  self.seed,
            'width': self.width,
            'depth': self.depth,
            'plan':  {f"{x},{y},{z}": btype for (x,y,z), btype in self._plan.items()},
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))
        size_kb = os.path.getsize(filename) / 1024
        print(f"[World] Salvo em '{filename}'  ({size_kb:.1f} KB)")

    def load(self, filename=SAVE_FILE):
        if not os.path.exists(filename):
            print(f"[World] '{filename}' nao encontrado.")
            return False
        for block in self.blocks.values():
            destroy(block)
        self.blocks.clear()
        self._plan.clear()

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.seed  = data.get('seed',  self.seed)
        self.width = data.get('width', self.width)
        self.depth = data.get('depth', self.depth)
        self._ox   = self.width  // 2
        self._oz   = self.depth  // 2

        for key, btype in data['plan'].items():
            x, y, z = map(int, key.split(','))
            self._plan[(x,y,z)] = btype

        created = 0
        for pos, btype in self._plan.items():
            if self._is_exposed(pos):
                block = Block(position=pos, block_type=btype)
                self.blocks[pos] = block
                created += 1

        print(f"[World] Carregado | {created} entidades")
        return True

    def get_block(self, position):
        pos = (int(position[0]), int(position[1]), int(position[2]))
        return self.blocks.get(pos)

    def spawn_height(self):
        return self._get_height(self.width // 2, self.depth // 2) + 3
