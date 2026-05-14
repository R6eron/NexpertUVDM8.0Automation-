RESET = "\u001B[0m"
BOLD = "\u001B[1m"
CYAN = "\u001B[96m"
GREEN = "\u001B[92m"
YELLOW = "\u001B[93m"
RED = "\u001B[91m"
MAGENTA = "\u001B[95m"

PERCENT_EQUIVALENT = 0.05

def c(text, colour, bold=False):
    if bold:
        return BOLD + colour + str(text) + RESET
    return colour + str(text) + RESET

def stop_eq(high):
    return round(high * (1 - PERCENT_EQUIVALENT), 7)

def action(px, stop):
    if px > stop:
        return "HOLD"
    if px == stop:
        return "SET_STOP"
    return "EXIT_MKT"

def acol(act):
    if act == "HOLD":
        return GREEN
    if act == "SET_STOP":
        return YELLOW
    return RED

assets = {
    "XLM_FUTURES":   {"px": 0.1950000, "high": 0.2000000},
    "XLM_SPOT":      {"px": 0.1850000, "high": 0.1900000},
    "FLR_SPOT":      {"px": 0.0086270, "high": 0.0089500},
    "SGB_SPOT":      {"px": 0.0016870, "high": 0.0018000},
    "NEXO_SPOT":     {"px": 0.9018000, "high": 1.1000000},
    "XRPAYNET_XUMM": {"px": 0.0014500, "high": 0.0016000},
    "PAXG_SPOT":     {"px": 4701.2900000, "high": 4711.6100000},
}

print(c("#UVDM Wingman TM", CYAN, True))
print(c("Digital Immortal number 001", CYAN))
print()

print(c("LIVE INPUTS", CYAN, True))
print("FLR_SPOT  : 0.0086270")
print("SGB_SPOT  : 0.0016870")
print("NEXO_SPOT : 0.9018000")
print("PAXG_SPOT : 4701.2900000")
print()

print(c("MULTI-ASSET STATUS", CYAN, True))
for name in assets:
    a = assets[name]
    s = stop_eq(a["high"])
    act = action(a["px"], s)
    line = name
    line += " | px=" + format(a["px"], ".7f")
    line += " | high=" + format(a["high"], ".7f")
    line += " | stop=" + format(s, ".7f")
    line += " | action=" + act
    print(c(line, acol(act), act != "HOLD"))
print()

print(c("DOCTRINE", MAGENTA, True))
print(c("Use current local swing highs, not stale macro highs.", MAGENTA))
print(c("Process over outcome. No revenge trading.", MAGENTA, True))
print(c("Obey. Do not argue.", MAGENTA, True))

def _uvdm_patch_assets_and_render():
    for name in assets:
        a = assets[name]
        if "onboard_limit" not in a:
            a["onboard_limit"] = round(a["px"] * 0.97, 7)
        if "ladder" not in a:
            a["ladder"] = [
                round(a["px"] * 0.98, 7),
                round(a["px"] * 0.95, 7),
                round(a["px"] * 0.92, 7),
            ]
        if "tp_rung" not in a:
            a["tp_rung"] = 1
        if "tp" not in a:
            a["tp"] = round(a["px"] * 1.06, 7)
        if "armed" not in a:
            a["armed"] = a["px"] <= a["onboard_limit"]

    print()
    print(c("PATCHED ASSET LADDER STATUS", CYAN, True))
    for name in assets:
        a = assets[name]
        s = stop_eq(a["high"])
        act = action(a["px"], s)
        line = name
        line += " | px=" + format(a["px"], ".7f")
        line += " | high=" + format(a["high"], ".7f")
        line += " | stop=" + format(s, ".7f")
        line += " | onboard=" + format(a["onboard_limit"], ".7f")
        line += " | ladder=" + str(a["ladder"])
        line += " | rung=" + str(a["tp_rung"])
        line += " | tp=" + format(a["tp"], ".7f")
        line += " | armed=" + str(a["armed"])
        line += " | action=" + act
        print(c(line, acol(act), act != "HOLD"))

_uvdm_patch_assets_and_render()

