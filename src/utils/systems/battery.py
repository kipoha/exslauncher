import psutil


def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return {"percent": 0, "plugged": False}
    return {
        "percent": int(battery.percent),
        "plugged": battery.power_plugged
    }
