from gi.repository import GLib

import subprocess
from fabric.widgets.entry import Entry
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox

from widgets.base import AnimatedWindow as Window


class FirefoxSearch(Window):
    def __init__(self):
        super().__init__(
            title="firefox-search",
            name="firefox-search",
            layer="top",
            anchor="center bottom",
            keyboard_mode="on-demand",
            exclusivity="none",
            visible=False,
            all_visible=False,
        )

        self.search = Entry(placeholder="Search in Firefox...", h_expand=True, name="firefox-search-input", size=(400, 32))
        self.search.connect("activate", self.launch_firefox)
        self.main_box = Box(orientation="v", spacing=0, name="firefox-search-main-box", children=[
            self.search
        ])

        self.box = Box(
            name="firefox-search-box", orientation="v",
            children=[self.main_box],
        )
        self.children = CenterBox(center_children=self.box)
        self.connect("key-release-event", self.on_window_key_release)
        self.connect("focus-out-event", self.on_focus_out)

    def launch_firefox(self, *_):
        query = self.search.get_text().strip()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            subprocess.Popen(["firefox", "--new-window", url])
            self.search.set_text("")
            self.animate_hide()

    def animate_show(self):
        GLib.idle_add(self.search.grab_focus)
        super().animate_show()
