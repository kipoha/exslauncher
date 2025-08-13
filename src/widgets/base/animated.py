from typing import Literal
from gi.repository import GLib
from windows.wayland import WaylandWindow as Window

class AnimatedWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        anim_direction: Literal["bottom", "top", "left", "right"] = kwargs.get("anim_direction", "bottom")
        self.anim_direction = anim_direction
        self.anim_current_offset = -40
        self.anim_target_offset = -40
        self.anim_current_opacity = 0
        self.anim_target_opacity = 0

        self.animation_running = False
        self.speed = 0.15

        self.connect("key-release-event", self.on_window_key_release)
        self.connect("focus-out-event", self.on_focus_out)

    def on_window_key_release(self, widget, event):
        keyval = event.get_keyval()[1]
        if keyval == 65307:
            self.animate_hide()
            return True

    def on_focus_out(self, *args):
        self.animate_hide()
        return False

    def animation_step(self):
        margin_dict: dict[str, tuple[int, int, int, int]] = {
            "bottom": (0, 0, int(self.anim_current_offset), 0),
            "top":    (int(self.anim_current_offset), 0, 0, 0),
            "left":   (0, 0, 0, int(self.anim_current_offset)),
            "right":  (0, int(self.anim_current_offset), 0, 0),
        }
        
        diff = self.anim_target_offset - self.anim_current_offset
        self.anim_current_offset += diff * self.speed

        diff_opacity = self.anim_target_opacity - self.anim_current_opacity
        self.anim_current_opacity += diff_opacity * self.speed

        margin = margin_dict.get(self.anim_direction, (0, 0, int(self.anim_current_offset), 0))
        self.set_margin(margin)
        self.set_opacity(self.anim_current_opacity)

        if abs(diff) < 1 and abs(diff_opacity) < 0.01:
            self.anim_current_offset = self.anim_target_offset
            self.anim_current_opacity = self.anim_target_opacity
            self.set_margin(margin)
            self.set_opacity(self.anim_current_opacity)

            self.animation_running = False

            if self.anim_current_opacity <= 0:
                self.hide()
            return False

        return True

    def animate_show(self):
        self.show_all()

        self.prepare_offsets(True)
        self.anim_current_opacity = 0
        self.anim_target_opacity = 1.0

        if not self.animation_running:
            self.animation_running = True
            GLib.timeout_add(8, self.animation_step)


    def animate_hide(self):
        self.prepare_offsets(False)
        self.anim_target_opacity = 0

        if not self.animation_running:
            self.animation_running = True
            GLib.timeout_add(8, self.animation_step)

    def toggle(self):
        if self.is_visible():
            self.animate_hide()
        else:
            self.animate_show()

    def prepare_offsets(self, show: bool):
        width, height = self.get_size()
        if self.anim_direction in ["bottom", "top"]:
            offset = height 
        else:
            offset = width
        offset = offset / 2
        visible_position = -40
        if show:
            self.anim_current_offset = -offset
            self.anim_target_offset = visible_position
        else:
            self.anim_current_offset = visible_position
            self.anim_target_offset = -offset
