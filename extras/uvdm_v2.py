import time,os
from datetime import datetime

XLMPRICE  = 0.1512
ENTRY     = 0.1529
FLOOR     = 0.1490
VOLMA     = 790000
CAGR_TGT  = 0.20
SHARPE_TGT= 2.1

def log(m):
    ts=datetime.now().strftime('%H:%M')
    print(f'[{ts}] {m}')
    with open('uvdm.log','a') as f:f.write(f'[{ts}] {m}
')

cycle=0
while 1:
    cycle+=1
    vol=VOLMA*1.6  # spike sim
    pnl=(XLMPRICE-ENTRY)/ENTRY
    
    if XLMPRICE<FLOOR and vol>VOLMA*1.5:
        log(f'🚀 CYCLE {cycle} BUY! ${XLMPRICE:.5f} +{vol/1000:.0f}K vol')
    
    if pnl>0.25:
        log(f'🎯 TP25% → Sharpe {SHARPE_TGT:.1f}')
    
    if pnl>0.33:
        log(f'💰 TP33% → CAGR {CAGR_TGT*100:.1f}%')
    
    log(f'XLM ${XLMPRICE:.5f} PnL {pnl*100:+.1f}% LTV 58.82%')
    time.sleep(60)
