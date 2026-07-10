#!/usr/bin/env bash
set -euo pipefail

amount="${1:-}"
asset="${2:-}"
mode="${3:-}"
lev="${4:-}"

if [ -z "$amount" ] || [ -z "$asset" ] || [ -z "$mode" ] || [ -z "$lev" ]; then
  echo "usage: tools/limit_ladder.sh <amount> <asset> <mode> <leverage>"
  exit 1
fi

python3 - "$amount" "$asset" "$mode" "$lev" <<'PY'
import sys
amount = float(sys.argv[1])
asset = sys.argv[2]
mode = sys.argv[3]
lev = sys.argv[4]

weights = [0.5, 0.3, 0.2]
steps = [0.0025, 0.0050, 0.0075]

print(f"limit_ladder_plan={asset} {mode} {lev}")
for i, (w, s) in enumerate(zip(weights, steps), 1):
    size = round(amount * w, 8)
    pct = round(s * 100, 2)
    print(f"ladder_{i}=size:{size} pullback:{pct}%")
PY
