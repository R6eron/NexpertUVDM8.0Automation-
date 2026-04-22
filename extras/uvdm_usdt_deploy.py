#!/usr/bin/env python3
# UVDM SWING DETECTOR - 60min rolling avg + volume
import requests, time, collections, os
from datetime import datetime

prices = collections.deque(maxlen=60)
API_KEY = os.getenv('MEXC_API_KEY')

print("🚀 UVDM SWING LIVE | Keys:", "✅" if API_KEY else "❌")

while True:
    try:
        ticker = requests.get("https://api.mexc.com/api/v3/ticker/24hr?symbol=XLMUSDT", timeout=10).json()
        p = float(ticker['lastPrice'])
        prices.append(p)
        
        if len(prices) >= 60:
            avg_price = sum(prices) / 60
            print(f"XLM ${p:.6f} | 60m AVG ${avg_price:.6f} | Swing: {'ARMED' if p < avg_price*0.95 else 'HOLD'}")
            if p < avg_price * 0.95:
                print(f"🌊 UVDM SWING TRIGGER! ${p:.6f} < ${avg_price*0.95:.6f}")
        else:
            print(f"Warmup {len(prices)}/60 | XLM ${p:.6f}")
            
    except Exception as e:
        print(f"❌ {e}")
    
    time.sleep(60)
