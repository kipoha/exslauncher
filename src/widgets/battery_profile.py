import subprocess

from gi.repository import Gdk, GLib

from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.label import Label

from widgets.base import AnimatedWindow as Window

from events.mouse_trigger import TriggerWindow


class BatteryProfile(Window):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            name="battery-profile",
            layer="top",
            anchor="left bottom",
            exclusivity="none",
            anim_direction="left",
            visible=False,
            **kwargs
        )
        self.performance_button = Button(
            label="󰓅",
            name="battery-profile-performance-button",
            markup="Performance",
            h_expand=False,
            v_expand=False,
            on_clicked=self.set_performance,
        )
        self.balanced_button = Button(
            label="",
            name="battery-profile-balanced-button",
            markup="Balanced",
            h_expand=False,
            v_expand=False,
            on_clicked=self.set_balanced,
        )
        self.power_save_button = Button(
            label="󰌪",
            name="battery-profile-power-save-button",
            markup="Power Save",
            h_expand=False,
            v_expand=False,
            on_clicked=self.set_power_save,
        )
        self.buttons = Box(
            name="battery-profile-buttons",
            orientation="h",
            h_expand=True,
            v_expand=True,
            children=[self.power_save_button, self.balanced_button, self.performance_button],
            spacing=5
        )

        self.percentage = Label(
            label="N/A",
            name="battery-profile-percentage",
            h_expand=True,
            v_expand=False,
        )

        self.main_box = Box(
            name="battery-profile-main-box",
            orientation="v",
            h_expand=True,
            v_expand=True,
            children=[self.percentage, self.buttons],
            spacing=3
        )

        self.content_box = Box(
            name="battery-profile-content-box",
            orientation="v",
            h_expand=True,
            v_expand=True,
            children=[self.main_box],
            spacing=3
        )

        self.children = self.content_box

        self.trigger_window = TriggerWindow(self, size=(20, 35))
        self._hide_timeout = GLib.timeout_add(2000, self.__hide_timeout)
        self.highlight_active_profile()

    def __hide_timeout(self):
        self.animate_hide()
        return True

    def set_performance(self, *_):
        subprocess.run(["powerprofilesctl", "set", "performance"])
        self.highlight_active_profile()

    def set_balanced(self, *_):
        subprocess.run(["powerprofilesctl", "set", "balanced"])
        self.highlight_active_profile()

    def set_power_save(self, *_):
        subprocess.run(["powerprofilesctl", "set", "power-saver"])
        self.highlight_active_profile()

    def highlight_active_profile(self):
        for button in [self.performance_button, self.balanced_button, self.power_save_button]:
            button.remove_style_class("active")

        result = subprocess.run(["powerprofilesctl", "get"], capture_output=True, text=True)
        current = result.stdout.strip()

        for button in self.children:
            button.remove_style_class("active")

        if current == "performance":
            self.performance_button.add_style_class("active")
        elif current == "balanced":
            self.balanced_button.add_style_class("active")
        elif current == "power-saver":
            self.power_save_button.add_style_class("active")
