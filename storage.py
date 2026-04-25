import json
import uuid
from datetime import datetime
from pathlib import Path

STORAGE_DIR = Path("incidents")
STORAGE_DIR.mkdir(exist_ok=True)


def save_incident(
    title:       str,
    org:         str,
    environment: str,
    severity:    str,
    log_snippet: str,
    agents:      list,
    results:     dict,
) -> dict:
    record = {
        "id":          str(uuid.uuid4())[:8],
        "title":       title,
        "org":         org,
        "environment": environment,
        "severity":    severity,
        "log_snippet": log_snippet,
        "agents":      agents,
        "results":     results,
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    path = STORAGE_DIR / f"{record['id']}.json"
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    return record


def load_all_incidents() -> list:
    records = []
    for path in sorted(STORAGE_DIR.glob("*.json")):
        try:
            with open(path) as f:
                records.append(json.load(f))
        except Exception:
            pass
    return records


def clear_all_incidents():
    for path in STORAGE_DIR.glob("*.json"):
        path.unlink()
