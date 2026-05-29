#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def getenv_decimal(name: str, default: str) -> Decimal:
    return Decimal(str(os.getenv(name, default)).strip())


def load_realized_pnl() -> Decimal:
    path = os.getenv("REALIZED_PNL_FILE", "uvdm_realized_pnl.json").strip()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, (int, float, str)):
        pnl = Decimal(str(data))
    elif isinstance(data, dict):
        pnl = Decimal(str(data.get("pnl_usdt", data.get("pnl", "0"))))
    else:
        raise ValueError("Unsupported pnl file format")

    if pnl <= 0:
        raise ValueError(f"PnL must be positive, got {pnl}")

    return pnl


def setup_logger() -> logging.Logger:
    log_file = os.getenv("LOG_FILE", "uvdm_full_auto.log").strip()
    logger = logging.getLogger("uvdm_allocator")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    fh = logging.FileHandler(log_file)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger


def quantize_qty(value: Decimal, places: int = 6) -> Decimal:
    q = Decimal("1." + ("0" * places))
    return value.quantize(q, rounding=ROUND_DOWN)


def bitrue_headers(api_key: str) -> Dict[str, str]:
    ts = str(int(time.time() * 1000))
    return {
        "X-MBX-APIKEY": api_key,
        "X-CH-TS": ts,
        "Content-Type": "application/x-www-form-urlencoded",
    }


def sign_params(secret: str, params: Dict[str, Any]) -> str:
    payload = "&".join(f"{k}={v}" for k, v in params.items())
    sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return payload + "&signature=" + sig


def get_price(base_url: str, symbol: str) -> Decimal:
    r = requests.get(f"{base_url}/api/v1/ticker/price", params={"symbol": symbol}, timeout=15)
    r.raise_for_status()
    data = r.json()
    return Decimal(str(data["price"]))


def place_market_buy_quantity(
    base_url: str,
    api_key: str,
    api_secret: str,
    symbol: str,
    quantity: Decimal,
    logger: logging.Logger,
) -> Dict[str, Any]:
    headers = bitrue_headers(api_key)
    timestamp = headers["X-CH-TS"]
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quantity": str(quantity),
        "recvWindow": 5000,
        "timestamp": timestamp,
    }
    payload = sign_params(api_secret, params)
    r = requests.post(f"{base_url}/api/v1/order", headers=headers, data=payload, timeout=20)
    logger.info("Bitrue response %s %s", r.status_code, r.text[:500])
    r.raise_for_status()
    return r.json()


def compute_allocations(pnl_usdt: Decimal) -> Dict[str, Decimal]:
    xlm_pct = getenv_decimal("ALLOC_XLM_PCT", "0.5")
    flr_pct = getenv_decimal("ALLOC_FLR_PCT", "0.25")
    sgb_pct = getenv_decimal("ALLOC_SGB_PCT", "0.25")

    total = xlm_pct + flr_pct + sgb_pct
    if total != Decimal("1.0"):
        raise ValueError(f"Allocation percentages must sum to 1.0, got {total}")

    return {
        "XLM": pnl_usdt * xlm_pct,
        "FLR": pnl_usdt * flr_pct,
        "SGB": pnl_usdt * sgb_pct,
    }


def run_allocator() -> Dict[str, Any]:
    logger = setup_logger()

    mode = os.getenv("WINGMAN_MODE", "paper").strip().lower()
    base_url = os.getenv("BITRUE_BASE_URL", "https://openapi.bitrue.com").strip()
    api_key = os.getenv("BITRUE_API_KEY", "").strip()
    api_secret = os.getenv("BITRUE_API_SECRET", "").strip()

    xlm_pair = os.getenv("SPOT_XLM_PAIR", "XLMUSDT").strip().upper()
    flr_pair = os.getenv("SPOT_FLR_PAIR", "FLRUSDT").strip().upper()
    sgb_pair = os.getenv("SPOT_SGB_PAIR", "SGBUSDT").strip().upper()

    keep_gas_flr = getenv_decimal("KEEP_GAS_FLR", "5")
    pnl_usdt = load_realized_pnl()
    allocations = compute_allocations(pnl_usdt)

    plan = {
        "mode": mode,
        "pnl_usdt": str(quantize_qty(pnl_usdt, 2)),
        "allocations_usdt": {
            "XLM": str(quantize_qty(allocations["XLM"], 2)),
            "FLR": str(quantize_qty(allocations["FLR"], 2)),
            "SGB": str(quantize_qty(allocations["SGB"], 2)),
        },
        "pairs": {
            "XLM": xlm_pair,
            "FLR": flr_pair,
            "SGB": sgb_pair,
        },
        "keep_gas_flr": str(keep_gas_flr),
    }

    logger.info("ALLOC_PLAN %s", json.dumps(plan, indent=2))
    print(json.dumps(plan, indent=2))

    if mode != "live":
        logger.info("Paper mode active. No live Bitrue orders sent.")
        return {"ok": True, "mode": mode, "plan": plan, "orders": []}

    if not api_key or not api_secret:
        raise ValueError("Live mode requires BITRUE_API_KEY and BITRUE_API_SECRET")

    orders = []

    xlm_price = get_price(base_url, xlm_pair)
    xlm_qty = quantize_qty(allocations["XLM"] / xlm_price, 4)
    orders.append(place_market_buy_quantity(base_url, api_key, api_secret, xlm_pair, xlm_qty, logger))

    flr_price = get_price(base_url, flr_pair)
    flr_qty = quantize_qty(allocations["FLR"] / flr_price, 4)
    if flr_qty > keep_gas_flr:
        flr_qty = quantize_qty(flr_qty - keep_gas_flr, 4)
    orders.append(place_market_buy_quantity(base_url, api_key, api_secret, flr_pair, flr_qty, logger))

    sgb_price = get_price(base_url, sgb_pair)
    sgb_qty = quantize_qty(allocations["SGB"] / sgb_price, 4)
    orders.append(place_market_buy_quantity(base_url, api_key, api_secret, sgb_pair, sgb_qty, logger))

    logger.info("Live allocation complete.")
    return {"ok": True, "mode": mode, "plan": plan, "orders": orders}


if __name__ == "__main__":
    result = run_allocator()
    print(json.dumps(result, indent=2, default=str))
