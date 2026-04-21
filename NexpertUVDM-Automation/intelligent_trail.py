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

    if roe >= 0.10 and stop_loss < entry * 1.001:
        updated_stop = entry * 1.001
        ctx.set_stop_loss(updated_stop)
        ctx.log(f"FREE-RIDE: +{roe * 100:.1f}% -> breakeven at {updated_stop:.6f}")
        stop_loss = updated_stop

    if mark <= entry * 0.985 and ctx.spare_margin >= 100:
        add_price = mark * 0.99
        ctx.place_limit_add(add_price)
        ctx.log(f"DIP ADD: placed add order at {add_price:.6f}")

    try:
        if mark < entry * 0.97 and (ctx.volume_spike_down() or ctx.macd_bear_div()):
            atr_value = ctx.atr()
            if atr_value > 0:
                new_sl = mark - atr_value
                if new_sl > stop_loss:
                    updated_stop = new_sl
                    ctx.set_stop_loss(updated_stop)
                    ctx.log(f"PULLBACK TRAIL: stop moved to {updated_stop:.6f}")
                    stop_loss = updated_stop
    except Exception as exc:
        ctx.log(f"TRAIL WARNING: signal/ATR computation failed: {exc}")

    try:
        atr_value = ctx.atr()
        if atr_value > 0:
            atr_trail = mark - (atr_value * 1.5)
            if atr_trail > stop_loss:
                updated_stop = atr_trail
                ctx.set_stop_loss(updated_stop)
                ctx.log(f"ATR TRAIL: stop moved to {updated_stop:.6f}")
    except Exception as exc:
        ctx.log(f"TRAIL WARNING: ATR trail update failed: {exc}")

    return updated_stop


def demo() -> None:
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


if __name__ == "__main__":
    demo()