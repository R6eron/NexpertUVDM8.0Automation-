"""
Intelligent trailing stop module for UVDM bots.

Exposes:
- TrailContext: dependency container
- update_intelligent_trail: core trailing + add-logic
- demo(): simple CLI harness
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrailContext:
    """
    Injected dependencies and state for trailing logic.

    All callables should wrap your exchange / execution layer
    or indicator engine. This keeps the core logic pure and testable.
    """

    spare_margin: float
    set_stop_loss: Callable[[float], None]
    place_limit_add: Callable[[float], None]
    volume_spike_down: Callable[[], bool]
    macd_bear_div: Callable[[], bool]
    atr: Callable[[], float]
    log: Callable[[str], None] = logger.info


def update_intelligent_trail(
    pos: Dict[str, Any],
    ctx: TrailContext
) -> Optional[float]:
    """
    Update trailing stop for a single open position.

    Parameters
    ----------
    pos : mapping
        Must provide 'entryPrice', 'markPrice', and optionally 'stopLossPrice'.
        Values can be strings or floats; they will be cast to float.
    ctx : TrailContext
        Injected dependencies and state.

    Returns
    -------
    Optional[float]
        New stop price if updated, otherwise None.
    """
    try:
        entry = float(pos["entryPrice"])
        mark = float(pos["markPrice"])
    except (KeyError, TypeError, ValueError) as exc:
        ctx.log(f"TRAIL ERROR: invalid price data in pos: {exc}")
        return None

    stop_loss = float(pos.get("stopLossPrice") or 0.0)
    roe = (mark - entry) / entry if entry != 0 else 0.0
    updated_stop: Optional[float] = None

    # 1) FREE-RIDE LOCK: once ROE >= +10%, lock ~breakeven if not done yet
    if roe >= 0.10 and stop_loss < entry * 1.001:
        updated_stop = entry * 1.001
        ctx.set_stop_loss(updated_stop)
        ctx.log(f"FREE-RIDE: +{roe * 100:.1f}% -> breakeven at {updated_stop:.6f}")
        stop_loss = updated_stop

    # 2) PYRAMID DIPS: ~1.5%+ dip and decent spare margin → scale in
    if mark <= entry * 0.985 and ctx.spare_margin >= 100:
        add_price = mark * 0.99
        ctx.place_limit_add(add_price)
        ctx.log(f"DIP ADD: placed add order at {add_price:.6f}")

    # 3) PULLBACK-ONLY TIGHTENING:
    #    only tighten if we're below -3% and see some warning (volume/MACD)
    try:
        if mark < entry * 0.97 and (ctx.volume_spike_down() or ctx.macd_bear_div()):
            new_sl = mark - ctx.atr() * 1.0
            if new_sl > stop_loss:
                updated_stop = new_sl
                ctx.set_stop_loss(updated_stop)
                ctx.log(f"PULLBACK TRAIL: stop moved to {updated_stop:.6f}")
                stop_loss = updated_stop
    except Exception as exc:  # keep trail alive even if indicator code fails
        ctx.log(f"TRAIL WARNING: signal/ATR computation failed: {exc}")

    # 4) LOOSE ATR TRAIL: always keep a soft leash under price
    try:
        atr_value = ctx.atr()
        atr_trail = mark - (atr_value * 1.5)
        if atr_trail > stop_loss:
            updated_stop = atr_trail
            ctx.set_stop_loss(updated_stop)
            ctx.log(f"ATR TRAIL: stop moved to {updated_stop:.6f}")
    except Exception as exc:
        ctx.log(f"TRAIL WARNING: ATR trail update failed: {exc}")

    return updated_stop


def demo() -> None:
    """
    Run a simple CLI demo of the trail logic.

    Safe to call from the command line:
        python intelligent_trail_full.py
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(name)s: %(message)s",
    )

    def _set_stop(price: float) -> None:
        logger.info("set_stop_loss(%.6f)", price)

    def _place_add(price: float) -> None:
        logger.info("place_limit_add(%.6f)", price)

    ctx = TrailContext(
        spare_margin=150.0,
        set_stop_loss=_set_stop,
        place_limit_add=_place_add,
        volume_spike_down=lambda: False,
        macd_bear_div=lambda: True,
        atr=lambda: 0.0025,
    )

    pos = {
        "entryPrice": 0.1665,
        "markPrice": 0.1835,
        "stopLossPrice": 0.1500,
    }

    logger.info("Initial pos: %s", pos)
    new_sl = update_intelligent_trail(pos, ctx)
    logger.info("New stop from trail: %s", new_sl)


