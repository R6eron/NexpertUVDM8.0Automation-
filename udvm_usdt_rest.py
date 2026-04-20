#!/usr/bin/env python3
import requests, hmac, hashlib, time, os, json
from datetime import datetime

API_KEY = os.getenv('MEXC_API_KEY')
SECRET = os.getenv('MEXC_SECRET')

def mexc_request(method, endpoint, params={}):
    timestamp = str(int(time.time() * 1000))
    query = '&'.join([f"{k}={v}" for k,v in params.items()])
    query += f"&timestamp={timestamp}"
    signature = hmac.new(SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    headers = {'X-MEXC-APIKEY': API_KEY, 'Content-Type': 'application/json'}
    url = f"https://api.mexc.com{endpoint}?{query}&signature={signature}"
    return requests.get(url, headers=headers).json()

print("🚀 XRPEASY REST-API LIVE | Keys:", "✅" if API_KEY else "❌")

PIVOT_FLOOR = 0.149
USDT_DEPLOYED = False

while True:
    try:
        ticker = requests.get("https://api.mexc.com/api/v3/ticker/price?symbol=XLMUSDT").json()
        p = float(ticker['price'])
        
        print(f"XLM ${p:.6f} | USDT: {'READY' if not USDT_DEPLOYED else 'DEPLOYED'} | {datetime.now().strftime('%H:%M')}")
        
        # USDT DEPLOYMENT LOGIC (market buy when spring)
        if p <= PIVOT_FLOOR * 0.97 and not USDT_DEPLOYED and API_KEY:
            print("🌊 SPRING → USDT DEPLOY TRIGGER")
            # LIVE BUY ORDER (uncomment when ready):
            # balance = mexc_request('/api/v3/account')
            # usdt_free = next(b['free'] for b in balance['balances'] if b['asset']=='USDT')
            # order = requests.post("https://api.mexc.com/api/v3/order", 
            #     data={'symbol':'XLMUSDT','side':'BUY','type':'MARKET','quoteOrderQty':str(usdt_free*0.95)})
            USDT_DEPLOYED = True
        
        elif p >= PIVOT_FLOOR * 1.05:
            USDT_DEPLOYED = False
            print("🔄 USDT READY")
            
    except Exception as e:
        print(f"❌ {e}")
    
    time.sleep(60)
