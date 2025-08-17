from gi.repository import Gdk, GdkPixbuf

from fabric.widgets.box import Box
from fabric.widgets.label import Label

from windows.wayland import WaylandWindow as Window

class Bar(Window):
    def __init__(self, *args, **kwargs):
        screen = Gdk.Screen.get_default()
        width = screen.get_width()
        height = screen.get_height()
        super().__init__(
            title="Vertical Bar",
            name="bar-window",
            layer="top",
            keyboard_mode="off",
            exclusivity="none",
            visible=True,
            all_visible=True,
            size=(width, height),
            **kwargs
        )

        self.main_box = Box(name="main-box", orientation="h", h_expand=True, v_expand=True)
        self.add(self.main_box)

        self.side_bar = Box(
            name="side-bar",
            orientation="v",
            width=60,
            h_expand=False,
            v_expand=True,
        )
        self.main_box.pack_start(self.side_bar, False, False, 0)

        self.content_box = Box(name="content-box", orientation="v", h_expand=True, v_expand=True)
        self.main_box.pack_start(self.content_box, True, True, 0)

        # Добавим кнопки в ба
        for i in range(5):
            lbl = Label(f"Btn {i+1}")
            self.side_bar.pack_start(lbl, False, False, 5)

        self.show_all()
        #
        # self.main_box = Box(name="main-box", orientation="h", h_expand=True, v_expand=True)
        # self.add(self.main_box)
        #
        # self.side_bar = Box(
        #     name="side-bar",
        #     orientation="v",
        #     width=60,
        #     h_expand=False,
        #     v_expand=True,
        # )
        # self.main_box.pack_start(self.side_bar, False, False, 0)
        #
        # self.content_box = Box(name="content-box", orientation="v", h_expand=True, v_expand=True)
        # self.main_box.pack_start(self.content_box, True, True, 0)
        #
        # for i in range(5):
        #     lbl = Label(f"Btn {i+1}")
        #     self.side_bar.pack_start(lbl, False, False, 5)
        #
        # self.set_corner_radius(20)  # примерная функция, зависит от реализации Window
        # self.set_border_color("#444")  # цвет рамки
        # self.set_border_width(4)
        # self.show_all()
