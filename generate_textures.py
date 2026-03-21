"""
generate_textures.py — Gera texturas 16x16 + atlas para o jogo.
Execute UMA VEZ: python generate_textures.py
Requer: pip install Pillow
"""

import os
import random
from PIL import Image, ImageDraw

OUTPUT_DIR = 'textures'
SIZE = 16
os.makedirs(OUTPUT_DIR, exist_ok=True)
random.seed(42)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def new_img():
    return Image.new('RGBA', (SIZE, SIZE))

def noise_pixel(r, g, b, spread=18):
    d = random.randint(-spread, spread)
    return (max(0,min(255,r+d)), max(0,min(255,g+d)), max(0,min(255,b+d)), 255)

def fill_noise(img, r, g, b, spread=18):
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            px[x, y] = noise_pixel(r, g, b, spread)
    return img

def save(img, name):
    path = os.path.join(OUTPUT_DIR, f'{name}.png')
    img.save(path)
    print(f'  OK  {path}')
    return img

# ─── Texturas ─────────────────────────────────────────────────────────────────

def make_grass_top():
    img = fill_noise(new_img(), 95, 175, 70, 22)
    px  = img.load()
    for _ in range(14):
        x, y = random.randint(0,SIZE-1), random.randint(0,SIZE-1)
        px[x,y] = noise_pixel(55, 140, 40, 10)
    return save(img, 'grass_top')

def make_grass_side():
    """Lateral: faixa verde fina no TOPO (y=0..3), terra embaixo (y=4..15)."""
    img = new_img()
    px  = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            if y == 0:
                px[x,y] = noise_pixel(95, 175, 70, 18)
            elif y == 1:
                px[x,y] = noise_pixel(80, 155, 58, 15)
            elif y == 2:
                px[x,y] = noise_pixel(110, 120, 68, 12)
            elif y == 3:
                px[x,y] = noise_pixel(128, 105, 70, 12)
            else:
                px[x,y] = noise_pixel(134, 96, 67, 18)
    for _ in range(10):
        x = random.randint(0, SIZE-1)
        y = random.randint(5, SIZE-1)
        px[x,y] = noise_pixel(90, 60, 38, 8)
    return save(img, 'grass_side')

def make_dirt():
    img = fill_noise(new_img(), 134, 96, 67, 20)
    px  = img.load()
    for _ in range(14):
        x, y = random.randint(0,SIZE-1), random.randint(0,SIZE-1)
        px[x,y] = noise_pixel(90, 60, 40, 8)
    return save(img, 'dirt')

def make_stone():
    img = fill_noise(new_img(), 128, 128, 128, 16)
    px  = img.load()
    for _ in range(10):
        x0 = random.randint(0, SIZE-1)
        y0 = random.randint(0, SIZE-1)
        for i in range(random.randint(2,5)):
            nx = max(0, min(SIZE-1, x0+random.randint(-1,1)))
            ny = max(0, min(SIZE-1, y0+i))
            px[nx,ny] = (88,88,88,255)
    return save(img, 'stone')

def make_sand():
    img = fill_noise(new_img(), 210, 195, 140, 14)
    px  = img.load()
    for _ in range(20):
        x, y = random.randint(0,SIZE-1), random.randint(0,SIZE-1)
        v = random.randint(220, 240)
        px[x,y] = (v, v-10, v-40, 255)
    return save(img, 'sand')

