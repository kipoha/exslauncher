from fabric import Application

from widgets.launcher import Launcher
from widgets.clipboard import Clipboard
from widgets.wallpaper import WallpaperChooser
from widgets.firefox_search import FirefoxSearch

from utils.path import get_root_path
from utils.load_config import config


if __name__ == "__main__":
    launcher = Launcher()
    clipboard = Clipboard()
    wallpaper = WallpaperChooser(config.get("wallpapers_path", "~/.local/share/wallpapers"))
    browser = FirefoxSearch()
    app = Application()

    app.set_stylesheet_from_file(str(get_root_path() / "main.css"))

    app.run()
