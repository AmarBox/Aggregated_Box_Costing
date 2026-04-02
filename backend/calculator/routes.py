import os
from flask import Blueprint, jsonify, request, send_file, current_app
from werkzeug.utils import secure_filename
from .box_cost_calculator import (
    BoxCostCalculator,
    BoxDimensions,
    BoxType,
    PaperQuality,
    ProductionDetails,
    ManufacturingOptions,
)
from .material_costs import get_all_monthly_costs, get_costs_for_date, upsert_monthly_costs
from .batch_processor import process_workbook, generate_template
from .estimate_transfer import transfer
from .inventory import get_all_reels, add_reel, update_reel, delete_reel, get_inventory_summary

api_bp = Blueprint("api", __name__)
calculator = BoxCostCalculator()

# Paper quality → available weights mapping
QUALITY_WEIGHTS = {
    "KRAFT": [80, 100, 120, 140],
    "GOLDEN": [120, 150, 180],
    "DUPLEX": [200, 230, 285],
    "ITC": [250, 300, 350, 400],
    "PREPRINTED": [0],
}

# Qualities that allow manual GSM entry (user can type a custom value)
CUSTOM_GSM_QUALITIES = ["DUPLEX", "ITC"]

BOX_TYPES = [bt.value for bt in BoxType]
UNIT_OPTIONS = ["cm", "m", "inch"]
FLUTE_TYPES = ["EF", "NF"]
ATTACHMENT_TYPES = ["none", "pinning", "hand_pasting"]


@api_bp.route("/options", methods=["GET"])
def get_options():
    return jsonify(
        {
            "paper_qualities": list(QUALITY_WEIGHTS.keys()),
            "quality_weights": QUALITY_WEIGHTS,
            "custom_gsm_qualities": CUSTOM_GSM_QUALITIES,
            "box_types": BOX_TYPES,
            "units": UNIT_OPTIONS,
            "flute_types": FLUTE_TYPES,
            "attachment_types": ATTACHMENT_TYPES,
        }
    )


@api_bp.route("/sheet-size", methods=["POST"])
def calculate_sheet_size():
    data = request.get_json()
    try:
        box_dims = BoxDimensions(
            length=float(data["length"]),
            width=float(data["width"]),
            height=float(data["height"]),
            units=data.get("units", "cm"),
        )
        box_type = BoxType(data.get("box_type", "universal"))

        sheet_length, sheet_width = calculator.calculate_sheet_size_from_box(
            box_dims, box_type
        )
        return jsonify({"sheet_length": sheet_length, "sheet_width": sheet_width})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/calculate", methods=["POST"])
