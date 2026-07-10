# BITRUE SIMPLE v1.1 – RETRY + FALLBACK
import os
import time
import requests
from datetime import datetime

API_KEY = os.getenv("BITRUE_API_KEY", "")
SECRET = os.getenv("BITRUE_API_SECRET", "")
pivot = 0.1468
entry = 0.1529
logfile = "bitrue_simple.log"

URLS = [
    "https://api.bitrue.com/api/v1/spot/ticker?symbol=XLMUSDT",
    "https://openapi.bitrue.com/api/v1/spot/ticker?symbol=XLMUSDT",
]

def log(msg):
    ts = datetime.now().strftime("%H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\
")

def get_price():
    last_error = None
    for url in URLS:
        for attempt in range(1, 3):
            try:
                r = requests.get(url, timeout=20)
                r.raise_for_status()
                data = r.json()
                price = data.get("close") or data.get("lastPrice") or data.get("price")
                if price is None:
                    last_error = f"unexpected payload from {url}: {data}"
                    log(last_error)
                    break
                if attempt > 1:
                    log(f"retry success via {url}")
                return float(price)
            except Exception as e:
                last_error = f"attempt {attempt} failed via {url}: {e}"
                log(last_error)
                if attempt < 2:
                    time.sleep(2)
    log(f"price fetch error: {last_error}")
    return None

def main():
    regime = os.getenv("UVDM_REGIME", "unknown")
    log(f"start regime={regime} pivot={pivot} entry={entry}")
    px = get_price()
    if px is None:
        return 1
    log(f"XLMUSDT={px:.6f}")
    if px > entry:
        log("above entry")
    elif px > pivot:
        log("between pivot and entry")
    else:
        log("below pivot")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