def _uvdm_one_page_focus():
    wanted = ["BTC_SPOT", "BTC_FUTURES", "XLM_FUTURES", "XLM_SPOT", "FLR_SPOT", "SGB_SPOT", "XRP_SPOT", "XRPAYNET_XUMM"]
    print()
    print(c("ONE PAGE FOCUS", CYAN, True))
    for name in wanted:
        if name not in assets:
            continue
        a = assets[name]
        if "onboard_limit" not in a:
            a["onboard_limit"] = round(a["px"] * 0.97, 7)
        if "ladder" not in a:
            a["ladder"] = [
                round(a["px"] * 0.98, 7),
                round(a["px"] * 0.95, 7),
                round(a["px"] * 0.92, 7),
            ]
        if "tp_rung" not in a:
            a["tp_rung"] = 1
        if "tp" not in a:
            a["tp"] = round(a["px"] * 1.06, 7)
        if "armed" not in a:
            a["armed"] = a["px"] <= a["onboard_limit"]

        s = stop_eq(a["high"])
        act = action(a["px"], s)

        line = name
        line += " | px=" + format(a["px"], ".7f")
        line += " | high=" + format(a["high"], ".7f")
        line += " | stop=" + format(s, ".7f")
        line += " | onboard=" + format(a["onboard_limit"], ".7f")
        line += " | rung=" + str(a["tp_rung"])
        line += " | tp=" + format(a["tp"], ".7f")
        line += " | action=" + act
        print(c(line, acol(act), act != "HOLD"))

_uvdm_one_page_focus()

assets["BTC_SPOT"] = {"px": 103000.0000000, "high": 106000.0000000}

assets["BTC_SPOT"] = {"px": 103000.0000000, "high": 106000.0000000}
_uvdm_one_page_focus()

def _uvdm_reclaim_level(a):
    return round(a["high"] * 0.975, 7)

def _uvdm_lock_state(a):
    s = stop_eq(a["high"])
    act = action(a["px"], s)
    reclaim = _uvdm_reclaim_level(a)

    if "locked" not in a:
        a["locked"] = False
    if "lock_reason" not in a:
        a["lock_reason"] = "NONE"

    if act == "EXIT_MKT":
        a["locked"] = True
        a["lock_reason"] = "EXIT_MKT"

    if a["locked"] and a["px"] >= reclaim:
        a["locked"] = False
        a["lock_reason"] = "RECLAIMED"

    return reclaim, act

def _uvdm_can_onboard(a):
    reclaim, act = _uvdm_lock_state(a)
    return (not a["locked"]), reclaim, act

def _uvdm_one_page_focus_locked():
    wanted = [
        "BTC_SPOT",
        "BTC_FUTURES",
        "XLM_FUTURES",
        "XLM_SPOT",
        "FLR_SPOT",
        "SGB_SPOT",
        "XRP_SPOT",
        "XRPAYNET_XUMM",
    ]

    print()
    print(c("ONE PAGE FOCUS LOCKED", CYAN, True))

    for name in wanted:
        if name not in assets:
            continue

        a = assets[name]

        if "onboard_limit" not in a:
            a["onboard_limit"] = round(a["px"] * 0.97, 7)
        if "ladder" not in a:
            a["ladder"] = [
                round(a["px"] * 0.98, 7),
                round(a["px"] * 0.95, 7),
                round(a["px"] * 0.92, 7),
            ]
        if "tp_rung" not in a:
            a["tp_rung"] = 1
        if "tp" not in a:
            a["tp"] = round(a["px"] * 1.06, 7)
        if "armed" not in a:
            a["armed"] = a["px"] <= a["onboard_limit"]

        can_onboard, reclaim, act = _uvdm_can_onboard(a)
        s = stop_eq(a["high"])

        line = name
        line += " | px=" + format(a["px"], ".7f")
        line += " | high=" + format(a["high"], ".7f")
        line += " | stop=" + format(s, ".7f")
        line += " | onboard=" + format(a["onboard_limit"], ".7f")
        line += " | reclaim=" + format(reclaim, ".7f")
        line += " | rung=" + str(a["tp_rung"])
        line += " | tp=" + format(a["tp"], ".7f")
        line += " | lock=" + str(a["locked"])
        line += " | allow_onboard=" + str(can_onboard)
        line += " | action=" + act

        print(c(line, acol(act), act != "HOLD"))

