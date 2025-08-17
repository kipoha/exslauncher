from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.system_tray.widgets import SystemTray
from fabric.widgets.centerbox import CenterBox

from windows.wayland import WaylandWindow as Window

from widgets.bar.battery import Battery
from widgets.bar.wifi import Wifi
from widgets.bar.bluetooth import Bluetooth
from widgets.bar.clock import Clock


class Bar(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="bar-window",
            layer="top",
            anchor="top left bottom",
            exclusivity="auto",
            **kwargs
        )
        # top


        # center
        self.clock = Clock(name="bar-clock", fmt="%H\n%M", interval=1000, h_align="center")
        self.clock_icon = Label(label="", size=20, name="bar-clock-icon", h_align="center")
        self.time_box = Box(orientation="v", spacing=2, name="bar-time-box", children=[self.clock_icon, self.clock])


        # bottom
        self.tray = SystemTray(name="bar-system-tray", icon_size=20, orientation="v", spacing=3)
        self.bluetooth = Bluetooth()
        self.wifi = Wifi()
        self.battery = Battery()
        self.systems = Box(orientation="v", spacing=3, name="bar-systems", children=[
            self.bluetooth,
            self.wifi,
            self.battery
        ])

        self.top_box = Box(orientation="v", spacing=10, name="bar-top-box", v_align="start", children=[

        ])
        self.center_box = Box(orientation="v", spacing=10, name="bar-center-box", v_align="center", children=[
            self.time_box
        ])
        self.bottom_box = Box(orientation="v", spacing=10, name="bar-bottom-box", v_align="end", children=[
            self.tray,
            self.systems
        ])
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
