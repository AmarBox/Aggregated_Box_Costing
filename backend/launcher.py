"""
Entry point for the bundled .exe.

Starts the Flask app on the first available local port, polls until it's
accepting connections, then opens the user's default browser. Leaving the
console window open keeps the app running; closing it stops the app.

Run from source for testing:
    python launcher.py

Bundled via PyInstaller — see build.ps1.
"""

import socket
import sys
import threading
import time
import webbrowser
from contextlib import closing

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


def _open_browser_when_ready(port: int) -> None:
    if _wait_until_ready(port):
        webbrowser.open(f"http://localhost:{port}/")
    else:
        print(f"[launcher] server did not become ready within {READY_TIMEOUT_SECONDS}s")


def main() -> None:
    try:
        port = _find_open_port()
    except RuntimeError as e:
        print(f"[launcher] {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    print("=" * 60)
    print(f"  {APP_NAME}")
    print("=" * 60)
    print(f"  Open in browser:  http://localhost:{port}/")
    print(f"  Stop the app:     close this window")
    print("=" * 60)

    threading.Thread(
        target=_open_browser_when_ready, args=(port,), daemon=True
    ).start()

    # Production-friendly: no debug, no reloader, listen only on localhost.
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
