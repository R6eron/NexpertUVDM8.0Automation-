# UVDM Deploy Doctrine

## 1. Purpose

- Define when deploy is allowed.
- Ensure deploy follows guards, exposure caps, and structure.

## 2. Preconditions

- ML stop must be in an allowed state.
- Pivot guard must hold or be cleanly reclaimed.
- Portfolio cap and exposure rules must pass.

## 3. Deploy sequence

- Read current state.
- Validate guards.
- Print failing conditions if any guard fails.
- Only place orders when all guards pass.

## 4. Principles

- Guardrails first, orders second.
- No forced deploys.
- No emotional overrides.
