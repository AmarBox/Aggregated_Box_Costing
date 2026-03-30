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

## Build for Production

```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`.

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
| Backend port | `backend/app.py` | 5000 |
| Frontend port | `frontend/vite.config.js` | 5173 |
| API proxy target | `frontend/vite.config.js` | http://localhost:5000 |
| Material costs data | `backend/calculator/material_costs.json` | Editable via Admin Console or directly |
| Inventory data | `backend/calculator/inventory.json` | Editable via Admin Console |

## Supported Options

- **Paper qualities**: KRAFT, GOLDEN (includes 180gsm at GOLDEN180 pricing), DUPLEX, ITC, PREPRINTED
- **Box types**: Universal, Bottom Locking, Mobile Type, Ring Flap
- **Units**: cm, m, inch
- **Flute types**: EF, NF
- **Attachment types**: None, Pinning, Hand Pasting
- **Customer groups** (batch processing): A (5%), B (10%), C (15%), D (20%)
