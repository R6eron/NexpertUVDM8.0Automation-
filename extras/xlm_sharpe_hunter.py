#!/data/data/com.termux/files/usr/bin/python3
import requests,time,subprocess,json,os,numpy as np
from datetime import datetime
from collections import deque

SYMBOL = "stellar"
TARGET = 0.16
TOLERANCE = 0.0005
INTERVAL = 180  # 3min (sharpe optimized)
VIBRATE_MS = 800
VOL_WINDOW = 10  # rolling volatility

prices = deque(maxlen=VOL_WINDOW)

def get_price():
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={SYMBOL}&vs_currencies=usd", timeout=10)
        return float(r.json().get(SYMBOL, {}).get("usd", 0))
    except:
        return 0

def calc_sharpe():
    if len(prices) < 2: return 0
    returns = np.diff(list(prices))/list(prices)[:-1]
    return np.mean(returns)/np.std(returns)*np.sqrt(252/INTERVAL) if np.std(returns)>0 else 0

def alert(msg):
    subprocess.run(["termux-vibrate", "-d", str(VIBRATE_MS)])
    subprocess.run(["termux-tts-speak", f"XLM pyramid zone. {msg}"])
    subprocess.run(["termux-notification", "--title", "🦈 XLM SHARPE HIT", "--content", msg])

print("🚀 XRPEASY SHARPE-OPTIMIZED XLM HUNTER v2.0 | Target: $0.16")
print("📊 Real-time Sharpe + volatility tracking")
print("📱 800ms SHAKE + optimized 3min heartbeat")

while True:
    price = get_price()
    if price > 0:
        prices.append(price)
        now = datetime.now().strftime("%H:%M:%S")
        sharpe = calc_sharpe()
        vol = np.std(list(prices))/np.mean(list(prices))*100 if len(prices)>1 else 0
        
        print(f"[{now}] XLM:${price:.5f} | Sharpe:{sharpe:.3f} | Vol:{vol:.1f}% | n={len(prices)}")
        
        if price <= TARGET + TOLERANCE:
            msg = f"SHARPE BUY ZONE! ${price:.5f} | Sharpe:{sharpe:.3f}"
            alert(msg)
            print(f"🦈 {msg} → PYRAMID $50+ NOW")
            time.sleep(INTERVAL * 3)  # extended cooldown
    time.sleep(INTERVAL)
