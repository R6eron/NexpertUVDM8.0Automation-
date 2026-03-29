
# NOW paste Python code (NOT in terminal):
def update_intelligent_trail(pos):
    entry = pos['entryPrice']
    mark = pos['markPrice']
    roe = (mark - entry) / entry
    
    # FREE-RIDE LOCK
    if roe >= 0.10 and pos['stopLossPrice'] < entry * 1.001:
        set_stop_loss(entry * 1.001)
        log(f"FREE-RIDE: +{roe*100:.1f}% → breakeven")
    
    # PYRAMID DIPS
    if mark <= entry * 0.985 and spare_margin >= 100:
        place_limit_add(mark * 0.99)
    
    # PULLBACK ONLY
    if mark < entry * 0.97 and (volume_spike_down() or macd_bear_div()):
        new_sl = mark - atr() * 1.0
        if new_sl > pos['stopLossPrice']:
# Exit bash → Go to Python file
nano intelligent_trail.py

# NOW paste Python code (NOT in terminal):
def update_intelligent_trail(pos):
    entry = pos['entryPrice']
    mark = pos['markPrice']
    roe = (mark - entry) / entry
    
    # FREE-RIDE LOCK
    if roe >= 0.10 and pos['stopLossPrice'] < entry * 1.001:
        set_stop_loss(entry * 1.001)
        log(f"FREE-RIDE: +{roe*100:.1f}% → breakeven")
    
    # PYRAMID DIPS
    if mark <= entry * 0.985 and spare_margin >= 100:
        place_limit_add(mark * 0.99)
    
    # PULLBACK ONLY
    if mark < entry * 0.97 and (volume_spike_down() or macd_bear_div()):
        new_sl = mark - atr() * 1.0
        if new_sl > pos['stopLossPrice']:
            set_stop_loss(new_sl)
    
    # LOOSE TRAIL
    atr_trail = mark - (atr() * 1.5)
    if atr_trail > pos['stopLossPrice']:
        set_stop_loss(atr_trail)

# Ctrl+O → ENTER → Ctrl+X
# Exit bash → Go to Python file
nano intelligent_trail.py

# NOW paste Python code (NOT in terminal):
def update_intelligent_trail(pos):
    entry = pos['entryPrice']
    mark = pos['markPrice']
    roe = (mark - entry) / entry
    
    # FREE-RIDE LOCK
    if roe >= 0.10 and pos['stopLossPrice'] < entry * 1.001:
        set_stop_loss(entry * 1.001)
        log(f"FREE-RIDE: +{roe*100:.1f}% → breakeven")
    
    # PYRAMID DIPS
    if mark <= entry * 0.985 and spare_margin >= 100:
        place_limit_add(mark * 0.99)
    
    # PULLBACK ONLY
    if mark < entry * 0.97 and (volume_spike_down() or macd_bear_div()):
        new_sl = mark - atr() * 1.0
        if new_sl > pos['stopLossPrice']:
            set_stop_loss(new_sl)
    
    # LOOSE TRAIL
    atr_trail = mark - (atr() * 1.5)
    if atr_trail > pos['stopLossPrice']:
        set_stop_loss(atr_trail)

# Ctrl+O → ENTER → Ctrl+X
# You're at ~/NexpertUVDM-Automation $
pkill -f main_bot    # Kill old bot
nohup python3 main_bot.py > bot.log 2>&1 &  # Restart with trail
tmux attach empire   # Monitor P10 XLM 0.1665
1. Ctrl+O          → WRITE OUT (SAVE FILE)
2. ENTER           → Confirm "intelligent_trail.py"  
3. Ctrl+X          → EXIT NANO
            set_stop_loss(new_sl)
    
    # LOOSE TRAIL
    atr_trail = mark - (atr() * 1.5)
    if atr_trail > pos['stopLossPrice']:
        set_stop_loss(atr_trail)

# Ctrl+O → ENTER → Ctrl+X

# 4. ADD MORE DIP HUNTERS
# XRP: TARGET=0.45
# SGB: TARGET=0.015#!/bin/bash
TARGET=0.45          # XRP dip trigger
INTERVAL=30          # 30s checks  
LOG=~/xrp_dip.log

while true; do
  PRICE=$(curl -s "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT" | grep -o "[0-9]+.[0-9]+" | head -1)
  if (( $(echo "$PRICE <= $TARGET" | bc -l) )); then
    termux-vibrate -d 600
    echo "$(date) – XRP DIP HIT: $PRICE" >> "$LOG"
  fi
  sleep $INTERVAL
done

