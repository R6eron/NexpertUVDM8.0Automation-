import json, os, tempfile
from pathlib import Path
from datetime import datetime, UTC

BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / "state"
STATE_DIR.mkdir(exist_ok=True)
EVENT_FILE = STATE_DIR / "latest_profit_event.json"

def write_profit_event(event_id: str, pnl_usdt: float, meta: dict | None = None):
    data = {
        "id": event_id,
        "pnl_usdt": pnl_usdt,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    if meta:
        data["meta"] = meta

    with tempfile.NamedTemporaryFile("w", delete=False, dir=STATE_DIR) as tmp:
        json.dump(data, tmp, separators=(",", ":"))
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name

    os.replace(tmp_name, EVENT_FILE)
    return data

if __name__ == "__main__":
    e = write_profit_event("MANUAL_SHELL_TEST", 999.99, {"note": "shell test"})
    print("Wrote event:", e)
