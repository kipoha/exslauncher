from gi.repository import GdkPixbuf

class CustomCommand:
    def __init__(self, name: str, command: str | list[str], icon_path: str | None = None):
        self.name = name
        self.display_name = name
        self.command = command
        self.icon_path = icon_path

    def launch(self):
        import subprocess
        shell = True if isinstance(self.command, str) else False
        subprocess.Popen(self.command, shell=shell)

    def get_icon_pixbuf(self, size=24):
        if self.icon_path:
            try:
                return GdkPixbuf.Pixbuf.new_from_file_at_size(self.icon_path, size, size)
            except Exception:
                import traceback
                traceback.print_exc()
                return None
        return None
