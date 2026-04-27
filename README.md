cd ~/NexpertUVDM-Automation

cat > uvdm8_operator.py <<'EOF'
#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

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

def get_runtime_regime() -> str:
    return os.getenv("UVDM_REGIME", "sos_lps").strip().lower()

def write_state_for_wingman(step: DeriskStep, path: str = "uvdm8_state.json") -> None:
    """
    Minimal JSON handoff to Bitrue Wingman (paper mode only).
    """
    handoff: Dict[str, Any] = {
        "regime": step.regime,
        "max_leverage_today": step.max_leverage,
        "notes": step.notes,
        # suggested mappings for SL/TP based purely on regime/max_leverage
        "wingman": {
            "sl_pct": 1.0 if step.max_leverage <= 3.0 else 1.5,
            "tp1_pct": 1.0,
            "tp2_pct": 2.0,
            "tp3_pct": 3.0,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(handoff, f, indent=2)

def main() -> None:
    regime = get_runtime_regime()
    step = get_derisk_step(regime)
    print("[DE-RISK LADDER]")
    print(json.dumps(step.__dict__, indent=2))
    # JSON handoff for Wingman (paper mode)
    write_state_for_wingman(step)
    print("[STATE] Wrote uvdm8_state.json for Bitrue Wingman")

if __name__ == "__main__":
    main()
EOF

chmod +x uvdm8_operator.py
python -m py_compile uvdm8_operator.py