#!/usr/bin/env python3
import sys
from typing import Optional, Tuple

CYAN = "\u001B[96m"
YELLOW = "\u001B[93m"
GREEN = "\u001B[92m"
RED = "\u001B[91m"
BOLD = "\u001B[1m"
RESET = "\u001B[0m"

PROJECT = "[SHELL:~/NexpertUVDM-Automation]"

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

FLR_LADDER = [
    (0.0088, "shallow"),
    (0.0084, "shallow"),
    (0.0080, "mid"),
    (0.0076, "deep"),
    (0.0072, "cut"),
]

SGB_LADDER = [
    (0.00078, "shallow"),
    (0.00074, "shallow"),
    (0.00070, "mid"),
    (0.00068, "deep"),
    (0.00065, "deep"),
]

def choose_mode(token: str, regime: str) -> str:
    token = token.upper()
    regime = regime.lower()

    if token == "XLMUSDT" and regime == "leader":
        return "10x"
    if token == "BTCUSDT" and regime in ("leader", "normal"):
        return "5x"
    if token == "XRPUSDT" and regime == "laggard":
        return "5x"
    if token in ("FLRUSDT", "SGBUSDT") and regime == "lamboed":
        return "3x"
    return "spot"

def mode_note(token: str, regime: str, mode: str) -> str:
    token = token.upper()
    regime = regime.lower()
    mode = mode.lower()

    if token == "XLMUSDT" and regime == "leader" and mode == "10x":
        return "XLM may be a 10x-capable asset; current second leg tuned to 7x."
    if token == "BTCUSDT" and regime in ("leader", "normal"):
        return "BTC remains the primary market leader; keep structure-first risk."
    if token == "XRPUSDT" and regime == "laggard" and mode == "5x":
        return "XRP boxed as laggard; capped at 5x to respect tape."
    if token == "FLRUSDT" and regime == "lamboed" and mode == "3x":
        return "FLR in lamboed basket; upside framed at 3x sizing, built from surplus."
    if token == "SGBUSDT" and regime == "lamboed" and mode == "3x":
        return "SGB in lamboed basket; 3x tail, starter size until structure proves."
    return "Default spot posture; no aggressive leverage bias."

def phase_for(token: str, regime: str, mode: str) -> str:
    token = token.upper()
    regime = regime.lower()
    mode = mode.lower()

    if token == "XLMUSDT" and regime == "leader" and mode == "10x":
        return "Phase E (late Phase D / early Phase E, reaccumulation -> markup)."
    if token == "BTCUSDT" and regime in ("leader", "normal"):
        return "Phase E (primary markup leader)."
    if token == "XRPUSDT" and regime == "laggard":
        return "Phase D/E laggard participation; capped risk."
    if token == "FLRUSDT" and regime == "lamboed" and mode == "3x":
        return "Phase E basket rotation: FLR rides markup via surplus from leaders."
    if token == "SGBUSDT" and regime == "lamboed" and mode == "3x":
        return "Phase E basket rotation: SGB as high-beta tail in lamboed stack."
    return "Neutral phase; wait for clearer structure."

def format_ladder(name: str, ladder) -> str:
    parts = []
    for price, depth in ladder:
        if isinstance(price, int):
            parts.append(f"{price} ({depth})")
        else:
            fmt = f"{price:.4f}" if price >= 0.001 else f"{price:.6f}"
            parts.append(f"{fmt} ({depth})")
    return f"{name} bid ladder: " + ", ".join(parts)

def xlm_zone_note(current_price: float) -> str:
    if 0.1585 <= current_price <= 0.1605:
        return (
            "XLM in 0.1585-0.1605 demand band; expect sharp reaction; "
            "hard invalidation is below zone low."
        )
    if current_price < 0.1585:
        return "XLM below demand band; invalidation risk rising if weakness persists."
    if current_price > 0.1720:
        return "XLM above upper ladder; momentum is extended versus resting bids."
    return "XLM between ladder levels; maintain constructive bias while 0.16-0.15 holds."

def btc_zone_note(current_price: float) -> str:
    if 60000 <= current_price <= 70000:
        return "BTC inside structural bid range; constructive while 60k-55k holds."
    if current_price < 60000:
        return "BTC below deep ladder support; hedge or cut if 55k fails with volume."
    return "BTC above resting ladder; leader strength intact."

