"""
world.py — Chunk Mesh Merging  (v3 — sem gaps, FPS estável)

Correções:
  · double_sided=True no mesh  → elimina os gaps/rasgos de céu
  · SEM collider='mesh' (lentíssimo) → colisão por caixas invisíveis
    de superfície (1 box por coluna X,Z do chunk, na altura do topo)
  · Winding order revisado para todas as 6 faces
"""

import math, random, json, os
from ursina import *
from block import BLOCK_TYPES

# =============================================================================
CHUNK_SIZE      = 16
RENDER_DISTANCE = 2
BASE_HEIGHT     = 4
MAX_HEIGHT      = 9
TREE_CHANCE     = 0.04
SAVE_FILE       = 'savegame.json'

# normal → offset dos 4 vértices (CCW visto de fora)
FACE_DATA = {
    'top':    ((0, 1, 0),  [(-0.5, 0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5, 0.5, 0.5),(-0.5, 0.5, 0.5)]),
    'bottom': ((0,-1, 0),  [(-0.5,-0.5, 0.5),( 0.5,-0.5, 0.5),( 0.5,-0.5,-0.5),(-0.5,-0.5,-0.5)]),
    'right':  (( 1, 0, 0), [( 0.5,-0.5, 0.5),( 0.5, 0.5, 0.5),( 0.5, 0.5,-0.5),( 0.5,-0.5,-0.5)]),
    'left':   ((-1, 0, 0), [(-0.5,-0.5,-0.5),(-0.5, 0.5,-0.5),(-0.5, 0.5, 0.5),(-0.5,-0.5, 0.5)]),
    'front':  ((0, 0, 1),  [( 0.5,-0.5, 0.5),( 0.5, 0.5, 0.5),(-0.5, 0.5, 0.5),(-0.5,-0.5, 0.5)]),
    'back':   ((0, 0,-1),  [(-0.5,-0.5,-0.5),(-0.5, 0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5,-0.5,-0.5)]),
}

FACE_BRIGHTNESS = {
    'top': 1.00, 'bottom': 0.45,
    'right': 0.75, 'left': 0.65,
    'front': 0.85, 'back': 0.60,
}

# =============================================================================
def _smooth_noise(x, z, seed):
    s = seed * 0.1
    v = (
        math.sin((x+s)*0.25)*0.40 + math.cos((z+s)*0.25)*0.40 +
        math.sin((x+z+s)*0.15)*0.25 + math.cos((x-z+s)*0.18)*0.20 +
        math.sin((x*1.7+s)*0.10)*0.10 + math.cos((z*1.5+s)*0.10)*0.10
    )
    return (v + 1.45) / 2.90


