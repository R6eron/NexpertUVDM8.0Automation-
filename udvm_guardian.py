#!/usr/bin/env python3
import requests
import pandas as pd
r = requests.get("https://api.binance.com/api/v3/klines?symbol=XLMUSDT&interval=1h&limit=1")
data = r.json()
df = pd.DataFrame(data)
price = float(df[4].iloc[0])
atr_raw = float(df[1].iloc[0]) - float(df[3].iloc[0])
sl = price - (atr_raw * 1.5)
print("🚀 UVDM LIVE XLM/USDT")
print("Price: $" + str(price))
print("1.5x ATR SL: $" + str(sl))
print("XRPEASY.CO.UK | Jesse100")
