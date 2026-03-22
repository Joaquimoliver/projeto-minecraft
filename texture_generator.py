"""
texture_generator.py — Gera texturas procedurais PNG para blocos (32x32).
Executa uma vez, depois usa cache. Leve e rápido!
"""

import os
from PIL import Image, ImageDraw, ImageFilter
import random

TEXTURE_SIZE = 32
TEXTURES_DIR = 'textures'

def ensure_textures_dir():
    if not os.path.exists(TEXTURES_DIR):
        os.makedirs(TEXTURES_DIR)

def rgb(r, g, b):
    return (int(r), int(g), int(b))

# Cores base (mesmas do BLOCK_TYPES)
BLOCK_COLORS = {
    'grass':       rgb(106, 166, 85),
    'dirt':        rgb(134, 96, 67),
    'stone':       rgb(128, 128, 128),
    'sand':        rgb(210, 195, 140),
    'wood':        rgb(101, 67, 33),
    'leaves':      rgb(50, 110, 40),
    'planks':      rgb(180, 140, 80),
    'cobblestone': rgb(105, 105, 105),
}

def generate_grass_texture():
    """Grama com manchinhas e variações."""
    img = Image.new('RGB', (TEXTURE_SIZE, TEXTURE_SIZE), BLOCK_COLORS['grass'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    random.seed(42)
    for _ in range(60):
        x = random.randint(0, TEXTURE_SIZE-2)
        y = random.randint(0, TEXTURE_SIZE-2)
        c = random.randint(40, 80)
        draw.rectangle([x, y, x+1, y+1], fill=(c, c+20, c, 100))
    
    return img

def generate_dirt_texture():
    """Terra com textura nodosa."""
    img = Image.new('RGB', (TEXTURE_SIZE, TEXTURE_SIZE), BLOCK_COLORS['dirt'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    random.seed(43)
    for _ in range(40):
        x = random.randint(0, TEXTURE_SIZE-4)
        y = random.randint(0, TEXTURE_SIZE-4)
        size = random.randint(1, 2)
        c = random.randint(-20, 30)
        r, g, b = BLOCK_COLORS['dirt']
        draw.ellipse([x, y, x+size, y+size], 
                     fill=(max(0,r+c), max(0,g+c), max(0,b+c), 80))
    
    return img

def generate_stone_texture():
    """Pedra com rachaduras."""
    img = Image.new('RGB', (TEXTURE_SIZE, TEXTURE_SIZE), BLOCK_COLORS['stone'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    random.seed(44)
    for _ in range(30):
        x1 = random.randint(0, TEXTURE_SIZE-1)
        y1 = random.randint(0, TEXTURE_SIZE-1)
        x2 = x1 + random.randint(-4, 4)
        y2 = y1 + random.randint(-4, 4)
        draw.line([(x1, y1), (x2, y2)], fill=(80, 80, 80, 60), width=1)
    
    return img

def generate_sand_texture():
    """Areia com grãos."""
    img = Image.new('RGB', (TEXTURE_SIZE, TEXTURE_SIZE), BLOCK_COLORS['sand'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    random.seed(45)
    for _ in range(120):
        x = random.randint(0, TEXTURE_SIZE-1)
        y = random.randint(0, TEXTURE_SIZE-1)
        c = random.randint(-40, 40)
        r, g, b = BLOCK_COLORS['sand']
        draw.point((x, y), fill=(max(0,r+c), max(0,g+c), max(0,b+c)))
    
    return img

def generate_wood_texture():
    """Madeira com anéis."""
    img = Image.new('RGB', (TEXTURE_SIZE, TEXTURE_SIZE), BLOCK_COLORS['wood'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Anéis concêntricos
    for i in range(3, TEXTURE_SIZE, 6):
        draw.ellipse([TEXTURE_SIZE//2-i, TEXTURE_SIZE//2-i, 
                      TEXTURE_SIZE//2+i, TEXTURE_SIZE//2+i], 
                     outline=(60, 40, 20, 100), width=1)
    
    return img

def generate_leaves_texture():
    """Folhas com padrão."""
    img = Image.new('RGB', (TEXTURE_SIZE, TEXTURE_SIZE), BLOCK_COLORS['leaves'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    random.seed(47)
    for _ in range(80):
        x = random.randint(0, TEXTURE_SIZE-3)
        y = random.randint(0, TEXTURE_SIZE-3)
        draw.ellipse([x, y, x+2, y+2], fill=(30, 80, 20, 100))
    
    return img

def generate_planks_texture():
    """Tábuas com veios."""
    img = Image.new('RGB', (TEXTURE_SIZE, TEXTURE_SIZE), BLOCK_COLORS['planks'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Linhas verticais simulando madeira
    for x in range(0, TEXTURE_SIZE, 8):
        draw.line([(x, 0), (x, TEXTURE_SIZE)], fill=(140, 100, 50, 80), width=1)
        if x + 3 < TEXTURE_SIZE:
            draw.line([(x+3, 0), (x+3, TEXTURE_SIZE)], fill=(180, 150, 80, 80), width=1)
    
    return img

def generate_cobblestone_texture():
    """Pedregulho com mosaico."""
    img = Image.new('RGB', (TEXTURE_SIZE, TEXTURE_SIZE), BLOCK_COLORS['cobblestone'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Grid de pedras
    step = TEXTURE_SIZE // 4
    for i in range(0, TEXTURE_SIZE, step):
        for j in range(0, TEXTURE_SIZE, step):
            draw.rectangle([i, j, i+step-1, j+step-1], 
                          outline=(70, 70, 70, 100), width=1)
    
    return img

GENERATORS = {
    'grass':       generate_grass_texture,
    'dirt':        generate_dirt_texture,
    'stone':       generate_stone_texture,
    'sand':        generate_sand_texture,
    'wood':        generate_wood_texture,
    'leaves':      generate_leaves_texture,
    'planks':      generate_planks_texture,
    'cobblestone': generate_cobblestone_texture,
}

def generate_all_textures():
    """Gera todas as texturas PNG."""
    ensure_textures_dir()
    
    for block_type, generator in GENERATORS.items():
        filepath = os.path.join(TEXTURES_DIR, f'{block_type}.png')
        
        if os.path.exists(filepath):
            print(f"  ✓ {block_type}.png (cached)")
            continue
        
        img = generator()
        img.save(filepath, 'PNG')
        print(f"  ✓ {block_type}.png (gerado)")
    
    print(f"[Texturas] Prontas em '{TEXTURES_DIR}/'")

if __name__ == '__main__':
    print("[Texturas] Gerando texturas procedurais...")
    generate_all_textures()