_uvdm_one_page_focus_locked()

assets["SGB_SPOT"]["px"] = 0.0017710

assets["SGB_SPOT"]["px"] = 0.0017710

assets["SGB_SPOT"]["px"] = 0.0017710

def _uvdm_set_px(name, px):
    if name not in assets:
        print("NO_ASSET", name)
        return False
    assets[name]["px"] = float(px)
    print("PX_SET", name, format(assets[name]["px"], ".7f"))
    return True

def _uvdm_one_page_focus_locked_spaced():
    wanted = [
        "BTC_SPOT",
        "BTC_FUTURES",
        "XLM_FUTURES",
        "XLM_SPOT",
        "FLR_SPOT",
        "SGB_SPOT",
        "XRP_SPOT",
        "XRPAYNET_XUMM",
    ]

    print()
    print(c("#UVDM Wingman TM at the top Digital Immortal number 001", CYAN, True))
    print()
    print(c("ONE PAGE FOCUS LOCKED SPACED", CYAN, True))
    print()

    for name in wanted:
        if name not in assets:
            continue

        a = assets[name]

        if "onboard_limit" not in a:
            a["onboard_limit"] = round(a["px"] * 0.97, 7)
        if "ladder" not in a:
            a["ladder"] = [
                round(a["px"] * 0.98, 7),
                round(a["px"] * 0.95, 7),
                round(a["px"] * 0.92, 7),
            ]
        if "tp_rung" not in a:
            a["tp_rung"] = 1
        if "tp" not in a:
            a["tp"] = round(a["px"] * 1.06, 7)
        if "armed" not in a:
            a["armed"] = a["px"] <= a["onboard_limit"]

        can_onboard, reclaim, act = _uvdm_can_onboard(a)
        s = stop_eq(a["high"])

        line = name
        line += " | px=" + format(a["px"], ".7f")
        line += " | high=" + format(a["high"], ".7f")
        line += " | stop=" + format(s, ".7f")
        line += " | onboard=" + format(a["onboard_limit"], ".7f")
        line += " | reclaim=" + format(reclaim, ".7f")
        line += " | rung=" + str(a["tp_rung"])
        line += " | tp=" + format(a["tp"], ".7f")
        line += " | lock=" + str(a["locked"])
        line += " | allow_onboard=" + str(can_onboard)
        line += " | action=" + act

        print(c(line, acol(act), act != "HOLD"))
        print()

_uvdm_one_page_focus_locked_spaced()

def _uvdm_phase_header():
    print()
    print(c("#UVDM Wingman TM at the top Digital Immortal number 001", CYAN, True))
    print()
    print(c("WYCKOFF PHASE / TRANSITION", CYAN, True))
    print(c("DIRECTION OF LEAST RESISTANCE", YELLOW, True))
    print()

def _uvdm_one_page_focus_locked_spaced():
    wanted = [
        "BTC_SPOT",
        "BTC_FUTURES",
        "XLM_FUTURES",
        "XLM_SPOT",
        "FLR_SPOT",
        "SGB_SPOT",
        "XRP_SPOT",
        "XRPAYNET_XUMM",
    ]

    _uvdm_phase_header()

    for name in wanted:
        if name not in assets:
            continue

        a = assets[name]

        if "onboard_limit" not in a:
            a["onboard_limit"] = round(a["px"] * 0.97, 7)
        if "ladder" not in a:
            a["ladder"] = [
                round(a["px"] * 0.98, 7),
                round(a["px"] * 0.95, 7),
                round(a["px"] * 0.92, 7),
            ]
        if "tp_rung" not in a:
            a["tp_rung"] = 1
        if "tp" not in a:
            a["tp"] = round(a["px"] * 1.06, 7)
        if "armed" not in a:
            a["armed"] = a["px"] <= a["onboard_limit"]

        can_onboard, reclaim, act = _uvdm_can_onboard(a)
        s = stop_eq(a["high"])

        line = name
        line += " | px=" + format(a["px"], ".7f")
        line += " | high=" + format(a["high"], ".7f")
        line += " | stop=" + format(s, ".7f")
        line += " | onboard=" + format(a["onboard_limit"], ".7f")
        line += " | reclaim=" + format(reclaim, ".7f")
        line += " | rung=" + str(a["tp_rung"])
        line += " | tp=" + format(a["tp"], ".7f")
        line += " | lock=" + str(a["locked"])
        line += " | allow_onboard=" + str(can_onboard)
        line += " | action=" + act

        print(c(line, acol(act), act != "HOLD"))
        print()

