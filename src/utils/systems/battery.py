import subprocess


def get_battery_status():
    try:
        output = subprocess.check_output(["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT0"]).decode()
        percent = next(line for line in output.splitlines() if "percentage" in line).split(":")[1].strip()
        state = next(line for line in output.splitlines() if "state" in line).split(":")[1].strip()
        return f"{percent} ({state})"
    except Exception:
        return "Battery N/A"
