import subprocess

from commands.launcher import CustomCommand
from utils.path import get_root_path
from utils.notify_system import send_notification


class ColorPickerCommand(CustomCommand):
    def __init__(self):
        super().__init__(
            "Color Picker",
            [],   
            str(get_root_path() / "icons" / "color_picker.png"),
        )

    def launch(self):
        proc = subprocess.Popen(
            "hyprpicker -a", shell=True, stdout=subprocess.PIPE, text=True
        )
        color, _ = proc.communicate()
        color = color.strip()

        if not color:
            return

        subprocess.run(["wl-copy"], input=color, text=True)

        send_notification(
            "Color Picker",
            "Color copied to clipboard",
            urgency="low",
            color_icon=color
        )


def get_custom_commands() -> list[CustomCommand]:
    root = get_root_path()
    commands = [
        CustomCommand(
            "Search in Browser",
            "fabric-cli exec default browser.toggle\\(\\)",
            str(root / "icons" / "search.png"),
        ),
        CustomCommand(
            "Clipboard",
            "fabric-cli exec default clipboard.toggle\\(\\)",
            str(root / "icons" / "clipboard.png"),
        ),
        CustomCommand(
            "Wallpaper Changer",
            "fabric-cli exec default wallpaper.toggle\\(\\)",
            str(root / "icons" / "wallpaper.png"),
        ),
        ColorPickerCommand(),
        CustomCommand(
            "Lock Screen", "hyprlock", str(root / "icons" / "lock_screen.png")
        ),
        CustomCommand(
            "Shutdown", "systemctl poweroff", str(root / "icons" / "shutdown.png")
        ),
        CustomCommand("Logout", "pkill niri", str(root / "icons" / "logout.png")),
        CustomCommand("Reboot", "systemctl reboot", str(root / "icons" / "reboot.png")),
    ]
    return commands
