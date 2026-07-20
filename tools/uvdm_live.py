#!/usr/bin/env python3
import sys, os, json, time, hmac, hashlib, urllib.request, subprocess, shutil
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITRUE_API_KEY", "")
API_SECRET = os.getenv("BITRUE_API_SECRET", "")

def c(code, text): return f"\u001B[{code}m{text}\u001B[0m"

def speak(msg: str):
    try:
        subprocess.run(["termux-tts-speak", msg], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def strip_ansi(text: str) -> str:
    for seq in [
        "\u001B[0m", "\u001B[31m", "\u001B[32m", "\u001B[33m", "\u001B[35m",
        "\u001B[36m", "\u001B[37m", "\u001B[1m", "\u001B[1;31m", "\u001B[1;33m",
        "\u001B[1;35m", "\u001B[1;36m", "\u001B[1;37m"
    ]:
        text = text.replace(seq, "")
    return text

def put(label, value):
    width = shutil.get_terminal_size((80, 20)).columns
    raw_val = strip_ansi(str(value))
    if len(f"{label:<7}: {raw_val}") > width - 2:
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
    url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}"
    try:
        data = jget(url)
        if "price" in data:
            return Decimal(str(data["price"])), url
    except Exception:
        pass
    return None, None

def get_reference_anchor(asset: str):
    path = Path.home() / ".config" / "uvdm" / "runtime" / "anchors.json"
    if path.exists():
        try:
            with open(path) as f:
                data = json.load(f)
            if asset.upper() in data:
                return Decimal(str(data[asset.upper()]))
        except Exception:
            pass
    fallback = {
        "XLM": "0.19", "XRP": "0.50", "BTC": "100000", "ETH": "3000",
        "SOL": "150", "DOGE": "0.12", "ADA": "0.60", "HBAR": "0.08", "FLR": "0.02"
    }
    return Decimal(fallback.get(asset.upper(), "1.0"))

def movement_voice(asset: str, live_price: Decimal, anchor: Decimal, strategy: str):
    if anchor <= 0:
        return f"Ron. {asset} live price ready."
    delta = ((live_price / anchor) - Decimal("1")) * Decimal("100")
    if delta >= Decimal("2.0"):
        msg = f"{asset} has pushed up and is trading strong."
    elif delta > Decimal("0.25"):
        msg = f"{asset} is sideways and slightly up."
    elif delta <= Decimal("-2.0"):
        msg = f"{asset} is under pressure and trading below anchor."
    elif delta < Decimal("-0.25"):
        msg = f"{asset} is sideways and slightly down."
    else:
        msg = f"{asset} is flat around anchor."
    plan_msg = "Limit ladder ready." if strategy == "ladder" else "Single shot ready."
    return f"Ron. {msg} {plan_msg}"

def sign_headers(method, path, body=None):
    ts = str(int(time.time() * 1000))
    body_str = json.dumps(body, separators=(",", ":")) if body else ""
    payload = f"{ts}{method.upper()}{path}{body_str}"
    sig = hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-CH-APIKEY": API_KEY,
        "X-CH-TS": ts,
        "X-CH-SIGN": sig
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
        "leverage": int(leverage.replace("x", ""))
    }
    if not live:
        return {"dry_run": True, "body": body}
    try:
        req = urllib.request.Request(
            "https://fapi.bitrue.com/fapi/v2/order",
            data=json.dumps(body, separators=(",", ":")).encode(),
            headers=sign_headers("POST", "/fapi/v2/order", body),
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def q8(x):
    return x.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)

def dynamic_step(price: Decimal, anchor: Decimal) -> Decimal:
    base = Decimal("0.0025")
    if anchor <= 0:
        return base
    dislocation = abs((price / anchor) - Decimal("1"))
    if dislocation >= Decimal("0.08"):
        return Decimal("0.0040")
    if dislocation >= Decimal("0.05"):
        return Decimal("0.0035")
    if dislocation >= Decimal("0.03"):
        return Decimal("0.0030")
    return base

