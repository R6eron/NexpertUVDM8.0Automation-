#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from uvdm_post_fill_allocator import get_price
from typing import Any, Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def load_uvdm_state(path: str = "uvdm8_state.json") -> dict:
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


def load_wingman_config() -> Dict[str, Any]:
    uvdm_state = load_uvdm_state()
    wingman_cfg = uvdm_state.get("wingman", {}) if uvdm_state else {}
    trail_cfg = uvdm_state.get("trail", {}) if uvdm_state else {}

    config = {
        "mode": os.getenv("WINGMAN_MODE", "paper").strip().lower(),
        "symbol": os.getenv("WINGMAN_SYMBOL", "XLMUSDT").strip().upper(),
        "side": os.getenv("WINGMAN_SIDE", "LONG").strip().upper(),
        "sl_pct": float(wingman_cfg.get("sl_pct", os.getenv("WINGMAN_SL_PCT", "1.5"))),
        "tp1_pct": float(wingman_cfg.get("tp1_pct", os.getenv("WINGMAN_TP1_PCT", "1.0"))),
        "tp2_pct": float(wingman_cfg.get("tp2_pct", os.getenv("WINGMAN_TP2_PCT", "2.0"))),
        "tp3_pct": float(wingman_cfg.get("tp3_pct", os.getenv("WINGMAN_TP3_PCT", "3.0"))),
        "tp1_size": float(os.getenv("WINGMAN_TP1_SIZE", "0.25")),
        "tp2_size": float(os.getenv("WINGMAN_TP2_SIZE", "0.25")),
        "tp3_size": float(os.getenv("WINGMAN_TP3_SIZE", "0.50")),
        "trail_type": trail_cfg.get("type", "none"),
        "trail_atr_len": int(trail_cfg.get("atr_len", 14)),
        "trail_entry_mult": float(trail_cfg.get("entry_mult", 2.5)),
        "trail_tp1_mult": float(trail_cfg.get("tp1_mult", 2.0)),
        "trail_tp2_mult": float(trail_cfg.get("tp2_mult", 1.5)),
        "uvdm_state": uvdm_state,
    }

    if uvdm_state:
        print(
            f"[WINGMAN] UVDM handoff active: "
            f"regime={uvdm_state.get('regime')} "
            f"max_leverage={uvdm_state.get('max_leverage_today')}"
        )
        print(
            f"[WINGMAN] Using SL/TP: "
            f"SL={config['sl_pct']}% "
            f"TP1={config['tp1_pct']}% "
            f"TP2={config['tp2_pct']}% "
            f"TP3={config['tp3_pct']}%"
        )
        print(
            f"[WINGMAN] Trail config: "
            f"type={config['trail_type']} "
            f"atr_len={config['trail_atr_len']} "
            f"entry_mult={config['trail_entry_mult']} "
            f"tp1_mult={config['trail_tp1_mult']} "
            f"tp2_mult={config['trail_tp2_mult']}"
        )
    else:
        print("[WINGMAN] No UVDM handoff active; using env/default SL/TP settings.")

    return config


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
        if last_price >= ladder["tp2"]["price"]:
            return "tp2"
        if last_price >= ladder["tp1"]["price"]:
            return "tp1"
        return "entry"

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

    if tp_stage == "tp2":
        mult = cfg["trail_tp2_mult"]
    elif tp_stage == "tp1":
        mult = cfg["trail_tp1_mult"]
    else:
        mult = cfg["trail_entry_mult"]

    is_long = side.upper() == "LONG"

    if is_long:
        return round(highest_price - (mult * atr_value), 6)

    return round(lowest_price + (mult * atr_value), 6)


def main() -> None:
    cfg = load_wingman_config()

    market = os.getenv("WINGMAN_MARKET", "spot").strip().lower()
    symbol = cfg["symbol"]

    if market == "spot":
        base_url = os.getenv("BITRUE_BASE_URL", "https://openapi.bitrue.com").strip()
        entry_price = float(get_price(base_url, symbol))
    else:
        raise ValueError("Futures getter not implemented yet")
    ladder = build_ladder(entry_price=entry_price, side=cfg["side"], cfg=cfg)

    print("[WINGMAN] Ladder preview")
    print(json.dumps(ladder, indent=2))

    last_price = float(os.getenv("WINGMAN_LAST_PRICE", str(entry_price)))
    highest_price = float(os.getenv("WINGMAN_HIGHEST_PRICE", str(max(entry_price, last_price))))
    lowest_price = float(os.getenv("WINGMAN_LOWEST_PRICE", str(min(entry_price, last_price))))
    atr_value = float(os.getenv("WINGMAN_ATR_VALUE", "0.002500"))

    tp_stage = get_tp_stage(last_price=last_price, ladder=ladder, side=cfg["side"])
    trail_stop = compute_trailing_stop(
        side=cfg["side"],
        highest_price=highest_price,
        lowest_price=lowest_price,
        atr_value=atr_value,
        tp_stage=tp_stage,
        cfg=cfg,
    )

    if trail_stop is not None:
        print("[WINGMAN] Trail preview")
        print(
            json.dumps(
                {
                    "trail_type": cfg["trail_type"],
                    "atr_len": cfg["trail_atr_len"],
                    "atr_value": round(atr_value, 6),
                    "last_price": round(last_price, 6),
                    "highest_price": round(highest_price, 6),
                    "lowest_price": round(lowest_price, 6),
                    "tp_stage": tp_stage,
                    "trail_stop": trail_stop,
                },
                indent=2,
            )
        )

    if cfg["mode"] == "live":
        print("[WINGMAN] Live mode selected. Existing live order logic should run here unchanged.")
    else:
        print("[WINGMAN] Paper mode selected. No live orders sent.")


if __name__ == "__main__":
    main()