def xrp_zone_note(current_price: float) -> str:
    if current_price <= 1.80:
        return "XRP at/below cut band; hedge or exit if weakness persists."
    if 1.80 < current_price < 2.00:
        return "XRP in 1.80-2.00 caution band; keep laggard risk capped."
    return "XRP above 2.00; laggard participation allowed, but remain selective."

def flr_zone_note(current_price: float) -> str:
    if 0.0076 <= current_price <= 0.0084:
        return (
            "FLR in 0.0076-0.0084 swing accumulation band; "
            "accumulate only from surplus leader profits."
        )
    if 0.0072 <= current_price < 0.0076:
        return (
            "FLR slightly under main band; acceptable only if leaders remain strong "
            "and reclaim is in progress."
        )
    if current_price < 0.0072:
        return "FLR below 0.0072 structural cut; treat as failed until reclaimed."
    return "FLR above 0.0084; favour controlled participation or trim into strength."

def sgb_zone_note(current_price: float) -> str:
    if 0.00068 <= current_price <= 0.00074:
        return (
            "SGB in 0.00068-0.00074 support band; starter campaign only "
            "until breakout proof."
        )
    if current_price < 0.00065:
        return "SGB below 0.00065 cut line; treat as failure until reclaimed."
    return "SGB above band; rotate profits into strength but respect illiquidity."

def xlm_risk_doctrine() -> str:
    return (
        "Bias constructive while 0.1585-0.1500 structure holds. "
        "Close or hedge if 0.1500 fails with volume."
    )

def btc_risk_doctrine() -> str:
    return (
        "BTC is the main leader. Stay constructive while 60k-55k structure holds; "
        "close or hedge if 55k fails with volume."
    )

def xrp_risk_doctrine() -> str:
    return (
        "Cut: close/hedge XRP if 1.80 fails with volume. "
        "Bias: CAUTIOUS while 2.00-1.80 holds. "
        "Doctrine: laggard participation only; respect relative weakness."
    )

def flr_risk_doctrine() -> str:
    return (
        "FLR lamboed 3x: surplus-only swing tail built from XLM/BTC wins. "
        "Accumulate 0.0076-0.0084, tolerate soft weakness to 0.0072 only if leaders stay strong, "
        "and cut if 0.0072 fails with volume."
    )

def sgb_risk_doctrine() -> str:
    return (
        "SGB lamboed 3x: high-beta tail. "
        "Support 0.00068-0.00074; cut exposure if 0.00065 fails. "
        "Starter size until sustained reclaim above band."
    )

def xlm_risk_light(current_price: Optional[float]) -> Tuple[str, str]:
    if current_price is None:
        return YELLOW, "XLM CAUTION: price ?, respect demand band."
    if current_price < 0.1500:
        return RED, "XLM CUT: below 0.1500, structure failure risk."
    if 0.1500 <= current_price <= 0.1605:
        return YELLOW, "XLM CAUTION: inside/near demand band, expect sharp reaction."
    return GREEN, "XLM GO: above demand zone, constructive bias intact."

def btc_risk_light(current_price: Optional[float]) -> Tuple[str, str]:
    if current_price is None:
        return YELLOW, "BTC CAUTION: price ?, preserve leader discipline."
    if current_price < 55000:
        return RED, "BTC CUT: below 55k, structure failure."
    if 55000 <= current_price <= 60000:
        return YELLOW, "BTC CAUTION: testing lower structure."
    return GREEN, "BTC GO: above 60k, leader strength intact."

def xrp_risk_light(current_price: Optional[float]) -> Tuple[str, str]:
    if current_price is None:
        return YELLOW, "XRP CAUTION: price ?, keep laggard risk capped."
    if current_price <= 1.80:
        return RED, "XRP CUT: <=1.80, hedge or exit."
    if 1.80 < current_price < 2.00:
        return YELLOW, "XRP CAUTION: 1.80-2.00 band."
    return GREEN, "XRP GO: >2.00, laggard risk only."

def flr_risk_light(current_price: Optional[float]) -> Tuple[str, str]:
    if current_price is None:
        return YELLOW, "FLR CAUTION: price ?, only rotate surplus into FLR."
    if current_price < 0.0072:
        return RED, "FLR CUT: below 0.0072, structure failed until reclaim."
    if 0.0072 <= current_price < 0.0076:
        return YELLOW, "FLR SOFT CAUTION: under main band; acceptable only if XLM/BTC leaders stay strong."
    if 0.0076 <= current_price <= 0.0084:
        return YELLOW, "FLR CAUTION: inside swing accumulation band; 3x lamboed sizing only."
    return GREEN, "FLR GO: above 0.0084, controlled 3x participation allowed from surplus."

