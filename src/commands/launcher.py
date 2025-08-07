from gi.repository import GdkPixbuf

from utils.path import get_root_path

class CustomCommand:
    def __init__(self, name: str, description: str, command: str | list[str], icon_path: str | None = None):
        self.name = name
        self.description = description
        self.command = command
        self.icon_path = icon_path or str(get_root_path() / "icons" / "default.png")

    @property
    def display_name(self) -> str:
        return self.name

    def launch(self):
        import subprocess
        shell = True if isinstance(self.command, str) else False
        subprocess.Popen(self.command, shell=shell)

    def get_icon_pixbuf(self, size=24):
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_size(self.icon_path, size, size)
        except Exception:
            import traceback
            traceback.print_exc()
            return None
