# UVDM Stop & Guard Doctrine – ML Stop, Pivot Guard, SL

## 1. Purpose

- Define how UVDM protects capital during campaigns.
- Combine ML-based stops, pivot levels, and human SL doctrine.
- Keep behaviour consistent across XLM / FLR / SGB.

## 2. ML Stop

- State example: ML Stop State: HOLD_RECLAIM
- Role:
    - Classifies current regime (e.g. trending up, chop, reclaim).
    - Blocks deploy if regime is hostile to the planned action.
- Behaviour:
    - If ML stop is not in an allowed state, deploy aborts regardless of other inputs.
    - No orders are placed while ML stop is in a hard-block state.

## 3. Pivot Guard

- Example: Pivot Guard: 0.1495
- Role:
    - Key reclaim/invalid level for the main asset (XLM in current config).
    - Acts as a line-in-the-sand for risk: above = constructive, below = caution.
- Behaviour:
    - If price loses pivot and fails reclaim, UVDM shifts bias to defence.
    - Deploy may be reduced, delayed, or blocked depending on guard settings.

## 4. Stop-Loss (SL) Doctrine

- Philosophy:
    - Process over outcome; avoid emotional cuts.
    - Stops are placed based on structure and guard levels, not on fear.
- Rules of thumb:
    - SL sits beyond obvious liquidity pools, not inside them.
    - Adjust SL only when structure changes, not because of PnL noise.
    - Trail only when campaign is in profit and structure confirms.

## 5. Guardrail / Deploy interaction

- Deploy can only proceed when:
    - ML stop is in an allowed state (e.g. HOLD_RECLAIM or better).
    - Pivot Guard is not violated (or has been cleanly reclaimed).
    - Portfolio cap and exposure guards pass.
- If any of these fail:
    - Script prints the failing condition.
    - No orders are placed, even after confirmations.

## 6. Operator responsibilities

- Check:
    - ML stop state.
    - Pivot guard levels vs current price.
    - Hard floor / invalidate and Action guidance in market fingertips.
- Only proceed if:
    - Structure, guards, and doctrine agree.
    - You are prepared to let the campaign play out without micromanaging.

## 7. Principles

- Guardrails first, orders second.
- Use ML and pivots to reduce subjective noise.
- Never override stop/guard signals out of frustration or boredom.
