# Corrugated Costing

A web application for calculating the cost of corrugated cardboard boxes. Supports multiple paper qualities, box types, flute types, and unit systems. Includes monthly material cost tracking, paper reel inventory management, batch processing of orders from Excel, and an admin console.

## Prerequisites

- Python 3.12+
- Node.js 18+
- npm

## Setup

### 1. Backend

```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

The Flask API server will start on **http://localhost:5000**.

### 2. Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

The React dev server will start on **http://localhost:5173**. It automatically proxies API requests (`/api/*`) to the backend.

### 3. Open the App

Navigate to **http://localhost:5173** in your browser.

> Both the backend and frontend must be running simultaneously.

## Features

### Calculator (Main Page)

A multi-step form to calculate box costs:

1. **Input Type** — Choose between box dimensions or direct sheet size
2. **Dimensions** — Enter box/sheet measurements
3. **Box Properties** — Select paper qualities and weights for each layer. For Duplex and ITC in the Top layer, you can enter a custom GSM value not in the dropdown.
4. **Production Details** — Set ply count, boxes per sheet, quantity, attachment type, and optional **cost date**
5. **Manufacturing Options** — Toggle punching, scoring, lamination, printing, etc.
6. **Results** — Full cost breakdown, sales prices with tax rates, and the material costs used

### Cost Date

An optional month input in the Production Details step. This determines which month's raw material prices are used for the calculation:

- **If a date is provided**: Uses the material costs for that month (or the closest earlier month if exact match not found)
- **If left empty**: Uses the latest available month's costs

### Admin Console

Accessible via the **Admin Console** tab in the header. Contains three tabbed sections:

#### Material Costs

A table showing raw material costs (INR/kg) per paper quality for each month. You can:

- **View** all stored monthly costs
- **Edit inline** — click Edit on any row to modify costs directly in the table
- **Add** a new month (pre-filled from the latest month for convenience)

Costs are stored in `backend/calculator/material_costs.json` and can also be edited directly.

#### Inventory

Track individual paper reels organized by type, then grammage (GSM), then deckel (size in inches):

- **Add** reels with type, GSM, deckel, weight (kg), and optional count for bulk entry
- **Edit** any reel's details inline
- **Delete** reels when consumed or removed
- Reels are grouped by paper type (Kraft, Golden, Duplex, ITC) for easy browsing

Data is stored in `backend/calculator/inventory.json`.

#### Batch Processing

Process orders from an Excel workbook:

1. **Upload Raw_Work.xlsx** — Contains order rows with customer name, group, date, dimensions, paper specs, quantities
2. **Click "Process"** — Calculates cost per box for each row using the order date to look up the correct monthly material costs, applies a margin based on customer group (A=5%, B=10%, C=15%, D=20%), rounds the rate to the nearest 0.25, and writes Rate + Total back to the file
3. **Upload Estimates.xlsx** (optional) — If you have an existing estimates file; otherwise a blank one is created
4. **Click "Transfer"** — Moves processed rows into customer-named sheets in Estimates.xlsx and removes them from Raw_Work.xlsx
5. **Download** the processed files

### Raw_Work.xlsx Format

| Column | Field |
|--------|-------|
| A | Customer Name |
| B | Group (A/B/C/D) |
| C | Order Date |
| D | Sheet Length (inches) |
| E | Sheet Width (inches) |
| F | Bottom Paper Weight (gsm) |
| G | Bottom Paper Quality |
| H | Flute Paper Weight (gsm) |
| I | Flute Paper Quality |
| J | Top Paper Weight (gsm) |
| K | Top Paper Quality |
| L | Number of Plies |
| M | Order Type (All/Corrugation/Labour) |
| N | Boxes per Sheet (UPS) |
| O | Number of Boxes |
| P | Punching (Y/N) |
| Q | Pins per Box |
| R | Item/Product Name |
| S | Rate (calculated) |
| T | Total (calculated) |

Valid paper quality values: `kraft`, `duplex`, `golden`, `golden180`, `itc`, `preprinted`

## CLI Usage

You can run batch processing from the command line without the web server:

```bash
cd backend

# Calculate costs for all rows in Raw_Work.xlsx
python cli.py process path/to/Raw_Work.xlsx

# Transfer processed rows to Estimates.xlsx
python cli.py transfer path/to/Raw_Work.xlsx path/to/Estimates.xlsx

# Do both in sequence
python cli.py all path/to/Raw_Work.xlsx path/to/Estimates.xlsx
```

The CLI uses the same calculation engine and monthly material costs as the web app.

## Building

### Frontend Production Bundle

```bash
cd frontend
npm run build
```

Output: `frontend/dist/`. This is what Flask serves at `/` when the bundled `.exe` runs (no Vite dev server in production).

### Standalone Windows App (.exe)

For non-technical end users, the app ships as a single self-contained `AggregatedBoxCosting.exe` (~19 MB) that needs no Python, Node, or browser-tab juggling. The .exe runs Flask on the first free port in `5000-5050`, opens the React UI in the user's default browser, and shows a system-tray icon.

**For end users:**

1. Double-click `AggregatedBoxCosting.exe`.
2. The default browser opens to `http://localhost:<port>/` automatically.
3. A small brown box icon appears in the system tray (click the `^` chevron in the taskbar to see hidden icons; pin it to keep it visible).
4. Right-click the tray icon for **Open** (re-opens the browser tab) and **Quit** (fully shuts down the app).
5. **Closing the browser tab does not stop the app** — use Quit from the tray menu.
6. Windows SmartScreen / Defender may flag the unsigned binary on first run — click "More info" → "Run anyway".

**Build prerequisites (build machine only):**

- Python 3.12+ with pip
- Node.js 18+ with npm
- PowerShell 5+ (Windows)
- Two **user-scope** environment variables:
  - `CONFIG_REPO_RAW_URL` — full URL to the remote `app_config.json`. For a private GitHub repo, use the contents API:  
    `https://api.github.com/repos/<OWNER>/<REPO>/contents/<path>/app_config.json?ref=main`
  - `CONFIG_REPO_PAT` — a fine-grained, read-only Personal Access Token scoped to that single config repo

To set them once (PowerShell, user scope):
```powershell
[Environment]::SetEnvironmentVariable("CONFIG_REPO_RAW_URL", "https://api.github.com/...", "User")
[Environment]::SetEnvironmentVariable("CONFIG_REPO_PAT", "github_pat_...", "User")
```
Then open a **new** shell so the variables are loaded.

**Build the .exe:**

```powershell
cd C:\path\to\Aggregated_Box_Costing
powershell -ExecutionPolicy Bypass -File build.ps1
```

Output: `backend\dist\AggregatedBoxCosting.exe`. The script takes ~1–2 minutes and:

1. Validates that both env vars are set.
2. Runs `npm run build` to produce `frontend/dist/`.
3. Installs Python deps + PyInstaller against the system Python (not the WSL venv).
4. Writes `backend/calculator/_build_secrets.py` containing the URL + PAT (gitignored).
5. Runs PyInstaller with `--onefile --windowed`, embedding:
   - `frontend/dist/` (React build)
   - `backend/calculator/app_config.default.json` (fallback config)
   - `backend/app_icon.ico` (tray + EXE header icon)
6. **Always** deletes `_build_secrets.py` after PyInstaller finishes — even if PyInstaller fails — so secrets never linger on disk.

> **Security note:** the PAT is baked into the binary. Anyone with the .exe can extract it. Only distribute to trusted users, and use a fine-grained read-only token scoped to a single repo so the blast radius is small.

**Build artifacts (gitignored):**

- `backend/dist/AggregatedBoxCosting.exe` — the shippable binary
- `backend/build/` — PyInstaller scratch dir
- `backend/AggregatedBoxCosting.spec` — PyInstaller spec
- `backend/calculator/_build_secrets.py` — created and deleted by `build.ps1`

### Customizing the App Icon

The icon is a simple cardboard-brown isometric box outline at `backend/app_icon.ico` (multi-resolution: 16, 32, 48, 64, 128, 256). It is used in two places:

- **EXE header** — shown by Windows Explorer / taskbar (via PyInstaller `--icon`)
- **System tray** — loaded at runtime by `launcher.py` from the bundled copy

To redesign it, edit the drawing code in `backend/generate_icon.py` and rerun:

```bash
cd backend
python generate_icon.py
```

This rewrites `backend/app_icon.ico` in place. The next `build.ps1` run will pick it up.

## Remote Configuration

In addition to per-user data (`material_costs.json`, `inventory.json`), the app loads a central `app_config.json` from a private GitHub repo on every startup. This lets you push pricing/processing rate changes to all installed .exes without rebuilding. The full schema is documented in `backend/calculator/app_config.default.json`.

**Resolution order** (every startup, see `backend/calculator/remote_config.py`):

1. **Remote** — HTTPS GET of `CONFIG_REPO_RAW_URL` with the bundled PAT, 5-second timeout. Validates required top-level keys, then writes a copy to the on-disk cache.
2. **Cache** — `%APPDATA%\AggregatedBoxCosting\app_config.json` (used if the network or remote is unavailable).
3. **Bundled default** — `app_config.default.json` baked into the .exe (last-resort fallback; should always succeed).

The launcher console prints which source loaded successfully, e.g. `[config] loaded v1.0.0 from remote`.

**To update the live config:**

1. Edit `app_config.json` in the config repo (whatever `CONFIG_REPO_RAW_URL` points at).
2. Bump `config_version`.
3. Commit + push. End users pick up the new config on their next app launch.

## Project Structure

```
build.ps1                           # PowerShell build script for the .exe
README.md                           # This file
CLAUDE.md                           # Project context for Claude Code

backend/
  app.py                            # Flask entry point: serves /api/* + frontend/dist at /
  launcher.py                       # .exe entry point: Flask + tray icon orchestration
  cli.py                            # CLI for batch processing
  generate_icon.py                  # One-shot script to regenerate app_icon.ico
  app_icon.ico                      # Multi-res tray + EXE header icon
  requirements.txt                  # Python deps: flask, flask-cors, pint, openpyxl, pystray, pillow
  uploads/                          # Uploaded Excel files (created at runtime)
  calculator/
    routes.py                       # All API endpoints
    box_cost_calculator.py          # Core calculation engine
    material_costs.py               # Monthly cost lookup/management
    material_costs.json             # Monthly raw material costs data
    inventory.py                    # Paper reel inventory management
    inventory.json                  # Paper reel inventory data (created at runtime)
    batch_processor.py              # Process Raw_Work.xlsx (calculate costs)
    estimate_transfer.py            # Transfer processed rows to Estimates.xlsx
    remote_config.py                # Loads app_config.json (remote → cache → bundled)
    app_config.default.json         # Bundled fallback config
    _build_secrets.py               # AUTO-GENERATED by build.ps1, deleted after build (gitignored)
  venv/                             # Python virtual environment
  dist/                             # PyInstaller output (gitignored)
  build/                            # PyInstaller scratch (gitignored)

frontend/
  package.json                      # React app config
  vite.config.js                    # Dev server config, proxies /api -> localhost:5000
  src/
    App.jsx                         # Main component with Calculator/Admin tabs
    App.css                         # Application styles
    api/calculatorApi.js            # API client for all endpoints
    components/
      Stepper.jsx                   # Multi-step form navigation
      AdminPage.jsx                 # Admin console (Material Costs, Inventory, Batch Processing)
      BatchProcessingPage.jsx       # Standalone batch processing page
      steps/                        # Calculator form step components
  dist/                             # Vite production build (gitignored, bundled into .exe)
```

## Two Run Modes

Two distinct ways to run the app — different entry points, different process layouts:

| | Dev mode | Bundled .exe |
|---|---|---|
| Entry point | `python backend/app.py` + `npm run dev` | `AggregatedBoxCosting.exe` (`launcher.py`) |
| Frontend | Vite dev server on :5173, HMR enabled | React build served by Flask at `/` |
| Backend | Flask on :5000 (debug, reloader) | Flask on first free port 5000–5050 (no debug, no reloader) |
| API proxy | Vite proxies `/api/*` → `localhost:5000` | Same process, no proxy |
| Browser | Manual: open `http://localhost:5173` | Auto-opens default browser |
| Lifecycle | Ctrl+C in two terminals | Tray icon → Quit |
| Console | Visible (logs + errors) | Hidden (`--windowed`) |
| Config source | `app_config.default.json` (or env-var-driven remote, if set) | Remote → cache → bundled |

## Launcher Internals (`backend/launcher.py`)

The bundled .exe runs `launcher.py` as the main entry point. Flow:

1. `_find_open_port()` — scan ports 5000–5050, bind to the first free one.
2. Spawn a **daemon thread** that calls `app.run(host="127.0.0.1", port=…, debug=False, use_reloader=False)`.
3. Spawn a second daemon thread that polls the port and calls `webbrowser.open()` once the server accepts a connection (15-second timeout).
4. **Main thread** runs `pystray.Icon(...).run()`, which blocks on a Win32 message loop displaying the tray icon. The tray must be on the main thread on Windows.
5. **Quit** menu item calls `icon.stop()` then `os._exit(0)` — the daemon Flask thread is killed automatically.

If you change Flask startup, keep it inside the daemon thread; if you change the tray menu, keep `default=True` on **Open** so left-clicking the tray icon does the obvious thing.

## API Endpoints

### Calculator

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/options` | Paper qualities, quality→weights map, custom GSM qualities, box types, units, flute types, attachment types |
| POST | `/api/sheet-size` | Calculate sheet dimensions from box dimensions |
| POST | `/api/calculate` | Full cost calculation (accepts optional `cost_date` field) |

### Material Costs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/material-costs` | List all monthly cost records |
| POST | `/api/material-costs` | Add or update a month's costs |

### Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inventory` | List all reels sorted by type → GSM → deckel |
| POST | `/api/inventory` | Add reel(s): `{type, gsm, deckel, weight, count?}` |
| PUT | `/api/inventory/<id>` | Update a reel's fields |
| DELETE | `/api/inventory/<id>` | Delete a reel |
| GET | `/api/inventory/summary` | Grouped summary with counts and total weights |

### Batch Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/raw-work` | Upload Raw_Work.xlsx |
| POST | `/api/upload/estimates` | Upload Estimates.xlsx |
| POST | `/api/batch/process` | Calculate costs for uploaded Raw_Work |
| POST | `/api/batch/transfer` | Transfer processed rows to Estimates |
| GET | `/api/download/template` | Download empty Raw_Work template |
| GET | `/api/download/raw-work` | Download processed Raw_Work.xlsx |
| GET | `/api/download/estimates` | Download Estimates.xlsx |

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Backend port (dev) | `backend/app.py` | 5000 |
| Backend port (.exe) | `backend/launcher.py` | First free port in 5000–5050 |
| Frontend port (dev) | `frontend/vite.config.js` | 5173 |
| API proxy target | `frontend/vite.config.js` | http://localhost:5000 |
| Material costs data | `backend/calculator/material_costs.json` | Editable via Admin Console or directly |
| Inventory data | `backend/calculator/inventory.json` | Editable via Admin Console |
| Bundled default config | `backend/calculator/app_config.default.json` | Last-resort fallback baked into the .exe |
| Per-user config cache | `%APPDATA%\AggregatedBoxCosting\app_config.json` | Created at runtime after first remote fetch |
| Remote config URL | env var `CONFIG_REPO_RAW_URL` (build-time) | Required for `build.ps1` |
| Remote config token | env var `CONFIG_REPO_PAT` (build-time) | Required for `build.ps1`; baked into .exe |
| Tray icon | `backend/app_icon.ico` | Regenerate via `python backend/generate_icon.py` |

## Supported Options

- **Paper qualities**:
  - **KRAFT** — 80, 100, 120, 140 gsm
  - **GOLDEN** — 120, 150, 180 gsm (180gsm uses GOLDEN180 pricing)
  - **DUPLEX** — 180, 200, 230, 285 gsm (custom gsm allowed in Top layer)
  - **ITC** — 250, 300, 350, 400 gsm (custom gsm allowed in Top layer)
  - **PREPRINTED** — Top layer only, no weight
- **Box types**: Universal, Bottom Locking, Mobile Type, Ring Flap
- **Units**: cm, m, inch
- **Flute types**: EF, NF
- **Attachment types**: None, Pinning, Hand Pasting
- **Customer groups** (batch processing): A (5%), B (10%), C (15%), D (20%)
