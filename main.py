"""
main.py — PyMinecraft 3D | Otimizado para 60 FPS
Otimizações:
  - Culling por distância a cada 10 frames
  - Raycast só quando necessário
  - Sombra ambiente removida (custo de render)
  - Fog reduzido para esconder bordas do culling
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

# ── Céu ───────────────────────────────────────────────────────────────────────
SKY_COLOR = color.Color(0.53, 0.81, 0.92, 1)
camera.background = SKY_COLOR

Entity(model='sphere', scale=300, color=SKY_COLOR, double_sided=True, unlit=True)

# ── Iluminação mínima (menos custo de render) ─────────────────────────────────
sun = DirectionalLight()
sun.look_at(Vec3(1, -2, 0.5))

# SEM AmbientLight separado — o DirectionalLight já ilumina o suficiente

# ── Fog curto para esconder borda do culling ───────────────────────────────────
scene.fog_color   = SKY_COLOR
scene.fog_density = 0.035     # mais denso = esconde mais longe = mais FPS

# =============================================================================
# MUNDO E JOGADOR
# =============================================================================
world  = World(seed=None)
world.generate()

spawn_y = world.spawn_height()
player  = Player(spawn_position=Vec3(0, spawn_y, 0))

# =============================================================================
# HIGHLIGHT DE BLOCO (sem entidade auxiliar)
# =============================================================================
REACH = 7
_highlighted = None

def _apply_highlight(block):
    block.color = color.Color(1.3, 1.3, 1.3, 1) if block.texture else color.Color(
        min(block._base_color.r+0.25,1),
        min(block._base_color.g+0.25,1),
        min(block._base_color.b+0.25,1), 1)

def _clear_highlight(block):
    block.color = color.white if block.texture else block._base_color

def _update_highlight():
    global _highlighted
    if not mouse.locked:
        if _highlighted:
            _clear_highlight(_highlighted)
            _highlighted = None
        return
    hit = raycast(camera.world_position, camera.forward, distance=REACH,
                  ignore=[player], traverse_target=scene)
    target = hit.entity if (hit.hit and hasattr(hit.entity, 'block_type')) else None
    if target is not _highlighted:
        if _highlighted: _clear_highlight(_highlighted)
        if target:       _apply_highlight(target)
        _highlighted = target

# =============================================================================
# HUD
# =============================================================================
info_text = Text(
    text='', origin=(-0.5, 0.5), position=(-0.87, 0.48),
    scale=0.85, color=color.white, background=True, parent=camera.ui,
)
feedback_text = Text(
    text='', origin=(0,0), position=(0, 0.35), scale=1.4,
    color=color.lime, parent=camera.ui, enabled=False,
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
    px, py, pz = (round(v,1) for v in player.position)
    fps = round(1 / max(time.dt, 0.001))
    info_text.text = (
        f" Pos: ({px}, {py}, {pz})\n"
        f" Bloco: {BLOCK_TYPES[player.selected_block]['name']}\n"
        f" Entidades: {sum(1 for b in world.blocks.values() if b.enabled)}/{len(world.blocks)}\n"
        f" FPS: {fps}\n"
        f" F5: Salvar  |  F6: Carregar"
    )

# =============================================================================
# INTERAÇÃO
# =============================================================================
def _break_block():
    hit = raycast(camera.world_position, camera.forward, distance=REACH,
                  ignore=[player], traverse_target=scene)
    if hit.hit and hasattr(hit.entity, 'block_type'):
        world.remove_block(hit.entity.position)

def _place_block():
    hit = raycast(camera.world_position, camera.forward, distance=REACH,
                  ignore=[player], traverse_target=scene)
    if hit.hit and hasattr(hit.entity, 'block_type'):
        new_pos = hit.entity.position + hit.normal
        new_pos = Vec3(round(new_pos.x), round(new_pos.y), round(new_pos.z))
        if not player.is_too_close(new_pos):
            world.add_block(new_pos, player.selected_block)

# =============================================================================
# CALLBACKS
# =============================================================================
_frame = 0
_CULL_INTERVAL = 10      # atualiza visibilidade a cada N frames

def input(key):
    if   key == 'left mouse button'  and mouse.locked: _break_block()
    elif key == 'right mouse button' and mouse.locked: _place_block()
    elif key == 'escape':  mouse.locked = not mouse.locked
    elif key == 'q':       application.quit()
    elif key == 'f5':
        world.save()
        _show_feedback('Mundo salvo! (F6 para carregar)', color.lime)
    elif key == 'f6':
        ok = world.load()
        if ok:
            _show_feedback('Mundo carregado!', color.cyan)
            player.y = max(player.y, world.spawn_height())
        else:
            _show_feedback('Nenhum save encontrado.', color.orange)

def update():
    global _frame
    _frame += 1

    _update_info()
    _update_highlight()
    _update_feedback()

    # Culling por distância — não roda todo frame
    if _frame % _CULL_INTERVAL == 0:
        world.update_visibility(player.position)

# =============================================================================
# START
# =============================================================================
if __name__ == '__main__':
    print("=" * 52)
    print("  PyMinecraft 3D  |  60 FPS Edition")
    print("  WASD: Mover  |  Espaco: Pular  |  Shift: Correr")
    print("  1-7/Scroll: Bloco")
    print("  LMB: Quebrar  |  RMB: Colocar  |  Q: Sair")
    print("  F5: Salvar  |  F6: Carregar")
    print("=" * 52)
    app.run()
