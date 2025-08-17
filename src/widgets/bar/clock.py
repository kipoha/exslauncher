from gi.repository import GLib

from datetime import datetime

from fabric.widgets.label import Label


class Clock(Label):
    def __init__(self, fmt="%H\n%M", interval=1000, **kwargs):
        super().__init__(label=datetime.now().strftime(fmt), **kwargs)
        self.fmt = fmt
        self._timer_id = GLib.timeout_add(interval, self._tick)

    def _tick(self):
        self.set_properties(label=datetime.now().strftime(self.fmt))
        return True