def sgb_risk_light(current_price: Optional[float]) -> Tuple[str, str]:
    if current_price is None:
        return YELLOW, "SGB CAUTION: price ?, high-beta tail; keep size tiny."
    if current_price < 0.00065:
        return RED, "SGB CUT: below 0.00065, treat structure as failed."
    if 0.00065 <= current_price <= 0.00074:
        return YELLOW, "SGB CAUTION: inside support band; starter-only campaign."
    return GREEN, "SGB GO: above 0.00074, 3x lamboed participation within cap."

def print_line(tag: str, text: str, color: str = YELLOW, bold: bool = False) -> None:
    prefix = f"{color}{BOLD}[{tag}]{RESET}" if bold else f"{color}[{tag}]{RESET}"
    print(f"{prefix} {text}")

def main() -> int:
    print("INPUT = PYTHON")

    if len(sys.argv) < 3:
        print(f"{PROJECT}$ python xlm_mode_note.py <TOKEN> <REGIME> [CURRENT_PRICE]")
        return 1

    token = sys.argv[1].upper()
    regime = sys.argv[2].lower()
    current_price = None

    if len(sys.argv) >= 4:
        try:
            current_price = float(sys.argv[3])
        except ValueError:
            print_line("ERROR", f"Invalid current price: {sys.argv[3]}", RED, bold=True)
            return 1

    mode = choose_mode(token, regime)
    note = mode_note(token, regime, mode)
    phase = phase_for(token, regime, mode)

    print_line("MODE", f"{token} | regime={regime} -> {mode}", CYAN, bold=True)
    print_line("NOTE", note, YELLOW)
    print_line("PHASE", phase, YELLOW)

    if token == "XLMUSDT":
        print_line("LADDER", format_ladder("XLM", XLM_LADDER), YELLOW)
        print_line("RISK", xlm_risk_doctrine(), YELLOW)
        if current_price is not None:
            print_line("ZONE", xlm_zone_note(current_price), YELLOW)
        light_color, light_text = xlm_risk_light(current_price)
        print_line("LIGHT", light_text, light_color, bold=True)
        return 0

    if token == "BTCUSDT":
        print_line("LADDER", format_ladder("BTC", BTC_LADDER), YELLOW)
        print_line("RISK", btc_risk_doctrine(), YELLOW)
        if current_price is not None:
            print_line("ZONE", btc_zone_note(current_price), YELLOW)
        light_color, light_text = btc_risk_light(current_price)
        print_line("LIGHT", light_text, light_color, bold=True)
        return 0

    if token == "XRPUSDT":
        print_line("LADDER", format_ladder("XRP", XRP_LADDER), YELLOW)
        print_line("RISK", xrp_risk_doctrine(), YELLOW)
        if current_price is not None:
            print_line("ZONE", xrp_zone_note(current_price), YELLOW)
        light_color, light_text = xrp_risk_light(current_price)
        print_line("LIGHT", light_text, light_color, bold=True)
        return 0

    if token == "FLRUSDT":
        print_line("LADDER", format_ladder("FLR", FLR_LADDER), YELLOW)
        print_line("RISK", flr_risk_doctrine(), YELLOW)
        if current_price is not None:
            print_line("ZONE", flr_zone_note(current_price), YELLOW)
        light_color, light_text = flr_risk_light(current_price)
        print_line("LIGHT", light_text, light_color, bold=True)
        return 0

    if token == "SGBUSDT":
        print_line("LADDER", format_ladder("SGB", SGB_LADDER), YELLOW)
        print_line("RISK", sgb_risk_doctrine(), YELLOW)
        if current_price is not None:
            print_line("ZONE", sgb_zone_note(current_price), YELLOW)
        light_color, light_text = sgb_risk_light(current_price)
        print_line("LIGHT", light_text, light_color, bold=True)
        return 0

    print_line("WARN", f"No doctrine configured for {token}; showing default posture only.", YELLOW, bold=True)
    print_line("LIGHT", "Default CAUTION: unsupported token.", YELLOW, bold=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
