import json
import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import requests
import urllib3
from pystray import Icon, MenuItem, Menu
from PIL import Image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_LOL_PATH = os.path.join("D:\\", "Riot Games", "League of Legends")
CONFIG_FILENAME = "config.json"


def resource_path(filename):
    """Resolve o caminho do recurso tanto em dev quanto empacotado pelo PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def config_path():
    """Retorna o caminho do arquivo de configuração ao lado do executável."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(os.path.dirname(sys.executable), CONFIG_FILENAME)
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), CONFIG_FILENAME
    )


def load_config():
    """Carrega a configuração do arquivo JSON."""
    path = config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"lol_path": DEFAULT_LOL_PATH}


def save_config(cfg):
    """Salva a configuração no arquivo JSON."""
    path = config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def get_lockfile_path():
    """Retorna o caminho do lockfile baseado na configuração atual."""
    cfg = load_config()
    return os.path.join(cfg["lol_path"], "lockfile")


def open_config_dialog(on_save=None):
    """Abre o modal de configuração para selecionar o caminho do LoL."""
    cfg = load_config()

    root = tk.Tk()
    root.title("Auto-Accept LoL — Configuração")
    root.resizable(False, False)
    root.configure(bg="#1a1a2e")

    window_width, window_height = 520, 210
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - window_width) // 2
    y = (screen_h - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    try:
        root.iconbitmap(resource_path("icon.ico"))
    except tk.TclError:
        pass

    label = tk.Label(
        root,
        text="Pasta de instalação do League of Legends:",
        bg="#1a1a2e",
        fg="#e0e0e0",
        font=("Segoe UI", 10),
    )
    label.pack(pady=(18, 4), padx=16, anchor="w")

    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(padx=16, fill="x")

    path_var = tk.StringVar(value=cfg["lol_path"])
    entry = tk.Entry(
        frame,
        textvariable=path_var,
        font=("Segoe UI", 10),
        bg="#16213e",
        fg="#e0e0e0",
        insertbackground="#e0e0e0",
        relief="flat",
        highlightthickness=1,
        highlightcolor="#0f3460",
        highlightbackground="#0f3460",
    )
    entry.pack(side="left", fill="x", expand=True, ipady=4)

    def browse():
        folder = filedialog.askdirectory(
            title="Selecione a pasta do League of Legends",
            initialdir=path_var.get(),
        )
        if folder:
            path_var.set(folder)

    btn_browse = tk.Button(
        frame,
        text="Procurar…",
        command=browse,
        bg="#0f3460",
        fg="#e0e0e0",
        activebackground="#1a1a5e",
        activeforeground="#ffffff",
        relief="flat",
        font=("Segoe UI", 9),
        cursor="hand2",
    )
    btn_browse.pack(side="left", padx=(8, 0), ipady=2)

    hint = tk.Label(
        root,
        text="Ex: D:\\Riot Games\\League of Legends",
        bg="#1a1a2e",
        fg="#666680",
        font=("Segoe UI", 8),
    )
    hint.pack(padx=16, anchor="w")

    btn_frame = tk.Frame(root, bg="#1a1a2e")
    btn_frame.pack(pady=(18, 12))

    saved = {"value": False}

    def do_save():
        chosen = path_var.get().strip()
        if not chosen:
            messagebox.showwarning(
                "Caminho vazio",
                "Informe o caminho de instalação do LoL.",
                parent=root,
            )
            return
        cfg["lol_path"] = chosen
        save_config(cfg)
        saved["value"] = True
        root.destroy()

    def do_cancel():
        root.destroy()

    btn_save = tk.Button(
        btn_frame,
        text="Salvar",
        command=do_save,
        width=12,
        bg="#e94560",
        fg="#ffffff",
        activebackground="#c73850",
        activeforeground="#ffffff",
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        cursor="hand2",
    )
    btn_save.pack(side="left", padx=6)

    btn_cancel = tk.Button(
        btn_frame,
        text="Cancelar",
        command=do_cancel,
        width=12,
        bg="#16213e",
        fg="#e0e0e0",
        activebackground="#1a1a5e",
        activeforeground="#ffffff",
        relief="flat",
        font=("Segoe UI", 10),
        cursor="hand2",
    )
    btn_cancel.pack(side="left", padx=6)

    root.protocol("WM_DELETE_WINDOW", do_cancel)
    root.mainloop()

    if saved["value"] and on_save:
        on_save()


def load_tray_icon():
    return Image.open(resource_path("tray_icon.png"))


def read_lockfile():
    lockfile = get_lockfile_path()
    try:
        with open(lockfile, "r") as f:
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


def on_configure(icon):
    """Abre o diálogo de configuração a partir da bandeja."""
    threading.Thread(target=open_config_dialog, daemon=True).start()


def main():
    if not os.path.exists(config_path()):
        open_config_dialog()

    tray_image = load_tray_icon()

    icon = Icon(
        "auto-accept-lol",
        icon=tray_image,
        title="Auto-Accept LoL - Iniciando...",
        menu=Menu(
            MenuItem("Configurar", on_configure),
            MenuItem("Sair", on_exit),
        ),
    )

    thread = threading.Thread(target=run_loop, args=(icon,), daemon=True)
    thread.start()

    icon.run()


if __name__ == "__main__":
    main()
