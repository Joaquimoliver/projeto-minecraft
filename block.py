"""
block.py — Bloco voxel com TEXTURAS procedurais (Ursina 8.x).
Texturas são geradas uma única vez e cacheadas em textures/
"""

from ursina import *

def rgb(r, g, b):
    return color.Color(r/255, g/255, b/255, 1)

BLOCK_TYPES = {
    'grass':       {'color': rgb(106,166, 85), 'name': 'Grama',      'hardness': 1, 'texture': 'textures/grass.png'},
    'dirt':        {'color': rgb(134, 96, 67), 'name': 'Terra',      'hardness': 1, 'texture': 'textures/dirt.png'},
    'stone':       {'color': rgb(128,128,128), 'name': 'Pedra',      'hardness': 3, 'texture': 'textures/stone.png'},
    'sand':        {'color': rgb(210,195,140), 'name': 'Areia',      'hardness': 1, 'texture': 'textures/sand.png'},
    'wood':        {'color': rgb(101, 67, 33), 'name': 'Madeira',    'hardness': 2, 'texture': 'textures/wood.png'},
    'leaves':      {'color': rgb( 50,110, 40), 'name': 'Folhas',     'hardness': 1, 'texture': 'textures/leaves.png'},
    'planks':      {'color': rgb(180,140, 80), 'name': 'Tabua',      'hardness': 2, 'texture': 'textures/planks.png'},
    'cobblestone': {'color': rgb(105,105,105), 'name': 'Pedregulho', 'hardness': 3, 'texture': 'textures/cobblestone.png'},
}

INVENTORY_ORDER = ['grass','dirt','stone','sand','wood','planks','cobblestone']

# Cache de texturas (carregadas uma única vez)
_texture_cache = {}

def _load_texture(texture_path):
    """Carrega textura uma vez e cacheia."""
    if texture_path in _texture_cache:
        return _texture_cache[texture_path]
    
    try:
        tex = load_texture(texture_path)
        _texture_cache[texture_path] = tex
        return tex
    except:
        # Fallback se textura não existir (ainda)
        return None

class Block(Entity):
    def __init__(self, position=(0,0,0), block_type='grass'):
        props = BLOCK_TYPES.get(block_type, BLOCK_TYPES['grass'])
        self._base_color = props['color']
        
        # Tenta carregar textura; usa cor fallback se não existir
        texture = _load_texture(props['texture'])

        super().__init__(
            model='cube',
            texture=texture,  # Aplica textura se disponível
            color=self._base_color,  # Cor base (fallback ou tint)
            position=position,
            collider='box',
        )

        self.block_type = block_type
        self.name       = props['name']
        self.hardness   = props['hardness']

    def on_mouse_enter(self):
        """Efeito highlight ao passar mouse."""
        c = self._base_color
        self.color = color.Color(min(c.r+0.2,1), min(c.g+0.2,1), min(c.b+0.2,1), 1)

    def on_mouse_exit(self):
        self.color = self._base_color