def make_wood():
    img  = fill_noise(new_img(), 101, 67, 33, 12)
    draw = ImageDraw.Draw(img)
    px   = img.load()
    for x in range(0, SIZE, 3):
        for y in range(SIZE):
            r,g,b,a = px[x,y]
            px[x,y] = (max(0,r-20), max(0,g-15), max(0,b-10), 255)
    cx, cy = SIZE//2, SIZE//2
    for radius in [2,4,6]:
        draw.ellipse([cx-radius, cy-radius//2, cx+radius, cy+radius//2],
                     outline=(70,45,20,200), width=1)
    return save(img, 'wood')

def make_leaves():
    img = fill_noise(new_img(), 55, 120, 45, 20)
    px  = img.load()
    for _ in range(18):
        x, y = random.randint(0,SIZE-1), random.randint(0,SIZE-1)
        px[x,y] = (20, 60, 15, 255)
    for _ in range(10):
        x, y = random.randint(0,SIZE-1), random.randint(0,SIZE-1)
        px[x,y] = (100, 200, 60, 255)
    return save(img, 'leaves')

def make_planks():
    img     = new_img()
    px      = img.load()
    PLANK_H = 4
    for y in range(SIZE):
        plank  = y // PLANK_H
        for x in range(SIZE):
            px[x,y] = noise_pixel(175+plank*4, 135+plank*3, 75+plank*2, 12)
    for y in range(PLANK_H-1, SIZE, PLANK_H):
        for x in range(SIZE):
            px[x,y] = (90,60,30,255)
    for y in range(SIZE):
        joint_x = (8 + (y//PLANK_H)*5) % SIZE
        px[joint_x,y] = (90,60,30,255)
    return save(img, 'planks')

def make_cobblestone():
    img  = fill_noise(new_img(), 110, 110, 110, 14)
    draw = ImageDraw.Draw(img)
    for (x0,y0,x1,y1) in [(0,0,7,7),(9,0,15,7),(0,9,7,15),(9,9,15,15)]:
        draw.rectangle([x0,y0,x1,y1], outline=(70,70,70,255))
        draw.line([(x0+1,y0+1),(x1-1,y0+1)], fill=(155,155,155,255))
        draw.line([(x0+1,y0+1),(x0+1,y1-1)], fill=(155,155,155,255))
    return save(img, 'cobblestone')

# ─── Atlas ────────────────────────────────────────────────────────────────────
#
#  Layout (4 cols x 3 rows, cada célula 16x16):
#
#   col→  0            1            2       3
#   row0: grass_top    grass_side   dirt    stone
#   row1: sand         wood         leaves  planks
#   row2: cobblestone  ---          ---     ---
#
#  No Panda3D/Ursina: UV(0,0) = canto INFERIOR ESQUERDO da imagem
#  Então row_img=0 (topo da imagem) → v próximo de 1.0

ATLAS_COLS = 4
ATLAS_ROWS = 3

SLOT_MAP = {
    'grass_top':   (0, 0),
    'grass_side':  (1, 0),
    'dirt':        (2, 0),
    'stone':       (3, 0),
    'sand':        (0, 1),
    'wood':        (1, 1),
    'leaves':      (2, 1),
    'planks':      (3, 1),
    'cobblestone': (0, 2),
}


def build_atlas(textures: dict):
    atlas_w = ATLAS_COLS * SIZE
    atlas_h = ATLAS_ROWS * SIZE
    atlas   = Image.new('RGBA', (atlas_w, atlas_h), (0,0,0,0))
    for name, (col, row_img) in SLOT_MAP.items():
        if name in textures:
            atlas.paste(textures[name], (col * SIZE, row_img * SIZE))
    path = os.path.join(OUTPUT_DIR, 'atlas.png')
    atlas.save(path)
    print(f'\n  OK  Atlas -> {path}  ({atlas_w}x{atlas_h}px)')

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f'\nGerando texturas em ./{OUTPUT_DIR}/ ...\n')
    textures = {
        'grass_top':   make_grass_top(),
        'grass_side':  make_grass_side(),
        'dirt':        make_dirt(),
        'stone':       make_stone(),
        'sand':        make_sand(),
        'wood':        make_wood(),
        'leaves':      make_leaves(),
        'planks':      make_planks(),
        'cobblestone': make_cobblestone(),
    }
    # grass.png para o HUD (usa a lateral)
    textures['grass_side'].save(os.path.join(OUTPUT_DIR, 'grass.png'))
    build_atlas(textures)
    print('\nPronto! python main.py')
