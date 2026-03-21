"""
generate_textures.py — Gera texturas 16x16 para cada tipo de bloco.
Execute UMA VEZ antes de rodar o jogo: python generate_textures.py
Requer: pip install Pillow
"""

import os
import random
from PIL import Image, ImageDraw

OUTPUT_DIR = 'textures'
SIZE = 16

os.makedirs(OUTPUT_DIR, exist_ok=True)
random.seed(42)


def new_img():
    return Image.new('RGBA', (SIZE, SIZE))

def noise_pixel(r, g, b, spread=18):
    d = random.randint(-spread, spread)
    return (max(0, min(255, r+d)), max(0, min(255, g+d)), max(0, min(255, b+d)), 255)

def fill_noise(img, r, g, b, spread=18):
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            px[x, y] = noise_pixel(r, g, b, spread)
    return img

def save(img, name):
    path = os.path.join(OUTPUT_DIR, f'{name}.png')
    img.save(path)
    print(f'  ✔  {path}')


# ─── GRASS (lado) ─────────────────────────────────────────────────────────────
# Faixa verde fina no topo, terra embaixo — igual ao Minecraft clássico
def make_grass():
    img = new_img()
    px  = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            if y <= 1:
                px[x, y] = noise_pixel(95, 175, 70, 18)   # verde topo
            elif y <= 3:
                t = (y - 2) / 2.0
                r = int(95  + t * (134 - 95))
                g = int(155 + t * (96  - 155))
                b = int(60  + t * (67  - 60))
                px[x, y] = noise_pixel(r, g, b, 12)        # transição
            else:
                px[x, y] = noise_pixel(134, 96, 67, 16)    # terra
    for _ in range(10):
        x = random.randint(0, SIZE-1)
        y = random.randint(5, SIZE-1)
        px[x, y] = noise_pixel(90, 60, 38, 8)
    save(img, 'grass')


# ─── DIRT ─────────────────────────────────────────────────────────────────────
def make_dirt():
    img = fill_noise(new_img(), 134, 96, 67, 20)
    px  = img.load()
    for _ in range(14):
        x, y = random.randint(0, SIZE-1), random.randint(0, SIZE-1)
        px[x, y] = noise_pixel(90, 60, 40, 8)
    save(img, 'dirt')


# ─── STONE ────────────────────────────────────────────────────────────────────
def make_stone():
    img = fill_noise(new_img(), 128, 128, 128, 16)
    px  = img.load()
    for _ in range(10):
        x0 = random.randint(0, SIZE-1)
        y0 = random.randint(0, SIZE-1)
        for i in range(random.randint(2, 5)):
            nx = max(0, min(SIZE-1, x0 + random.randint(-1, 1)))
            ny = max(0, min(SIZE-1, y0 + i))
            px[nx, ny] = (88, 88, 88, 255)
    save(img, 'stone')


# ─── SAND ─────────────────────────────────────────────────────────────────────
def make_sand():
    img = fill_noise(new_img(), 210, 195, 140, 14)
    px  = img.load()
    for _ in range(20):
        x, y = random.randint(0, SIZE-1), random.randint(0, SIZE-1)
        v = random.randint(220, 240)
        px[x, y] = (v, v-10, v-40, 255)
    save(img, 'sand')


# ─── WOOD ─────────────────────────────────────────────────────────────────────
def make_wood():
    img  = fill_noise(new_img(), 101, 67, 33, 12)
    draw = ImageDraw.Draw(img)
    px   = img.load()
    for x in range(0, SIZE, 3):
        for y in range(SIZE):
            r, g, b, a = px[x, y]
            px[x, y] = (max(0, r-20), max(0, g-15), max(0, b-10), 255)
    cx, cy = SIZE//2, SIZE//2
    for radius in [2, 4, 6]:
        draw.ellipse([cx-radius, cy-radius//2, cx+radius, cy+radius//2],
                     outline=(70, 45, 20, 200), width=1)
    save(img, 'wood')


# ─── LEAVES ───────────────────────────────────────────────────────────────────
def make_leaves():
    img = fill_noise(new_img(), 55, 120, 45, 20)
    px  = img.load()
    for _ in range(18):
        x, y = random.randint(0, SIZE-1), random.randint(0, SIZE-1)
        px[x, y] = (20, 60, 15, 255)
    for _ in range(10):
        x, y = random.randint(0, SIZE-1), random.randint(0, SIZE-1)
        px[x, y] = (100, 200, 60, 255)
    save(img, 'leaves')


# ─── PLANKS ───────────────────────────────────────────────────────────────────
def make_planks():
    img     = new_img()
    px      = img.load()
    PLANK_H = 4
    for y in range(SIZE):
        plank  = y // PLANK_H
        base_r = 175 + plank * 4
        base_g = 135 + plank * 3
        base_b = 75  + plank * 2
        for x in range(SIZE):
            px[x, y] = noise_pixel(base_r, base_g, base_b, 12)
    for y in range(PLANK_H-1, SIZE, PLANK_H):
        for x in range(SIZE):
            px[x, y] = (90, 60, 30, 255)
    for y in range(SIZE):
        joint_x = (8 + (y // PLANK_H) * 5) % SIZE
        px[joint_x, y] = (90, 60, 30, 255)
    save(img, 'planks')


# ─── COBBLESTONE ──────────────────────────────────────────────────────────────
def make_cobblestone():
    img  = fill_noise(new_img(), 110, 110, 110, 14)
    draw = ImageDraw.Draw(img)
    for (x0, y0, x1, y1) in [(0,0,7,7),(9,0,15,7),(0,9,7,15),(9,9,15,15)]:
        draw.rectangle([x0, y0, x1, y1], outline=(70, 70, 70, 255))
        draw.line([(x0+1, y0+1), (x1-1, y0+1)], fill=(155, 155, 155, 255))
        draw.line([(x0+1, y0+1), (x0+1, y1-1)], fill=(155, 155, 155, 255))
    save(img, 'cobblestone')


if __name__ == '__main__':
    print(f'\nGerando texturas 16x16 em ./{OUTPUT_DIR}/ ...\n')
    make_grass()
    make_dirt()
    make_stone()
    make_sand()
    make_wood()
    make_leaves()
    make_planks()
    make_cobblestone()
    print('\nPronto! Execute o jogo normalmente agora.')