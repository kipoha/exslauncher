import subprocess


def get_clipboard_history(limit=50):
    result = subprocess.run(["cliphist", "list"], capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.strip().split("\n")
        history = []
        for line in lines[:limit]:
            idx, raw = line.split("\t", 1)
            history.append({
                "id": idx,
                "raw": raw,
                "is_binary": "[[ binary data" in raw,
            })
        return history
    return []
