import threading
import subprocess

from gi.repository import GLib

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.overlay import Overlay
from fabric import Fabricator

from widgets.base import AnimatedWindow as Window
# from events.mouse_trigger import TriggerWindow


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
            layer="overlay",
            keyboard_mode="off",
            exclusivity="none",
            anchor="right center",
            visible=False,
            all_visible=False,
            anim_direction="right",
        )
        # self.trigger = TriggerWindow(self)
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

        self._last_device = self._get_volume_device()

        self.volume_device = Fabricator(
            poll_from=lambda _: self._get_volume_device(),
            interval=1000,
        )

        self.volume_device.connect(
            "changed",
            lambda _, new_value: self._on_device_changed(_, new_value),
        )

        self.children = CenterBox(center_children=box)

        self._debounce_pending = False
        self._hide_timeout_id = None
        self._active = False
        self._animation_ids = {}

        self._muted = self.is_muted()
        self._last_volume = self.get_volume()
        self._last_brightness = self.get_brightness()

        self._init_bars()

    def _get_volume_device(self):
        try:
            out = subprocess.check_output(["pactl", "info"], text=True)
            for line in out.splitlines():
                if line.startswith("Default Sink:"):
                    result = line.split(":", 1)[1].strip()
                    return result
        except subprocess.CalledProcessError:
            return None
        return None

    def _update_osd(self):
        self._last_volume = self.get_volume()
        self._muted = self.is_muted()
        self._init_bars()

    def _on_device_changed(self, _, new_value):
        if new_value != self._last_device:
            self._last_device = new_value
            self._update_osd()

    def _init_bars(self):
        self.animate_value(self.brightness_widget.bar, self._last_brightness)
        self.animate_value(self.volume_widget.bar, self._last_volume)
        self._show_osd()

    def _show_osd(self):
        if not self.is_visible():
            self.set_visible(True)
            self.animate_show()
            self._active = True
        self._reset_hide_timer()

    def _reset_hide_timer(self):
        if self._hide_timeout_id:
            GLib.source_remove(self._hide_timeout_id)
        self._hide_timeout_id = GLib.timeout_add_seconds(1, self.animate_hide)

    def animate_value(self, bar: CircularProgressBar, target: int, duration=100):
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

    def update_volume(self):
        self.animate_value(self.volume_widget.bar, self._last_volume)
        self._show_osd()

    def update_brightness(self):
        self.animate_value(self.brightness_widget.bar, self._last_brightness)
        self._show_osd()

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

    def is_muted(self) -> bool:
        try:
            result = subprocess.run(
                ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                capture_output=True, text=True
            )
            return "MUTED" in result.stdout
        except Exception as e:
            print("Error checking mute state:", e)
            return False

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
        if up and self._last_volume < 100:
            self._last_volume = min(self._last_volume + 5, 100)
            subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"])
        elif not up and self._last_volume > 0:
            self._last_volume = max(self._last_volume - 5, 0)
            subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"])
        self.update_volume()
        self._show_osd()

    def mute_volume(self):
        self._muted = not self._muted
        subprocess.Popen(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])

        if self._muted:
            self.volume_widget.icon_label.set_properties(label="")
        else:
            self.volume_widget.icon_label.set_properties(label="")

        self._show_osd()

    def set_brightness(self, up: bool = True):
        if up and self._last_brightness < 100:
            self._last_brightness = min(self._last_brightness + 5, 100)
            subprocess.Popen(["brightnessctl", "set", "5%+"])
        elif not up and self._last_brightness > 0:
            self._last_brightness = max(self._last_brightness - 5, 0)
            subprocess.Popen(["brightnessctl", "set", "5%-"])
        self.update_brightness()
        self._show_osd()