_uvdm_one_page_focus_locked_spaced()

def _uvdm_market_state_summary():
    wanted = [
        "BTC_SPOT",
        "BTC_FUTURES",
        "XLM_FUTURES",
        "XLM_SPOT",
        "FLR_SPOT",
        "SGB_SPOT",
        "XRP_SPOT",
        "XRPAYNET_XUMM",
    ]

    total = 0
    hold_count = 0
    exit_count = 0
    locked_count = 0
    clear_count = 0

    for name in wanted:
        if name not in assets:
            continue

        a = assets[name]
        can_onboard, reclaim, act = _uvdm_can_onboard(a)

        total += 1
        if act == "HOLD":
            hold_count += 1
        if act == "EXIT_MKT":
            exit_count += 1
        if a.get("locked", False):
            locked_count += 1
        if a["px"] >= reclaim:
            clear_count += 1

    if locked_count == 0 and hold_count >= 4:
        lor = "UP BIAS"
        phase = "RECLAIMED / CONSTRUCTIVE"
        col = GREEN
    elif locked_count <= 2 and hold_count >= 3:
        lor = "MIXED-UP"
        phase = "TRANSITION / SELECTIVE"
        col = YELLOW
    else:
        lor = "DOWN / DEFENSIVE"
        phase = "MARKDOWN RISK"
        col = RED

    print()
    print(c("#UVDM Wingman TM at the top Digital Immortal number 001", CYAN, True))
    print()
    print(c("STATE: " + str(hold_count) + " HOLD / " + str(exit_count) + " EXIT_LOCK / " + str(total) + " TRACKED", CYAN, True))
    print(c("RECLAIM STATUS: " + str(clear_count) + " CLEAR / " + str(locked_count) + " LOCKED", CYAN, True))
    print(c("PHASE: " + phase, col, True))
    print(c("LOR: " + lor, col, True))
    print()

def _uvdm_one_page_focus_locked_spaced():
    wanted = [
        "BTC_SPOT",
        "BTC_FUTURES",
        "XLM_FUTURES",
        "XLM_SPOT",
        "FLR_SPOT",
        "SGB_SPOT",
        "XRP_SPOT",
        "XRPAYNET_XUMM",
    ]

    _uvdm_market_state_summary()

    for name in wanted:
        if name not in assets:
            continue

        a = assets[name]

        if "onboard_limit" not in a:
            a["onboard_limit"] = round(a["px"] * 0.97, 7)
        if "ladder" not in a:
            a["ladder"] = [
                round(a["px"] * 0.98, 7),
                round(a["px"] * 0.95, 7),
                round(a["px"] * 0.92, 7),
            ]
        if "tp_rung" not in a:
            a["tp_rung"] = 1
        if "tp" not in a:
            a["tp"] = round(a["px"] * 1.06, 7)
        if "armed" not in a:
            a["armed"] = a["px"] <= a["onboard_limit"]

        can_onboard, reclaim, act = _uvdm_can_onboard(a)
        s = stop_eq(a["high"])

        line = name
        line += " | px=" + format(a["px"], ".7f")
        line += " | high=" + format(a["high"], ".7f")
        line += " | stop=" + format(s, ".7f")
        line += " | onboard=" + format(a["onboard_limit"], ".7f")
        line += " | reclaim=" + format(reclaim, ".7f")
        line += " | rung=" + str(a["tp_rung"])
        line += " | tp=" + format(a["tp"], ".7f")
        line += " | lock=" + str(a["locked"])
        line += " | allow_onboard=" + str(can_onboard)
        line += " | action=" + act

        print(c(line, acol(act), act != "HOLD"))
        print()

