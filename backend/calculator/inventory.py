"""
Paper reel inventory management.

Stores a list of paper reels with type, grammage (GSM), deckel (size in inches),
and weight remaining (kg). Data is persisted to inventory.json.
"""

import json
import os

_DATA_FILE = os.path.join(os.path.dirname(__file__), 'inventory.json')


def _load():
    if not os.path.exists(_DATA_FILE):
        return {"next_id": 1, "reels": []}
    with open(_DATA_FILE, 'r') as f:
        return json.load(f)


def _save(data):
    with open(_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_all_reels():
    """Return all reels sorted by type, then GSM, then deckel."""
    data = _load()
    reels = data.get("reels", [])
    # Sort order: type (alphabetical), then GSM (ascending), then deckel (ascending)
    type_order = {"KRAFT": 0, "GOLDEN": 1, "DUPLEX": 2, "ITC": 3, "PREPRINTED": 4}
    reels.sort(key=lambda r: (
        type_order.get(r.get("type", ""), 99),
        r.get("gsm", 0),
        r.get("deckel", 0),
    ))
    return reels


def add_reel(reel_type, gsm, deckel, weight, count=1):
    """Add a new reel (or multiple identical reels) to inventory."""
    data = _load()
    added = []
    for _ in range(count):
        reel = {
            "id": data["next_id"],
            "type": reel_type.upper(),
            "gsm": int(gsm),
            "deckel": float(deckel),
            "weight": float(weight),
        }
        data["reels"].append(reel)
        added.append(reel)
        data["next_id"] += 1
    _save(data)
    return added


def update_reel(reel_id, updates):
    """Update a reel's fields (weight, gsm, deckel, type)."""
    data = _load()
    for reel in data["reels"]:
        if reel["id"] == reel_id:
            for key in ("type", "gsm", "deckel", "weight"):
                if key in updates:
                    if key == "type":
                        reel[key] = str(updates[key]).upper()
                    elif key == "gsm":
                        reel[key] = int(updates[key])
                    else:
                        reel[key] = float(updates[key])
            _save(data)
            return reel
    return None


def delete_reel(reel_id):
    """Remove a reel from inventory."""
    data = _load()
    before = len(data["reels"])
    data["reels"] = [r for r in data["reels"] if r["id"] != reel_id]
    if len(data["reels"]) < before:
        _save(data)
        return True
    return False


def get_inventory_summary():
    """Get a summary grouped by type → GSM → deckel with counts and total weight."""
    reels = get_all_reels()
    summary = {}
    for r in reels:
        key = (r["type"], r["gsm"], r["deckel"])
        if key not in summary:
            summary[key] = {"type": r["type"], "gsm": r["gsm"], "deckel": r["deckel"], "count": 0, "total_weight": 0}
        summary[key]["count"] += 1
        summary[key]["total_weight"] += r["weight"]
    return list(summary.values())
