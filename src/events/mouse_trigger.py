from fabric.widgets.box import Box
from gi.repository import GLib, Gdk
from windows.wayland import WaylandWindow as Window

class TriggerWindow(Window):
    def __init__(self, target_window: Window, name="trigger", size=(100, 100), pos=(0, 0), anchor="left bottom", **kwargs):
        super().__init__(
            title="Trigger",
            name=name,
            layer="top",
            visible=True,
            keyboard_mode="off",
            exclusivity="none",
            exclusive=False,
            **kwargs
        )
        self.target_window = target_window
        container = Box()
        container.set_size_request(size[0], size[1])
        self.children = container

        self.anchor = anchor
        self.offset = pos

        self.connect("enter-notify-event", self.on_mouse_enter)
        # self.connect("leave-notify-event", self.on_mouse_leave)
        self.show()

    def on_mouse_enter(self, *args):
        self.target_window.animate_show()
        return True

    def on_mouse_leave(self, *args):
        self.target_window.animate_hide()
        return True