_uvdm_one_page_focus_locked_spaced()

def _uvdm_deploy_qa():
    print()
    print(c("#UVDM Wingman TM at the top Digital Immortal number 001", CYAN, True))
    print()

    deploy_in = input("Q: Deploy amount? ").strip()
    portfolio_in = input("Q: Portfolio size? ").strip()
    asset_in = input("Q: Asset? ").strip()
    px_in = input("Q: Current price? ").strip()

    asset = _uvdm_resolve_asset_name(asset_in)

    print()

    if asset not in assets:
        print(c("A: asset = " + asset + " | status = UNKNOWN_ASSET", RED, True))
        print()
        return

    try:
        deploy_amt = float(deploy_in)
        portfolio_amt = float(portfolio_in)
        px = float(px_in)
    except ValueError:
        print(c("A: invalid numeric input", RED, True))
        print()
        return

    if px <= 0:
        print(c("A: current price must be > 0", RED, True))
        print()
        return

    assets[asset]["px"] = px
    a = assets[asset]

    can_onboard, reclaim, act = _uvdm_can_onboard(a)
    s = stop_eq(a["high"])

    units = deploy_amt / px
    deploy_pct = 0.0
    if portfolio_amt > 0:
        deploy_pct = (deploy_amt / portfolio_amt) * 100.0

    if can_onboard and act == "HOLD":
        status = "ONBOARD_OK"
        col = GREEN
    elif (not can_onboard) or act == "EXIT_MKT":
        status = "BLOCKED"
        col = RED
    else:
        status = "WAIT"
        col = YELLOW

    print(c("A: deploy = " + format(deploy_amt, ".2f"), CYAN, True))
    print(c("A: portfolio = " + format(portfolio_amt, ".2f"), CYAN, True))
    print(c("A: asset = " + asset, CYAN, True))
    print(c("A: px = " + format(a["px"], ".7f"), col, True))
    print(c("A: units = " + format(units, ".7f"), col))
    print(c("A: deploy_pct = " + format(deploy_pct, ".2f") + "%", col))
    print(c("A: stop = " + format(s, ".7f"), col))
    print(c("A: reclaim = " + format(reclaim, ".7f"), col))
    print(c("A: lock = " + str(a["locked"]), col))
    print(c("A: allow_onboard = " + str(can_onboard), col, True))
    print(c("A: action = " + act, col, True))
    print(c("A: status = " + status, col, True))
    print()


def _uvdm_resolve_asset_name(name):
    raw = str(name).strip().upper()
    alias_map = {
        "BTC": "BTC_SPOT",
        "XLM": "XLM_SPOT",
        "FLR": "FLR_SPOT",
        "SGB": "SGB_SPOT",
        "XRP": "XRPAYNET_XUMM",
        "BTC_SPOT": "BTC_SPOT",
        "XLM_SPOT": "XLM_SPOT",
        "FLR_SPOT": "FLR_SPOT",
        "SGB_SPOT": "SGB_SPOT",
        "XRPAYNET_XUMM": "XRPAYNET_XUMM",
    }
    return alias_map.get(raw, raw)

def _uvdm_resolve_market(asset_name, venue_type):
    asset = str(asset_name).strip().upper()
    venue = str(venue_type).strip().lower()

    if asset == "BTC":
        return "BTC_SPOT"
    if asset == "FLR":
        return "FLR_SPOT"
    if asset == "SGB":
        return "SGB_SPOT"
    if asset == "XRP":
        return "XRPAYNET_XUMM"
    if asset == "XLM":
        if venue.startswith("f"):
            return "XLM_FUTURES"
        return "XLM_SPOT"

    return _uvdm_resolve_asset_name(asset)

