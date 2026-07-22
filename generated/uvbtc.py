#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ASSET_NAME = "btc"
ASSET_SYMBOL = "BTCUSDT"
ASSET_ALIAS = "uvbtc"
ASSET_TYPE = "spot_futures"
ASSET_MAX_LIVE_LEVERAGE = 3
ASSET_ML_PROFILE = "btc_core"

HOME = Path.home()
ROOT = HOME / "NexpertUVDM-Automation"
CONFIG_PATH = ROOT / "config" / "assets.json"
ASSET_ENV_PATH = ROOT / "generated" / (ASSET_NAME + ".env.json")

DOCTRINE = [
    "I do not predict; I wait for proof.",
    "I do not chase; I manage what is live.",
    "I do not hope; I define invalidation first."
]

def load_registry():
    return json.loads(CONFIG_PATH.read_text())["defaults"]

def load_asset_env():
    if ASSET_ENV_PATH.exists():
        return json.loads(ASSET_ENV_PATH.read_text())
    return {}

def parse_leverage(value):
    text = str(value).strip().lower()
    if text.endswith("x"):
        text = text[:-1]
    try:
        return int(text)
    except Exception:
        return None

def fail(text):
    sys.stderr.write(text + chr(10))
    sys.exit(1)

def usage():
    lines = [
        "Usage: <amount-usdt> <symbol> <spot|long|futures> <1x|3x|5x|7x|10x> <dry|live> [invalidation]",
        "Example: 250 xrp spot 1x dry",
        "Example: 250 xrp futures 3x live 0.4875"
    ]
    sys.stderr.write(chr(10).join(lines) + chr(10))
    sys.exit(1)

def main():
    defaults = load_registry()
    asset_env = load_asset_env()
    argv = sys.argv[1:]

    if not argv:
        usage()

    if len(argv) < 5:
        fail("UVDM ultrasafe refusal: missing required arguments.")

    amount = argv[0]
    symbol_in = argv[1].strip().lower()
    mode = argv[2].strip().lower()
    leverage = argv[3].strip().lower()
    run_mode = argv[4].strip().lower()
    invalidation = argv[5].strip() if len(argv) > 5 else ""

    if symbol_in != ASSET_NAME:
        fail("UVDM ultrasafe refusal: this wrapper is locked to " + ASSET_NAME + ".")

    if mode == "long":
        mode = "futures"

    if mode not in ("spot", "futures"):
        fail("UVDM ultrasafe refusal: mode must be spot, long, or futures.")

    lev_num = parse_leverage(leverage)
    if lev_num is None:
        fail("UVDM ultrasafe refusal: leverage must look like 1x, 3x, 5x.")

    if mode == "spot" and lev_num != 1:
        fail("UVDM ultrasafe refusal: spot implies 1x only.")

    if ASSET_TYPE == "spot_only" and mode != "spot":
        fail("UVDM ultrasafe refusal: " + ASSET_NAME + " is configured as spot-only.")

    if run_mode not in ("dry", "live"):
        fail("UVDM ultrasafe refusal: final flag must be dry or live.")

    if run_mode == "live" and lev_num > ASSET_MAX_LIVE_LEVERAGE:
        fail("UVDM ultrasafe refusal: leverage exceeds max live leverage for " + ASSET_NAME + ".")

    if defaults.get("require_invalidation", True) and run_mode == "live" and not invalidation:
        fail("UVDM ultrasafe refusal: live deploy requires invalidation first.")

    if defaults.get("require_proof", True) and run_mode == "live":
        sys.stderr.write("Tape truth: Obey. Do not argue." + chr(10))
        sys.stderr.write("Process over outcome. No revenge trading." + chr(10))

    payload = {
        "asset_name": ASSET_NAME,
        "asset_symbol": ASSET_SYMBOL,
        "asset_alias": ASSET_ALIAS,
        "asset_type": ASSET_TYPE,
        "asset_ml_profile": ASSET_ML_PROFILE,
        "amount_usdt": amount,
        "mode": mode,
        "leverage": leverage,
        "run_mode": run_mode,
        "invalidation": invalidation,
        "defaults": defaults,
        "asset_env": asset_env,
        "doctrine": DOCTRINE
    }

    if "ml" in asset_env:
        payload["ml"] = asset_env["ml"]
    if "execution" in asset_env:
        payload["execution"] = asset_env["execution"]

    exec_cfg = asset_env.get("execution", {})
    if exec_cfg.get("spot_allowed") is False and mode == "spot":
        fail("UVDM ultrasafe refusal: " + ASSET_NAME + " does not allow spot.")
    if exec_cfg.get("futures_allowed") is False and mode == "futures":
        fail("UVDM ultrasafe refusal: " + ASSET_NAME + " does not allow futures.")
    if exec_cfg.get("live_allowed") is False and run_mode == "live":
        fail("UVDM ultrasafe refusal: " + ASSET_NAME + " does not allow live mode.")
    if exec_cfg.get("requires_invalidation", defaults.get("require_invalidation", True)) and run_mode == "live" and not invalidation:
        fail("UVDM ultrasafe refusal: live deploy requires invalidation first.")
    if exec_cfg.get("requires_proof", defaults.get("require_proof", True)) and run_mode == "live":
        pass

    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
