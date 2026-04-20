#!/usr/bin/env python3
import ccxt, os, time
from datetime import datetime

exchange = ccxt.mexc({
    'apiKey': os.getenv('MEXC_API_KEY'),
    'secret': os.getenv('MEXC_SECRET'),
    'sandbox': False,  # LIVE
    'enableRateLimit': True,
})

PIVOT_FLOOR = 0.149
USDT_DEPLOYED = False

print("🚀 XRPEASY CCXT LIVE | Keys:", "✅" if exchange.apiKey else "❌")

while True:
    try:
        ticker = exchange.fetch_ticker('XLM/USDT')
        p = ticker['last']
        print(f"XLM ${p:.6f} | USDT: {'READY' if not USDT_DEPLOYED else 'DEPLOYED'}")
        
        if p <= PIVOT_FLOOR * 0.97 and not USDT_DEPLOYED:
            print("🌊 LIVE USDT→XLM DEPLOYMENT")
            balance = exchange.fetch_balance()
            usdt_free = balance['USDT']['free']
            if usdt_free > 10:
                order = exchange.create_market_buy_order('XLM/USDT', usdt_free*0.95/ p)
                print(f"✅ BOUGHT {order['filled']} XLM | ID: {order['id']}")
            USDT_DEPLOYED = True
        
        elif p >= PIVOT_FLOOR * 1.05:
            USDT_DEPLOYED = False
            print("🔄 USDT READY")
            
    except Exception as e:
        print(f"❌ {e}")
    
    time.sleep(60)
