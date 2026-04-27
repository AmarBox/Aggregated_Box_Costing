"""
Flask entry point.

Two modes:
  * Dev: `python app.py` — Vite serves the frontend on :5173 and proxies /api
    here. The frontend/dist catch-all routes below 404 silently in this case.
  * Bundled .exe (PyInstaller): the React build sits at frontend/dist and is
    served from this same Flask process — no separate frontend server.
"""

import os
import sys
from pathlib import Path

from flask import Flask, send_from_directory, abort
from flask_cors import CORS

from calculator.routes import api_bp
from calculator import remote_config


# ─── Path resolution (handles PyInstaller --onefile via sys._MEIPASS) ─────

def _resource_root() -> Path:
    """Root directory for bundled resources (same as repo root in dev)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return Path(__file__).parent.parent


FRONTEND_DIST = _resource_root() / "frontend" / "dist"


# ─── App setup ─────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.register_blueprint(api_bp, url_prefix="/api")


# ─── Static frontend serving ──────────────────────────────────────────────

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    """Serve the React build. Falls back to index.html for SPA routing."""
    if not FRONTEND_DIST.exists():
        # Dev mode without a build — Vite handles the frontend on its own.
        abort(404)

    candidate = FRONTEND_DIST / path
    if path and candidate.is_file():
        return send_from_directory(str(FRONTEND_DIST), path)
    return send_from_directory(str(FRONTEND_DIST), "index.html")


# ─── Startup ──────────────────────────────────────────────────────────────

def _bootstrap_config():
    """Load remote config once at startup; log where it came from."""
    cfg = remote_config.load()
    status = remote_config.status()
    print(
        f"[config] loaded v{cfg.get('config_version')} "
        f"from {status['source']}"
        + (f" (error: {status['error']})" if status.get("error") else "")
    )


_bootstrap_config()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
