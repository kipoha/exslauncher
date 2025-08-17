import subprocess


def get_bluetooth_status():
    try:
        output = subprocess.check_output(["bluetoothctl", "show"]).decode()
        powered = next(line for line in output.splitlines() if "Powered:" in line).split(":")[1].strip()
        return powered == "yes"
    except Exception:
        import traceback
        traceback.print_exc()
        return False
