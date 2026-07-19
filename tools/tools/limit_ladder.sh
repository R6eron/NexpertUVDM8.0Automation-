#!/usr/bin/env bash
set -euo pipefail

usdt="${1:-}"
asset="${2:-}"
mode="${3:-}"
lev="${4:-}"

if [ -z "$usdt" ] || [ -z "$asset" ] || [ -z "$mode" ] || [ -z "$lev" ]; then
  echo "Usage: limit_ladder.sh <usdt> <asset> <mode> <leverage>"
  exit 1
fi

python3 - "$usdt" "$asset" "$mode" "$lev" <<'PY'
import sys

usdt = float(sys.argv[1])
asset = sys.argv[2].upper()
mode = sys.argv[3]
lev = sys.argv[4]

anchors = {
    "XLM": 0.19,
    "XRP": 0.50,
    "BTC": 100000.0,
    "ETH": 3000.0,
    "SOL": 150.0,
    "DOGE": 0.12,
    "ADA": 0.60,
    "HBAR": 0.08,
    "FLR": 0.02,
}
anchor = anchors.get(asset, 1.0)

pullbacks = [0.0025, 0.0050, 0.0075]
weights = [0.50, 0.30, 0.20]

budgets = [usdt * w for w in weights]
prices = [anchor * (1 - p) for p in pullbacks]
qtys = [budget / price if price > 0 else 0.0 for budget, price in zip(budgets, prices)]

def c(code, text):
    return f"\u001B[{code}m{text}\u001B[0m"

print(c("1;36", "UVDM Wingman TM 2025"))
print(c("37", "LEWIS RS 15081968001"))
print(c("36", "────────────────────────"))
print(c("1;36", "LIMIT LADDER"))
print(c("36", "────────────────────────"))
print(f"Budget : {c('33', f'${usdt:.2f}')} USDT")
print(f"Plan   : {c('1;37', asset)} {mode} {lev}")
print(f"Anchor : {c('32', f'${anchor:.6f}')}")
print("")

ladder_colors = ["35", "34", "36"]

for i, (qty, price, budget, pb, col) in enumerate(zip(qtys, prices, budgets, pullbacks, ladder_colors), 1):
    print(c(f"1;{col}", f"LADDER {i}"))
    print(f"Budget : {c('33', f'${budget:.2f}')} USDT")
    print(f"Qty    : {c('1;37', f'{qty:.8f}')} {asset}")
    print(f"Limit  : {c('32', f'${price:.6f}')}")
    print(f"Dip    : {c('31', f'{pb*100:.2f}%')}")
    print("")

print(c("36", "TOTAL"))
print(f"Budget : {c('33', f'${usdt:.2f}')} USDT")
print(f"Qty    : {c('1;37', f'{sum(qtys):.8f}')} {asset}")
PY
