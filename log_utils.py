import io
import json
import csv


def read_upload(uploaded_file) -> str:
    """
    Read an uploaded Streamlit file and return its content as a plain string.
    Supports: .txt, .log, .csv, .json
    """
    name = uploaded_file.name.lower()
    raw  = uploaded_file.read()

    if name.endswith(".json"):
        return _read_json(raw)
    elif name.endswith(".csv"):
        return _read_csv(raw)
    else:
        # .txt / .log — plain text
        return raw.decode("utf-8", errors="ignore")


def _read_json(raw: bytes) -> str:
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
        if isinstance(data, list):
            lines = []
            for item in data:
                if isinstance(item, dict):
                    lines.append("  ".join(f"{k}={v}" for k, v in item.items()))
                else:
                    lines.append(str(item))
            return "\n".join(lines)
        elif isinstance(data, dict):
            return json.dumps(data, indent=2)
        else:
            return str(data)
    except Exception as e:
        return f"[JSON parse error: {e}]\n" + raw.decode("utf-8", errors="ignore")


def _read_csv(raw: bytes) -> str:
    try:
        text   = raw.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))
        lines  = []
        for row in reader:
            lines.append("  ".join(f"{k}={v}" for k, v in row.items()))
        return "\n".join(lines)
    except Exception as e:
        return f"[CSV parse error: {e}]\n" + raw.decode("utf-8", errors="ignore")
