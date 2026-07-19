#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import time
from datetime import UTC, datetime

import ccxt

parser = argparse.ArgumentParser(description="Livermore Pivot Guard â€” whisper or auto-exit")
parser.add_argument("--auto", action="store_true", help="Enable AUTO market sells (high risk â€” watch closely)")
args = parser.parse_args()
AUTO_MODE = args.auto

exchange = ccxt.mexc({
    "enableRateLimit": True,
    "apiKey": os.getenv("MEXC_API_KEY"),
    "secret": os.getenv("MEXC_SECRET"),
})

symbol = "XLM/USDT"
max_risk_pct = 0.10
pivot_floor = 0.1490
trail_start_gain_pct = 0.007
tight_trail_after_pct = 0.15
vault_floor_pct = 0.80
stall_timeout_hours = 4

highest_seen = 0.0
initial_usdt = None
stalled_start_price = None
stalled_start_time = None


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


def whisper(ts, message, auto_action_msg=None):
    print(f"[{ts}] WHISPER â†’ {message}")
    if AUTO_MODE and auto_action_msg:
        print(f"          AUTO â†’ {auto_action_msg}")


def execute_market_sell(amount_xlm, reason):
    if amount_xlm <= 0:
        return
    try:
        order = exchange.create_market_sell_order(symbol, amount_xlm)
        whisper(
            utc_stamp(),
            f"EXECUTED SELL: {reason}",
            f"Sold {amount_xlm:.4f} XLM | Order ID: {order.get('id', 'N/A')}",
        )
    except Exception as e:
        whisper(utc_stamp(), f"AUTO SELL FAILED ({reason}): {str(e)}")


def get_usdt_free():
    global initial_usdt
    try:
        bal = exchange.fetch_balance()
        free_usdt = float(bal.get("USDT", {}).get("free", 0))
        if initial_usdt is None and free_usdt > 0:
            initial_usdt = free_usdt
        return free_usdt
    except Exception:
        return 0.0


def get_xlm_free():
    try:
        bal = exchange.fetch_balance()
        return float(bal.get("XLM", {}).get("free", 0))
    except Exception:
        return 0.0


def get_current_price():
    try:
        ticker = exchange.fetch_ticker(symbol)
        return float(ticker["last"])
    except Exception:
        return 0.0


def guard_loop():
    global AUTO_MODE, highest_seen, stalled_start_price, stalled_start_time

    try:
        price = get_current_price()
        if price <= 0:
            return

        usdt_free = get_usdt_free()
        xlm_hold = get_xlm_free()
        if xlm_hold <= 0:
            return

        entry = 0.1529
        pnl_pct = (price - entry) / entry if entry > 0 else 0
        pos_value = xlm_hold * price
        unreal_pnl = pos_value * pnl_pct
        risk_usdt = -unreal_pnl if unreal_pnl < 0 else 0.0
        ts = utc_stamp()

        if initial_usdt and usdt_free < initial_usdt * vault_floor_pct:
            whisper(ts, f"VAULT ALERT! Balance ${usdt_free:,.0f} < {vault_floor_pct * 100}% initial â†’ AUTO disabled.")
            AUTO_MODE = False
            return

        max_risk_allowed = initial_usdt * max_risk_pct if initial_usdt else 999999
        if risk_usdt > max_risk_allowed:
            msg = f"MAX RISK HIT! Loss ${-unreal_pnl:,.0f} ({pnl_pct * 100:.1f}%)"
            whisper(ts, msg + " â†’ partial exit advised")
            if AUTO_MODE:
                execute_market_sell(xlm_hold * 0.50, "max risk â€” 50% partial")

        if price < pivot_floor * 0.985:
            msg = f"PIVOT FLOOR SMASHED â†’ {price:.6f} < {pivot_floor}"
            whisper(ts, msg + " â†’ full exit NOW")
            if AUTO_MODE:
                execute_market_sell(xlm_hold, "pivot break â€” full cut")

        near_entry = abs(price - entry) < 0.003 and pnl_pct < 0.005
        if near_entry:
            if stalled_start_price is None:
                stalled_start_price = price
                stalled_start_time = time.time()
            elif stalled_start_time and (time.time() - stalled_start_time) > (3600 * stall_timeout_hours):
                whisper(ts, f"Stalled {stall_timeout_hours}+ hours near {price:.6f} â€” scratch advised")
                if AUTO_MODE:
                    execute_market_sell(xlm_hold, "long stall â€” full scratch")
        else:
            stalled_start_price = None
            stalled_start_time = None

        if price > highest_seen:
            highest_seen = price

        profit_from_entry = highest_seen - entry
        if profit_from_entry > entry * trail_start_gain_pct:
            trail_pct = 0.004 if pnl_pct > tight_trail_after_pct else trail_start_gain_pct
            suggested_stop = highest_seen * (1 - trail_pct)
            whisper(ts, f"TRAIL ACTIVE â†’ suggested stop {suggested_stop:.6f} (locking {(profit_from_entry / entry) * 100:.1f}%)")

        if pnl_pct > 0.25:
            whisper(ts, f"EUPHORIA ZONE ({pnl_pct * 100:.1f}% up) â†’ bank some profits")
            if AUTO_MODE:
                execute_market_sell(xlm_hold * 0.33, "greed â€” 33% partial take")

    except Exception as e:
        whisper(utc_stamp(), f"Guard error: {str(e)}")


mode_str = "AUTO-EXIT ENABLED (executes sells)" if AUTO_MODE else "WHISPER-ONLY (alerts only)"
print(f"Livermore Pivot Guard running â€” {mode_str}")
print("XLM/USDT pivot floor: 0.1490 | Your entry: 0.1529 | Tape is choppy â€” stay sharp.")
print("----------------------------------------------------")

while True:
    guard_loop()
    time.sleep(300)