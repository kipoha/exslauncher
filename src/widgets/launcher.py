from gi.repository import GLib

from fabric.utils import get_desktop_applications
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow

from commands.commands import get_custom_commands

from utils.load_config import config
from utils.path import get_root_path

from widgets.base import AnimatedWindow as Window


class Launcher(Window):
    def __init__(self):
        super().__init__(
            title="launcher",
            name="launcher",
            layer="top",
            keyboard_mode="on-demand",
            exclusivity="none",
            anchor="center bottom",
            visible=False,
            all_visible=False,
        )
        self.all_apps = get_desktop_applications()
        self.visible_apps = self.all_apps.copy()
        self.commands = get_custom_commands()
        self.focus_index = -1
        self.focus_mode = False
        self.buttons = []
        self.set_app_paintable(True)
        self._refresh_timeout_id = None

        self.anim_current_content_height = 300
        self.anim_target_content_height = 300

        self.viewport = Box(orientation="v", spacing=4)

        self.set_opacity(0)

        self.search = Entry(
            placeholder=f"Write {config.get('prefix', '>')} to search commands",
            h_expand=True,
            on_changed=self.on_search_changed,
            size=(700, 0),
        )
        self.search_image_box = Box(
            name="launcher-search-image-box",
            orientation="h",
            spacing=4,
            children=[
                Image(
                    str(get_root_path() / "icons" / "search.png"),
                    size=(28, 28),
                    v_align="center",
                    h_align="center",
                )
            ],
        )

        self.search_box = Box(
            name="launcher-search",
            orientation="h",
            spacing=4,
            children=[
                self.search_image_box,
                self.search,
            ],
        )

        self.apps_scrolled = ScrolledWindow(
            child=self.viewport,
            min_content_size=(400, 300),
            max_content_size=(600, 400),
            name="launcher-apps-scrolled",
            overlay_scroll=True,
            kinetic_scroll=True,
        )

        main_box = Box(
            orientation="v",
            spacing=1,
            name="launcher-main-box",
            children=[
                self.apps_scrolled,
                self.search_box,
            ],
        )

        box = Box(
            orientation="v",
            spacing=8,
            name="launcher-box",
            children=[
                main_box,
            ],
        )

        self.children = CenterBox(center_children=box)

        self.refresh_buttons()

        self.connect("key-release-event", self.on_window_key_release)
        self.connect("focus-out-event", self.on_focus_out)

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
            buttons_to_show = self.visible_apps[:max_buttons_to_show]

            for app in buttons_to_show:
                btn = self.create_app_button(app)
                btn.get_style_context().add_class("fade-in")
                self.viewport.add(btn)
                self.buttons.append(btn)

            item_height = 40
            spacing = self.viewport.get_spacing() or 4
            new_height = min(len(buttons_to_show) * (item_height + spacing), 400)

            self.anim_current_content_height = new_height
            self.anim_target_opacity = 1.0
            self.anim_search_target_opacity = 1.0

            self.anim_target_content_height = new_height + 20

            if not self.animation_running:
                self.animation_running = True
                GLib.timeout_add(10, self.animation_step)

            self.focus_index = -1
            self.focus_mode = False

            self._refresh_timeout_id = None
            return False

        self._refresh_timeout_id = GLib.timeout_add(160, remove_old_and_add_new)

    def create_app_button(self, app):
        icon = Image(pixbuf=app.get_icon_pixbuf(size=30))
        label = Label(
            label=app.display_name or app.name or "Unknown",
            h_expand=True,
            h_align="start",
            size_hint=(1.0, None),
            style="""
                font-size: 15px;
                font-weight: bold;
            """
        )
        desc = Label(
            label=app.description or "",
            size_hint=(1.0, None),
            h_expand=True,
            h_align="start",
            style="""
                font-size: 11px;
                font-style: italic;
                color: #888;
            """
        )
        label_data_box = Box(
            orientation="v", spacing=0, children=[label, desc]
        )

        box = Box(orientation="h", spacing=6, children=[icon, label_data_box], h_expand=True)

        btn = Button(child=box, name="launcher-app-button")

        def on_click(*_):
            self.animate_hide()
            app.launch()

            def clear_text_later():
                self.search.set_text("")
                return False

            GLib.timeout_add(500, clear_text_later)

        btn.connect("clicked", on_click)
        btn._launcher_click = on_click
        return btn

    def on_search_changed(self, entry):
        text = entry.get_text().strip().casefold()
        if text.startswith(config.get("prefix", ">")):
            self.visible_apps = [
                cmd
                for cmd in self.commands
                if text[1:]
                in ((cmd.display_name or "") + " " + (cmd.name or "")).casefold()
            ]
        else:
            self.visible_apps = [
                app
                for app in self.all_apps
                if text
                in ((app.display_name or "") + " " + (app.name or "")).casefold()
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
        cont = super().animation_step()

        diff_content_height = self.anim_target_content_height - self.anim_current_content_height
        if abs(diff_content_height) < 1:
            self.anim_current_content_height = self.anim_target_content_height
        else:
            self.anim_current_content_height += diff_content_height * self.speed

        min_height = int(self.anim_current_content_height)
        max_height = min_height + 20
        self.apps_scrolled.set_min_content_size((400, min_height))
        self.apps_scrolled.set_max_content_size((600, max_height))

        return cont

    def animate_show(self):
        self.refresh_buttons()
        self.visible_apps = self.all_apps.copy()
        GLib.idle_add(self.search.grab_focus)
        super().animate_show()
