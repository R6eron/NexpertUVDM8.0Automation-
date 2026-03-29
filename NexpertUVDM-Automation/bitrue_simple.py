# BITRUE SIMPLE v1.0 – NO COMPILATION – LIVE NOW
import requests,time,os
from datetime import datetime

API_KEY="1a09b266449b93c7b09f49f4b63dd05ed9c39eabe7fdc6086e3db94511611cb6"
SECRET="92c073bee88ae4e6cea6d6d8720b14201095b7797612c3af3df658cb769aa7c2"
pivot=0.1468
entry=0.1529
logfile="bitrue_simple.log"

def log(msg):
 ts=datetime.now().strftime("%H:%M")
 line=f"[{ts}]{msg}"
 print(line)
 open(logfile,"a").write(line+"
")

def get_price():
 try:
  r=requests.get("https://api.bitrue.com/api/v1/spot/ticker?symbol=XLMUSDT",timeout=10)
  return float(r.json()['data'][0]['lastPrice'])
 except:
  return 0

while True:
 price=get_price()
 if price>0:
  pnl=(price-entry)/entry*100
  log(f"XLM${price:.5f} PnL{pnl:+.1f}% {'🗡️PIVOT!' if price<pivot*0.985 else ''}")
 time.sleep(60)
