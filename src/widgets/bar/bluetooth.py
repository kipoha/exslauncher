from gi.repository import GLib

from fabric.widgets.label import Label

from utils.systems.bluetooth import get_bluetooth_status


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
