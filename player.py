"""
player.py — Controlador FPS + inventário + HUD (compatível com Ursina 8.x).
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from block import BLOCK_TYPES, INVENTORY_ORDER

HUD_SLOT_SIZE = 0.06
HUD_GAP       = 0.075
HUD_Y         = -0.42


class Player(FirstPersonController):

    def __init__(self, spawn_position=Vec3(0, 10, 0)):
        super().__init__(
            position=spawn_position,
            speed=6,
            height=2,
            jump_height=2.5,
            jump_duration=0.35,
            gravity=0.8,
            mouse_sensitivity=Vec2(40, 40),
        )

        self.inventory      = INVENTORY_ORDER[:]
        self.selected_index = 0
        self.selected_block = self.inventory[0]
        self._base_speed    = self.speed

        self._hud_slots = []
        self._build_hud()

        # Crosshair
        Text(text='+', origin=(0, 0), scale=2,
             color=color.white, parent=camera.ui)

        # Nome do bloco selecionado
        self._block_label = Text(
            text='', origin=(0, 0), position=(0, -0.35),
            scale=1.1, color=color.white, parent=camera.ui,
        )
        self._refresh_hud()

    # ——— HUD ——————————————————————————————————————————————————————————————
    def _build_hud(self):
        n = len(self.inventory)
        start_x = -((n - 1) * HUD_GAP) / 2

        for i, btype in enumerate(self.inventory):
            props = BLOCK_TYPES[btype]
            x = start_x + i * HUD_GAP

            # Fundo (borda) do slot
            bg = Entity(
                parent=camera.ui,
                model='quad',
                color=color.Color(0, 0, 0, 0.6),
                scale=(HUD_SLOT_SIZE + 0.008, HUD_SLOT_SIZE + 0.008),
                position=(x, HUD_Y, 1),
            )
            # Ícone colorido
            icon = Entity(
                parent=camera.ui,
                model='quad',
                color=props['color'],
                scale=(HUD_SLOT_SIZE, HUD_SLOT_SIZE),
                position=(x, HUD_Y, 0),
            )
            # Número
            Text(
                parent=camera.ui,
                text=str(i + 1),
                origin=(-0.5, 0.5),
                position=(x - HUD_SLOT_SIZE * 0.45, HUD_Y + HUD_SLOT_SIZE * 0.42),
                scale=0.65,
                color=color.white,
            )
            self._hud_slots.append((bg, icon))

    def _refresh_hud(self):
        for i, (bg, icon) in enumerate(self._hud_slots):
            if i == self.selected_index:
                bg.color    = color.Color(1, 1, 1, 0.8)
                icon.scale  = HUD_SLOT_SIZE * 1.15
            else:
                bg.color    = color.Color(0, 0, 0, 0.6)
                icon.scale  = HUD_SLOT_SIZE

        btype = self.inventory[self.selected_index]
        self._block_label.text = BLOCK_TYPES[btype]['name']

    # ——— Seleção ——————————————————————————————————————————————————————————
    def select_block(self, index):
        self.selected_index = index % len(self.inventory)
        self.selected_block = self.inventory[self.selected_index]
        self._refresh_hud()

    # ——— Input ————————————————————————————————————————————————————————————
    def input(self, key):
        super().input(key)

        for i in range(len(self.inventory)):
            if key == str(i + 1):
                self.select_block(i)
                return

        if key == 'scroll up':
            self.select_block(self.selected_index - 1)
        elif key == 'scroll down':
            self.select_block(self.selected_index + 1)
        elif key == 'left shift':
            self.speed = self._base_speed * 1.8
        elif key == 'left shift up':
            self.speed = self._base_speed

    def is_too_close(self, position, min_dist=1.8):
        return (Vec3(position) - self.position).length() < min_dist