def _uvdm_deploy_qa_v2():
    print()
    print(c("#UVDM Wingman TM at the top Digital Immortal number 001", CYAN, True))
    print()

    deploy_in = input("Q: Deploy amount? ").strip()
    portfolio_in = input("Q: Portfolio size? ").strip()
    asset_in = input("Q: Asset? ").strip()
    venue_in = input("Q: Spot or futures? ").strip()
    px_in = input("Q: Current price? ").strip()

    market = _uvdm_resolve_market(asset_in, venue_in)

    lev_in = ""
    leverage = 1.0
    if str(venue_in).strip().lower().startswith("f"):
        lev_in = input("Q: Leverage? max 10x, recommended 7x & under: ").strip()

    print()

    if market not in assets:
        print(c("A: market = " + market + " | status = UNKNOWN_MARKET", RED, True))
        print()
        return

    try:
        deploy_amt = float(deploy_in)
        portfolio_amt = float(portfolio_in)
        px = float(px_in)
        if lev_in != "":
            leverage = float(lev_in)
    except ValueError:
        print(c("A: invalid numeric input", RED, True))
        print()
        return

    if px <= 0:
        print(c("A: current price must be > 0", RED, True))
        print()
        return

    if leverage < 1:
        leverage = 1.0
    if leverage > 10:
        leverage = 10.0

    assets[market]["px"] = px
    a = assets[market]

    can_onboard, reclaim, act = _uvdm_can_onboard(a)
    s = stop_eq(a["high"])

    notional = deploy_amt * leverage
    units = notional / px
    deploy_pct = 0.0
    if portfolio_amt > 0:
        deploy_pct = (deploy_amt / portfolio_amt) * 100.0

    if can_onboard and act == "HOLD":
        status = "ONBOARD_OK"
        col = GREEN
    elif (not can_onboard) or act == "EXIT_MKT":
        status = "BLOCKED"
        col = RED
    else:
        status = "WAIT"
        col = YELLOW

    print(c("A: deploy = " + format(deploy_amt, ".2f"), CYAN, True))
    print(c("A: portfolio = " + format(portfolio_amt, ".2f"), CYAN, True))
    print(c("A: market = " + market, CYAN, True))
    print(c("A: px = " + format(a["px"], ".7f"), col, True))
    print(c("A: venue = " + str(venue_in).strip().lower(), col))
    print(c("A: leverage = " + format(leverage, ".2f") + "x", col))
    print(c("A: recommended = 7.00x and under", YELLOW, True))
    print(c("A: notional = " + format(notional, ".2f"), col))
    print(c("A: units = " + format(units, ".7f"), col))
    print(c("A: deploy_pct = " + format(deploy_pct, ".2f") + "%", col))
    print(c("A: stop = " + format(s, ".7f"), col))
    print(c("A: reclaim = " + format(reclaim, ".7f"), col))
    print(c("A: lock = " + str(a["locked"]), col))
    print(c("A: allow_onboard = " + str(can_onboard), col, True))
    print(c("A: action = " + act, col, True))
    print(c("A: status = " + status, col, True))
    print()

import json
import urllib.request
import urllib.parse
import ssl

def _uvdm_resolve_market(asset_name, venue_type):
    asset = str(asset_name).strip().upper()
    venue = str(venue_type).strip().lower()

    if asset == "BTC":
        return "BTC_SPOT"
    if asset == "FLR":
        return "FLR_SPOT"
    if asset == "SGB":
        return "SGB_SPOT"
    if asset == "XRP":
        return "XRPAYNET_XUMM"
    if asset == "XLM":
        if venue.startswith("f"):
            return "XLM_FUTURES"
        return "XLM_SPOT"

    return _uvdm_resolve_asset_name(asset)

def _uvdm_symbol_to_feed(asset_name):
    a = str(asset_name).strip().upper()
    mapping = {
        "BTC": "BTC/USD",
        "FLR": "FLR/USD",
        "SGB": "SGB/USD",
        "XRP": "XRP/USD",
        "XLM": "XLM/USD",
    }
    return mapping.get(a, a + "/USD")

def _uvdm_fetch_json(url, timeout=10):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "UVDM-Wingman/1.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        raw = r.read().decode("utf-8", errors="ignore")
        return json.loads(raw)

