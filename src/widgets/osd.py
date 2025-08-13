import subprocess

from gi.repository import GLib

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.overlay import Overlay

from widgets.base import AnimatedWindow as Window


class IconCircular(Box):
    def __init__(self, icon: str, name: str):
        super().__init__(orientation="overlay", h_align="center", v_align="center")
        self.bar = CircularProgressBar(min_value=0, max_value=100, size=70, name=name)
        self.icon_label = Label(label=icon, name=f"{name}-icon", h_align="center", v_align="center")
        self.children = CenterBox(center_children=Overlay(child=self.bar, overlays=[self.icon_label]))


class OSD(Window):
    def __init__(self):
        super().__init__(
            title="OSD",
            name="osd",
            layer="top",
            keyboard_mode="off",
            exclusivity="none",
            anchor="right center",
            visible=False,
            all_visible=False,
            anim_direction="right",
        )

        self.brightness_widget = IconCircular("󰃞", "brightness-bar")
        self.volume_widget = IconCircular("", "volume-bar")

        main_box = Box(
            orientation="v",
            spacing=10,
            children=[self.brightness_widget, self.volume_widget],
            h_align="center",
            v_align="center",
            name="osd-main-box",
        )

        box = Box(
            orientation="h",
            spacing=0,
            children=[main_box],
            name="osd-box",
        )

        self.children = CenterBox(center_children=box)

        self._hide_timeout_id = None
        self._active = False
        self._animation_ids = {}

        self.update_volume()
        self.update_brightness()

    def animate_value(self, bar: CircularProgressBar, target: int, duration=200):
        if bar in self._animation_ids:
            GLib.source_remove(self._animation_ids[bar])
            del self._animation_ids[bar]

        start = bar.value
        steps = max(abs(target - start), 1)
        step_time = int(duration / steps)

        step = 0

        def update():
            nonlocal step
            step += 1
            if step >= steps:
                bar.value = target
                if bar in self._animation_ids:
                    del self._animation_ids[bar]
                return False
            bar.value = start + (target - start) * step / steps
            return True

        self._animation_ids[bar] = GLib.timeout_add(step_time, update)

    def _reset_hide_timer(self):
        if self._hide_timeout_id:
            GLib.source_remove(self._hide_timeout_id)
        self._hide_timeout_id = GLib.timeout_add_seconds(1, self.animate_hide)

    def update_volume(self):
        value = self.get_volume()
        self.animate_value(self.volume_widget.bar, value)
        self._show_osd()

    def update_brightness(self):
        value = self.get_brightness()
        self.animate_value(self.brightness_widget.bar, value)
        self._show_osd()

    def _show_osd(self):
        if not self.is_visible():
            self.set_visible(True)
            self.animate_show()
            self._active = True
        else:
            self._reset_hide_timer()

    def get_volume(self) -> int:
        try:
            result = subprocess.run(
                ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                capture_output=True, text=True
            )
            parts = result.stdout.strip().split()
            if len(parts) < 2:
                return 0
            return int(float(parts[1]) * 100)
        except Exception as e:
            print("Error getting volume:", e)
            return 0

    def get_brightness(self) -> int:
        try:
            bright = int(subprocess.run(
                ["brightnessctl", "get"], capture_output=True, text=True
            ).stdout.strip())
            max_bright = int(subprocess.run(
                ["brightnessctl", "max"], capture_output=True, text=True
            ).stdout.strip())
            return int(bright * 100 / max_bright)
        except Exception as e:
            print("Error getting brightness:", e)
            return 0

    def set_volume(self, up: bool = True):
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+" if up else "5%-"])
        self.update_volume()
        self._show_osd()

    def mute_volume(self):
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])

        result = subprocess.run(
            ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
            capture_output=True, text=True
        )
        muted = "MUTED" in result.stdout

        if muted:
            vol = 0
            self.volume_widget.icon_label.set_properties(label="")
        else:
            vol = int(float(result.stdout.strip().split()[1]) * 100)
            self.volume_widget.icon_label.set_properties(label="")

        self.animate_value(self.volume_widget.bar, vol)
        self._show_osd()

    def set_brightness(self, up: bool = True):
        subprocess.run(["brightnessctl", "set", "5%+" if up else "5%-"])
        self.update_brightness()
        self._show_osd()
