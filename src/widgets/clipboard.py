import subprocess

from gi.repository import GLib, GdkPixbuf

from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow

from utils.clipboard_history import get_clipboard_history

from windows.wayland import WaylandWindow as Window


class Clipboard(Window):
    def __init__(self):
        super().__init__(
            title="clipboard",
            name="clipboard",
            layer="top",
            anchor="center bottom",
            exclusivity="none",
            keyboard_mode="on-demand",
            visible=False,
            all_visible=False,
            margin=(0, 0, -40, 0),
        )

        self.buffers = get_clipboard_history()
        self.visible_buffers = []
        self.focus_index = -1
        self.focus_mode = False
        self.buttons = []
        self.set_app_paintable(True)
        self._refresh_timeout_id = None

        self.viewport = Box(orientation="v", spacing=4)

        self.set_opacity(0)

        self.anim_current_height = 0
        self.anim_target_height = 0
        self.anim_current_opacity = 0
        self.anim_target_opacity = 0
        self.anim_search_opacity = 0
        self.anim_search_target_opacity = 0
        self.animation_running = False

        self.search = Entry(
            placeholder="",
            h_expand=True,
            on_changed=self.on_search_changed,
            name="clipboard-search",
            size=(900, 0),
        )

        self.buffers_scrolled = ScrolledWindow(
            child=self.viewport,
            min_content_size=(400, 300),
            max_content_size=(600, 400),
            name="clipboard-buffers-scrolled",
            overlay_scroll=True,
            kinetic_scroll=True,
        )

        main_box = Box(orientation="v", spacing=1, name="clipboard-main-box", children=[
            self.buffers_scrolled,
            self.search,
        ])

        box = Box(orientation="v", spacing=8, name="clipboard-box", children=[
            main_box,
        ])

        self.children = CenterBox(center_children=box)

        self.refresh_buttons()

        self.connect("key-release-event", self.on_window_key_release)

    def refresh_buttons(self):
        if self._refresh_timeout_id is not None:
            GLib.source_remove(self._refresh_timeout_id)
            self._refresh_timeout_id = None

        old_children = list(self.viewport.children)

        for child in old_children:
            child.get_style_context().add_class("fade-out")

        def remove_old_and_add_new():

            for child in old_children:
                self.viewport.remove(child)

            self.buttons = []
            max_buttons_to_show = 20
            buttons_to_show = self.visible_buffers[:max_buttons_to_show]

            for app in buttons_to_show:
                btn = self.create_app_button(app)
                btn.get_style_context().add_class("fade-in")
                self.viewport.add(btn)
                self.buttons.append(btn)

            item_height = 40  
            spacing = self.viewport.get_spacing() or 4

            new_height = min(len(buttons_to_show) * (item_height + spacing), 400)

            self.anim_target_height = new_height
            self.anim_target_opacity = 1.0
            self.anim_search_target_opacity = 1.0

            if not self.animation_running:
                self.animation_running = True
                GLib.timeout_add(10, self.animation_step)

            self.focus_index = -1
            self.focus_mode = False

            self._refresh_timeout_id = None
            return False

        self._refresh_timeout_id = GLib.timeout_add(160, remove_old_and_add_new)

    def create_app_button(self, buffer_data):
        buffer_id = buffer_data["id"]
        raw_text = buffer_data["raw"]
        is_binary = buffer_data["is_binary"]

        if is_binary:
            proc = subprocess.run(["cliphist", "decode", str(buffer_id)], capture_output=True)
            image_bytes = proc.stdout

            loader = GdkPixbuf.PixbufLoader.new()
            loader.write(image_bytes)
            loader.close()
            pixbuf = loader.get_pixbuf()

            target_height = 80
            original_width = pixbuf.get_width()
            original_height = pixbuf.get_height()
            target_width = int(original_width * (target_height / original_height))

            pixbuf = pixbuf.scale_simple(target_width, target_height, GdkPixbuf.InterpType.BILINEAR)

            image = Image(pixbuf=pixbuf, size=(0, target_height), keep_aspect=False)
            box = Box(orientation="h", spacing=6, children=[image], h_expand=True)

        else:
            label = Label(label=raw_text.split("\t", 1)[-1])
            box = Box(orientation="h", spacing=6, children=[label], h_expand=True)

        btn = Button(child=box, name="clipboard-buffer-button")

        def on_click(*_):
            self.animate_hide()
            proc = subprocess.Popen(["cliphist", "decode", str(buffer_id)], stdout=subprocess.PIPE)
            subprocess.run(["wl-copy"], stdin=proc.stdout)
            proc.stdout.close()
            proc.wait()

            GLib.timeout_add(500, lambda: self.search.set_text("") or False)

        btn.connect("clicked", on_click)
        btn._launcher_click = on_click
        return btn

    def on_search_changed(self, entry):
        text = entry.get_text().strip().casefold()
        self.visible_buffers = [
            buffer for buffer in self.buffers
            if text in buffer["raw"].casefold()
        ]
        self.refresh_buttons()

    def on_window_key_release(self, widget, event):
        keyval = event.get_keyval()[1]
        if keyval == 65307:
            self.animate_hide()
            return True
        if self.focus_mode:
            if keyval == 65364:
                if self.focus_index < len(self.buttons) - 1:
                    self.focus_index += 1
                    self.buttons[self.focus_index].grab_focus()
                return True

            if keyval == 65362:
                if self.focus_index > 0:
                    self.focus_index -= 1
                    self.buttons[self.focus_index].grab_focus()
                return True

            if keyval == 65293:
                if 0 <= self.focus_index < len(self.buttons):
                    self.buttons[self.focus_index]._launcher_click
                return True

            self.focus_mode = False
            self.search.grab_focus()
            return False

        else:
            if keyval == 65364:
                if self.buttons:
                    self.focus_mode = True
                    self.focus_index = 0
                    self.buttons[0].grab_focus()
                return True
        return False

    def animation_step(self):
        speed = 0.3

        diff_height = self.anim_target_height - self.anim_current_height
        self.anim_current_height += diff_height * speed

        diff_opacity = self.anim_target_opacity - self.anim_current_opacity
        self.anim_current_opacity += diff_opacity * speed

        diff_search_opacity = self.anim_search_target_opacity - self.anim_search_opacity
        self.anim_search_opacity += diff_search_opacity * speed

        height = int(self.anim_current_height) + 10
        min_height = max(height, 1)
        max_height = max(min_height, 1)
        self.buffers_scrolled.set_min_content_size((400, min_height))
        self.buffers_scrolled.set_max_content_size((600, max_height))

        self.set_opacity(self.anim_current_opacity)
        self.search.set_opacity(self.anim_search_opacity)

        if abs(diff_height) < 1 and abs(diff_opacity) < 0.01 and abs(diff_search_opacity) < 0.01:
            self.anim_current_height = self.anim_target_height
            self.anim_current_opacity = self.anim_target_opacity
            self.anim_search_opacity = self.anim_search_target_opacity
            height = int(self.anim_current_height) + 10
            min_height = max(height, 1)
            max_height = max(min_height, 1)
            self.buffers_scrolled.set_min_content_size((400, min_height))
            self.buffers_scrolled.set_max_content_size((600, max_height))
            self.set_opacity(self.anim_current_opacity)
            self.search.set_opacity(self.anim_search_opacity)
            self.animation_running = False

            if self.anim_current_opacity <= 0:
                self.hide()

            return False

        return True

    def animate_hide(self):
        self.anim_target_height = 0
        self.anim_target_opacity = 0
        self.anim_search_target_opacity = 0
        if not self.animation_running:
            self.animation_running = True
            GLib.timeout_add(10, self.animation_step)

    def animate_show(self):
        self.show_all()
        self.buffers = get_clipboard_history()
        self.visible_buffers = self.buffers.copy()
        self.anim_current_height = 0
        self.anim_current_opacity = 0
        self.anim_search_opacity = 0

        self.anim_target_opacity = 1.0
        self.anim_search_target_opacity = 1.0

        self.refresh_buttons()
        GLib.idle_add(self.search.grab_focus)
        if not self.animation_running:
            self.animation_running = True
            GLib.timeout_add(10, self.animation_step)

    def toggle(self):
        if self.is_visible():
            self.animate_hide()
        else:
            self.animate_show()
