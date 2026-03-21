"""
block.py — Bloco voxel otimizado para Ursina 8.x.
Sem textura = menos overhead de GPU por bloco.
"""

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


class Block(Entity):
    def __init__(self, position=(0,0,0), block_type='grass'):
        props = BLOCK_TYPES.get(block_type, BLOCK_TYPES['grass'])
        self._base_color = props['color']

        super().__init__(
            model='cube',
            color=self._base_color,
            position=position,
            collider='box',
            # SEM textura = muito mais rápido (cor sólida é 1 draw call simples)
        )

        self.block_type = block_type
        self.name       = props['name']
        self.hardness   = props['hardness']

    def on_mouse_enter(self):
        c = self._base_color
        self.color = color.Color(min(c.r+0.2,1), min(c.g+0.2,1), min(c.b+0.2,1), 1)

    def on_mouse_exit(self):
        self.color = self._base_color
