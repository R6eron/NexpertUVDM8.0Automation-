# livermore_pivot_guard_auto.py
# Livermore-inspired AUTO + whisper exit guard — Bitrue spot XLM/USDT only
# Run: python livermore_pivot_guard_auto.py          → whisper/alerts only
#       python livermore_pivot_guard_auto.py --auto   → enables market sells
#
# Protects the vault: partials on risk/greed, full cut on pivot break or long stall
# "When the pivotal point cracks — the blade falls. No debate, no hope."

import ccxt
import time
import argparse
from datetime import datetime

# CLI flag for auto mode
parser = argparse.ArgumentParser(description="Livermore Pivot Guard — whisper or auto-exit")
parser.add_argument('--auto', action='store_true', help='Enable AUTO7u market sells (high risk — watch closely)')
args = parser.parse_args()
AUTO_MODE = args.auto

exchange = ccxt.mexc({
    'enableRateLimit': True,
    # Uncomment and fill or better: use environment variables
    # 'apiKey': os.getenv('MEXC_API_KEY'),
    # 'secret': os.getenv('MEXC_SECRET'),
})

symbol = 'XLM/USDT'
max_risk_pct = 0.10                 # Max account risk per position
pivot_floor = 0.1490                # Update manually when structure changes
trail_start_gain_pct = 0.007        # Start trailing after \~0.7% unrealized
tight_trail_after_pct = 0.15        # Tighten trail after 15% gain
vault_floor_pct = 0.80              # Kill auto if balance <80% of initial
stall_timeout_hours = 4             # Wyckoff: no progress → scratch after this

# Persistent state
highest_seen = 0.0
initial_usdt = None
stalled_start_price = None
stalled_start_time = None

def whisper(ts, message, auto_action_msg=None):
    print(f"[{ts}] WHISPER → {message}")
    if AUTO_MODE and auto_action_msg:
        print(f"          AUTO → {auto_action_msg}")

def execute_market_sell(amount_xlm, reason):
    if amount_xlm <= 0:
        return
    try:
        order = exchange.create_market_sell_order(symbol, amount_xlm)
        whisper(
            datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            f"EXECUTED SELL: {reason}",
            f"Sold {amount_xlm:.4f} XLM | Order ID: {order.get('id', 'N/A')}"
        )
    except Exception as e:
        whisper(
            datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            f"AUTO SELL FAILED ({reason}): {str(e)}"
        )

def get_usdt_free():
    global initial_usdt
    try:
        bal = exchange.fetch_balance()
        free_usdt = float(bal.get('USDT', {}).get('free', 0))
        if initial_usdt is None and free_usdt > 0:
            initial_usdt = free_usdt
        return free_usdt
    except:
        return 0.0

def get_xlm_free():
    try:
        bal = exchange.fetch_balance()
        return float(bal.get('XLM', {}).get('free', 0))
    except:
        return 0.0

def get_current_price():
    try:
        ticker = exchange.fetch_ticker(symbol)
        return float(ticker['last'])
    except:
        return 0.0

def guard_loop():
    global highest_seen, stalled_start_price, stalled_start_time

    try:
        price = get_current_price()
        if price <= 0:
            return

        usdt_free = get_usdt_free()
        xlm_hold = get_xlm_free()

        if xlm_hold <= 0:
            return  # flat — nothing to guard

        # Hardcoded entry — improve later with fetch_my_trades average
        entry = 0.1529                      # ← YOUR REAL AVERAGE ENTRY PRICE HERE

        pnl_pct = (price - entry) / entry if entry > 0 else 0
        pos_value = xlm_hold * price
        unreal_pnl = pos_value * pnl_pct
        risk_usdt = -unreal_pnl if unreal_pnl < 0 else 0.0

        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        # 0. Vault kill-switch (Douglas: capital preservation rule #1)
        if initial_usdt and usdt_free < initial_usdt * vault_floor_pct:
            whisper(ts, f"VAULT ALERT! Balance ${usdt_free:,.0f} < {vault_floor_pct*100}% initial → AUTO disabled.")
            global AUTO_MODE
            AUTO_MODE = False
            return

        # 1. Max risk breach → partial cut
        max_risk_allowed = initial_usdt * max_risk_pct if initial_usdt else 999999
        if risk_usdt > max_risk_allowed:
            msg = f"MAX RISK HIT! Loss ${-unreal_pnl:,.0f} ({pnl_pct*100:.1f}%)"
            whisper(ts, msg + " → partial exit advised")
            if AUTO_MODE:
                sell_qty = xlm_hold * 0.50
                execute_market_sell(sell_qty, "max risk — 50% partial")

        # 2. Pivotal floor violation → full exit
        if price < pivot_floor * 0.985:  # wick buffer
            msg = f"PIVOT FLOOR SMASHED → {price:.6f} < {pivot_floor}"
            whisper(ts, msg + " → full exit NOW")
            if AUTO_MODE:
                execute_market_sell(xlm_hold, "pivot break — full cut")

        # 3. Long stall (Wyckoff: no effort = potential distribution)
        near_entry = abs(price - entry) < 0.003 and pnl_pct < 0.005
        if near_entry:
            if stalled_start_price is None:
                stalled_start_price = price
                stalled_start_time = time.time()
            elif (time.time() - stalled_start_time) > (3600 * stall_timeout_hours):
                whisper(ts, f"Stalled {stall_timeout_hours}+ hours near {price:.6f} — scratch advised")
                if AUTO_MODE:
                    execute_market_sell(xlm_hold, "long stall — full scratch")
        else:
            stalled_start_price = None
            stalled_start_time = None

        # 4. Trailing protection whisper (progressive lock)
        if price > highest_seen:
            highest_seen = price

        profit_from_entry = highest_seen - entry
        if profit_from_entry > entry * trail_start_gain_pct:
            trail_pct = 0.004 if pnl_pct > tight_trail_after_pct else trail_start_gain_pct
            suggested_stop = highest_seen * (1 - trail_pct)
            whisper(ts, f"TRAIL ACTIVE → suggested stop {suggested_stop:.6f} "
                       f"(locking {(profit_from_entry/entry)*100:.1f}%)")

        # 5. Greed zone → partial bank (Livermore loved this)
        if pnl_pct > 0.25:
            whisper(ts, f"EUPHORIA ZONE ({pnl_pct*100:.1f}% up) → bank some profits")
            if AUTO_MODE:
                sell_qty = xlm_hold * 0.33
                execute_market_sell(sell_qty, "greed — 33% partial take")

    except Exception as e:
        whisper(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), f"Guard error: {str(e)}")

# Startup banner
mode_str = "AUTO-EXIT ENABLED (executes sells)" if AUTO_MODE else "WHISPER-ONLY (alerts only)"
print(f"Livermore Pivot Guard running — {mode_str}")
print("XLM/USDT pivot floor: 0.1490 | Your entry: 0.1529 | Tape is choppy — stay sharp.")
print("----------------------------------------------------")

while True:
    guard_loop()
    time.sleep(300)  # 5 minutes — balanced for crypto without spamcd \~/NexpertUVDM-Automation
nano livermore_pivot_guard_auto.py68.53