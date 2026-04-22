#!/usr/bin/env python3
import time,ccxt
ex=ccxt.mexc()
print("🎯 UVDM Jesse100 PUBLIC LIVE")
FLOOR=0.1490
VMULT=1.5
_last=0
while True:
 try:
  print("📊 PUBLIC OK")
  c=ex.fetch_ohlcv('XLM/USDT','1h',limit=2)[-2]
  if c[0]>_last:
   _last=c[0]
   p=c[4]
   v=c[5]
   m=sum(x[5]for x in ex.fetch_ohlcv('XLM/USDT','1h',limit=20))/20
   print(f"XLM: {p:.4f} Vol: {v:,.0f} MA: {m:,.0f}")
   if p<=FLOOR and v>VMULT*m:
    print("🔥 JESSE100 CUT! BUY NOW",p,v)
  print("✅ Hunting volume spikes...")
  time.sleep(30)
 except Exception as e:
  print("ERR:",e)
  time.sleep(10)
