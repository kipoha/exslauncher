import subprocess


def get_wifi_status():
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,DEVICE,TYPE", "con", "show", "--active"],
            capture_output=True,
            text=True,
        )

        active_iface = None
        for line in result.stdout.splitlines():
            name, device, type_ = line.strip().split(":")
            if type_ == "802-11-wireless":
                active_iface = device
                break

        if not active_iface:
            return {"ssid": None, "signal": 0, "speed": None}

        wifi_list = subprocess.run(
            ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,RATE", "dev", "wifi"],
            capture_output=True,
            text=True,
        )
        for wline in wifi_list.stdout.splitlines():
            in_use, ssid, signal, rate = wline.strip().split(":")
            if in_use == "*":  # это активная сеть
                return {"ssid": ssid, "signal": int(signal), "speed": rate}

        return {"ssid": None, "signal": 0, "speed": None}

    except Exception:
        import traceback
        traceback.print_exc()
        return {"ssid": None, "signal": 0, "speed": None}
