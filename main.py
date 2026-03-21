"""
main.py — PyMinecraft 3D  |  Ursina 8.x  |  Versão otimizada
Fix: outline preto removido — hover direto no bloco (sem artefato preto)
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from block  import BLOCK_TYPES
from world  import World
from player import Player

# =============================================================================
# APP
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

# ── CÉU ───────────────────────────────────────────────────────────────────────
camera.background = color.Color(0.53, 0.81, 0.92, 1)

sky_dome = Entity(
    model='sphere',
    scale=300,
    color=color.Color(0.53, 0.81, 0.92, 1),
    double_sided=True,
    unlit=True,
)

# ── ILUMINAÇÃO ────────────────────────────────────────────────────────────────
sun = DirectionalLight()
sun.look_at(Vec3(1, -2, 0.5))

ambient = AmbientLight()
ambient.color = color.Color(0.5, 0.52, 0.55, 1)

# ── FOG ───────────────────────────────────────────────────────────────────────
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
# HIGHLIGHT DO BLOCO MIRANDO
# Substituímos o wireframe (que causava o quadrado preto) por um
# tingimento direto no bloco — sem entidade auxiliar, sem artefatos.
# =============================================================================
REACH = 7
_highlighted_block = None   # bloco atualmente destacado


def _update_highlight():
    global _highlighted_block

    if not mouse.locked:
        if _highlighted_block:
            _clear_highlight(_highlighted_block)
            _highlighted_block = None
        return

    hit = raycast(
        origin=camera.world_position,
        direction=camera.forward,
        distance=REACH,
        ignore=[player],
        traverse_target=scene,
    )

    new_target = hit.entity if (hit.hit and hasattr(hit.entity, 'block_type')) else None

    if new_target is not _highlighted_block:
        # Remove destaque do bloco anterior
        if _highlighted_block:
            _clear_highlight(_highlighted_block)
        # Aplica destaque no novo bloco
        if new_target:
            _apply_highlight(new_target)
        _highlighted_block = new_target


def _apply_highlight(block):
    """Deixa o bloco levemente mais claro para indicar seleção."""
    if block.texture:
        block.color = color.Color(1.3, 1.3, 1.3, 1)
    else:
        c = block._base_color
        block.color = color.Color(min(c.r + 0.25, 1), min(c.g + 0.25, 1), min(c.b + 0.25, 1), 1)


def _clear_highlight(block):
    """Restaura a cor original do bloco."""
    block.color = color.white if block.texture else block._base_color


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
    _feedback_timer = 2.5


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
    elif key == 'f5':
        world.save()
        _show_feedback('💾  Mundo salvo!  (F6 para carregar)', color.lime)
    elif key == 'f6':
        ok = world.load()
        if ok:
            _show_feedback('📂  Mundo carregado!', color.cyan)
            player.y = max(player.y, world.spawn_height())
        else:
            _show_feedback('⚠️  Nenhum save encontrado.', color.orange)


def update():
    _update_info()
    _update_highlight()
    _update_feedback()


# =============================================================================
# START
# =============================================================================
if __name__ == '__main__':
    print("=" * 52)
    print("  PyMinecraft 3D  |  Com texturas")
    print("  WASD: Mover  |  Mouse: Olhar  |  Espaco: Pular")
    print("  Shift: Correr  |  1-7/Scroll: Bloco")
    print("  LMB: Quebrar  |  RMB: Colocar  |  Q: Sair")
    print("  F5: Salvar mundo  |  F6: Carregar mundo")
    print("=" * 52)
    app.run()