from gi.repository import GLib

from datetime import datetime

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.system_tray.widgets import SystemTray, SystemTrayItem
from fabric.widgets.shapes import Corner
from fabric.widgets.centerbox import CenterBox


from windows.wayland import WaylandWindow as Window


BORDER_SIZE = 3

class Clock(Label):
    def __init__(self, fmt="%H\n%M", interval=1000, **kwargs):
        super().__init__(label=datetime.now().strftime(fmt), **kwargs)
        self.fmt = fmt
        self._timer_id = GLib.timeout_add(interval, self._tick)

    def _tick(self):
        self.set_properties(label=datetime.now().strftime(self.fmt))
        return True


class Bar(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="bar-window",
            layer="top",
            anchor="top left bottom",
            exclusivity="auto",
            **kwargs
        )

        self.top_box = Box(orientation="v", spacing=10, name="bar-top-box", v_align="start")
        self.center_box = Box(orientation="v", spacing=10, name="bar-center-box", v_align="center")
        self.bottom_box = Box(orientation="v", spacing=10, name="bar-bottom-box", v_align="end")

        self.date_time = Clock()
        self.center_box.add(self.date_time)

        # self.tray = SystemTray(name="system-tray", size=20, orientation="v", spacing=3)
        # self.bottom_box.add(self.tray)

        self.children = CenterBox(
            orientation="v",
            start_children=[
                self.top_box,
            ],
            center_children=[
                self.center_box,
            ],
            end_children=[
                self.bottom_box
            ]
        )


class Border(Window):
    def __init__(self, name, anchor, size, **kwargs):
        super().__init__(
            name=name,
            layer="top",
            anchor=anchor,
            exclusivity="auto",
            size=size,
            **kwargs
        )
        self.children = Box(name=name, children=[Label(label="", v_expand=True, h_expand=True, size=size)], orientation="h")
        self.show()


class TopBorder(Border):
    def __init__(self, **kwargs):
        super().__init__("screen-border-top" ,"left top right", [0, BORDER_SIZE], **kwargs)


class BottomBorder(Border):
    def __init__(self, **kwargs):
        super().__init__("screen-border-bottom", "left bottom right", [0, BORDER_SIZE], **kwargs)


class RightBorder(Window):
    def __init__(self, **kwargs):
        name = "screen-border-right"
        super().__init__(
            name=name,
            layer="top",
            anchor="top right bottom",
            exclusivity="auto",
            size=[BORDER_SIZE, 0],
            **kwargs
        )
        self.children = Box(
            name=name,
            children=[Label(label="", v_expand=True, h_expand=True, angle=90, size=[BORDER_SIZE, 0])],
            orientation="v"
        )
        self.show()


class TopCorners(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="top-corners",
            layer="overlay",
            anchor="left top right",
            exclusivity="none",
            **kwargs
        )
        self.top_box = CenterBox(
            orientation="h",
            start_children=[
                Corner("top-left", name="corner-top-left", size=20),
            ],
            end_children=[
                Corner("top-right", name="corner-top-right", size=20),
            ]
        )
        self.add(Box(orientation="v", children=[self.top_box]))

        self.show()


class BottomCorners(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="bottom-corners",
            layer="overlay",
            anchor="left bottom right",
            exclusivity="none",
            **kwargs
        )
        self.bottom_box = CenterBox(
            orientation="h",
            start_children=[
                Corner("bottom-left", name="corner-bottom-left", size=20),
            ],
            end_children=[
                Corner("bottom-right", name="corner-bottom-right", size=20),
            ]
        )
        self.add(Box(orientation="v", children=[self.bottom_box]))

        self.show()


class Corners:
    def __init__(self) -> None:
        self.top_border = TopBorder()
        self.bottom_border = BottomBorder()
        self.right_border = RightBorder()
        self.top = TopCorners()
        self.bottom = BottomCorners()
