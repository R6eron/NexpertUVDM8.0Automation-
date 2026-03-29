#!/bin/bash
AMOUNT=50
PRICE=0.166
SYMBOL="XLMUSDT"
echo "$(date) - Placing limit buy: $AMOUNT USDT at $PRICE for $SYMBOL" >> \~/add_log.log
# Replace with your Bitrue API call - example placeholder
curl -X POST "https://api.bitrue.com/api/v1/futures/order" \
  -H "X-API-KEY: your_key_here" \
  -H "Content-Type: application
AMOUNT=50
PRICE=0.166
SYMBOL="XLMUSDT"
echo "$(date) - Adding $AMOUNT USDT at $PRICE" >> add_log.log

python3 - <<EOF >> add_log.log 2>&1
import ccxt
exchange = ccxt.bitrue()  # loads your keys from config
order = exchange.create_limit_buy_order(SYMBOL, AMOUNT / PRICE, PRICE, {leverage: 7})
print("Order placed:", order)
EOF

termux-toast "XLM add $AMOUNT at $PRICE" && termux-vibrate -d 300
