import json
import ssl
import urllib.request
import urllib.parse
import shutil

USER_AGENT = "UVDM-Wingman/2.2"

RESET = "\u001B[0m"
BOLD = "\u001B[1m"
CYAN = "\u001B[1;36m"
BLUE = "\u001B[1;34m"
GREEN = "\u001B[0;32m"
YELLOW = "\u001B[1;33m"
RED = "\u001B[0;31m"
WHITE = "\u001B[1;37m"

ASSETS = ["FLR", "SGB", "XRP", "XLM", "ETH", "BTC"]


def term_width():
    return shutil.get_terminal_size((80, 20)).columns


def c(text, color=RESET, bold=False):
    prefix = color + (BOLD if bold else "")
    return f"{prefix}{text}{RESET}"


def center(text, color=CYAN, bold=True):
    width = term_width()
    raw = str(text)
    pad = max(0, (width - len(raw)) // 2)
    return " " * pad + c(raw, color, bold)


def hr(color=CYAN):
    width = term_width()
    return c("-" * min(width, 56), color)


def fetch_json(url, timeout=10):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return json.loads(r.read().decode("utf-8", errors="ignore"))


def extract_numeric_price(obj):
    if isinstance(obj, (int, float)):
        return float(obj)

    if isinstance(obj, str):
        try:
            return float(obj)
        except Exception:
            return None

    if isinstance(obj, list):
        for item in obj:
            v = extract_numeric_price(item)
            if v is not None and v > 0:
                return v
        return None

    if isinstance(obj, dict):
        for key in ["price", "value", "median", "latest", "close", "usd", "rate", "feed_value", "feedValue"]:
            if key in obj:
                v = extract_numeric_price(obj[key])
                if v is not None and v > 0:
                    return v
        for _, val in obj.items():
            v = extract_numeric_price(val)
            if v is not None and v > 0:
                return v

    return None


def normalize_asset(raw):
    raw = str(raw).strip().upper()
    if raw in ASSETS:
        return raw
    if raw.endswith("X") and raw[:-1] in ASSETS:
        return raw[:-1]
    return None


def normalize_asset_choice(raw):
    s = str(raw).strip().upper()
    if s.isdigit():
        idx = int(s) - 1
        if 0 <= idx < len(ASSETS):
            return ASSETS[idx]
    return normalize_asset(s)


def symbol_to_feed(asset_name):
    mapping = {
        "BTC": "BTC/USD",
        "ETH": "ETH/USD",
        "FLR": "FLR/USD",
        "SGB": "SGB/USD",
        "XRP": "XRP/USD",
        "XLM": "XLM/USD",
    }
    a = str(asset_name).strip().upper()
    return mapping.get(a, a + "/USD")


def get_live_ftso_px(asset_name):
    feed = symbol_to_feed(asset_name)
    enc = urllib.parse.quote(feed, safe="")
    urls = [
        "https://ftso-v2-data-provider.flare.network/feed-values/" + enc,
        "https://api.flareforge.io/api/v1/oracle-lab/feeds",
    ]

    last_err = None

    for url in urls:
        try:
            data = fetch_json(url, timeout=10)
            px = extract_numeric_price(data)
            if px is not None and px > 0:
                return px, "FTSO_LIVE"
        except Exception as e:
            last_err = e

    return None, ("FTSO_UNAVAILABLE: " + str(last_err) if last_err else "FTSO_UNAVAILABLE")


def get_live_offchain_px(asset_name):
    asset = str(asset_name).strip().upper()
    urls = [
        f"https://api.coinbase.com/v2/prices/{asset}-USDT/spot",
        f"https://api.coinbase.com/v2/prices/{asset}-USD/spot",
    ]

    last_err = None

    for url in urls:
        try:
            data = fetch_json(url, timeout=10)
            px = extract_numeric_price(data)
            if px is not None and px > 0:
                return px, "OFFCHAIN_LIVE"
        except Exception as e:
            last_err = e

    return None, ("OFFCHAIN_UNAVAILABLE: " + str(last_err) if last_err else "OFFCHAIN_UNAVAILABLE")


def stop_from_entry(entry_ref, risk_pct):
    return entry_ref * (1.0 - risk_pct)


def target_from_entry(entry_ref, tp_pct):
    return entry_ref * (1.0 + tp_pct)


def demand_zone(entry_ref):
    return entry_ref * 0.90, entry_ref * 0.95


def spot_onboard(live_px, stop_px, target_px):
    if live_px <= stop_px:
        return False, "EXIT_MKT", True, "BREACHED_STOP"
    if stop_px < live_px < target_px:
        return True, "HOLD", False, "ONBOARD_OK"
    if live_px >= target_px:
        return False, "EXIT_MKT", True, "AT_OR_ABOVE_TARGET"
    return False, "WAIT", False, "WAIT"


def futures_onboard(live_px, stop_px, target_px):
    if live_px <= stop_px:
        return False, "EXIT_MKT", True, "BREACHED_STOP"
    if live_px >= target_px:
        return False, "EXIT_MKT", True, "AT_OR_ABOVE_TARGET"
    if stop_px < live_px < target_px:
        return True, "HOLD", False, "ONBOARD_OK"
    return False, "WAIT", False, "WAIT"


def sharpe_gate(v):
    if v >= 3.1:
        return "PASS"
    if v >= 2.0:
        return "WATCH"
    return "SOFT_FAIL"


def ask(prompt, default=None):
    x = input(prompt).strip()
    return x if x else default


def ask_float(prompt, default=None, min_value=None):
    while True:
        raw = ask(prompt, default)
        raw = raw.strip().lower().replace("x", "").replace("%", "")
        try:
            val = float(raw)
        except ValueError:
            print(c("enter a valid number", RED, True))
            continue

        if min_value is not None and val <= min_value:
            print(c(f"value must be > {min_value}", RED, True))
            continue

        return val


def ask_choice_asset():
    while True:
        print()
        print(c("Choose asset or insert your own:", CYAN, True))
        for i, asset in enumerate(ASSETS, 1):
            print(c(f"{i}. {asset}", WHITE, True))

        raw = input(c("Select [1-6] or type ticker: ", YELLOW)).strip()
        asset = normalize_asset_choice(raw)

        if asset:
            return asset

        print(c("enter 1-6 or valid ticker", RED, True))


def ask_choice_venue():
    while True:
        print()
        print(c("Choose venue:", CYAN, True))
        print(c("1. Futures", WHITE, True))
        print(c("2. Spot", WHITE, True))
        raw = input(c("Select [1-2] or type futures/spot: ", YELLOW)).strip().lower()

        if raw in ("1", "f", "future", "futures", "long"):
            return "futures"
        if raw in ("2", "s", "spot"):
            return "spot"

        print(c("enter 1/2 or futures/spot", RED, True))


def status_color(status):
    if status == "ONBOARD_OK":
        return GREEN
    if "BREACHED" in status or "ABOVE" in status or status == "EXIT_MKT":
        return RED
    if status in {"WAIT", "WATCH", "SOFT_FAIL"}:
        return YELLOW
    return CYAN


def build_ladder(px, deploy_amt, leverage):
    price_steps = [0.005, 0.015, 0.025, 0.035, 0.045]
    weights = [0.16, 0.18, 0.20, 0.22, 0.24]
    tags = ["UPPER", "MID1", "MID2", "LOWER", "VALUE"]
    rows = []

    for tag, step, w in zip(tags, price_steps, weights):
        rung_px = px * (1.0 - step)
        margin = deploy_amt * w
        notional = margin * leverage
        units = notional / rung_px if rung_px > 0 else 0.0
        rows.append((tag, rung_px, margin, notional, units))

    return rows


def print_kv(label, value, color=WHITE):
    print(f"{label.ljust(14)} {c(str(value), color, False)}")


def print_ladder(rows, futures_mode):
    print()
    if term_width() < 72:
        if futures_mode:
            print(c("TAG      PRICE        MARGIN      UNITS", CYAN, True))
            for tag, rung_px, margin, rung_notional, rung_units in rows:
                print(f"{tag:<8} {rung_px:>10.6f} {margin:>11.2f} {rung_units:>10.0f}")
        else:
            print(c("TAG      PRICE        DEPLOY      UNITS", CYAN, True))
            for tag, rung_px, margin, rung_notional, rung_units in rows:
                print(f"{tag:<8} {rung_px:>10.6f} {margin:>11.2f} {rung_units:>10.2f}")
    else:
        if futures_mode:
            print(c("TAG      PRICE        MARGIN     NOTIONAL        UNITS", CYAN, True))
            for tag, rung_px, margin, rung_notional, rung_units in rows:
                print(f"{tag:<8} {rung_px:>10.6f} {margin:>11.2f} {rung_notional:>12.2f} {rung_units:>12.2f}")
        else:
            print(c("TAG      PRICE        DEPLOY          UNITS", CYAN, True))
            for tag, rung_px, margin, rung_notional, rung_units in rows:
                print(f"{tag:<8} {rung_px:>10.6f} {margin:>11.2f} {rung_units:>14.2f}")


def main():
    print()
    print(center("Wingman TM 2025", CYAN, True))
    print(center("Digital Immortal live onboarding", WHITE, False))
    print()

    asset = ask_choice_asset()
    venue = ask_choice_venue()
    deploy_amt = ask_float(c("Deploy amount? ", YELLOW), "0", 0)
    portfolio_amt = ask_float(c("Portfolio size? [30000] ", YELLOW), "30000", 0)

    use_live = ask(c("Use live FTSO/offchain price first? (y/n) [y] ", YELLOW), "y").lower()

    px = None
    source = "MANUAL"

    if use_live.startswith("y"):
        px, source = get_live_ftso_px(asset)
        if px is None:
            px, source = get_live_offchain_px(asset)

    if px is None:
        px = ask_float(c("Current price? ", YELLOW), "0", 0)
        source = "MANUAL"

    risk_pct = ask_float(c("Stop Loss (SL) % below entry? [5] ", YELLOW), "5", 0) / 100.0
    target_pct = ask_float(c("Target % above entry? [8] ", YELLOW), "8", 0) / 100.0
    sharpe = ask_float(c("Sharpe ratio? [3.1] ", YELLOW), "3.1")

    leverage = 1.0
    if venue == "futures":
        leverage = ask_float(c("Leverage? max 10x, recommended 7x & under [5] ", YELLOW), "5", 0)
        leverage = max(1.0, min(leverage, 10.0))

    entry_ref = float(px)
    stop_px = stop_from_entry(entry_ref, risk_pct)
    target_px = target_from_entry(entry_ref, target_pct)
    demand_low, demand_high = demand_zone(entry_ref)

    if venue == "futures":
        can_onboard, act, lock, status = futures_onboard(px, stop_px, target_px)
    else:
        can_onboard, act, lock, status = spot_onboard(px, stop_px, target_px)

    notional = deploy_amt * leverage
    units = notional / px if px > 0 else 0.0
    deploy_pct = (deploy_amt / portfolio_amt) * 100.0 if portfolio_amt > 0 else 0.0
    risk_budget = portfolio_amt * 0.02
    stop_gap = abs(px - stop_px)
    sg = sharpe_gate(sharpe)
    ladder = build_ladder(px, deploy_amt, leverage)

    col = status_color(status)
    sg_col = status_color(sg)

    print()
    print(hr())
    print(c("SUMMARY", CYAN, True))
    print_kv("Asset", asset)
    print_kv("Venue", venue)
    print_kv("Source", source)
    print_kv("Price", format(px, ".7f"), col)
    print_kv("Deploy", format(deploy_amt, ".2f"))
    print_kv("Port", format(portfolio_amt, ".2f"))
    print_kv("Deploy %", format(deploy_pct, ".2f") + "%")
    print_kv("Lev", format(leverage, ".2f") + "x")
    print_kv("Notional", format(notional, ".2f"))
    print_kv("Units", format(units, ".7f"))

    print(hr())
    print(c("LEVELS", CYAN, True))
    print_kv("Entry", format(entry_ref, ".7f"))
    print_kv("Demand", f"{format(demand_low, '.7f')} -> {format(demand_high, '.7f')}")
    print_kv("SL", format(stop_px, ".7f"), RED)
    print_kv("Gap", format(stop_gap, ".7f"))
    print_kv("Target", format(target_px, ".7f"), GREEN)

    print(hr())
    print(c("RISK", CYAN, True))
    print_kv("Budget", format(risk_budget, ".2f"))
    print_kv("Sharpe", format(sharpe, ".2f"))
    print_kv("Gate", sg, sg_col)

    print()
    print(hr())
    print(c("DECISION", CYAN, True))
    print_kv("Onboard", str(can_onboard), col)
    print_kv("Action", act, col)
    print_kv("Status", status, col)
    print_kv("Lock", str(lock), col)

    print(hr())
    print(c("LADDER", CYAN, True))
    print_ladder(ladder, venue == "futures")

    if venue == "futures":
        print()
        print(c("TP doctrine:", CYAN, True))
        print(c("Move all stops to zero @ +8%", WHITE))
        print(c("TP1 -> reduce leverage one step", WHITE))
        print(c("TP2 -> reduce leverage again", WHITE))
        print(c("TP3 -> move toward 3x or 1x", WHITE))

    print(hr())
    print()


if __name__ == "__main__":
    main()