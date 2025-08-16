import subprocess


def get_wifi_status():
    try:
        output = subprocess.check_output(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"]).decode()
        for line in output.splitlines():
            active, ssid = line.split(":")
            if active == "yes":
                return f"{ssid}"
        return "No Wi-Fi"
    except Exception:
        return "Wi-Fi N/A"