def calculate_cost():
    data = request.get_json()
    try:
        input_mode = data.get("input_mode", "sheet")

        # Parse paper qualities and weights
        quality_names = data.get("paper_quality", ["KRAFT", "KRAFT", "PREPRINTED"])
        paper_weight = data.get("paper_weight", [100, 100, 0])
        paper_weight = [float(w) for w in paper_weight]

        # Resolve GOLDEN + 180gsm → GOLDEN180 for pricing
        resolved_names = []
        for i, qn in enumerate(quality_names):
            if qn == "GOLDEN" and paper_weight[i] == 180:
                resolved_names.append("GOLDEN180")
            else:
                resolved_names.append(qn)
        paper_qualities = [PaperQuality[q] for q in resolved_names]

        # Attachment type
        attachment_type = data.get("attachment_type", "none")
        is_hand_pasted = attachment_type == "hand_pasting"
        pins_per_box = int(data.get("pins_per_box", 0))
        if attachment_type != "pinning":
            pins_per_box = 0

        # Flute type
        flute_type = data.get("flute_type", "EF")
        is_nf = flute_type == "NF"

        production_details = ProductionDetails(
            ply_num=int(data.get("ply_num", 3)),
            box_per_sheet=int(data.get("box_per_sheet", 1)),
            pins_per_box=pins_per_box,
            number_of_boxes=int(data.get("number_of_boxes", 1000)),
            paper_weight=paper_weight,
            paper_quality=paper_qualities,
        )

        manufacturing_options = ManufacturingOptions(
            is_punching=bool(data.get("is_punching", True)),
            is_scoring=bool(data.get("is_scoring", False)),
            is_laminated=bool(data.get("is_laminated", False)),
            is_printed=bool(data.get("is_printed", False)),
            is_hand_pasted=is_hand_pasted,
            is_nf=is_nf,
            only_corrugation=bool(data.get("only_corrugation", False)),
        )

        # Determine sheet dimensions
        sheet_length = None
        sheet_width = None
        box_dims = None
        box_type = None

        if input_mode == "box":
            bd = data.get("box_dimensions", {})
            box_dims = BoxDimensions(
                length=float(bd["length"]),
                width=float(bd["width"]),
                height=float(bd["height"]),
                units=bd.get("units", "cm"),
            )
            box_type = BoxType(bd.get("box_type", "universal"))
        else:
            sd = data.get("sheet_dimensions", {})
            sheet_length = float(sd["length"])
            sheet_width = float(sd["width"])

        # Resolve material costs based on optional date
        cost_date = data.get("cost_date")  # YYYY-MM or YYYY-MM-DD, or None
        cost_overrides = get_costs_for_date(cost_date)

        result = calculator.calculate_total_cost(
            sheet_length=sheet_length,
            sheet_width=sheet_width,
            box_dims=box_dims,
            box_type=box_type,
            production_details=production_details,
            manufacturing_options=manufacturing_options,
            cost_overrides=cost_overrides,
        )

        # Build sales prices with tax rates
        sales_prices_list = []
        for i, price in enumerate(result.sales_prices):
            margin_pct = (i + 1) * 5
            sales_prices_list.append(
                {
                    "margin_pct": margin_pct,
                    "price": round(price, 2),
                    "with_legacy_tax": round(price * 1.12, 2),
                    "with_new_tax": round(price * 1.05, 2),
                }
            )

        return jsonify(
            {
                "sheet_size": {
                    "length": sheet_length
                    if sheet_length
                    else calculator.calculate_sheet_size_from_box(box_dims, box_type)[0],
                    "width": sheet_width
                    if sheet_width
                    else calculator.calculate_sheet_size_from_box(box_dims, box_type)[1],
                    "area": round(result.sheet_area, 2),
                },
                "sheet_weight": {
                    "backing": round(result.sheet_weight[0], 4)
                    if len(result.sheet_weight) > 0
                    else 0,
                    "fluting": round(result.sheet_weight[1], 4)
                    if len(result.sheet_weight) > 1
                    else 0,
                    "top": round(result.sheet_weight[2], 4)
                    if len(result.sheet_weight) > 2
                    else 0,
                    "total": round(sum(result.sheet_weight), 4),
                },
                "cost_breakdown": {
                    k: round(v, 2) for k, v in result.cost_components.items()
                },
                "manufacturing_cost_per_box": round(
                    result.manufacturing_cost_per_box, 2
                ),
                "sales_prices": sales_prices_list,
                "material_costs_used": cost_overrides,
                "cost_date": cost_date,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/material-costs", methods=["GET"])
def list_material_costs():
    """Return all monthly material cost records."""
    return jsonify(get_all_monthly_costs())


@api_bp.route("/material-costs", methods=["POST"])
def update_material_costs():
    """Add or update material costs for a month.

    Expected JSON body:
    {
        "month": "2026-03",
        "costs": {"KRAFT": 35.5, "DUPLEX": 45, ...}
    }
    """
    data = request.get_json()
    try:
        month = data["month"]
        costs = data["costs"]
        updated = upsert_monthly_costs(month, costs)
        return jsonify({"month": month, "costs": updated})
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Invalid request: {e}"}), 400


# ---------------------------------------------------------------------------
# Batch processing endpoints (Admin console)
# ---------------------------------------------------------------------------

def _upload_path(filename):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)


RAW_WORK_FILE = 'Raw_Work.xlsx'
ESTIMATES_FILE = 'Estimates.xlsx'


@api_bp.route("/upload/raw-work", methods=["POST"])
def upload_raw_work():
    """Upload a Raw_Work.xlsx file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({"error": "No file selected"}), 400
    dest = _upload_path(RAW_WORK_FILE)
    f.save(dest)
    return jsonify({"message": f"Uploaded {RAW_WORK_FILE}", "path": dest})


@api_bp.route("/upload/estimates", methods=["POST"])
def upload_estimates():
    """Upload an Estimates.xlsx file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({"error": "No file selected"}), 400
    dest = _upload_path(ESTIMATES_FILE)
    f.save(dest)
    return jsonify({"message": f"Uploaded {ESTIMATES_FILE}", "path": dest})


@api_bp.route("/batch/process", methods=["POST"])
def batch_process():
    """Process the uploaded Raw_Work.xlsx and transfer to Estimates.xlsx."""
    raw_path = _upload_path(RAW_WORK_FILE)
    est_path = _upload_path(ESTIMATES_FILE)
    if not os.path.exists(raw_path):
        return jsonify({"error": "Raw_Work.xlsx not uploaded yet"}), 400

    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "fresh")

    try:
        results = process_workbook(raw_path)

        if mode == "fresh" or not os.path.exists(est_path):
            import openpyxl
            wb = openpyxl.Workbook()
            wb.save(est_path)

        summary = transfer(raw_path, est_path)
        summary["rows_processed"] = len(results)
        summary["mode"] = mode
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Inventory endpoints
# ---------------------------------------------------------------------------

