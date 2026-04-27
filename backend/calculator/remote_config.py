"""
Remote configuration loader.

Fetches app_config.json from a private GitHub repo on startup, validates it,
caches it under %APPDATA%, and falls back gracefully if the network or remote
is unavailable.

Resolution order on every load():
    1. Remote (HTTPS GET against CONFIG_REPO_RAW_URL with optional Bearer PAT)
    2. Local cache file under %APPDATA%/AggregatedBoxCosting/
    3. Bundled default (shipped inside the .exe via PyInstaller --add-data)

Build-time configuration (read at startup from environment variables):
    CONFIG_REPO_RAW_URL  Full URL returning the raw JSON. For a private GitHub
                         repo, use the API endpoint with raw accept header:
                         https://api.github.com/repos/OWNER/REPO/contents/app_config.json?ref=main
    CONFIG_REPO_PAT      Fine-grained read-only Personal Access Token, scoped
                         to the single config repo.

Both values are baked into the PyInstaller binary at build time. Distributing
the .exe distributes the PAT — only ship to trusted users.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

# ─── Build-time injected (read at import) ──────────────────────────────────
# In a packaged .exe, calculator/_build_secrets.py is generated at build time
# by build.ps1 from environment variables CONFIG_REPO_RAW_URL / CONFIG_REPO_PAT
# and bundled into the binary. The file is gitignored so secrets never enter
# source control. In dev mode the env vars are read directly.
try:
    from . import _build_secrets  # type: ignore[attr-defined]
    CONFIG_REPO_RAW_URL = getattr(_build_secrets, "CONFIG_REPO_RAW_URL", "").strip()
    CONFIG_REPO_PAT = getattr(_build_secrets, "CONFIG_REPO_PAT", "").strip()
except ImportError:
    CONFIG_REPO_RAW_URL = os.environ.get("CONFIG_REPO_RAW_URL", "").strip()
    CONFIG_REPO_PAT = os.environ.get("CONFIG_REPO_PAT", "").strip()

# How long to wait for the remote fetch before giving up and falling back.
FETCH_TIMEOUT_SECONDS = 5

# Top-level keys every valid config must contain.
REQUIRED_TOP_LEVEL_KEYS = (
    "config_version",
    "material_costs",
    "processing_rates",
    "punching_tiers",
    "hand_pasting_tiers",
    "printing_tiers",
    "margins",
    "options",
    "template_validation",
)

APP_NAME = "AggregatedBoxCosting"


# ─── Paths ─────────────────────────────────────────────────────────────────

def _cache_dir() -> Path:
    """Per-user cache directory. Uses %APPDATA% on Windows."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    return Path.home() / f".{APP_NAME.lower()}"


def _cache_file() -> Path:
    return _cache_dir() / "app_config.json"


def _bundled_default_path() -> Path:
    """Path to the bundled default config.

    Inside a PyInstaller --onefile build, files added with --add-data live
    under sys._MEIPASS at runtime.
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
        return base / "calculator" / "app_config.default.json"
    return Path(__file__).parent / "app_config.default.json"


# ─── Module state ──────────────────────────────────────────────────────────
_loaded_config: dict | None = None
_load_status: dict = {"source": None, "fetched_at": None, "error": None}
_lock = Lock()


# ─── Public API ────────────────────────────────────────────────────────────

def load(force_refresh: bool = False) -> dict:
    """Load configuration. Tries remote → cache → bundled.

    Sets the module's loaded config and returns it. Safe to call repeatedly;
    later calls only re-fetch if force_refresh=True.
    """
    global _loaded_config, _load_status

    with _lock:
        if _loaded_config is not None and not force_refresh:
            return _loaded_config

        last_error: str | None = None

        # 1. Remote
        if CONFIG_REPO_RAW_URL:
            try:
                cfg = _fetch_remote()
                _validate(cfg)
                _save_cache(cfg)
                _loaded_config = cfg
                _load_status = {
                    "source": "remote",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "error": None,
                }
                return cfg
            except Exception as e:
                last_error = f"remote: {e}"

        # 2. Cache
        cache_path = _cache_file()
        if cache_path.exists():
            try:
                with cache_path.open("r", encoding="utf-8") as f:
                    cfg = json.load(f)
                _validate(cfg)
                _loaded_config = cfg
                _load_status = {
                    "source": "cache",
                    "fetched_at": datetime.fromtimestamp(
                        cache_path.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                    "error": last_error,
                }
                return cfg
            except Exception as e:
                last_error = f"{last_error}; cache: {e}" if last_error else f"cache: {e}"

        # 3. Bundled default — must always succeed; if it doesn't, raise loudly.
        bundled = _bundled_default_path()
        with bundled.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
        _validate(cfg)
        _loaded_config = cfg
        _load_status = {
            "source": "bundled",
            "fetched_at": None,
            "error": last_error,
        }
        return cfg


def get() -> dict:
    """Get the loaded config, loading on first access."""
    if _loaded_config is None:
        load()
    return _loaded_config  # type: ignore[return-value]


def status() -> dict:
    """Return where the current config came from and any non-fatal errors."""
    return dict(_load_status)


# ─── Internal helpers ──────────────────────────────────────────────────────

def _fetch_remote() -> dict:
    """GET CONFIG_REPO_RAW_URL with PAT auth, return parsed JSON."""
    req = urllib.request.Request(CONFIG_REPO_RAW_URL)
    if CONFIG_REPO_PAT:
        req.add_header("Authorization", f"Bearer {CONFIG_REPO_PAT}")
    # Ask the GitHub API to return raw file content (no base64 wrapper).
    # Harmless for non-API URLs.
    req.add_header("Accept", "application/vnd.github.raw")
    req.add_header("User-Agent", f"{APP_NAME}/config-loader")

    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _save_cache(cfg: dict) -> None:
    cache_dir = _cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp = _cache_file().with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    tmp.replace(_cache_file())


def _validate(cfg) -> None:
    if not isinstance(cfg, dict):
        raise ValueError("config root must be a JSON object")
    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in cfg]
    if missing:
        raise ValueError(f"config missing required keys: {missing}")