def main():
    if len(sys.argv) < 6:
        print("Usage: python3 tools/uvdm_live.py <usdt> <asset> <mode> <leverage> <strategy:single|ladder> [live]")
        sys.exit(1)

    usdt = Decimal(sys.argv[1])
    asset = sys.argv[2].upper()
    mode = sys.argv[3]
    lev = sys.argv[4]
    strategy = sys.argv[5].lower()
    live = len(sys.argv) > 6 and sys.argv[6].lower() == "live"

    ref_anchor = get_reference_anchor(asset)
    live_price, source = get_live_price(asset)
    price = live_price if live_price is not None else ref_anchor
    step = dynamic_step(price, ref_anchor)

    print(c("1;36", "UVDM Wingman TM 2025"))
    print(c("37", "LEWIS RS 15081968001"))
    print(c("36", "────────────────────────"))
    print(c("1;36", "SMART SINGLE SHOT" if strategy == "single" else "LIMIT LADDER"))
    print(c("36", "────────────────────────"))
    print(f"{asset} Algo @ ~${price:.8f}")

    speak(movement_voice(asset, price, ref_anchor, strategy))

    delta = ((price / ref_anchor) - Decimal("1")) * Decimal("100") if ref_anchor > 0 else Decimal("0")

    put("Budget", c("33", f"${usdt:.2f} USDT"))
    put("Plan", c("1;37", f"{asset} {mode} {lev}"))
    put("Live", c("32", f"${price:.8f}"))
    put("Anchor", f"${ref_anchor:.8f}")
    put("Delta", c("32" if delta >= 0 else "31", f"{delta:+.2f}%"))
    put("Step", c("35", f"{(step * 100):.2f}%"))
    put("State", c("1;31" if live else "1;33", "LIVE" if live else "DRY RUN"))
    if source:
        put("Source", c("36", source.replace("https://", "")))
    print("")

    cname = f"E-{asset}-USDT"

    if strategy == "single":
        pb = step
        limit_price = q8(price * (Decimal("1") - pb))
        qty = q8(usdt / limit_price)
        result = place_order(cname, "BUY", qty, limit_price, lev, live=live)

        print(c("1;35", "ENTRY BAND"))
        put("Qty", c("1;37", f"{qty} {asset}"))
        put("USDT", c("33", f"${usdt:.2f}"))
        put("Limit", c("32", f"${limit_price}"))
        put("Dip", c("31", f"{(pb * 100):.2f}%"))
        put("Order", json.dumps(result, separators=(",", ":")))
        print("")
        print("Single shot complete.")
    else:
        total_qty = Decimal("0")

        if asset == "XLM":
            levels = [
                (Decimal("0.20"), "probe", Decimal("0.1852"), "starter fill"),
                (Decimal("0.35"), "core",  Decimal("0.1845"), "main reaction zone"),
                (Decimal("0.45"), "value", Decimal("0.1839"), "structural low add"),
            ]
            invalidation = Decimal("0.1838")
            bias_text = "Constructive while 0.1838 holds"
            plan_text = "Hybrid probe / core / value"
        else:
            levels = [
                (Decimal("0.20"), "probe", q8(price * (Decimal("1") - step * Decimal("0.8"))), "starter fill"),
                (Decimal("0.35"), "core",  q8(price * (Decimal("1") - step * Decimal("1.4"))), "main reaction zone"),
                (Decimal("0.45"), "value", q8(price * (Decimal("1") - step * Decimal("2.4"))), "structural low add"),
            ]
            invalidation = q8(price * (Decimal("1") - step * Decimal("2.6")))
            bias_text = f"Constructive while {invalidation} holds"
            plan_text = "Hybrid probe / core / value"

        print(c("1;36", "VOL / DEMAND LADDER"))
        print(c("36", "────────────────────────────────────────"))
        put("Symbol", c("1;36", f"{asset}USDT Perpetual"))
        put("Bias", c("1;32", bias_text))
        put("Plan", c("1;33", plan_text))
        put("State", c("1;31" if live else "1;35", "LIVE" if live else "DRY RUN"))
        print("")
        print(c("1;36", "LADDER"))

        for i, (w, role, limit_price, route_note) in enumerate(levels, 1):
            budget = (usdt * w).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            qty = q8(budget / limit_price)
            total_qty += qty
            result = place_order(cname, "BUY", qty, limit_price, lev, live=live)

            print(
                f"  {c('1;37', f'{i})')} "
                f"{c('1;36', f'{limit_price:.8f}')} | "
                f"{c('1;32', f'{qty} {asset}')} | "
                f"{c('1;33', f'{budget:.2f} USDT')} | "
                f"{c('1;37', role)}"
            )
            put("Route", c("35", route_note))
            put("Order", json.dumps(result, separators=(",", ":")))

        print("")
        print(c("1;36", "TOTAL"))
        put("Size", c("1;32", f"{total_qty} {asset}"))
        put("Budget", c("1;33", f"{usdt:.2f} USDT"))
        put("Invalidation", c("1;31", f"acceptance below {invalidation}"))
        print("")
        print(c("1;36", "DOCTRINE"))
        print(c("37", "  1. Start small (20%)."))
        print(c("37", "  2. Core at reaction (35%)."))
        print(c("37", "  3. Value at structural low (45%)."))
        print(c("37", "  4. Exit clean if demand fails."))
        print(c("36", "────────────────────────────────────────"))
        print(c("1;32", "Ladder complete."))

if __name__ == "__main__":
    main()