class World:
    def __init__(self, seed=None):
        self.seed            = seed if seed is not None else random.randint(0, 99_999)
        self._plan           = {}   # (x,y,z) → block_type
        self._chunks         = {}   # (cx,cz) → set of positions
        self._render_ents    = {}   # (cx,cz) → Entity (mesh visual, sem collider)
        self._collider_ents  = {}   # (cx,cz) → list[Entity] (boxes invisíveis de colisão)
        self._load_queue     = []
        self._player_chunk   = None
        print(f"[World] Seed={self.seed} | MESH MERGING v3")

    # ——— Helpers ——————————————————————————————————————————————————————————
    def _world_to_chunk(self, x, z):
        return (int(math.floor(x / CHUNK_SIZE)), int(math.floor(z / CHUNK_SIZE)))

    def _get_height(self, x, z):
        n = _smooth_noise(x, z, self.seed)
        return max(BASE_HEIGHT, min(int(n*(MAX_HEIGHT-BASE_HEIGHT))+BASE_HEIGHT, MAX_HEIGHT))

    # ——— Carga inicial ————————————————————————————————————————————————————
    def initial_load(self):
        total = (2*RENDER_DISTANCE+1)**2
        print(f"[World] Gerando {total} chunks...")
        for dcx in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
            for dcz in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
                self._load_chunk(dcx, dcz)
        self._player_chunk = (0, 0)
        print(f"[World] OK — {len(self._plan)} blocos | "
              f"{len(self._render_ents)} meshes")

    # ——— Loop dinâmico ————————————————————————————————————————————————————
    def update_chunks(self, player_pos):
        if self._load_queue:
            self._load_chunk(*self._load_queue.pop(0))
            return
        cx, cz = self._world_to_chunk(player_pos.x, player_pos.z)
        if (cx, cz) == self._player_chunk:
            return
        self._player_chunk = (cx, cz)
        desired = {
            (cx+dx, cz+dz)
            for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE+1)
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE+1)
        }
        for c in [k for k in self._chunks if k not in desired]:
            self._unload_chunk(c)
        self._load_queue = sorted(
            [c for c in desired if c not in self._chunks],
            key=lambda c: (c[0]-cx)**2 + (c[1]-cz)**2
        )

    # ——— Geração do plano lógico ——————————————————————————————————————————
    def _build_chunk_plan(self, cx, cz):
        plan, trees = {}, []
        for lx in range(CHUNK_SIZE):
            for lz in range(CHUNK_SIZE):
                wx, wz = cx*CHUNK_SIZE+lx, cz*CHUNK_SIZE+lz
                h = self._get_height(wx, wz)
                for wy in range(h):
                    if   wy == h-1: bt = 'grass'
                    elif wy >= h-3: bt = 'dirt'
                    else:           bt = 'stone'
                    plan[(wx, wy, wz)] = bt
                if random.random() < TREE_CHANCE:
                    trees.append((wx, h, wz))
        rng = random.Random(self.seed ^ (cx*73856093) ^ (cz*19349663))
        for spot in trees:
            self._add_tree(spot, plan, rng)
        return plan

    def _add_tree(self, base, plan, rng):
        bx, by, bz = base
        th = rng.randint(3, 5)
        for dy in range(th):
            plan[(bx, by+dy, bz)] = 'wood'
        top = by + th
        for dx in range(-2, 3):
            for dy in range(-1, 3):
                for dz in range(-2, 3):
                    if math.sqrt(dx**2+(dy*0.8)**2+dz**2) <= 2.2:
                        p = (bx+dx, top+dy, bz+dz)
                        if p not in plan:
                            plan[p] = 'leaves'

    # ——— MESH — apenas visual, SEM collider ——————————————————————————————
    def _build_render_entity(self, cx, cz):
        positions = self._chunks.get((cx, cz), set())
        verts, tris, cols, norms = [], [], [], []
        vi = 0
        for pos in positions:
            bt = self._plan.get(pos)
            if bt is None:
                continue
            base_c = BLOCK_TYPES[bt]['color']
            x, y, z = pos
            for face, (normal, offsets) in FACE_DATA.items():
                nx, ny, nz = normal
                if (x+nx, y+ny, z+nz) in self._plan:
                    continue
                b = FACE_BRIGHTNESS[face]
                c = color.Color(base_c.r*b, base_c.g*b, base_c.b*b, 1)
                for ox, oy, oz in offsets:
                    verts.append(Vec3(x+ox, y+oy, z+oz))
                    cols.append(c)
                    norms.append(Vec3(nx, ny, nz))
                tris += [vi, vi+1, vi+2, vi, vi+2, vi+3]
                vi += 4
        if not verts:
            return None
        mesh = Mesh(vertices=verts, triangles=tris, colors=cols, normals=norms)
        # double_sided=True elimina os gaps/rasgos do céu
        ent = Entity(model=mesh, double_sided=True)
        ent.is_chunk = True
        return ent

    # ——— COLISÃO — caixas invisíveis na superfície por coluna ————————————
    def _build_collider_entities(self, cx, cz):
        """
        Para cada coluna (x, z) do chunk: encontra o bloco mais alto
        e cria uma caixa invisível 1×1×1 nele.
        Muito mais leve que mesh collider.
        """
        positions = self._chunks.get((cx, cz), set())
        # top_y[x,z] = y mais alto do _plan nessa coluna
        top_y = {}
        for (px, py, pz) in positions:
            key = (px, pz)
            if key not in top_y or py > top_y[key]:
                top_y[key] = py

        ents = []
        for (px, pz), py in top_y.items():
            e = Entity(
                position=(px, py, pz),
                collider='box',
                visible=False,
                scale=(1, 1, 1),
            )
            ents.append(e)
        return ents

    # ——— Rebuild de um chunk ——————————————————————————————————————————————
    def _rebuild_chunk(self, cx, cz):
        # Visual
        old = self._render_ents.pop((cx, cz), None)
        if old:
            destroy(old)
        # Colisão
        for e in self._collider_ents.pop((cx, cz), []):
            destroy(e)

        if (cx, cz) in self._chunks:
            ent = self._build_render_entity(cx, cz)
            if ent:
                self._render_ents[(cx, cz)] = ent
            col_ents = self._build_collider_entities(cx, cz)
            if col_ents:
                self._collider_ents[(cx, cz)] = col_ents

    # ——— Carga / Descarga ————————————————————————————————————————————————
    def _load_chunk(self, cx, cz):
        if (cx, cz) in self._chunks:
            return
        plan = self._build_chunk_plan(cx, cz)
        self._plan.update(plan)
        self._chunks[(cx, cz)] = set(plan.keys())

        ent = self._build_render_entity(cx, cz)
        if ent:
            self._render_ents[(cx, cz)] = ent
        col_ents = self._build_collider_entities(cx, cz)
        if col_ents:
            self._collider_ents[(cx, cz)] = col_ents

        # Atualiza bordas dos vizinhos (remove faces que agora ficaram ocultas)
        for dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nc = (cx+dc[0], cz+dc[1])
            if nc in self._chunks:
                self._rebuild_chunk(*nc)

    def _unload_chunk(self, cx, cz):
        if (cx, cz) not in self._chunks:
            return
        for pos in self._chunks.pop((cx, cz)):
            self._plan.pop(pos, None)
        old = self._render_ents.pop((cx, cz), None)
        if old:
            destroy(old)
        for e in self._collider_ents.pop((cx, cz), []):
            destroy(e)

    # ——— Modificação em tempo real ————————————————————————————————————————
    def add_block(self, position, block_type='grass'):
        pos = (int(position[0]), int(position[1]), int(position[2]))
        if pos in self._plan:
            return False
        self._plan[pos] = block_type
        cx, cz = self._world_to_chunk(pos[0], pos[2])
        if (cx, cz) in self._chunks:
            self._chunks[(cx, cz)].add(pos)
            self._rebuild_chunk(cx, cz)
            for dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nc = (cx+dc[0], cz+dc[1])
                if nc in self._chunks:
                    self._rebuild_chunk(*nc)
        return True

    def remove_block(self, position):
        pos = (int(position[0]), int(position[1]), int(position[2]))
        if pos not in self._plan:
            return False
        del self._plan[pos]
        cx, cz = self._world_to_chunk(pos[0], pos[2])
        if (cx, cz) in self._chunks:
            self._chunks[(cx, cz)].discard(pos)
            self._rebuild_chunk(cx, cz)
            for dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nc = (cx+dc[0], cz+dc[1])
                if nc in self._chunks:
                    self._rebuild_chunk(*nc)
        return True

    # ——— Utilitários ——————————————————————————————————————————————————————
    def spawn_height(self):
        return self._get_height(0, 0) + 3

    @property
    def chunk_coords(self):
        return self._player_chunk or (0, 0)

    @property
    def entity_count(self):
        return len(self._render_ents)

    @property
    def block_count(self):
        return len(self._plan)

    # ——— Save / Load ——————————————————————————————————————————————————————
    def save(self, filename=SAVE_FILE):
        data = {
            'seed': self.seed,
            'plan': {f"{x},{y},{z}": bt for (x,y,z), bt in self._plan.items()},
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))
        kb = os.path.getsize(filename) / 1024
        print(f"[World] Salvo ({kb:.1f} KB, {self.block_count} blocos)")

    def load(self, filename=SAVE_FILE):
        if not os.path.exists(filename):
            return False
        for e in self._render_ents.values():
            destroy(e)
        for lst in self._collider_ents.values():
            for e in lst: destroy(e)
        self._render_ents.clear()
        self._collider_ents.clear()
        self._plan.clear()
        self._chunks.clear()
        self._load_queue.clear()
        self._player_chunk = None

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.seed = data.get('seed', self.seed)
        for key, bt in data['plan'].items():
            x, y, z = map(int, key.split(','))
            pos = (x, y, z)
            self._plan[pos] = bt
            cx, cz = self._world_to_chunk(x, z)
            self._chunks.setdefault((cx, cz), set()).add(pos)

        for (cx, cz) in list(self._chunks):
            ent = self._build_render_entity(cx, cz)
            if ent:
                self._render_ents[(cx, cz)] = ent
            col_ents = self._build_collider_entities(cx, cz)
            if col_ents:
                self._collider_ents[(cx, cz)] = col_ents

        print(f"[World] Carregado! {self.block_count} blocos | "
              f"{self.entity_count} meshes")
        return True
