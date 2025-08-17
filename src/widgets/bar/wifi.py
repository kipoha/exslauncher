from gi.repository import GLib

from fabric.widgets.label import Label
from utils.systems.wifi import get_wifi_status


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
