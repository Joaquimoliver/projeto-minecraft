"""
block.py — Bloco com topo correto na grama.
O quad filho é leve (sem collider) e é culled junto com o pai.
"""

import os
from ursina import *

def rgb(r, g, b):
    return color.Color(r/255, g/255, b/255, 1)

BLOCK_TYPES = {
    'grass':       {'color': rgb(106,166, 85), 'name': 'Grama',      'hardness': 1},
    'dirt':        {'color': rgb(134, 96, 67), 'name': 'Terra',      'hardness': 1},
    'stone':       {'color': rgb(128,128,128), 'name': 'Pedra',      'hardness': 3},
    'sand':        {'color': rgb(210,195,140), 'name': 'Areia',      'hardness': 1},
    'wood':        {'color': rgb(101, 67, 33), 'name': 'Madeira',    'hardness': 2},
    'leaves':      {'color': rgb( 50,110, 40), 'name': 'Folhas',     'hardness': 1},
    'planks':      {'color': rgb(180,140, 80), 'name': 'Tabua',      'hardness': 2},
    'cobblestone': {'color': rgb(105,105,105), 'name': 'Pedregulho', 'hardness': 3},
}

INVENTORY_ORDER = ['grass','dirt','stone','sand','wood','planks','cobblestone']
TEXTURE_DIR = 'textures'

_TEX_FILE = {
    'grass':       'grass_side.png',
    'dirt':        'dirt.png',
    'stone':       'stone.png',
    'sand':        'sand.png',
    'wood':        'wood.png',
    'leaves':      'leaves.png',
    'planks':      'planks.png',
    'cobblestone': 'cobblestone.png',
}

_tex_cache = {}

def _load_tex(name):
    if name in _tex_cache:
        return _tex_cache[name]
    path = os.path.join(TEXTURE_DIR, name)
    tex  = load_texture(path) if os.path.isfile(path) else None
    _tex_cache[name] = tex
    return tex


class Block(Entity):
    def __init__(self, position=(0,0,0), block_type='grass'):
        props = BLOCK_TYPES.get(block_type, BLOCK_TYPES['grass'])
        self._base_color = props['color']

        tex = _load_tex(_TEX_FILE.get(block_type, f'{block_type}.png'))

        super().__init__(
            model    = 'cube',
            texture  = tex,
            color    = color.white if tex else self._base_color,
            position = position,
            collider = 'box',
        )

        self.block_type = block_type
        self.name       = props['name']
        self.hardness   = props['hardness']

        # Topo verde da grama — quad filho leve (sem collider)
        # É culled automaticamente junto com o bloco pai
        self._top = None
        if block_type == 'grass':
            top_tex = _load_tex('grass_top.png')
            if top_tex:
                self._top = Entity(
                    parent     = self,
                    model      = 'quad',
                    texture    = top_tex,
                    color      = color.white,
                    position   = (0, 0.501, 0),
                    rotation_x = 90,
                    scale      = 1.0,
                )

    def on_mouse_enter(self):
        self.color = color.Color(1.3,1.3,1.3,1) if self.texture else color.Color(
            min(self._base_color.r+0.2,1), min(self._base_color.g+0.2,1),
            min(self._base_color.b+0.2,1), 1)
        if self._top:
            self._top.color = color.Color(1.3,1.3,1.3,1)

    def on_mouse_exit(self):
        self.color = color.white if self.texture else self._base_color
        if self._top:
            self._top.color = color.white
