"""
block.py — Bloco voxel com TEXTURAS para Ursina 8.x.
Requer que as texturas em /textures/ tenham sido geradas
pelo script generate_textures.py (usando Pillow).
"""

import os
from ursina import *

# ─────────────────────────────────────────────────────────────────────────────
# Utilitário de cor (mantido para o HUD e fallback)
# ─────────────────────────────────────────────────────────────────────────────
def rgb(r, g, b):
    return color.Color(r / 255, g / 255, b / 255, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Definição dos tipos de bloco
# ─────────────────────────────────────────────────────────────────────────────
BLOCK_TYPES = {
    'grass':       {'color': rgb(106, 166,  85), 'name': 'Grama',      'hardness': 1},
    'dirt':        {'color': rgb(134,  96,  67), 'name': 'Terra',      'hardness': 1},
    'stone':       {'color': rgb(128, 128, 128), 'name': 'Pedra',      'hardness': 3},
    'sand':        {'color': rgb(210, 195, 140), 'name': 'Areia',      'hardness': 1},
    'wood':        {'color': rgb(101,  67,  33), 'name': 'Madeira',    'hardness': 2},
    'leaves':      {'color': rgb( 50, 110,  40), 'name': 'Folhas',     'hardness': 1},
    'planks':      {'color': rgb(180, 140,  80), 'name': 'Tabua',      'hardness': 2},
    'cobblestone': {'color': rgb(105, 105, 105), 'name': 'Pedregulho', 'hardness': 3},
}

INVENTORY_ORDER = ['grass', 'dirt', 'stone', 'sand', 'wood', 'planks', 'cobblestone']

TEXTURE_DIR = 'textures'


# ─────────────────────────────────────────────────────────────────────────────
# Cache de texturas — cada arquivo é carregado uma única vez
# ─────────────────────────────────────────────────────────────────────────────
_texture_cache: dict = {}

def _load_texture(block_type: str):
    """
    Carrega a textura do disco na primeira chamada e devolve do cache
    nas chamadas seguintes. Retorna None se o arquivo não existir.
    """
    if block_type in _texture_cache:
        return _texture_cache[block_type]

    path = os.path.join(TEXTURE_DIR, f'{block_type}.png')
    if os.path.isfile(path):
        tex = load_texture(path)
    else:
        tex = None   # fallback para cor sólida
        print(f'[Block] Textura não encontrada: {path} — usando cor sólida.')

    _texture_cache[block_type] = tex
    return tex


# ─────────────────────────────────────────────────────────────────────────────
# Classe Block
# ─────────────────────────────────────────────────────────────────────────────
class Block(Entity):
    def __init__(self, position=(0, 0, 0), block_type='grass'):
        props = BLOCK_TYPES.get(block_type, BLOCK_TYPES['grass'])
        self._base_color = props['color']

        tex = _load_texture(block_type)

        super().__init__(
            model='cube',
            texture=tex,                              # textura ou None
            color=color.white if tex else self._base_color,  # branco = sem tingir a textura
            position=position,
            collider='box',
        )

        self.block_type = block_type
        self.name       = props['name']
        self.hardness   = props['hardness']

    # ── Hover ──────────────────────────────────────────────────────────────
    def on_mouse_enter(self):
        if self.texture:
            # Tingimento sutil para indicar hover sem desaparecer a textura
            self.color = color.Color(1.25, 1.25, 1.25, 1)
        else:
            c = self._base_color
            self.color = color.Color(
                min(c.r + 0.2, 1),
                min(c.g + 0.2, 1),
                min(c.b + 0.2, 1), 1
            )

    def on_mouse_exit(self):
        self.color = color.white if self.texture else self._base_color
