import json
import os
from datetime import datetime

# On Railway, mount a Volume at /data to persist across deploys.
# Locally it falls back to ./data/
DATA_DIR = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "data")
DB_FILE = os.path.join(DATA_DIR, "database.json")


def _load():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_FILE):
        _save({"email_counter": 1, "queries": {}})
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_jb_code():
    """Get next JB code and increment counter."""
    data = _load()
    counter = data.get("email_counter", 1)
    code = f"JB{counter:03d}"
    data["email_counter"] = counter + 1
    _save(data)
    return code


def add_query(jb_code: str, guests: str, checkin: str, checkout: str,
              hotel: str, status: str = "fresh", month: str = None):
    """Add a new query to the database."""
    data = _load()
    if "queries" not in data:
        data["queries"] = {}

    if month is None:
        # Parse month from checkin date e.g. "15.01.2025" -> "01.2025"
        try:
            parts = checkin.split(".")
            if len(parts) == 3:
                month = f"{parts[1]}.{parts[2]}"
            else:
                month = datetime.now().strftime("%m.%Y")
        except Exception:
            month = datetime.now().strftime("%m.%Y")

    data["queries"][jb_code] = {
        "jb_code": jb_code,
        "guests": guests,
        "checkin": checkin,
        "checkout": checkout,
        "hotel": hotel,
        "status": status,
        "month": month,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    _save(data)
    return data["queries"][jb_code]


def get_queries_by_status(status: str, month: str = None):
    """Get all queries filtered by status and optionally month."""
    data = _load()
    queries = data.get("queries", {})
    result = []
    for q in queries.values():
        if q["status"] == status:
            if month is None or q.get("month") == month:
                result.append(q)
    return sorted(result, key=lambda x: x["jb_code"])


def get_query(jb_code: str):
    """Get a single query by JB code."""
    data = _load()
    return data.get("queries", {}).get(jb_code)


def update_query_status(jb_code: str, new_status: str):
    """Update the status of a query."""
    data = _load()
    if jb_code in data.get("queries", {}):
        data["queries"][jb_code]["status"] = new_status
        _save(data)
        return True
    return False


def delete_query(jb_code: str):
    """Delete a query by JB code."""
    data = _load()
    if jb_code in data.get("queries", {}):
        del data["queries"][jb_code]
        _save(data)
        return True
    return False


def get_all_months():
    """Get all unique months that have queries."""
    data = _load()
    months = set()
    for q in data.get("queries", {}).values():
        if q.get("month"):
            months.add(q["month"])
    return sorted(months)
