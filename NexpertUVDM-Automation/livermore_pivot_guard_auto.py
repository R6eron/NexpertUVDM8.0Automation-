#!/usr/bin/env python3
import requests
import os
import time
from datetime import datetime

print(f"🚀 XRPEASY LIVEMORE PIVOT GUARD | {datetime.now().strftime('%H:%M GMT')}")

def fetch_xrp_price():
    try:
        url = "https://api.mexc.com/api/v3/ticker/24hr?symbol=XRPUSDT"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        price = float(data[0]['lastPrice'])
        change = float(data[0]['priceChangePercent'])
        return price, change
    except:
        return None, None

price, change = fetch_xrp_price()
if price:
    print(f"📊 XRP/USDT: ${price:.6f} | 24h: {change:+.2f}%")
    
    if change > 5.0:
        print("🟢 BULLISH PIVOT DETECTED → UDVM FLYWHEEL DEPLOY")
    elif change < -5.0:
        print("🔴 BEARISH PIVOT → TRAILING STOP ACTIVATED")
    else:
        print("🟡 NEUTRAL → MONITORING")
else:
    print("❌ API ERROR - RETRYING")

print("🔄 UDVM SENTINEL LIVE - Ctrl+C to exit")
while True:
    time.sleep(60)
    price, change = fetch_xrp_price()
    if price:
        print(f"[{datetime.now().strftime('%H:%M')}] XRP: ${price:.6f} ({change:+.2f}%)")