def _uvdm_extract_numeric_price(obj):
    if isinstance(obj, (int, float)):
        return float(obj)

    if isinstance(obj, str):
        try:
            return float(obj)
        except Exception:
            return None

    if isinstance(obj, list):
        for item in obj:
            v = _uvdm_extract_numeric_price(item)
            if v is not None and v > 0:
                return v
        return None

    if isinstance(obj, dict):
        preferred_keys = [
            "price", "value", "median", "latest", "close",
            "usd", "rate", "feed_value", "feedValue"
        ]
        for k in preferred_keys:
            if k in obj:
                v = _uvdm_extract_numeric_price(obj[k])
                if v is not None and v > 0:
                    return v

        for _, val in obj.items():
            v = _uvdm_extract_numeric_price(val)
            if v is not None and v > 0:
                return v

    return None

def _uvdm_get_live_ftso_px(asset_name):
    feed = _uvdm_symbol_to_feed(asset_name)
    enc = urllib.parse.quote(feed, safe="")
    urls = [
        "https://ftso-v2-data-provider.flare.network/feed-values/" + enc,
        "https://api.flareforge.io/api/v1/oracle-lab/feeds",
    ]

    last_err = None

    for url in urls:
        try:
            data = _uvdm_fetch_json(url, timeout=10)

            if "flareforge" in url:
                if isinstance(data, dict):
                    rows = None
                    for key in ["data", "feeds", "results", "items"]:
                        if key in data and isinstance(data[key], list):
                            rows = data[key]
                            break
                    if rows is None and isinstance(data, list):
                        rows = data
                elif isinstance(data, list):
                    rows = data
                else:
                    rows = []

                target = str(feed).upper()
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    name = str(
                        row.get("feed") or
                        row.get("name") or
                        row.get("symbol") or
                        row.get("pair") or
                        ""
                    ).upper()
                    if target == name or target.replace("/", "") == name.replace("/", ""):
                        px = _uvdm_extract_numeric_price(row)
                        if px is not None and px > 0:
                            return px, "FTSO_LIVE"
            else:
                px = _uvdm_extract_numeric_price(data)
                if px is not None and px > 0:
                    return px, "FTSO_LIVE"

        except Exception as e:
            last_err = e

    return None, ("FTSO_UNAVAILABLE: " + str(last_err) if last_err else "FTSO_UNAVAILABLE")

def _uvdm_stop_from_entry(entry_ref, risk_pct):
    return entry_ref * (1.0 - risk_pct)

def _uvdm_reclaim_from_entry(entry_ref, tp_pct):
    return entry_ref * (1.0 + tp_pct)

def _uvdm_futures_onboard(entry_ref, live_px, stop_px, reclaim_px):
    if live_px <= stop_px:
        return False, "EXIT_MKT", True, "BREACHED_STOP"
    if live_px >= reclaim_px:
        return False, "EXIT_MKT", True, "AT_OR_ABOVE_RECLAIM"
    if stop_px < live_px < reclaim_px:
        return True, "HOLD", False, "ONBOARD_OK"
    return False, "WAIT", False, "WAIT"

def _uvdm_spot_onboard(entry_ref, live_px, stop_px, reclaim_px):
    if live_px <= stop_px:
        return False, "EXIT_MKT", True, "BREACHED_STOP"
    if stop_px < live_px < reclaim_px:
        return True, "HOLD", False, "ONBOARD_OK"
    if live_px >= reclaim_px:
        return False, "EXIT_MKT", True, "AT_OR_ABOVE_RECLAIM"
    return False, "WAIT", False, "WAIT"

