import sys
import signal

from utils.notify_system import send_notification

try:
    from fabric import Application
except ImportError:
    send_notification(
        "Fabric Launcher",
        "Fabric Launcher is not installed\n```bash\nyay -S python-fabric-git\n```",
        urgency="critical",
        app_name="EXS Launcher",
    )
    exit(1)

from widgets.launcher import Launcher
from widgets.clipboard import Clipboard
from widgets.wallpaper import WallpaperChooser
from widgets.firefox_search import FirefoxSearch
from widgets.osd import OSD
from widgets.bar import Bar, Corners

from utils.path import get_root_path
from utils.load_config import config


def handle_exit(signum, frame):
    send_notification(
        "Fabric Launcher", "Launcher disabled\n", urgency="low", app_name="EXS Launcher"
    )
    exit(0)


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGTERM, handle_exit)
        signal.signal(signal.SIGINT, handle_exit)
        bar = Bar()
        corners = Corners()
        launcher = Launcher()
        clipboard = Clipboard()
        wallpaper = WallpaperChooser(
            config.get("wallpapers_path", "~/.local/share/wallpapers")
        )
        browser = FirefoxSearch()
        osd = OSD()
        app = Application()

        app.set_stylesheet_from_file(str(get_root_path() / "main.css"))
        reload = sys.argv[1] == "--reload" if len(sys.argv) > 1 else False
        if reload:
            send_notification(
                "Fabric Launcher",
                "Launcher reloaded\n",
                urgency="low",
                app_name="EXS Launcher",
            )
        app.run()
    except (KeyboardInterrupt, SystemExit, OSError):
        handle_exit(0, None)
    except Exception:
        import traceback
        error = traceback.format_exc()

        print(error)
        send_notification(
            "Fabric Launcher",
            f"Fabric Launcher is not running\n```py\n{error}\n```",
            urgency="critical",
            app_name="EXS Launcher",
        )
        exit(1)
