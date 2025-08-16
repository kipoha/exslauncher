from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.centerbox import CenterBox
from gi.repository import GLib
from windows.wayland import WaylandWindow as Window

class TriggerWindow(Window):
    def __init__(self, target_window: Window, name="trigger", size=(100, 100), **kwargs):
        super().__init__(
            title="Trigger",
            name=name,
            layer="top",
            visible=True,
            keyboard_mode="off",
            exclusivity="none",
            size=size,
            **kwargs
        )
        print("trigger window created")
        self.target_window = target_window

        self.children = CenterBox(center_children=Box(children=[Label(text="")]))

        self.connect("enter-notify-event", self.on_mouse_enter)
        self.connect("leave-notify-event", self.on_mouse_leave)
        self.show()

    def on_mouse_enter(self, *args):
        self.target_window.animate_show()
        return True

    def on_mouse_leave(self, *args):
        self.target_window.animate_hide()
        return True