if __name__ == "__main__":  # pragma: no cover
    demo()
# NOW paste Python code (NOT in terminal):
def update_intelligent_trail(pos):
    entry = pos['entryPrice']
    mark = pos['markPrice']
    roe = (mark - entry) / entry
    
    # FREE-RIDE LOCK
    if roe >= 0.10 and pos['stopLossPrice'] < entry * 1.001:
        set_stop_loss(entry * 1.001)
        log(f"FREE-RIDE: +{roe*100:.1f}% → breakeven")
    
    # PYRAMID DIPS
    if mark <= entry * 0.985 and spare_margin >= 100:
        place_limit_add(mark * 0.99)
    
    # PULLBACK ONLY
    if mark < entry * 0.97 and (volume_spike_down() or macd_bear_div()):
        new_sl = mark - atr() * 1.0
        if new_sl > pos['stopLossPrice']:
# Exit bash → Go to Python file
nano intelligent_trail.py

# NOW paste Python code (NOT in terminal):
def update_intelligent_trail(pos):
    entry = pos['entryPrice']
    mark = pos['markPrice']
    roe = (mark - entry) / entry
    
    # FREE-RIDE LOCK
    if roe >= 0.10 and pos['stopLossPrice'] < entry * 1.001:
        set_stop_loss(entry * 1.001)
        log(f"FREE-RIDE: +{roe*100:.1f}% → breakeven")
    
    # PYRAMID DIPS
    if mark <= entry * 0.985 and spare_margin >= 100:
        place_limit_add(mark * 0.99)
    
    # PULLBACK ONLY
    if mark < entry * 0.97 and (volume_spike_down() or macd_bear_div()):
        new_sl = mark - atr() * 1.0
        if new_sl > pos['stopLossPrice']:
            set_stop_loss(new_sl)
    
    # LOOSE TRAIL
    atr_trail = mark - (atr() * 1.5)
    if atr_trail > pos['stopLossPrice']:
        set_stop_loss(atr_trail)

# Ctrl+O → ENTER → Ctrl+X
# Exit bash → Go to Python file
nano intelligent_trail.py

# NOW paste Python code (NOT in terminal):
def update_intelligent_trail(pos):
    entry = pos['entryPrice']
    mark = pos['markPrice']
    roe = (mark - entry) / entry
    
    # FREE-RIDE LOCK
    if roe >= 0.10 and pos['stopLossPrice'] < entry * 1.001:
        set_stop_loss(entry * 1.001)
        log(f"FREE-RIDE: +{roe*100:.1f}% → breakeven")
    
    # PYRAMID DIPS
    if mark <= entry * 0.985 and spare_margin >= 100:
        place_limit_add(mark * 0.99)
    
    # PULLBACK ONLY
    if mark < entry * 0.97 and (volume_spike_down() or macd_bear_div()):
        new_sl = mark - atr() * 1.0
        if new_sl > pos['stopLossPrice']:
            set_stop_loss(new_sl)
    
    # LOOSE TRAIL
    atr_trail = mark - (atr() * 1.5)
    if atr_trail > pos['stopLossPrice']:
        set_stop_loss(atr_trail)

# Ctrl+O → ENTER → Ctrl+X
# You're at ~/NexpertUVDM-Automation $
pkill -f main_bot    # Kill old bot
nohup python3 main_bot.py > bot.log 2>&1 &  # Restart with trail
tmux attach empire   # Monitor P10 XLM 0.1665
1. Ctrl+O          → WRITE OUT (SAVE FILE)
2. ENTER           → Confirm "intelligent_trail.py"  
3. Ctrl+X          → EXIT NANO
            set_stop_loss(new_sl)
    
    # LOOSE TRAIL
    atr_trail = mark - (atr() * 1.5)
    if atr_trail > pos['stopLossPrice']:
        set_stop_loss(atr_trail)

# Ctrl+O → ENTER → Ctrl+X

# 4. ADD MORE DIP HUNTERS
# XRP: TARGET=0.45
# SGB: TARGET=0.015#!/bin/bash
TARGET=0.45          # XRP dip trigger
INTERVAL=30          # 30s checks  
LOG=~/xrp_dip.log

while true; do
  PRICE=$(curl -s "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT" | grep -o "[0-9]+.[0-9]+" | head -1)
  if (( $(echo "$PRICE <= $TARGET" | bc -l) )); then
    termux-vibrate -d 600
    echo "$(date) – XRP DIP HIT: $PRICE" >> "$LOG"
  fi
  sleep $INTERVAL
done

