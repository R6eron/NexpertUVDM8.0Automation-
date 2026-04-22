#!/usr/bin/env python3
import requests
import time

# YOUR 61K LONG POSITION
entry = 0.1620
size = "61K"
pivot = 0.1468  

print("🚀 XLM",size,"LONG @ $"+str(entry))
print("Pivot: $"+str(pivot))
print("Ctrl+C to stop")

while True:
    try:
        r = requests.get("https://api.bitrue.com/api/v1/spot/ticker?symbol=XLMUSDT")
        data = r.json()
        price = float(data['data'][0]['lastPrice'])
        pnl_pct = (price-entry)/entry*100
        pnl_usd = pnl_pct/100*61000
        
        ts = time.strftime("%H:%M:%S")
        status = ""
        if price < pivot:
            status = "🔔 PIVOT BREACH!"
            print("a")  # Terminal beep
        elif pnl_pct > 25:
            status = "💎 MOONSHOT!"
        elif pnl_pct < -15:
            status = "🚨 DANGER ZONE!"
            
        print(("[{}] XLM ${:.5f} | PnL %{:+.2f} (${:+.0f}) {}").format(ts,price,pnl_pct,pnl_usd,status))
        
    except:
        print("["+time.strftime("%H:%M:%S")+"] ERROR")
    
    time.sleep(15)  # Faster updates
