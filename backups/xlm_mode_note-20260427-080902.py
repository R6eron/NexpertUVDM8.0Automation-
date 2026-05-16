#!/usr/bin/env python3

CYAN = "\u001B[96m"
YELLOW = "\u001B[93m"
GREEN  = "\u001B[92m"
RED    = "\u001B[91m"
RESET  = "\u001B[0m"

XLM_DEMAND_LO = 0.1585
XLM_DEMAND_HI = 0.1605

XLM_LADDER = [
    (0.1720, "shallow"),
    (0.1700, "shallow"),
    (0.1680, "mid"),
    (0.1605, "deep"),
    (0.1585, "deep"),
]

BTC_LADDER = [
    (70000, "shallow"),
    (68000, "shallow"),
    (66000, "mid"),
    (62000, "deep"),
    (60000, "deep"),
]

XRP_LADDER = [
    (2.20, "shallow"),
    (2.10, "shallow"),
    (2.00, "mid"),
    (1.90, "deep"),
    (1.80, "deep"),
]

def choose_mode(token: str, regime: str) -> str:
    token = token.upper()
    regime = regime.lower()

    if token == "XLMUSDT":
        if regime == "leader":
            return "10x"
        if regime == "normal":
            return "7x"

    if token == "XRPUSDT":
        if regime == "leader":
            return "7x"
        if regime in ("laggard", "normal"):
            return "5x"

    if token == "BTCUSDT":
        if regime == "leader":
            return "5x"
        if regime == "normal":
            return "3x"

    return "3x"

def note_for(token: str, regime: str) -> str:
    token = token.upper()
    regime = regime.lower()

    if token == "XLMUSDT" and regime == "leader":
        return "XLM may be a 10x-capable asset; current second leg tuned to 7x."
    if token == "XLMUSDT" and regime == "normal":
        return "Running XLM at 7x for this leg despite 10x capability."
    if token == "XRPUSDT" and regime == "laggard":
        return "XRP boxed as laggard; capped at 5x to respect tape."
    if token == "BTCUSDT" and regime == "leader":
        return "BTC is structural leader; leverage kept at 5x."
    return ""

def phase_for(token: str, regime: str) -> str:
    token = token.upper()
    regime = regime.lower()
    mode = choose_mode(token, regime)

    if token == "XLMUSDT" and regime == "leader" and mode == "10x":
        return "Phase E (late Phase D / early Phase E, reaccumulation -> markup)"
    if token == "BTCUSDT" and regime in ("leader", "normal"):
        return "Phase E (primary markup leader)."
    if token == "XRPUSDT" and regime == "laggard":
        return "Phase D/E laggard participation; capped risk."
    return ""

def xlm_zone_note(current_price: float) -> str:
    if XLM_DEMAND_LO <= current_price <= XLM_DEMAND_HI:
        return (
            "XLM in 0.1585-0.1605 demand band; expect sharp reaction; "
            "hard invalidation is below zone low, not the line."
        )
    return ""

def xlm_ladder_note() -> str:
    parts = []
    for level, tier in XLM_LADDER:
        parts.append(f"{level:.4f} ({tier})")
    return "XLM bid ladder: " + ", ".join(parts)

def xlm_risk_doctrine() -> str:
    return (
        "Cut: close/hedge if 0.1500 fails with volume. "
        "Bias: CONSTRUCTIVE while 0.16-0.15 holds. "
        "Doctrine: I do not predict; I wait for proof. "
        "I do not chase; I position at levels. "
        "I do not hope; I define invalidation first. "
        "Tape truth: obey. Do not argue."
    )

def xlm_risk_light(current_price: float | None) -> tuple[str, str]:
    if current_price is None:
        return "YELLOW", "XLM CAUTION: price ?; size down."
    if current_price <= 0.1500:
        return "RED", "XLM CUT: <=0.1500, hedge/exit."
    if 0.1500 < current_price < 0.1600:
        return "YELLOW", "XLM CAUTION: 0.15-0.16 band, watch tape."
    return "GREEN", "XLM GO: above band, constructive."

def btc_ladder_note() -> str:
    parts = []
    for level, tier in BTC_LADDER:
        parts.append(f"{level:.0f} ({tier})")
    return "BTC bid ladder: " + ", ".join(parts)

def btc_risk_doctrine() -> str:
    return (
        "Cut: close/hedge BTC if 55k fails with volume. "
        "Bias: CONSTRUCTIVE while 60k-55k holds as structural range. "
        "Doctrine: BTC leads; respect its breakouts and breakdowns first."
    )

def btc_risk_light(current_price: float | None) -> tuple[str, str]:
    if current_price is None:
        return "YELLOW", "BTC CAUTION: price ?; keep risk modest."
    if current_price <= 55000:
        return "RED", "BTC CUT: <=55k, hedge/exit."
    if 55000 < current_price < 60000:
        return "YELLOW", "BTC CAUTION: 55k-60k, tape deciding."
    return "GREEN", "BTC GO: >60k, leader risk-on within size."

