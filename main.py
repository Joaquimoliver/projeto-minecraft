"""
main.py — PyMinecraft 3D  |  Ursina 8.x  |  Versão otimizada para 60 FPS
Novidades: outline no bloco mirando | F5 salva | F6 carrega
"""

from ursina import *
from panda3d.core import RenderModeAttrib
from ursina.prefabs.first_person_controller import FirstPersonController
from block  import BLOCK_TYPES
from world  import World
from player import Player

# =============================================================================
# APP — configurações de performance
# =============================================================================
app = Ursina(
    title='PyMinecraft 3D',
    borderless=False,
    fullscreen=False,
    development_mode=False,
    vsync=True,
)

window.fps_counter.enabled = True
window.exit_button.visible = False
window.render_mode = 'default'

# ——— CÉU ——————————————————————————————————————————————————————————————————
camera.background = color.Color(0.53, 0.81, 0.92, 1)

sky_dome = Entity(
    model='sphere',
    scale=300,
    color=color.Color(0.53, 0.81, 0.92, 1),
    double_sided=True,
    unlit=True,
)

# ——— ILUMINAÇÃO —————————————————————————————————————————————————————————
sun = DirectionalLight()
sun.look_at(Vec3(1, -2, 0.5))

ambient = AmbientLight()
ambient.color = color.Color(0.5, 0.52, 0.55, 1)

# ——— FOG —————————————————————————————————————————————————————————————————
scene.fog_color   = color.Color(0.53, 0.81, 0.92, 1)
scene.fog_density = 0.02

# =============================================================================
# MUNDO E JOGADOR
# =============================================================================
world  = World(seed=None)
world.generate()

spawn_y = world.spawn_height()
player  = Player(spawn_position=Vec3(0, spawn_y, 0))

# =============================================================================
# OUTLINE DO BLOCO MIRANDO
# =============================================================================
block_outline = Entity(
    model='cube',
    color=color.black,
    scale=1.005,
    enabled=False,
    unlit=True,
)
# Wireframe via Panda3D (funciona em qualquer versão Ursina/Panda3D)
block_outline.setAttrib(RenderModeAttrib.make(RenderModeAttrib.MWireframe, 2.0))

_last_outlined = None   # guarda a entidade que está sendo destacada

def _update_outline():
    global _last_outlined
    if not mouse.locked:
        block_outline.enabled = False
        _last_outlined = None
        return

    hit = raycast(
        origin=camera.world_position,
        direction=camera.forward,
        distance=REACH,
        ignore=[player],
        traverse_target=scene,
    )

    if hit.hit and hasattr(hit.entity, 'block_type'):
        target = hit.entity
        if target is not _last_outlined:
            _last_outlined = target
        block_outline.position = target.position
        block_outline.enabled  = True
    else:
        block_outline.enabled = False
        _last_outlined = None

# =============================================================================
# HUD INFO
# =============================================================================
info_text = Text(
    text='',
    origin=(-0.5, 0.5),
    position=(-0.87, 0.48),
    scale=0.85,
    color=color.white,
    background=True,
    parent=camera.ui,
)

# Mensagem de feedback (save/load)
feedback_text = Text(
    text='',
    origin=(0, 0),
    position=(0, 0.35),
    scale=1.4,
    color=color.lime,
    parent=camera.ui,
    enabled=False,
)
_feedback_timer = 0

def _show_feedback(msg, col=color.lime):
    global _feedback_timer
    feedback_text.text    = msg
    feedback_text.color   = col
    feedback_text.enabled = True
    _feedback_timer = 2.5   # segundos que a mensagem fica visível

def _update_feedback():
    global _feedback_timer
    if _feedback_timer > 0:
        _feedback_timer -= time.dt
        if _feedback_timer <= 0:
            feedback_text.enabled = False

def _update_info():
    px, py, pz = (round(v, 1) for v in player.position)
    blk  = player.selected_block
    nome = BLOCK_TYPES[blk]['name']
    fps  = round(1 / max(time.dt, 0.001))
    info_text.text = (
        f" Pos: ({px}, {py}, {pz})\n"
        f" Bloco: {nome}\n"
        f" Entidades: {len(world.blocks)}\n"
        f" FPS: {fps}\n"
        f" F5: Salvar  |  F6: Carregar"
    )

# =============================================================================
# INTERAÇÃO — quebrar / colocar blocos
# =============================================================================
REACH = 7

def _break_block():
    hit = raycast(
        origin=camera.world_position,
        direction=camera.forward,
        distance=REACH,
        ignore=[player],
        traverse_target=scene,
    )
    if hit.hit and hasattr(hit.entity, 'block_type'):
        world.remove_block(hit.entity.position)

def _place_block():
    hit = raycast(
        origin=camera.world_position,
        direction=camera.forward,
        distance=REACH,
        ignore=[player],
        traverse_target=scene,
    )
    if hit.hit and hasattr(hit.entity, 'block_type'):
        new_pos = hit.entity.position + hit.normal
        new_pos = Vec3(round(new_pos.x), round(new_pos.y), round(new_pos.z))
        if not player.is_too_close(new_pos):
            world.add_block(new_pos, player.selected_block)

# =============================================================================
# CALLBACKS
# =============================================================================
def input(key):
    if key == 'left mouse button' and mouse.locked:
        _break_block()
    elif key == 'right mouse button' and mouse.locked:
        _place_block()
    elif key == 'escape':
        mouse.locked = not mouse.locked
    elif key == 'q':
        application.quit()
    # ——— Save / Load ———————————————————————————————————————————————
    elif key == 'f5':
        world.save()
        _show_feedback('💾  Mundo salvo!  (F6 para carregar)', color.lime)
    elif key == 'f6':
        ok = world.load()
        if ok:
            _show_feedback('📂  Mundo carregado!', color.cyan)
            # Reposiciona o jogador em cima do spawn caso tenha caído
            player.y = max(player.y, world.spawn_height())
        else:
            _show_feedback('⚠️  Nenhum save encontrado.', color.orange)

def update():
    _update_info()
    _update_outline()
    _update_feedback()

# =============================================================================
# START
# =============================================================================
if __name__ == '__main__':
    print("=" * 52)
    print("  PyMinecraft 3D  |  Versao otimizada 60 FPS")
    print("  WASD: Mover  |  Mouse: Olhar  |  Espaco: Pular")
    print("  Shift: Correr  |  1-7/Scroll: Bloco")
    print("  LMB: Quebrar  |  RMB: Colocar  |  Q: Sair")
    print("  F5: Salvar mundo  |  F6: Carregar mundo")
    print("=" * 52)
    app.run()