def _uvdm_deploy_qa_v3():
    print()
    print(c("#UVDM Wingman TM at the top Digital Immortal number 001", CYAN, True))
    print()

    deploy_in = input("Q: Deploy amount? ").strip()
    portfolio_in = input("Q: Portfolio size? ").strip()
    asset_in = input("Q: Asset? ").strip()
    venue_in = input("Q: Spot or futures? ").strip()
    use_live_in = input("Q: Use live FTSO/offchain price first? (y/n) ").strip()

    lev_in = ""
    leverage = 1.0
    if str(venue_in).strip().lower().startswith("f"):
        lev_in = input("Q: Leverage? max 10x, recommended 7x & under: ").strip()

    px_in = ""
    live_source = "MANUAL"
    px = None

    if use_live_in.lower().startswith("y"):
        px, live_source = _uvdm_get_live_ftso_px(asset_in)

    if px is None:
        px_in = input("Q: Current price? ").strip()

    risk_in = input("Q: Stop risk % from entry? default 5: ").strip()
    tp_in = input("Q: Reclaim % above entry? default 8: ").strip()

    print()

    market = _uvdm_resolve_market(asset_in, venue_in)

    if market not in assets:
        print(c("A: market = " + market + " | status = UNKNOWN_MARKET", RED, True))
        print()
        return

    try:
        deploy_amt = float(deploy_in)
        portfolio_amt = float(portfolio_in)
        if px is 
cat >> wingman_cockpit.py <<'PY'
 None:
            px = float(px_in)
        if lev_in != "":
            leverage = float(lev_in)
        risk_pct = float(risk_in) / 100.0 if risk_in != "" else 0.05
        tp_pct = float(tp_in) / 100.0 if tp_in != "" else 0.08
    except ValueError:
        print(c("A: invalid numeric input", RED, True))
        print()
        return

    if px <= 0:
        print(c("A: current price must be > 0", RED, True))
        print()
        return

    if leverage < 1:
        leverage = 1.0
    if leverage > 10:
        leverage = 10.0

    if risk_pct <= 0:
        risk_pct = 0.05
    if tp_pct <= 0:
        tp_pct = 0.08

    assets[market]["px"] = px
    a = assets[market]

    entry_ref = float(px)
    stop_px = _uvdm_stop_from_entry(entry_ref, risk_pct)
    reclaim_px = _uvdm_reclaim_from_entry(entry_ref, tp_pct)

    venue_l = str(venue_in).strip().lower()
    if venue_l.startswith("f"):
        can_onboard, act, lock, status = _uvdm_futures_onboard(entry_ref, px, stop_px, reclaim_px)
    else:
        can_onboard, act, lock, status = _uvdm_spot_onboard(entry_ref, px, stop_px, reclaim_px)

    notional = deploy_amt * leverage
    units = notional / px

    deploy_pct = 0.0
    if portfolio_amt > 0:
        deploy_pct = (deploy_amt / portfolio_amt) * 100.0

    a["locked"] = lock

    col = GREEN if status == "ONBOARD_OK" else RED if "BREACHED" in status or "ABOVE" in status else YELLOW

    print(c("A: deploy = " + format(deploy_amt, ".2f"), CYAN, True))
    print(c("A: portfolio = " + format(portfolio_amt, ".2f"), CYAN, True))
    print(c("A: market = " + market, CYAN, True))
    print(c("A: px = " + format(px, ".7f"), col, True))
    print(c("A: price_source = " + str(live_source), col))
    print(c("A: venue = " + venue_l, col))
    print(c("A: leverage = " + format(leverage, ".2f") + "x", col))
    print(c("A: recommended = 7.00x and under", YELLOW, True))
    print(c("A: notional = " + format(notional, ".2f"), col))
    print(c("A: units = " + format(units, ".7f"), col))
    print(c("A: deploy_pct = " + format(deploy_pct, ".2f") + "%", col))
    print(c("A: entry_ref = " + format(entry_ref, ".7f"), col))
    print(c("A: stop_risk_pct = " + format(risk_pct * 100.0, ".2f") + "%", col))
    print(c("A: reclaim_pct = " + format(tp_pct * 100.0, ".2f") + "%", col))
    print(c("A: stop = " + format(stop_px, ".7f"), col))
    print(c("A: reclaim = " + format(reclaim_px, ".7f"), col))
    print(c("A: lock = " + str(lock), col))
    print(c("A: allow_onboard = " + str(can_onboard), col, True))
    print(c("A: action = " + act, col, True))
    print(c("A: status = " + status, col, True))
    print()

