# UVDM Reclaim Doctrine

## 1. Purpose

- Define how UVDM handles reclaim conditions after weakness, loss of pivot, or failed structure.
- Ensure re-entry and continuation only happen when structure is rebuilt.

## 2. Reclaim meaning

- Reclaim means price has lost a key level, then recovered it with acceptance.
- A reclaim is not just a wick through level; it requires confirmation by structure and behaviour.

## 3. Core checks

- Pivot guard must be recovered cleanly.
- ML stop state must return to an allowed condition.
- Price action must show support holding above the reclaimed level.
- Exposure rules must still pass before any deploy resumes.

## 4. Reclaim behaviour

- If reclaim is weak, UVDM remains defensive.
- If reclaim is clean and confirmed, deploy bias can improve from defence to constructive.
- If reclaim fails again, doctrine returns immediately to guard-first behaviour.

## 5. Operator responsibilities

- Check whether the level was truly reclaimed or only briefly touched.
- Confirm structure, ML state, and portfolio guardrails align.
- Avoid forcing re-entry out of impatience.

## 6. Principles

- Reclaim first, aggression second.
- Confirmation beats anticipation.
- Strong structure earns deploy; weak structure earns patience.
