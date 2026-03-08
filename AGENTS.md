# AGENTS.md

## Cursor Cloud specific instructions

### Overview

**Auto-Accept LoL** is a single-file Python application (`auto_accept.py`) that automatically accepts match queues in League of Legends via the LCU API. It runs as a Windows system tray icon using `pystray`.

### Important caveats

- **Windows-only at runtime**: The app is designed for Windows (`pystray` system tray, `pythonw`, Windows lockfile path `D:\Riot Games\...`). On Linux (Cloud VM), it starts and enters its main loop but emits a harmless `GLib-GIO-CRITICAL` D-Bus warning because there's no system tray.
- **No test suite**: The repository has no automated tests. Validation is limited to syntax checks, linting, import verification, and function-level smoke tests.
- **GTK3 required on Linux**: `pystray` on Linux needs `gir1.2-gtk-3.0` and `gir1.2-ayatanaappindicator3-0.1` system packages for imports to succeed.

### Key commands

| Task | Command |
|---|---|
| Install deps | `pip install -r requirements.txt` |
| Lint | `flake8 auto_accept.py` |
| Syntax check | `python3 -c "import py_compile; py_compile.compile('auto_accept.py', doraise=True)"` |
| Run (dev) | `python3 auto_accept.py` |
| Build exe | `pyinstaller --onefile --noconsole --name "AutoAcceptLoL" --icon=icon.ico --add-data "tray_icon.png:." auto_accept.py` |

### Function-level smoke testing

Since there's no test suite and the app requires a running LoL client, you can validate core functions:

```python
python3 -c "
import auto_accept
img = auto_accept.load_tray_icon()
port, pw = auto_accept.read_lockfile()  # returns (None, None) without LoL
result = auto_accept.accept_match('0', 'test')  # returns False without LoL
print('OK')
"
```
