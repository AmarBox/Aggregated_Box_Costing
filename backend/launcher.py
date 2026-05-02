"""
Entry point for the bundled .exe.

Starts the Flask app on the first available local port in a background
thread, opens the user's default browser once it's ready, and shows a
system-tray icon with Open / Quit. The app keeps running in the
background until Quit is selected from the tray menu.

Run from source for testing:
    python launcher.py

Bundled via PyInstaller — see build.ps1.
"""

import os
import socket
import sys
import threading
import time
import webbrowser
from contextlib import closing
from pathlib import Path

import pystray
from PIL import Image

from app import app

APP_NAME = "Aggregated Box Costing"
PORT_RANGE = range(5000, 5051)
READY_TIMEOUT_SECONDS = 15


def _find_open_port():
    for port in PORT_RANGE:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(
        f"No free port available in range {PORT_RANGE.start}-{PORT_RANGE.stop - 1}"
    )


def _wait_until_ready(port: int) -> bool:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(0.5)
            try:
                s.connect(("127.0.0.1", port))
                return True
            except OSError:
                time.sleep(0.2)
    return False


def _icon_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    else:
        base = Path(__file__).parent
    return base / "app_icon.ico"


def _load_tray_image() -> Image.Image:
    return Image.open(_icon_path())


def main() -> None:
    try:
        port = _find_open_port()
    except RuntimeError as e:
        print(f"[launcher] {e}")
        sys.exit(1)

    url = f"http://localhost:{port}/"

    threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1", port=port, debug=False, use_reloader=False
        ),
        daemon=True,
    ).start()

    def _open_when_ready():
        if _wait_until_ready(port):
            webbrowser.open(url)

    threading.Thread(target=_open_when_ready, daemon=True).start()

    def on_open(icon, item):
        webbrowser.open(url)

    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    icon = pystray.Icon(
        "AggregatedBoxCosting",
        _load_tray_image(),
        APP_NAME,
        menu=pystray.Menu(
            pystray.MenuItem("Open", on_open, default=True),
            pystray.MenuItem("Quit", on_quit),
        ),
    )
    icon.run()


if __name__ == "__main__":
    main()
