"""
main.py — PyMinecraft 3D | Ursina 8.x | Mesh Merging v3
"""

from ursina import *
from panda3d.core import RenderModeAttrib
from block  import BLOCK_TYPES
from world  import World, CHUNK_SIZE, RENDER_DISTANCE
from player import Player

# =============================================================================
app = Ursina(
    title='PyMinecraft 3D',
    borderless=False, fullscreen=False,
    development_mode=False, vsync=True,
)
window.fps_counter.enabled = True
window.exit_button.visible = False

SKY = color.Color(0.53, 0.81, 0.92, 1)
camera.background = SKY
Entity(model='sphere', scale=300, color=SKY, double_sided=True, unlit=True)

sun = DirectionalLight(); sun.look_at(Vec3(1, -2, 0.5))
amb = AmbientLight(); amb.color = color.Color(0.5, 0.52, 0.55, 1)

scene.fog_color   = SKY
scene.fog_density = 0.018

# =============================================================================
world  = World(seed=None)
world.initial_load()
player = Player(spawn_position=Vec3(0, world.spawn_height(), 0))

# =============================================================================
# OUTLINE
# =============================================================================
REACH = 7

block_outline = Entity(
    model='cube', color=color.black, scale=1.005,
    enabled=False, unlit=True,
)
block_outline.setAttrib(RenderModeAttrib.make(RenderModeAttrib.MWireframe, 2.0))

def _ray():
    return raycast(
        origin=camera.world_position, direction=camera.forward,
        distance=REACH, ignore=[player], traverse_target=scene,
    )

def _hit_block(hit):
    """Bloco atingido pelo ray em um chunk mesh."""
    p, n = hit.world_point, hit.normal
    return (int(round(p.x - n.x*0.5)),
            int(round(p.y - n.y*0.5)),
            int(round(p.z - n.z*0.5)))

def _hit_place(hit):
    """Posição adjacente ao bloco atingido (para colocar)."""
    bx, by, bz = _hit_block(hit)
    n = hit.normal
    return (bx + int(round(n.x)),
            by + int(round(n.y)),
            bz + int(round(n.z)))

def _update_outline():
    if not mouse.locked:
        block_outline.enabled = False
        return
    hit = _ray()
    if hit.hit and getattr(hit.entity, 'is_chunk', False):
        block_outline.position = Vec3(*_hit_block(hit))
        block_outline.enabled  = True
    else:
        block_outline.enabled = False

# =============================================================================
# HUD
# =============================================================================
info_text = Text(
    text='', origin=(-0.5, 0.5), position=(-0.87, 0.48),
    scale=0.85, color=color.white, background=True, parent=camera.ui,
)
fb_text = Text(
    text='', origin=(0,0), position=(0, 0.35),
    scale=1.4, color=color.lime, parent=camera.ui, enabled=False,
)
_fb = 0

def _show_feedback(msg, col=color.lime):
    global _fb
    fb_text.text = msg; fb_text.color = col
    fb_text.enabled = True; _fb = 2.5

def _update_feedback():
    global _fb
    if _fb > 0:
        _fb -= time.dt
        if _fb <= 0: fb_text.enabled = False

def _update_info():
    px,py,pz = (round(v,1) for v in player.position)
    cx,cz    = world.chunk_coords
    fps      = round(1/max(time.dt, 0.001))
    info_text.text = (
        f" Pos: ({px},{py},{pz})\n"
        f" Chunk: ({cx},{cz}) | Fila: {len(world._load_queue)}\n"
        f" Bloco: {BLOCK_TYPES[player.selected_block]['name']}\n"
        f" Meshes: {world.entity_count} | Blocos: {world.block_count}\n"
        f" FPS: {fps}\n"
        f" F5: Salvar  |  F6: Carregar"
    )

# =============================================================================
# INTERAÇÃO
# =============================================================================
def _break_block():
    hit = _ray()
    if hit.hit and getattr(hit.entity, 'is_chunk', False):
        world.remove_block(_hit_block(hit))

def _place_block():
    hit = _ray()
    if hit.hit and getattr(hit.entity, 'is_chunk', False):
        pp = _hit_place(hit)
        if not (abs(pp[0]-player.x)<1.5 and
                abs(pp[1]-player.y)<2.5 and
                abs(pp[2]-player.z)<1.5):
            world.add_block(pp, player.selected_block)

# =============================================================================
def input(key):
    if   key == 'left mouse button'  and mouse.locked: _break_block()
    elif key == 'right mouse button' and mouse.locked: _place_block()
    elif key == 'escape':  mouse.locked = not mouse.locked
    elif key == 'q':       application.quit()
    elif key == 'f5':
        world.save(); _show_feedback('💾  Mundo salvo!', color.lime)
    elif key == 'f6':
        ok = world.load()
        if ok:
            player.y = max(player.y, world.spawn_height())
            _show_feedback('📂  Mundo carregado!', color.cyan)
        else:
            _show_feedback('⚠️  Nenhum save encontrado.', color.orange)

def update():
    _update_info()
    _update_outline()
    _update_feedback()
    world.update_chunks(player.position)

# =============================================================================
if __name__ == '__main__':
    area = (2*RENDER_DISTANCE+1) * CHUNK_SIZE
    print("="*56)
    print(f"  PyMinecraft 3D  |  Área visível: ~{area}x{area} blocos")
    print("  WASD/Mouse | Espaço: Pular | Shift: Correr")
    print("  LMB: Quebrar | RMB: Colocar | 1-7/Scroll: Bloco")
    print("  Q: Sair | F5: Salvar | F6: Carregar")
    print("="*56)
    app.run()
