from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.shapes import Corner
from fabric.widgets.centerbox import CenterBox

from windows.wayland import WaylandWindow as Window


BORDER_SIZE = 3
BORDER_MARGIN = -12


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
        super().__init__("screen-border-top" ,"left top right", [0, BORDER_SIZE], margin=(BORDER_MARGIN, 0, 0, 0), **kwargs)


class BottomBorder(Border):
    def __init__(self, **kwargs):
        super().__init__("screen-border-bottom", "left bottom right", [0, BORDER_SIZE], margin=(0, 0, BORDER_MARGIN, 0), **kwargs)


class RightBorder(Window):
    def __init__(self, **kwargs):
        name = "screen-border-right"
        super().__init__(
            name=name,
            layer="top",
            anchor="top right bottom",
            exclusivity="auto",
            size=[BORDER_SIZE, 0],
            margin=(0, BORDER_MARGIN, 0, 0),
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
            layer="top",
            anchor="left top right",
            exclusivity="none",
            **kwargs
        )
        self.top_box = CenterBox(
            orientation="h",
            start_children=[
                Corner("top-left", name="corner-top-left", size=22),
            ],
            end_children=[
                Corner("top-right", name="corner-top-right", size=22),
            ]
        )
        self.add(Box(orientation="v", children=[self.top_box]))

        self.show()


class BottomCorners(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="bottom-corners",
            layer="top",
            anchor="left bottom right",
            exclusivity="none",
            **kwargs
        )
        self.bottom_box = CenterBox(
            orientation="h",
            start_children=[
                Corner("bottom-left", name="corner-bottom-left", size=22),
            ],
            end_children=[
                Corner("bottom-right", name="corner-bottom-right", size=22),
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
