#!/usr/bin/env python3
import sys
import os
import json
import time
import hmac
import hashlib
import urllib.request
import subprocess
import shutil
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

RUNTIME = Path.home() / ".config" / "uvdm" / "runtime"
RUNTIME.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("BITRUE_API_KEY", "")
API_SECRET = os.getenv("BITRUE_API_SECRET", "")

def c(code, text):
    return f"\u001B[{code}m{text}\u001B[0m"

def speak(msg: str):
    try:
        subprocess.run(
            ["termux-tts-speak", msg],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass

def put(label, value):
    width = shutil.get_terminal_size((80, 20)).columns
    # Stripping ANSI codes strictly for length calculation
    raw_val = value.replace('\u001B[1;37m', '').replace('\u001B[32m', '').replace('\u001B[31m', '').replace('\u001B[33m', '').replace('\u001B[0m', '')
    line_len = len(f"{label:<7}: {raw_val}")
    if line_len > width - 2:
        print(f"{label}:")
        print(value)
    else:
        print(f"{label:<7}: {value}")

def jget(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode())

def get_live_price(asset: str):
    symbol = f"{asset.upper()}USDT"
    urls = [
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}",
    ]
    for url in urls:
        try:
            data = jget(url)
            if "price" in data:
                return Decimal(str(data["price"])), url
        except Exception:
            pass
    return None, None

def get_reference_anchor(asset: str):
    anchors = {
        "XLM": Decimal("0.19"),
        "XRP": Decimal("0.50"),
        "BTC": Decimal("100000"),
        "ETH": Decimal("3000"),
        "SOL": Decimal("150"),
        "DOGE": Decimal("0.12"),
        "ADA": Decimal("0.60"),
        "HBAR": Decimal("0.08"),
        "FLR": Decimal("0.02"),
    }
    return anchors.get(asset.upper(), Decimal("1.0"))

def movement_voice(asset: str, live_price: Decimal, anchor: Decimal):
    if anchor <= 0:
        return f"Ron. {asset} live price ready."
    delta = ((live_price / anchor) - Decimal("1")) * Decimal("100")
    if delta >= Decimal("2.0"):
        return f"Ron. {asset} has pushed up and is trading strong."
    if delta > Decimal("0.25"):
        return f"Ron. {asset} is sideways and slightly up."
    if delta <= Decimal("-2.0"):
        return f"Ron. {asset} is under pressure and trading below anchor."
    if delta < Decimal("-0.25"):
        return f"Ron. {asset} is sideways and slightly down."
    return f"Ron. {asset} is flat around anchor."

def sign_headers(method, path, body=None):
    ts = str(int(time.time() * 1000))
    body_str = json.dumps(body, separators=(",", ":")) if body else ""
    payload = f"{ts}{method.upper()}{path}{body_str}"
    sig = hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-CH-APIKEY": API_KEY,
        "X-CH-TS": ts,
        "X-CH-SIGN": sig,
    }

def place_order(cname, side, qty, price, leverage, live=False):
    body = {
        "contractName": cname,
        "side": side,
        "type": "LIMIT",
        "positionType": 1,
        "open": "OPEN",
        "volume": float(qty),
        "price": float(price),
        "leverage": int(leverage.replace("x", "")),
    }
    if not live:
        return {"dry_run": True, "body": body}
    try:
        headers = sign_headers("POST", "/fapi/v2/order", body)
        req = urllib.request.Request(
            "https://fapi.bitrue.com/fapi/v2/order",
            data=json.dumps(body).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 5:
        print("Usage: python3 tools/limit_ladder_live.py <amount_xlm> <asset> <mode> <leverage> [live]")
        sys.exit(1)

    usdt = Decimal(sys.argv[1])
    asset = sys.argv[2].upper()
    mode = sys.argv[3]
    lev = sys.argv[4]
    live = len(sys.argv) > 5 and sys.argv[5].lower() == "live"

    ref_anchor = get_reference_anchor(asset)
    live_price, source = get_live_price(asset)
    price = live_price if live_price is not None else ref_anchor

    voice_line = movement_voice(asset, price, ref_anchor)
    
    print(c("1;36", "UVDM Wingman TM 2025"))
    print(c("37", "LEWIS RS 15081968001"))
    print(c("36", "────────────────────────"))
    print(c("1;36", "LIMIT LADDER"))
    print(c("36", "────────────────────────"))
    
    print(f"{asset} Ladder Algo @ ~${price}")
    speak(voice_line)

    weights = [Decimal("0.50"), Decimal("0.30"), Decimal("0.20")]
    pullbacks = [Decimal("0.0025"), Decimal("0.0050"), Decimal("0.0075")]

    cname = f"E-{asset}-USDT"

    delta = ((price / ref_anchor) - Decimal("1")) * Decimal("100") if ref_anchor > 0 else Decimal("0")

    put("Budget", c("33", f"${usdt:.2f} USDT"))
    put("Plan", c("1;37", f"{asset} {mode} {lev}"))
    put("Live", c("32", f"${price:.8f}"))
    put("Anchor", f"${ref_anchor:.8f}")
    
    delta_col = "32" if delta >= 0 else "31"
    put("Delta", c(delta_col, f"{delta:+.2f}%"))
    
    state_col = "1;31" if live else "1;33"
    put("State", c(state_col, "LIVE" if live else "DRY RUN"))
    if source:
        put("Source", c("36", source.replace("https://", "")))
    print("")

    ladder_colors = ["35", "34", "36"]
    total_qty = Decimal("0")
    
    for i, (w, pb, col) in enumerate(zip(weights, pullbacks, ladder_colors), 1):
        budget = (usdt * w).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        limit_price = (price * (Decimal("1") - pb)).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        qty = (budget / limit_price).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        total_qty += qty
        result = place_order(cname, "BUY", qty, limit_price, lev, live=live)

        print(c(f"1;{col}", f"LADDER {i}"))
        put("Budget", c("33", f"${budget:.2f} USDT"))
        put("Qty", c("1;37", f"{qty} {asset}"))
        put("Limit", c("32", f"${limit_price}"))
        put("Dip", c("31", f"{(pb * 100):.2f}%"))
        put("Order", json.dumps(result, separators=(",", ":")))
        print("")

    print(c("36", "TOTAL"))
    put("Budget", c("33", f"${usdt:.2f} USDT"))
    put("Qty", c("1;37", f"{total_qty} {asset}"))
    print("")
    print("Ladder complete.")

if __name__ == "__main__":
    main()