def xrp_ladder_note() -> str:
    parts = []
    for level, tier in XRP_LADDER:
        parts.append(f"{level:.2f} ({tier})")
    return "XRP bid ladder: " + ", ".join(parts)

def xrp_risk_doctrine() -> str:
    return (
        "Cut: close/hedge XRP if 1.80 fails with volume. "
        "Bias: CAUTIOUS while 2.00-1.80 holds. "
        "Doctrine: laggard participation only; respect relative weakness."
    )

def xrp_risk_light(current_price: float | None) -> tuple[str, str]:
    if current_price is None:
        return "YELLOW", "XRP CAUTION: price ?; keep risk capped."
    if current_price <= 1.80:
        return "RED", "XRP CUT: <=1.80, hedge/exit."
    if 1.80 < current_price < 2.00:
        return "YELLOW", "XRP CAUTION: 1.80-2.00 band."
    return "GREEN", "XRP GO: >2.00, laggard risk only."

def print_risk_light(label: str, color_name: str, message: str) -> None:
    if color_name == "GREEN":
        color = GREEN
        glyph = "🟢"
    elif color_name == "YELLOW":
        color = YELLOW
        glyph = "🟡"
    else:
        color = RED
        glyph = "🔴"
    print(f"{color}[LIGHT] {glyph} {label}: {message}{RESET}")

if __name__ == "__main__":
    import sys

    token = sys.argv[1]
    regime = sys.argv[2]

    mode = choose_mode(token, regime)
    print(f"{CYAN}[MODE]{RESET} {token} | regime={regime} -> {mode}")

    extra = note_for(token, regime)
    if extra:
        print(f"{YELLOW}[NOTE]{RESET} {extra}")

    phase = phase_for(token, regime)
    if phase:
        print(f"{YELLOW}[PHASE]{RESET} {phase}")

    price_arg = None
    if len(sys.argv) >= 4:
        try:
            price_arg = float(sys.argv[3])
        except ValueError:
            price_arg = None

    if token.upper() == "XLMUSDT":
        print(f"{YELLOW}[LADDER]{RESET} {xlm_ladder_note()}")
        print(f"{YELLOW}[RISK]{RESET} {xlm_risk_doctrine()}")
        color, msg = xlm_risk_light(price_arg)
        print_risk_light("XLM RISK LIGHT", color, msg)
        if price_arg is not None:
            znote = xlm_zone_note(price_arg)
            if znote:
                print(f"{YELLOW}[ZONE]{RESET} {znote}")

    if token.upper() == "BTCUSDT":
        print(f"{YELLOW}[LADDER]{RESET} {btc_ladder_note()}")
        print(f"{YELLOW}[RISK]{RESET} {btc_risk_doctrine()}")
        color, msg = btc_risk_light(price_arg)
        print_risk_light("BTC RISK LIGHT", color, msg)

    if token.upper() == "XRPUSDT":
        print(f"{YELLOW}[LADDER]{RESET} {xrp_ladder_note()}")
        print(f"{YELLOW}[RISK]{RESET} {xrp_risk_doctrine()}")
        color, msg = xrp_risk_light(price_arg)
        print_risk_light("XRP RISK LIGHT", color, msg)
def xrp_risk_light(current_price: float | None) -> tuple[str, str]:
    if current_price is None:
        return "YELLOW", "XRP CAUTION: price ?; keep risk capped."
    if current_price <= 1.80:
        return "RED", "XRP CUT: <=1.80, hedge/exit."
    if 1.80 < current_price < 2.00:
        return "YELLOW", "XRP CAUTION: 1.80-2.00, weak under pivot."
    if 2.00 <= current_price < 2.10:
        return "YELLOW", "XRP WATCH: 2.00-2.10 reclaim zone, wait for proof."
    return "GREEN", "XRP GO (CAPPED): >=2.10, laggard participation only."

def xrp_risk_doctrine() -> str:
    return (
        "Cut: close/hedge XRP if 1.80 fails with volume. "
        "Bias: CAUTIOUS while 2.10-1.80 holds. "
        "Doctrine: laggard participation only; demand proof of reclaim before sizing up."
    )

def xrp_risk_light(current_price: float | None) -> tuple[str, str]:
    if current_price is None:
        return "YELLOW", "XRP CAUTION: price ?; keep risk capped."
    if current_price <= 1.80:
        return "RED", "XRP CUT: <=1.80, hedge/exit."
    if 1.80 < current_price < 2.00:
        return "YELLOW", "XRP CAUTION: 1.80-2.00, weak under pivot."
    if 2.00 <= current_price < 2.10:
        return "YELLOW", "XRP WATCH: 2.00-2.10 reclaim zone, wait for proof."
    return "GREEN", "XRP GO (CAPPED): >=2.10, laggard participation only."

