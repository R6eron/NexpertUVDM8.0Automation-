#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


BITRUE_BASE_URL = os.getenv("BITRUE_BASE_URL", "https://openapi.bitrue.com").strip()
MEXC_BASE_URL = os.getenv("MEXC_BASE_URL", "https://api.mexc.com").strip()


def safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def load_uvdm_state(path: str = "uvdm8_state.json") -> Dict[str, Any]:
    mode = os.getenv("WINGMAN_MODE", "paper").strip().lower()
    if mode == "live":
        return {}
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        print(f"[WINGMAN] Failed to load {path}: {exc}")
        return {}


def fetch_json(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        raise ValueError("Unexpected JSON response shape")
    return data


def get_bitrue_spot_price(base_url: str, symbol: str) -> float:
    data = fetch_json(f"{base_url}/api/v1/ticker/price", {"symbol": symbol})
    return float(data["price"])


def get_mexc_spot_price(base_url: str, symbol: str) -> float:
    data = fetch_json(f"{base_url}/api/v3/ticker/price", {"symbol": symbol})
    return float(data["price"])


def get_futures_price(symbol: str) -> float:
    source = os.getenv("WINGMAN_FUTURES_SOURCE", "env").strip().lower()
    if source == "env":
        env_px = os.getenv("WINGMAN_FUTURES_PRICE", "").strip()
        if not env_px:
            raise ValueError("Futures price not supplied; set WINGMAN_FUTURES_PRICE")
        return float(env_px)
    raise ValueError(f"Unsupported futures source: {source}")


def load_wingman_config() -> Dict[str, Any]:
    uvdm_state = load_uvdm_state()
    wingman_cfg = uvdm_state.get("wingman", {}) if uvdm_state else {}
    trail_cfg = uvdm_state.get("trail", {}) if uvdm_state else {}

    config = {
        "mode": os.getenv("WINGMAN_MODE", "paper").strip().lower(),
        "market": os.getenv("WINGMAN_MARKET", "spot").strip().lower(),
        "venue": os.getenv("WINGMAN_VENUE", "bitrue").strip().lower(),
        "symbol": os.getenv("WINGMAN_SYMBOL", "XLMUSDT").strip().upper(),
        "side": os.getenv("WINGMAN_SIDE", "LONG").strip().upper(),
        "sl_pct": safe_float(wingman_cfg.get("sl_pct", os.getenv("WINGMAN_SL_PCT", "1.5")), 1.5),
        "tp1_pct": safe_float(wingman_cfg.get("tp1_pct", os.getenv("WINGMAN_TP1_PCT", "1.0")), 1.0),
        "tp2_pct": safe_float(wingman_cfg.get("tp2_pct", os.getenv("WINGMAN_TP2_PCT", "2.0")), 2.0),
        "tp3_pct": safe_float(wingman_cfg.get("tp3_pct", os.getenv("WINGMAN_TP3_PCT", "3.0")), 3.0),
        "tp1_size": safe_float(os.getenv("WINGMAN_TP1_SIZE", "0.25"), 0.25),
        "tp2_size": safe_float(os.getenv("WINGMAN_TP2_SIZE", "0.25"), 0.25),
        "tp3_size": safe_float(os.getenv("WINGMAN_TP3_SIZE", "0.50"), 0.50),
        "trail_type": str(trail_cfg.get("type", os.getenv("WINGMAN_TRAIL_TYPE", "none"))).strip().lower(),
        "trail_atr_len": int(safe_float(trail_cfg.get("atr_len", os.getenv("WINGMAN_TRAIL_ATR_LEN", "14")), 14)),
        "trail_entry_mult": safe_float(trail_cfg.get("entry_mult", os.getenv("WINGMAN_TRAIL_ENTRY_MULT", "2.5")), 2.5),
        "trail_tp1_mult": safe_float(trail_cfg.get("tp1_mult", os.getenv("WINGMAN_TRAIL_TP1_MULT", "2.0")), 2.0),
        "trail_tp2_mult": safe_float(trail_cfg.get("tp2_mult", os.getenv("WINGMAN_TRAIL_TP2_MULT", "1.5")), 1.5),
        "uvdm_state": uvdm_state,
    }

    validate_config(config)

    if uvdm_state:
        print(
            f"[WINGMAN] UVDM handoff active: regime={uvdm_state.get('regime')} "
            f"max_leverage={uvdm_state.get('max_leverage_today')}"
        )
    else:
        print("[WINGMAN] No UVDM handoff active; using env/default SL/TP settings.")

    print(
        f"[WINGMAN] Using SL/TP: SL={config['sl_pct']}% TP1={config['tp1_pct']}% "
        f"TP2={config['tp2_pct']}% TP3={config['tp3_pct']}%"
    )
    print(
        f"[WINGMAN] Trail config: type={config['trail_type']} atr_len={config['trail_atr_len']} "
        f"entry_mult={config['trail_entry_mult']} tp1_mult={config['trail_tp1_mult']} "
        f"tp2_mult={config['trail_tp2_mult']}"
    )
    return config


def validate_config(cfg: Dict[str, Any]) -> None:
    if cfg["side"] not in {"LONG", "SHORT"}:
        raise ValueError(f"Unsupported side: {cfg['side']}")
    if cfg["market"] not in {"spot", "futures"}:
        raise ValueError(f"Unsupported market: {cfg['market']}")
    if cfg["venue"] not in {"bitrue", "mexc"}:
        raise ValueError(f"Unsupported venue: {cfg['venue']}")
    if cfg["sl_pct"] <= 0:
        raise ValueError("SL must be positive")
    if min(cfg["tp1_pct"], cfg["tp2_pct"], cfg["tp3_pct"]) <= 0:
        raise ValueError("TP percentages must be positive")
    size_sum = round(cfg["tp1_size"] + cfg["tp2_size"] + cfg["tp3_size"], 6)
    if abs(size_sum - 1.0) > 1e-6:
        raise ValueError(f"TP sizes must sum to 1.0, got {size_sum}")
    if cfg["trail_type"] not in {"none", "atr"}:
        raise ValueError(f"Unsupported trail_type: {cfg['trail_type']}")


def build_ladder(entry_price: float, side: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    sl_pct = cfg["sl_pct"] / 100.0
    tp1_pct = cfg["tp1_pct"] / 100.0
    tp2_pct = cfg["tp2_pct"] / 100.0
    tp3_pct = cfg["tp3_pct"] / 100.0
    is_long = side.upper() == "LONG"

    if is_long:
        stop_loss = entry_price * (1.0 - sl_pct)
        tp1 = entry_price * (1.0 + tp1_pct)
        tp2 = entry_price * (1.0 + tp2_pct)
        tp3 = entry_price * (1.0 + tp3_pct)
    else:
        stop_loss = entry_price * (1.0 + sl_pct)
        tp1 = entry_price * (1.0 - tp1_pct)
        tp2 = entry_price * (1.0 - tp2_pct)
        tp3 = entry_price * (1.0 - tp3_pct)

    return {
        "entry_price": round(entry_price, 6),
        "side": side.upper(),
        "stop_loss": round(stop_loss, 6),
        "tp1": {"price": round(tp1, 6), "size": cfg["tp1_size"]},
        "tp2": {"price": round(tp2, 6), "size": cfg["tp2_size"]},
        "tp3": {"price": round(tp3, 6), "size": cfg["tp3_size"]},
    }


def get_tp_stage(last_price: float, ladder: Dict[str, Any], side: str) -> str:
    is_long = side.upper() == "LONG"
    if is_long:
        if last_price >= ladder["tp3"]["price"]:
            return "tp3"
        if last_price >= ladder["tp2"]["price"]:
            return "tp2"
        if last_price >= ladder["tp1"]["price"]:
            return "tp1"
        return "entry"
    if last_price <= ladder["tp3"]["price"]:
        return "tp3"
    if last_price <= ladder["tp2"]["price"]:
        return "tp2"
    if last_price <= ladder["tp1"]["price"]:
        return "tp1"
    return "entry"


def compute_trailing_stop(
    side: str,
    highest_price: float,
    lowest_price: float,
    atr_value: float,
    tp_stage: str,
    cfg: Dict[str, Any],
) -> float | None:
    if cfg["trail_type"] != "atr":
        return None
    if atr_value <= 0:
        raise ValueError("ATR value must be positive when ATR trailing is enabled")

    if tp_stage == "tp3":
        mult = min(cfg["trail_tp2_mult"], cfg["trail_tp1_mult"], cfg["trail_entry_mult"])
    elif tp_stage == "tp2":
        mult = cfg["trail_tp2_mult"]
    elif tp_stage == "tp1":
        mult = cfg["trail_tp1_mult"]
    else:
        mult = cfg["trail_entry_mult"]

    is_long = side.upper() == "LONG"
    if is_long:
        return round(highest_price - (mult * atr_value), 6)
    return round(lowest_price + (mult * atr_value), 6)


def resolve_entry_price(cfg: Dict[str, Any]) -> float:
    market = cfg["market"]
    symbol = cfg["symbol"]
    if market == "spot":
        if cfg["venue"] == "bitrue":
            return get_bitrue_spot_price(BITRUE_BASE_URL, symbol)
        if cfg["venue"] == "mexc":
            return get_mexc_spot_price(MEXC_BASE_URL, symbol)
    if market == "futures":
        return get_futures_price(symbol)
    raise ValueError(f"Could not resolve entry price for market={market} venue={cfg['venue']}")


def main() -> None:
    cfg = load_wingman_config()
    entry_price = resolve_entry_price(cfg)
    ladder = build_ladder(entry_price=entry_price, side=cfg["side"], cfg=cfg)

    print("[WINGMAN] Ladder preview")
    print(json.dumps(ladder, indent=2))

    last_price = safe_float(os.getenv("WINGMAN_LAST_PRICE", str(entry_price)), entry_price)
    highest_price = safe_float(os.getenv("WINGMAN_HIGHEST_PRICE", str(max(entry_price, last_price))), max(entry_price, last_price))
    lowest_price = safe_float(os.getenv("WINGMAN_LOWEST_PRICE", str(min(entry_price, last_price))), min(entry_price, last_price))
    atr_value = safe_float(os.getenv("WINGMAN_ATR_VALUE", "0.002500"), 0.0025)

    tp_stage = get_tp_stage(last_price=last_price, ladder=ladder, side=cfg["side"])
    trail_stop = compute_trailing_stop(
        side=cfg["side"],
        highest_price=highest_price,
        lowest_price=lowest_price,
        atr_value=atr_value,
        tp_stage=tp_stage,
        cfg=cfg,
    )

    preview = {
        "mode": cfg["mode"],
        "market": cfg["market"],
        "venue": cfg["venue"],
        "symbol": cfg["symbol"],
        "side": cfg["side"],
        "last_price": round(last_price, 6),
        "highest_price": round(highest_price, 6),
        "lowest_price": round(lowest_price, 6),
        "tp_stage": tp_stage,
        "trail_type": cfg["trail_type"],
        "trail_stop": trail_stop,
    }
    print("[WINGMAN] State preview")
    print(json.dumps(preview, indent=2))

    if cfg["mode"] == "live":
        print("[WINGMAN] Live mode selected. Hand off this ladder to the existing live order logic unchanged.")
    else:
        print("[WINGMAN] Paper mode selected. No live orders sent.")


if __name__ == "__main__":
    main()