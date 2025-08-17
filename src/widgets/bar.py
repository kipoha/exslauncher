from gi.repository import GLib, Gdk

from datetime import datetime

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.system_tray.widgets import SystemTray
from fabric.widgets.shapes import Corner
from fabric.widgets.centerbox import CenterBox

from widgets.battery_profile import BatteryProfile

from windows.wayland import WaylandWindow as Window

from utils.systems.battery import get_battery_status
from utils.systems.wifi import get_wifi_status
from utils.systems.bluetooth import get_bluetooth_status
from utils.notify_system import send_notification


BORDER_SIZE = 3
BORDER_MARGIN = -12

class Clock(Label):
    def __init__(self, fmt="%H\n%M", interval=1000, **kwargs):
        super().__init__(label=datetime.now().strftime(fmt), **kwargs)
        self.fmt = fmt
        self._timer_id = GLib.timeout_add(interval, self._tick)

    def _tick(self):
        self.set_properties(label=datetime.now().strftime(self.fmt))
        return True


class Battery(Label):
    def __init__(self, **kwargs):
        super().__init__(label="󰁽", size=20, name="bar-battery", h_align="center", **kwargs)
        self._timer_id = GLib.timeout_add(5000, self._update)

        self.popup_window = BatteryProfile()
        self.low_battery_notified = False
        self._update()

    def _update(self):
        info = get_battery_status()
        perc = info["percent"]
        plugged = info["plugged"]

        def update_icon(icon):
            self.set_properties(label=icon)

        if plugged:
            update_icon("󰂄")
        elif perc >= 100:
            update_icon("󰁹")
        elif perc >= 90 and perc < 100:
            update_icon("󰂂")
        elif perc >= 80 and perc < 90:
            update_icon("󰂁")
        elif perc >= 70 and perc < 80:
            update_icon("󰂀")
        elif perc >= 60 and perc < 70:
            update_icon("󰁿")
        elif perc >= 50 and perc < 60:
            update_icon("󰁾")
        elif perc >= 40 and perc < 50:
            update_icon("󰁽")
        elif perc >= 30 and perc < 40:
            update_icon("󰁼")
        elif perc >= 20 and perc < 30:
            update_icon("󰁻")
        elif perc >= 10 and perc < 20:
            update_icon("󰁺")
        elif perc >= 0 and perc < 10:
            update_icon("󰂃")

        if perc < 10 and not plugged and not self.low_battery_notified:
            send_notification("Battery low", f"{perc}% remaining")
            self.low_battery_notified = True
        elif perc >= 10 or plugged:  
            self.low_battery_notified = False

        if self.popup_window:
            status = "Charging" if plugged else "Discharging"
            self.popup_window.percentage.set_properties(label=f"{status}: {perc}%")

        return True


class Bluetooth(Label):
    def __init__(self, **kwargs):
        super().__init__(label="󰂱", size=20, name="bar-bluetooth", h_align="center", **kwargs)
        self._timer_id = GLib.timeout_add(5000, self._update)

    def _update(self):
        info = get_bluetooth_status()
        if info:
            self.set_properties(label="󰂱")
        else:
            self.set_properties(label="󰂲")
        return True


class Wifi(Label):
    def __init__(self, **kwargs):
        super().__init__(label="󰤟", size=20, name="bar-wifi", h_align="center", **kwargs)
        self._timer_id = GLib.timeout_add(5000, self._update)

    def _update(self):
        info = get_wifi_status()
        sig = info["signal"]
        if sig > 75:
            self.set_properties(label="󰤨")
        elif sig > 50:
            self.set_properties(label="󰤥")
        elif sig > 25:
            self.set_properties(label="󰤢")
        else:
            self.set_properties(label="󰤟") 
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
            layer="overlay",
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
            layer="overlay",
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
