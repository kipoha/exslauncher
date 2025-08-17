from gi.repository import GLib

from fabric.widgets.button import Button

from widgets.bar.battery_profile import BatteryProfile

from utils.systems.battery import get_battery_status
from utils.notify_system import send_notification


class Battery(Button):
    def __init__(self, **kwargs):
        super().__init__(label="󰁽", size=20, name="bar-battery", h_align="center", on_clicked=self.on_clicked, **kwargs)
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
    
    def on_clicked(self, *_):
        print("Battery clicked")
        self.popup_window.toggle()
