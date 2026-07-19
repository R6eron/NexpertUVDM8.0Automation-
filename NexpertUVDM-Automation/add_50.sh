#!/usr/bin/env bash
set -euo pipefail

AMOUNT=50
PRICE=0.166
SYMBOL="XLMUSDT"
# CCXT format for pairs usually expects a slash: XLM/USDT:USDT or XLM/USDT depending on spot vs futures.
# Bitrue futures in CCXT often use XLM/USDT:USDT or similar. We will pass what you had but CCXT might prefer the slash format.
CCXT_SYMBOL="XLM/USDT" 

echo "$(date) - Placing limit buy: $AMOUNT USDT at $PRICE for $SYMBOL" >> ~/add_log.log

# We use python3 to execute CCXT, appending both stdout and stderr to the log
python3 - <<EOF >> ~/add_log.log 2>&1
import ccxt

exchange = ccxt.bitrue({
    'enableRateLimit': True,
    # Keys should be set in environment variables: BITRUE_API_KEY and BITRUE_SECRET
})

symbol = "${CCXT_SYMBOL}"
amount_usdt = ${AMOUNT}
price = ${PRICE}
amount_coin = amount_usdt / price

try:
    # 1. Set leverage first (CCXT standard pattern for futures)
    # exchange.set_leverage(7, symbol) # Uncomment if using futures

    # 2. Place the order
    order = exchange.create_limit_buy_order(
        symbol, 
        amount_coin, 
        price, 
        params={'leverage': 7}
    )
    print("✅ Order placed successfully:", order['id'] if 'id' in order else order)
except Exception as e:
    print("❌ Order failed:", str(e))
EOF

# Notify the user on device
if command -v termux-toast &> /dev/null; then
    termux-toast "XLM add $AMOUNT at $PRICE" && termux-vibrate -d 300
else
    echo "XLM add $AMOUNT at $PRICE"
fi