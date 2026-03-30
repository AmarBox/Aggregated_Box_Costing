import json
import os
from datetime import datetime

COSTS_FILE = os.path.join(os.path.dirname(__file__), "material_costs.json")


def _load_costs():
    """Load the monthly costs JSON file."""
    if not os.path.exists(COSTS_FILE):
        return {}
    with open(COSTS_FILE, "r") as f:
        return json.load(f)


def _save_costs(data):
    """Save costs back to the JSON file."""
    with open(COSTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_all_monthly_costs():
    """Return all monthly cost records, sorted newest first."""
    data = _load_costs()
    return dict(sorted(data.items(), reverse=True))


def get_costs_for_date(date_str=None):
    """
    Get paper costs for a given date (YYYY-MM-DD or YYYY-MM).

    If date_str is None or empty, returns the latest month's costs.
    Returns a dict like {"KRAFT": 35.5, "DUPLEX": 45, ...} or None if no data.
    """
    data = _load_costs()
    if not data:
        return None

    if date_str:
        # Extract YYYY-MM from input (handles both YYYY-MM and YYYY-MM-DD)
        month_key = date_str[:7]
        if month_key in data:
            return data[month_key]
        # If exact month not found, find the closest earlier month
        sorted_months = sorted(data.keys(), reverse=True)
        for m in sorted_months:
            if m <= month_key:
                return data[m]
        # If all months are after the requested date, return the oldest
        return data[sorted_months[-1]]
    else:
        # No date provided — use the latest month
        latest_month = max(data.keys())
        return data[latest_month]


def upsert_monthly_costs(month_key, costs):
    """
    Add or update costs for a given month.

    month_key: "YYYY-MM"
    costs: dict of paper quality name -> cost per kg (e.g. {"KRAFT": 35.5})
    """
    data = _load_costs()
    if month_key in data:
        data[month_key].update(costs)
    else:
        data[month_key] = costs
    _save_costs(data)
    return data[month_key]
