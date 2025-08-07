import subprocess
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.centerbox import CenterBox

from windows.wayland import WaylandWindow as Window

from gi.repository import GLib


class FirefoxSearch(Window):
    def __init__(self):
        super().__init__(
            title="firefox-search",
            name="firefox-search",
            layer="top",
            anchor="center bottom",
            keyboard_mode="exclusive",
            exclusivity="none",
            accept_focus=True,
            visible=False,
            all_visible=False,
            margin=(0, 0, -40, 0),
        )

        self.anim_current_opacity = 0
        self.anim_target_opacity = 0
        self.animation_running = False

        self.entry = Entry(placeholder="Search in Firefox...", h_expand=True, name="firefox-search-input", size=(400, 32))
        self.entry.connect("activate", self.launch_firefox)
        self.main_box = Box(orientation="v", spacing=0, name="firefox-search-main-box", children=[
            self.entry
        ])

        self.box = Box(
            name="firefox-search-box", orientation="v",
            children=[self.main_box],
        )
        self.children = CenterBox(center_children=self.box)
        self.connect("key-release-event", self.on_window_key_release)

    def launch_firefox(self, *_):
        query = self.entry.get_text().strip()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            subprocess.Popen(["firefox", "--new-window", url])
            self.entry.set_text("")
            self.animate_hide()

    def animation_step(self):
        speed = 0.3

        diff_opacity = self.anim_target_opacity - self.anim_current_opacity
        self.anim_current_opacity += diff_opacity * speed
        self.set_opacity(self.anim_current_opacity)

        if abs(diff_opacity) < 0.01:
            self.anim_current_opacity = self.anim_target_opacity
            self.set_opacity(self.anim_current_opacity)
            self.animation_running = False

            if self.anim_current_opacity <= 0:
                self.hide()

            return False

        return True

    def animate_show(self):
        self.show_all()
        self.anim_current_opacity = 0
        self.anim_target_opacity = 1.0
        self.set_opacity(0)

        GLib.idle_add(self.entry.grab_focus)

        if not self.animation_running:
            self.animation_running = True
            GLib.timeout_add(10, self.animation_step)


    def animate_hide(self):
        self.anim_target_opacity = 0
        if not self.animation_running:
            self.animation_running = True
            GLib.timeout_add(10, self.animation_step)

    def toggle(self):
        if self.is_visible():
            self.animate_hide()
        else:
            self.animate_show()
            self.entry.grab_focus()

    def on_window_key_release(self, widget, event):
        keyval = event.get_keyval()[1]
        if keyval == 65307:
            self.animate_hide()
            return True