@api_bp.route("/inventory", methods=["GET"])
def list_inventory():
    """Return all reels sorted by type, GSM, deckel."""
    return jsonify(get_all_reels())


@api_bp.route("/inventory/summary", methods=["GET"])
def inventory_summary():
    """Return inventory grouped by type/GSM/deckel with counts."""
    return jsonify(get_inventory_summary())


@api_bp.route("/inventory", methods=["POST"])
def add_inventory():
    """Add a new reel. Body: {type, gsm, deckel, weight, count?}"""
    data = request.get_json()
    try:
        added = add_reel(
            reel_type=data["type"],
            gsm=data["gsm"],
            deckel=data["deckel"],
            weight=data["weight"],
            count=int(data.get("count", 1)),
        )
        return jsonify(added), 201
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid request: {e}"}), 400


@api_bp.route("/inventory/<int:reel_id>", methods=["PUT"])
def update_inventory(reel_id):
    """Update a reel. Body: {weight?, gsm?, deckel?, type?}"""
    data = request.get_json()
    reel = update_reel(reel_id, data)
    if reel is None:
        return jsonify({"error": "Reel not found"}), 404
    return jsonify(reel)


@api_bp.route("/inventory/<int:reel_id>", methods=["DELETE"])
def delete_inventory(reel_id):
    """Delete a reel by ID."""
    if delete_reel(reel_id):
        return jsonify({"message": "Deleted"})
    return jsonify({"error": "Reel not found"}), 404


@api_bp.route("/download/template", methods=["GET"])
def download_template():
    """Download an empty Raw_Work template with headers and sample rows."""
    path = _upload_path('Raw_Work_Template.xlsx')
    generate_template(path)
    return send_file(path, as_attachment=True, download_name='Raw_Work_Template.xlsx')


@api_bp.route("/download/raw-work", methods=["GET"])
def download_raw_work():
    """Download the processed Raw_Work.xlsx."""
    path = _upload_path(RAW_WORK_FILE)
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
    return send_file(path, as_attachment=True, download_name=RAW_WORK_FILE)


@api_bp.route("/download/estimates", methods=["GET"])
def download_estimates():
    """Download the Estimates.xlsx."""
    path = _upload_path(ESTIMATES_FILE)
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
    return send_file(path, as_attachment=True, download_name=ESTIMATES_FILE)
