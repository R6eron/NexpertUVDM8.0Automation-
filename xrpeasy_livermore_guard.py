#!/usr/bin/env python3
import requests
import os
import time
from datetime import datetime, timezone

PIVOT = 0.1468      # example Livermore/UVDM pivot for XRP
BUFFER = 0.0015     # small buffer around pivot
SYMBOL = "XRPUSDT"
API_URL = f"https://api.mexc.com/api/v3/ticker/24hr?symbol={SYMBOL}"

print(f"🚀 XRPEASY LIVERMORE PIVOT GUARD | {datetime.now().strftime('%H:%M GMT')}")

def fetch_xrp_stats():
    try:
        resp = requests.get(API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # MEXC returns a single object when 'symbol' is passed
        price = float(data["lastPrice"])
        change = float(data["priceChangePercent"])
        return price, change
    except Exception as e:
        print(f"❌ API ERROR: {e}")
        return None, None

def classify_pivot_state(price, change):
    if price is None:
        return "API_ERROR"

    if price >= PIVOT + BUFFER:
        if change is not None and change > 3.0:
            return "BULL_PIVOT_CONFIRMED"
        else:
            return "ABOVE_PIVOT_WEAK"
    elif price <= PIVOT - BUFFER:
        if change is not None and change < -3.0:
            return "BEAR_PIVOT_CONFIRMED"
        else:
            return "BELOW_PIVOT_WEAK"
    else:
        return "AT_PIVOT_ZONE"

def write_pivot_state(state, price, change):
    path = os.path.expanduser("~/.xrpeasy_pivot_state")
    ts = datetime.now(timezone.utc).isoformat()
    try:
        safe_price = price if price is not None else 0.0
        safe_change = change if change is not None else 0.0
        with open(path, "w") as f:
f.write(f"{ts},{state},{safe_price:.6f},{safe_change:+.2f}
")
    except Exception as e:
        print(f"⚠️ STATE WRITE ERROR: {e}")

# initial fetch and status
price, change = fetch_xrp_stats()
state = classify_pivot_state(price, change)

if price is not None:
    print(
        f"📊 XRP/USDT: ${price:.6f} | 24h: {change:+.2f}% | STATE: {state}"
    )
else:
    print("❌ INITIAL API ERROR - RETRYING")

write_pivot_state(state, price, change)
print("🔄 UDVM LIVERMORE SENTINEL LIVE - Ctrl+C to exit")

while True:
    time.sleep(60)
    price, change = fetch_xrp_stats()
    state = classify_pivot_state(price, change)

    if price is not None:
        print(
            f"[{datetime.now().strftime('%H:%M')}] "
            f"XRP: ${price:.6f} ({change:+.2f}%) → {state}"
        )

    write_pivot_state(state, price, change)
