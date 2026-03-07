import os
import sys
import time
import threading
import requests
import urllib3
from pystray import Icon, MenuItem, Menu
from PIL import Image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOCKFILE_PATH = os.path.join(
    "D:\\", "Riot Games", "League of Legends", "lockfile"
)


def resource_path(filename):
    """Resolve o caminho do recurso tanto em dev quanto empacotado pelo PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def load_tray_icon():
    return Image.open(resource_path("tray_icon.png"))


def read_lockfile():
    try:
        with open(LOCKFILE_PATH, "r") as f:
            content = f.read().strip()
        parts = content.split(":")
        return parts[2], parts[3]
    except (FileNotFoundError, IndexError, PermissionError):
        return None, None


def accept_match(port, password):
    url = f"https://127.0.0.1:{port}/lol-matchmaking/v1/ready-check"
    auth = ("riot", password)

    try:
        resp = requests.get(url, auth=auth, verify=False, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("state") == "InProgress" and data.get("playerResponse") == "None":
                requests.post(f"{url}/accept", auth=auth, verify=False, timeout=3)
                return True
    except (requests.ConnectionError, requests.Timeout):
        pass
    except Exception:
        pass

    return False


def run_loop(icon):
    icon.visible = True
    waiting_for_client = True
    accepted_count = 0

    while icon.visible:
        port, password = read_lockfile()

        if port is None:
            if not waiting_for_client:
                waiting_for_client = True
            icon.title = "Auto-Accept LoL - Aguardando cliente..."
            time.sleep(3)
            continue

        if waiting_for_client:
            waiting_for_client = False

        if accept_match(port, password):
            accepted_count += 1
            icon.title = f"Auto-Accept LoL - Partida aceita! ({accepted_count})"
            time.sleep(5)
        else:
            icon.title = f"Auto-Accept LoL - Monitorando... ({accepted_count} aceitas)"

        time.sleep(1)


def on_exit(icon):
    icon.visible = False
    icon.stop()
    os._exit(0)


def main():
    tray_image = load_tray_icon()

    icon = Icon(
        "auto-accept-lol",
        icon=tray_image,
        title="Auto-Accept LoL - Iniciando...",
        menu=Menu(MenuItem("Sair", on_exit)),
    )

    thread = threading.Thread(target=run_loop, args=(icon,), daemon=True)
    thread.start()

    icon.run()


if __name__ == "__main__":
    main()
