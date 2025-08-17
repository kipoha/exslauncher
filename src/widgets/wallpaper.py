import os
import subprocess
import threading

from gi.repository import GLib, GdkPixbuf
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow

from widgets.base import AnimatedWindow as Window
from utils.notify_system import send_notification

class WallpaperChooser(Window):
    def __init__(self, wallpapers_path="~/.local/share/wallpapers"):
        super().__init__(
            title="wallpaper-chooser",
            name="wallpaper-chooser",
            layer="top",
            anchor="center bottom",
            keyboard_mode="on-demand",
            exclusivity="none",
            visible=False,
            all_visible=False,
        )

        self.wallpapers_path = os.path.expanduser(wallpapers_path)
        self.all_wallpapers = self.get_wallpapers_list()
        self.visible_wallpapers = self.all_wallpapers.copy()
        self.focus_index = -1
        self.focus_mode = False
        self.buttons = []
        self.set_app_paintable(True)
        self._refresh_timeout_id = None
        self._loading_thread = None

        self.viewport = Box(orientation="h", spacing=4)

        self.set_opacity(0)

        self.search = Entry(
            placeholder="Search wallpapers",
            h_expand=True,
            on_changed=self.on_search_changed,
            name="wallpaper-search",
            size=(700, 0),
        )

        self.wallpapers_scrolled = ScrolledWindow(
            child=self.viewport,
            min_content_size=(1120, 250),
            max_content_size=(1120, 250),
            name="wallpaper-scrolled",
            overlay_scroll=True,
            kinetic_scroll=True,
            hscrollbar_policy="always",
        )

        main_box = Box(orientation="v", spacing=1, name="wallpaper-main-box", children=[
            self.wallpapers_scrolled,
            self.search,
        ])

        box = Box(orientation="v", spacing=8, name="wallpaper-box", children=[
            main_box,
        ])

        self.children = CenterBox(center_children=box)

        self.no_wallpapers_label = Label(label="No Wallpapers", name="no-wallpapers-label")
        self.no_wallpapers_label.get_style_context().add_class("large-text")
        self.no_wallpapers_container = CenterBox(
            center_children=self.no_wallpapers_label,
            name="no-wallpapers-container",
            size=(1120, 250),
        )
        self.no_wallpapers_container.set_visible(False)
        self.viewport.add(self.no_wallpapers_container)

        self.connect("key-release-event", self.on_window_key_release)
        self.connect("focus-out-event", self.on_focus_out)

        self.start_background_loading()

    def get_wallpapers_list(self):
        wallpapers = []
        valid_extensions = (".png", ".jpg", ".jpeg", ".bmp")
        if os.path.isdir(self.wallpapers_path):
            for file in os.listdir(self.wallpapers_path):
                if file.lower().endswith(valid_extensions):
                    wallpapers.append({
                        "name": file,
                        "path": os.path.join(self.wallpapers_path, file),
                        "pixbuf": None
                    })
        return wallpapers

    def load_pixbuf_async(self, wallpaper, callback):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(wallpaper["path"], -1, 90)
            target_height = 190
            original_width = pixbuf.get_width()
            original_height = pixbuf.get_height()
            target_width = int(original_width * (target_height / original_height))
            pixbuf = pixbuf.scale_simple(target_width, target_height, GdkPixbuf.InterpType.BILINEAR)
            wallpaper["pixbuf"] = pixbuf
        except Exception:
            wallpaper["pixbuf"] = None
        GLib.idle_add(callback, wallpaper)

    def start_background_loading(self):
        def load_wallpapers():
            for wallpaper in self.all_wallpapers:
                if wallpaper["pixbuf"] is None:
                    self.load_pixbuf_async(wallpaper, self.on_pixbuf_loaded)
            GLib.idle_add(self.refresh_buttons)

        self._loading_thread = threading.Thread(target=load_wallpapers, daemon=True)
        self._loading_thread.start()

    def on_pixbuf_loaded(self, wallpaper):
        if wallpaper in self.visible_wallpapers and self.is_visible():
            self.refresh_buttons()

    def refresh_buttons(self):
        if self._refresh_timeout_id is not None:
            GLib.source_remove(self._refresh_timeout_id)
            self._refresh_timeout_id = None

        old_children = list(self.viewport.children)
        if self.no_wallpapers_label in old_children:
            old_children.remove(self.no_wallpapers_container)

        for child in old_children:
            child.get_style_context().add_class("fade-out")

        def remove_old_and_add_new():
            for child in old_children:
                self.viewport.remove(child)

            self.buttons = []
            buttons_to_show = self.visible_wallpapers

            if not buttons_to_show:
                self.viewport.add(self.no_wallpapers_container)
                self.no_wallpapers_container.set_visible(True)
            else:
                self.no_wallpapers_container.set_visible(False)
                for wallpaper in buttons_to_show:
                    if wallpaper["pixbuf"] is not None:
                        btn = self.create_wallpaper_button(wallpaper)
                        btn.get_style_context().add_class("fade-in")
                        self.viewport.add(btn)
                        self.buttons.append(btn)

            self.anim_target_opacity = 1.0
            self.anim_search_target_opacity = 1.0

            if not self.animation_running:
                self.animation_running = True
                GLib.timeout_add(10, self.animation_step)

            self.focus_index = -1
            self.focus_mode = False

            self._refresh_timeout_id = None
            return False

        self._refresh_timeout_id = GLib.timeout_add(100, remove_old_and_add_new)

    def create_wallpaper_button(self, wallpaper):
        image = Image(pixbuf=wallpaper["pixbuf"], keep_aspect=True) if wallpaper["pixbuf"] else Label(label="[No Preview]", size=(190, 90))
        box = Box(orientation="v", spacing=0, children=[image], h_expand=False)

        btn = Button(child=box, name="wallpaper-button")

        def on_click(*_):

            self.animate_hide()

            subprocess.Popen(f"swww img --transition-fps 144 --transition-duration 1 -t any {wallpaper['path']}", shell=True)
            subprocess.Popen(f"ln -sf {wallpaper['path']} ~/.current.wall", shell=True)
            send_notification(
                "Wallpaper",
                f"Wallpaper changed to {wallpaper['name']}",
                urgency="low",
                icon=wallpaper["path"]
            )
            GLib.timeout_add(500, lambda: self.search.set_text("") or False)

        btn.connect("clicked", on_click)
        btn._launcher_click = on_click
        return btn

    def on_search_changed(self, entry):
        text = entry.get_text().strip().casefold()
        self.visible_wallpapers = [
            wallpaper for wallpaper in self.all_wallpapers
            if text in wallpaper["name"].casefold()
        ]
        self.refresh_buttons()

    def on_window_key_release(self, widget, event):
        keyval = event.get_keyval()[1]
        if keyval == 65307:  # Escape
            self.animate_hide()
            return True
        if self.focus_mode:
            if keyval == 65363:  # Right arrow
                if self.focus_index < len(self.buttons) - 1:
                    self.focus_index += 1
                    self.buttons[self.focus_index].grab_focus()
                    # GLib.idle_add(self.center_button, self.buttons[self.focus_index])
                return True
            if keyval == 65361:  # Left arrow
                if self.focus_index > 0:
                    self.focus_index -= 1
                    self.buttons[self.focus_index].grab_focus()
                    # GLib.idle_add(self.center_button, self.buttons[self.focus_index])
                return True

            if keyval == 65293:
                if 0 <= self.focus_index < len(self.buttons):
                    self.buttons[self.focus_index]._launcher_click
                return True

            self.focus_mode = False
            self.search.grab_focus()
            return False
        else:
            if keyval == 65363 or keyval == 65361:  # Right or Left arrow
                if self.buttons:
                    self.focus_mode = True
                    self.focus_index = 0
                    self.buttons[0].grab_focus()
                    # GLib.idle_add(self.center_button, self.buttons[0])
                return True
        return False
    
    def animate_show(self):
        self.refresh_buttons()
        self.visible_wallpapers = self.all_wallpapers.copy()
        GLib.idle_add(self.search.grab_focus)
        super().animate_show()
