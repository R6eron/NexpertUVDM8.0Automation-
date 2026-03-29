#!/bin/bash
AMOUNT=50
PRICE=0.166
SYMBOL="XLMUSDT"
LOG="add_log.log"

# Create log if missing
touch "$LOG"

echo "$(date) - Adding $AMOUNT USDT at $PRICE" >> "$LOG"

python3 - <<EOF >> "$LOG" 2>&1
import ccxt
exchange = ccxt.bitrue()  # loads your pre-set keys

# Market buy equivalent at target price
amount_xlm = AMOUNT / PRICE  # 50/0.166 = 301.20 XLM
order = exchange.create_market_buy_order(SYMBOL, amount_xlm)
print(f"BOUGHT: {amount_xlm:.2f} XLM @ market (~{PRICE})")
print(f"ORDER: {order}")
EOF
