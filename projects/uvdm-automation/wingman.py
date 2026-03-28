#!/usr/bin/env python3
import os,time,ccxt
from dotenv import load_dotenv
load_dotenv()
ex=ccxt.mexc({'apiKey':os.getenv('MEXC_API_KEY'),'secret':os.getenv('MEXC_SECRET')})
print("UVDM Jesse100 LIVE")
FLOOR=0.1490
VMULT=1.5
_last=0
while 1:
 try:
  b=ex.fetch_balance()
  print("USDT:",b['total'].get('USDT','0'))
  c=ex.fetch_ohlcv('XLM/USDT','1h',limit=2)[-2]
  if c[0]>_last:
   _last=c[0]
   p=c[4]
   v=c[5]
   m=sum(x[5]for x in ex.fetch_ohlcv('XLM/USDT','1h',limit=20))/20
   print("XLM:",p,"Vol:",v,"MA:",m)
   if p<=FLOOR and v>VMULT*m:
    print("CUT!",p,v)
  time.sleep(30)
 except Exception as e:
  print("ERR:",e)
  time.sleep(10)
