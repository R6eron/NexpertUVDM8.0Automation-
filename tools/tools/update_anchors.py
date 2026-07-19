#!/usr/bin/env python3
import json, urllib.request
from pathlib import Path

def jget(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode())

assets = ["XLM", "XRP", "BTC", "ETH", "SOL", "DOGE", "ADA", "HBAR", "FLR"]
anchors = {}

print("Fetching current market tape for anchors...")
for asset in assets:
    symbol = f"{asset}USDT"
    urls = [
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}"
    ]
    for u in urls:
        try:
            data = jget(u)
            if "price" in data:
                price = float(data["price"])
                anchors[asset] = price
                print(f"  {asset:<5}: {price:.8f}")
                break
        except Exception:
            pass

path = Path.home() / ".config" / "uvdm" / "runtime" / "anchors.json"
path.parent.mkdir(parents=True, exist_ok=True)
with open(path, "w") as f:
    json.dump(anchors, f, indent=2)

print("✅ Reference anchors updated. Voice greetings will baseline from these prices.")
