# Corrugated Costing App

Full-stack web app for calculating corrugated cardboard box costs, with monthly material cost tracking, paper reel inventory, and batch order processing.

## Tech Stack

- **Frontend**: React 18 + Vite 5 (JavaScript/JSX)
- **Backend**: Flask 3 + Python 3.12
- **Libraries**: Pint (unit conversions), flask-cors, openpyxl (Excel processing)

## Project Structure

```
backend/
  app.py                            # Flask entry point (port 5000)
  cli.py                            # CLI for batch processing
  requirements.txt                  # Python deps: flask, flask-cors, pint, openpyxl
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
  venv/                             # Python virtual environment

frontend/
  package.json                      # React app config
  vite.config.js                    # Dev server config, proxies /api -> localhost:5000
  src/
    App.jsx                         # Main component with Calculator/Admin tabs
    App.css                         # Application styles
    api/calculatorApi.js            # API client for all endpoints
    components/
      Stepper.jsx                   # Multi-step form navigation
      AdminPage.jsx                 # Admin console (3 tabs: Material Costs, Inventory, Batch Processing)
      steps/                        # Calculator form step components
```

## Running the App

### Backend

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Runs on http://localhost:5000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:5173 (or next available port). Proxies `/api` requests to the backend.

### CLI (Batch Processing)

```bash
cd backend
python cli.py process Raw_Work.xlsx
python cli.py transfer Raw_Work.xlsx Estimates.xlsx
python cli.py all Raw_Work.xlsx Estimates.xlsx
```

## API Endpoints

### Calculator
- `GET /api/options` - Paper qualities, quality→weights map, custom GSM qualities, box types, units, flute types, attachment types
- `POST /api/sheet-size` - Calculate sheet dimensions from box dimensions
- `POST /api/calculate` - Full cost calculation with breakdown (accepts optional `cost_date`)

### Material Costs
- `GET /api/material-costs` - List all monthly cost records
- `POST /api/material-costs` - Add or update a month's costs

### Inventory
- `GET /api/inventory` - List all paper reels (sorted by type → GSM → deckel)
- `POST /api/inventory` - Add reel(s): `{type, gsm, deckel, weight, count?}`
- `PUT /api/inventory/<id>` - Update a reel's fields
- `DELETE /api/inventory/<id>` - Delete a reel
- `GET /api/inventory/summary` - Grouped summary with counts and total weights

### Batch Processing
- `POST /api/upload/raw-work` - Upload Raw_Work.xlsx
- `POST /api/upload/estimates` - Upload Estimates.xlsx
- `POST /api/batch/process` - Calculate costs for uploaded Raw_Work
- `POST /api/batch/transfer` - Transfer processed rows to Estimates
- `GET /api/download/template` - Download empty Raw_Work template with headers and sample rows
- `GET /api/download/raw-work` - Download processed Raw_Work.xlsx
- `GET /api/download/estimates` - Download Estimates.xlsx

## Key Concepts

### Paper Qualities
- **KRAFT** — GSM: 80, 100, 120, 140
- **GOLDEN** — GSM: 120, 150, 180. When 180 GSM is selected, GOLDEN180 pricing is used automatically
- **DUPLEX** — GSM: 200, 230, 285. Supports custom GSM entry in the Top sheet layer
- **ITC** — GSM: 250, 300, 350, 400. Supports custom GSM entry in the Top sheet layer
- **PREPRINTED** — No weight (top sheet only, cost = 0)

GOLDEN180 exists as a separate pricing tier in `material_costs.json` and the `PaperQuality` enum, but is not shown as a separate option in the UI. It is resolved automatically when GOLDEN + 180 GSM is selected.

DUPLEX160 has been discontinued and removed.

### Monthly Material Costs
Raw material costs (INR/kg) are stored per month in `material_costs.json`. Tracked qualities: KRAFT, DUPLEX, GOLDEN, GOLDEN180, ITC, PREPRINTED. The calculator uses an optional `cost_date` to look up the right month's prices. If no date is provided, the latest month is used.

### Inventory
Paper reel tracking stored in `inventory.json`. Each reel has: type, GSM, deckel (size in inches), weight (kg). Reels are sorted by type (Kraft → Golden → Duplex → ITC) → GSM → deckel. Supports individual reel tracking with weight, add/edit/delete operations.

### Batch Processing Flow
1. Upload Raw_Work.xlsx (orders with customer name, group, date, dimensions, paper specs)
2. Process: calculates costs using each row's order date to look up material prices, applies group margin (A=5%, B=10%, C=15%, D=20%), writes Rate + Total
3. Transfer: moves processed rows into customer-named sheets in Estimates.xlsx

### Raw_Work.xlsx Column Layout
| Col | Header | Description |
|-----|--------|-------------|
| 1 | Name | Customer name |
| 2 | Group | Customer group (A/B/C/D) for margin |
| 3 | Date | Order date (used for material cost lookup) |
| 4-5 | Length, Width | Sheet dimensions (inches) |
| 6-11 | Bottom/Flute/Top Weight & Quality | Paper specs per layer |
| 12 | Ply | Ply count (odd number) |
| 13 | Order Type | All, Corrugation, or Labour |
| 14 | Ups | Boxes per sheet |
| 15 | Number of Boxes | Total quantity |
| 16 | Punching | Y/N |
| 17 | Pins | Pins per box (0 if none) |
| 18 | Name | Optional item/product name |
| 19 | Rate | Output: calculated rate per box |
| 20 | Total | Output: rate x quantity |

### Order Types (Order Type Column)
- **All** — Full cost calculation: paper material + corrugation processing + labour (punching, pasting, pins, hand pasting, scoring)
- **Corrugation** — Paper cost excluded, corrugation processing fee included (supports NF). Labour costs (pasting, punching, pins, hand pasting, scoring) still apply.
- **Labour** — No paper cost, no corrugation. Only charges for: pasting, punching, pins, hand pasting, and scoring as applicable.

## Common Tasks

- Backend changes: Edit files in `backend/calculator/`
- Frontend changes: Edit files in `frontend/src/`
- Add new API route: `backend/calculator/routes.py`
- Add new form step: Create component in `frontend/src/components/steps/`
- Update material costs: Edit `backend/calculator/material_costs.json` or use Admin Console → Material Costs tab
- Manage inventory: Use Admin Console → Inventory tab
- Batch process orders: Use Admin Console → Batch Processing tab or `python cli.py all Raw_Work.xlsx Estimates.xlsx`
