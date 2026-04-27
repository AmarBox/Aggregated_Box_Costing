"""
Material costs lookup — sourced from the remote config.

Monthly raw paper costs (INR/kg) live under cfg['material_costs']['monthly'].
A baseline 'default' map under cfg['material_costs']['default'] is used when
no monthly data matches the requested date.

End users cannot edit these values; updates flow from the central config
repo on next app launch.
"""

from . import remote_config


def _monthly() -> dict:
    return remote_config.get().get("material_costs", {}).get("monthly", {})


def _defaults() -> dict:
    return remote_config.get().get("material_costs", {}).get("default", {})


def get_all_monthly_costs() -> dict:
    """Return all monthly cost records, sorted newest first."""
    data = _monthly()
    return dict(sorted(data.items(), reverse=True))


def get_costs_for_date(date_str: str | None = None) -> dict | None:
    """Get paper costs for a given date (YYYY-MM-DD or YYYY-MM).

    If date_str is None or empty, returns the latest month's costs.
    Falls back to material_costs.default if no monthly data exists.
    Returns a dict like {"KRAFT": 35.5, "DUPLEX": 45, ...} or None.
    """
    data = _monthly()
    if not data:
        defaults = _defaults()
        return defaults or None

    if date_str:
        month_key = date_str[:7]
        if month_key in data:
            return data[month_key]
        sorted_months = sorted(data.keys(), reverse=True)
        for m in sorted_months:
            if m <= month_key:
                return data[m]
        return data[sorted_months[-1]]

    latest_month = max(data.keys())
    return data[latest_month]
