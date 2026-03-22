"""
block.py — Bloco voxel com TEXTURAS procedurais (Ursina 8.x).
Texturas são geradas uma única vez e cacheadas em textures/
Grass blocks têm modelo procedural com topo verde e laterais marrom!
"""

from ursina import *
from panda3d.core import CardMaker, NodePath

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

def create_grass_block_model():
    """Cria um modelo de grass block com topo verde e laterais marrom usando 6 planos."""
    
    # Carrega as texturas
    top_tex = _load_texture('textures/grass_top.png')
    side_tex = _load_texture('textures/grass_side.png')
    
    # Cria um Entity vazio para conter os 6 planos
    grass_model = Entity(model=None)
    
    # Dimensões do bloco
    size = 0.5
    
    # Topo (verde com grama)
    if top_tex:
        top = Entity(
            model='quad',
            texture=top_tex,
            position=(0, size, 0),
            rotation=(0, 0, 0),
            scale=(size*2, size*2, 1),
            parent=grass_model,
        )
    
    # Fundo (marrom com terra)
    if side_tex:
        bottom = Entity(
            model='quad',
            texture=side_tex,
            position=(0, -size, 0),
            rotation=(180, 0, 0),
            scale=(size*2, size*2, 1),
            parent=grass_model,
        )
    
    # Frente (marrom com terra)
    if side_tex:
        front = Entity(
            model='quad',
            texture=side_tex,
            position=(0, 0, size),
            rotation=(90, 0, 0),
            scale=(size*2, size*2, 1),
            parent=grass_model,
        )
    
    # Trás (marrom com terra)
    if side_tex:
        back = Entity(
            model='quad',
            texture=side_tex,
            position=(0, 0, -size),
            rotation=(90, 180, 0),
            scale=(size*2, size*2, 1),
            parent=grass_model,
        )
    
    # Esquerda (marrom com terra)
    if side_tex:
        left = Entity(
            model='quad',
            texture=side_tex,
            position=(-size, 0, 0),
            rotation=(90, 90, 0),
            scale=(size*2, size*2, 1),
            parent=grass_model,
        )
    
    # Direita (marrom com terra)
    if side_tex:
        right = Entity(
            model='quad',
            texture=side_tex,
            position=(size, 0, 0),
            rotation=(90, -90, 0),
            scale=(size*2, size*2, 1),
            parent=grass_model,
        )
    
    return grass_model

class Block(Entity):
    def __init__(self, position=(0,0,0), block_type='grass'):
        props = BLOCK_TYPES.get(block_type, BLOCK_TYPES['grass'])
        self._base_color = props['color']
        
        # Tenta carregar textura; usa cor fallback se não existir
        texture = _load_texture(props['texture'])
        
        # Para grass block, usar modelo especial com topo/lateral separados
        if block_type == 'grass':
            # Criar como Entity vazia (vamos preencher com planos)
            super().__init__(
                model=None,
                position=position,
                collider='box',
            )
            
            # Adicionar os 6 planos (topo verde, laterais marrom)
            self._create_grass_faces()
            
        else:
            # Blocos normais: cubo com textura única
            super().__init__(
                model='cube',
                texture=texture,
                color=self._base_color,
                position=position,
                collider='box',
            )

        self.block_type = block_type
        self.name       = props['name']
        self.hardness   = props['hardness']

    def _create_grass_faces(self):
        """Cria os 6 planos para o bloco de grama."""
        top_tex = _load_texture('textures/grass_top.png')
        side_tex = _load_texture('textures/grass_side.png')
        
        size = 0.5
        
        # Topo (verde com grama)
        if top_tex:
            Entity(
                model='quad',
                texture=top_tex,
                position=(0, size, 0),
                rotation=(90, 0, 0),
                scale=(size*2, size*2, 1),
                parent=self,
            )
        
        # Fundo (marrom com terra)
        if side_tex:
            Entity(
                model='quad',
                texture=side_tex,
                position=(0, -size, 0),
                rotation=(90, 0, 180),
                scale=(size*2, size*2, 1),
                parent=self,
            )
        
        # Frente (marrom com terra)
        if side_tex:
            Entity(
                model='quad',
                texture=side_tex,
                position=(0, 0, size),
                rotation=(0, 0, 0),
                scale=(size*2, size*2, 1),
                parent=self,
            )
        
        # Trás (marrom com terra)
        if side_tex:
            Entity(
                model='quad',
                texture=side_tex,
                position=(0, 0, -size),
                rotation=(0, 0, 180),
                scale=(size*2, size*2, 1),
                parent=self,
            )
        
        # Esquerda (marrom com terra)
        if side_tex:
            Entity(
                model='quad',
                texture=side_tex,
                position=(-size, 0, 0),
                rotation=(0, 90, 0),
                scale=(size*2, size*2, 1),
                parent=self,
            )
        
        # Direita (marrom com terra)
        if side_tex:
            Entity(
                model='quad',
                texture=side_tex,
                position=(size, 0, 0),
                rotation=(0, -90, 0),
                scale=(size*2, size*2, 1),
                parent=self,
            )

    def on_mouse_enter(self):
        """Efeito highlight ao passar mouse."""
        if self.block_type != 'grass':
            c = self._base_color
            self.color = color.Color(min(c.r+0.2,1), min(c.g+0.2,1), min(c.b+0.2,1), 1)

    def on_mouse_exit(self):
        if self.block_type != 'grass':
            self.color = self._base_color
