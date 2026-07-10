#!/usr/bin/env python3
import json, os, datetime

BASE = os.path.expanduser("~/NexpertUVDM-Automation")
alerts_path = os.path.join(BASE, "runtime", "alerts.json")
exec_log_path = os.path.join(BASE, "execution_log.jsonl")

def main():
    if not os.path.exists(alerts_path):
        print("no alerts.json, nothing to do")
        return

    with open(alerts_path, "r", encoding="utf-8") as f:
        alert = json.load(f)

    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    event = {
        "ts": ts,
        "user_key": "founder",
        "user_name": "XRPeasy Digital Solutions Founder",
        "digital_immortal_name": "Ron Alpa",
        "digital_immortal_number": "001",
        "symbol": alert.get("asset"),
        "side": "buy",
        "status": "executed_stub_dry_run",
        "reason": "Manual dry-run executor consumed execute_ready alert",
        "extra": {
            "regime": alert.get("regime"),
            "setup": alert.get("setup"),
            "level": alert.get("level"),
            "voice_cmd": alert.get("voice_cmd"),
            "operator_action": alert.get("operator_action"),
        },
    }

    with open(exec_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "
")

    print("manual execute recorded:", event["symbol"], event["status"])

if __name__ == "__main__":
    main()