def xrp_risk_doctrine() -> str:
    return (
        "Cut: close/hedge XRP if 1.80 fails with volume. "
        "Bias: CAUTIOUS while 2.10-1.80 holds. "
        "Doctrine: laggard participation only; demand proof of reclaim before sizing up."
    )

def xrp_risk_light(current_price: float | None) -> tuple[str, str]:
    if current_price is None:
        return "YELLOW", "XRP CAUTION: price ?; keep risk capped."
    if current_price <= 1.80:
        return "RED", "XRP CUT: <=1.80, hedge/exit."
    if 1.80 < current_price < 2.00:
        return "YELLOW", "XRP CAUTION: 1.80-2.00, weak under pivot."
    if 2.00 <= current_price < 2.10:
        return "YELLOW", "XRP WATCH: 2.00-2.10 reclaim zone, wait for proof."
    return "GREEN", "XRP GO (CAPPED): >=2.10, laggard participation only."

def btc_risk_doctrine() -> str:
    return (
        "Cut: close/hedge BTC if 55k fails with volume. "
        "Bias: CONSTRUCTIVE while 60k-55k holds as structural range. "
        "Doctrine: BTC leads; respect its breakouts and breakdowns first."
    )

def btc_risk_light(current_price: float | None) -> tuple[str, str]:
    if current_price is None:
        return "YELLOW", "BTC CAUTION: price ?; keep risk modest."
    if current_price <= 55000:
        return "RED", "BTC CUT: <=55k, hedge/exit."
    if 55000 < current_price < 60000:
        return "YELLOW", "BTC CAUTION: 55k-60k, tape deciding."
    if 60000 <= current_price < 62000:
        return "YELLOW", "BTC WATCH: 60k-62k reclaim zone, wait for proof."
    return "GREEN", "BTC GO: >=62k, leader risk-on within defined size."

def xlm_risk_doctrine() -> str:
    return (
        "Cut: close/hedge XLM if 0.1500 fails with volume. "
        "Bias: CONSTRUCTIVE while 0.16-0.15 holds. "
        "Doctrine: I do not predict; I wait for proof. "
        "I do not chase; I position at levels. "
        "I do not hope; I define invalidation first. "
        "Tape truth: obey. Do not argue."
    )

def xlm_risk_light(current_price: float | None) -> tuple[str, str]:
    if current_price is None:
        return "YELLOW", "XLM CAUTION: price ?; size down."
    if current_price <= 0.1500:
        return "RED", "XLM CUT: <=0.1500, hedge/exit."
    if 0.1500 < current_price < 0.1585:
        return "YELLOW", "XLM CAUTION: 0.1500-0.1585, weak into demand."
    if 0.1585 <= current_price <= 0.1605:
        return "YELLOW", "XLM WATCH: 0.1585-0.1605 demand band, react not predict."
    return "GREEN", "XLM GO: >0.1605, constructive while demand band holds as support."

RISK_COLOR_MAP = {
    "RED": 0,
    "YELLOW": 1,
    "GREEN": 2,
}

RISK_STATE_MAP = {
    "CUT": 0,
    "CAUTION": 1,
    "WATCH": 2,
    "GO_CAPPED": 3,
    "GO_FULL": 4,
}

def risk_label_from_light(color_name: str, message: str) -> tuple[int, int]:
    color_id = RISK_COLOR_MAP.get(color_name, 1)

    msg = message.upper()

    if "CUT:" in msg:
        state_id = RISK_STATE_MAP["CUT"]
    elif "WATCH:" in msg:
        state_id = RISK_STATE_MAP["WATCH"]
    elif "GO (CAPPED)" in msg:
        state_id = RISK_STATE_MAP["GO_CAPPED"]
    elif "GO:" in msg:
        state_id = RISK_STATE_MAP["GO_FULL"]
    elif "CAUTION:" in msg:
        state_id = RISK_STATE_MAP["CAUTION"]
    else:
        state_id = RISK_STATE_MAP["CAUTION"]

    return color_id, state_id

import csv
from datetime import datetime

def log_risk_sample(
    token: str,
    regime: str,
    price: float | None,
    color: str,
    message: str,
    leverage: float | None,
    position_size: float | None,
    csv_path: str = "risk_log.csv",
) -> None:
    color_id, state_id = risk_label_from_light(color, message)
    ts = datetime.utcnow().isoformat()

    header = [
        "timestamp",
        "token",
        "regime",
        "price",
        "color",
        "message",
        "color_id",
        "state_id",
        "leverage",
        "position_size",
    ]

    row = [
        ts,
        token,
        regime,
        price if price is not None else "",
        color,
        message,
        color_id,
        state_id,
        leverage if leverage is not None else "",
        position_size if position_size is not None else "",
    ]

    try:
        with open(csv_path, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(row)
    except FileExistsError:
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)
