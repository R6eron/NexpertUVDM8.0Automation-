#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


@dataclass
class DeriskStep:
    regime: str
    max_leverage: float
    profit_to_vault: float
    profit_to_spot: float
    redeployable_profit: float
    notes: str


DERISK_LADDER: List[DeriskStep] = [
    DeriskStep("accumulation", 7.0, 0.20, 0.40, 0.40, "Use aggression only if risk is controlled and liquidation distance is healthy."),
    DeriskStep("sos_lps", 7.0, 0.35, 0.35, 0.30, "Early markup/SOS/LPS: press edge, but bank hard and prep to step down."),
    DeriskStep("early_markup", 5.0, 0.45, 0.35, 0.20, "Trend is working; de-risk progressively into strength."),
    DeriskStep("late_markup", 3.0, 0.55, 0.30, 0.15, "Higher we go, further to fall. Remove fragility aggressively."),
    DeriskStep("distribution", 1.0, 0.70, 0.20, 0.10, "Protect capital; only tactical exposure if any."),
    DeriskStep("markdown", 1.0, 0.60, 0.30, 0.10, "Defensive posture; wait for structure to improve."),
]


def get_runtime_regime() -> str:
    return os.getenv("UVDM_REGIME", "sos_lps").strip().lower()


def get_output_path() -> Path:
    return Path(os.getenv("UVDM_STATE_PATH", "uvdm8_state.json")).expanduser()


def get_derisk_step(regime: str) -> DeriskStep:
    normalized = regime.strip().lower().replace(" ", "_")
    for step in DERISK_LADDER:
        if step.regime == normalized:
            return step
    return DeriskStep(
        regime=normalized or "unknown",
        max_leverage=3.0,
        profit_to_vault=0.50,
        profit_to_spot=0.30,
        redeployable_profit=0.20,
        notes="Fallback regime. Stay moderate until structure is clear.",
    )


def build_wingman_payload(step: DeriskStep) -> Dict[str, Any]:
    if step.max_leverage <= 1.0:
        sl_pct = 0.8
        tp1_pct, tp2_pct, tp3_pct = 0.8, 1.6, 2.4
    elif step.max_leverage <= 3.0:
        sl_pct = 1.0
        tp1_pct, tp2_pct, tp3_pct = 1.0, 2.0, 3.0
    elif step.max_leverage <= 5.0:
        sl_pct = 1.25
        tp1_pct, tp2_pct, tp3_pct = 1.2, 2.4, 3.6
    else:
        sl_pct = 1.5
        tp1_pct, tp2_pct, tp3_pct = 1.5, 3.0, 4.5

    return {
        "sl_pct": sl_pct,
        "tp1_pct": tp1_pct,
        "tp2_pct": tp2_pct,
        "tp3_pct": tp3_pct,
    }


def validate_step(step: DeriskStep) -> None:
    total = round(step.profit_to_vault + step.profit_to_spot + step.redeployable_profit, 6)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Profit allocation must sum to 1.0, got {total} for regime {step.regime}")
    if step.max_leverage <= 0:
        raise ValueError(f"Max leverage must be positive for regime {step.regime}")


def write_state_for_wingman(step: DeriskStep, path: Path) -> Dict[str, Any]:
    validate_step(step)
    payload: Dict[str, Any] = {
        "regime": step.regime,
        "max_leverage_today": step.max_leverage,
        "profit_to_vault": step.profit_to_vault,
        "profit_to_spot": step.profit_to_spot,
        "redeployable_profit": step.redeployable_profit,
        "notes": step.notes,
        "wingman": build_wingman_payload(step),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    regime = get_runtime_regime()
    step = get_derisk_step(regime)
    output_path = get_output_path()

    print("[DE-RISK LADDER]")
    print(json.dumps(asdict(step), indent=2))

    payload = write_state_for_wingman(step, output_path)
    print(f"[STATE] Wrote {output_path} for Bitrue Wingman")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()