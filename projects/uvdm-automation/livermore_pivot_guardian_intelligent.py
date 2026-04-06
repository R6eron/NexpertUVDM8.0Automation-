#!/usr/bin/env python3
"""
UVDM Wingman - Intelligent Livermore Pivot Guardian
XLM/USDT | 1.5 ATR + Volume & Momentum Filter | XRPEASY.CO.UK
Jesse100 eternal vigilance - Protects free ride without choking the long game
"""

import requests
import time
import pandas as pd
import talib
from datetime import datetime

print(f"🚀 UVDM Intelligent Livermore Pivot Guardian LIVE - XLM/USDT | {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
print("=" * 80)

PIVOT_FLOOR = 0.1490          # Hard Livermore line in sand
ATR_MULTIPLIER = 1.5          # Your requested base buffer
VOLUME_THRESHOLD = 1.5        # Volume spike filter
STOCH_RSI_THRESHOLD = 50      # Momentum fade filter

def get_xlm_data():
    """MEXC public API - last 100 1h candles"""
    try:
        url = "https://api.mexc.com/api/v3/klines?symbol=XLMUSDT&interval=1h&limit=100"
        response = requests.get(url, timeout=10)
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_base', 'taker_quote', 'ignore'])
        df = df.astype(float)
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        df['stoch_rsi_k'], _ = talib.STOCHRSI(df['close'], timeperiod=14, fastk_period=5, fastd_period=3)
        return df
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

# Main guard logic
df = get_xlm_data()

if df is not None:
    current_price = df['close'].iloc[-1]
    atr = df['atr'].iloc[-1]
    stoch_rsi = df['stoch_rsi_k'].iloc[-1]
    avg_volume = df['volume'].rolling(20).mean().iloc[-1]
    current_volume = df['volume'].iloc[-1]
    
    base_sl = current_price - (ATR_MULTIPLIER * atr)
    
    print(f"📊 Current Price:  ${current_price:.6f}")
    print(f"🛡️  1.5 ATR Buffer: ${ATR_MULTIPLIER * atr:.6f}")
    print(f"📈 StochRSI:       {stoch_rsi:.2f}")
    print(f"📊 Volume Spike:   {current_volume > VOLUME_THRESHOLD * avg_volume}")
    
    # Intelligent decision - only tighten on strong volume + bearish momentum
    if current_volume > VOLUME_THRESHOLD * avg_volume and stoch_rsi < STOCH_RSI_THRESHOLD:
        print(f"🔴 STRONG VOLUME + MOMENTUM FADE → Intelligent SL tightened to {base_sl:.5f}")
    else:
        print("🟢 Low-volume drift or no momentum fade → Holding current SL (no tightening)")
        
    if current_price <= PIVOT_FLOOR:
        print("🛑 CRITICAL: BELOW PIVOT FLOOR → Full defensive action")
        
else:
    print("❌ Data fetch failed → Default to safe hold")

print("=" * 80)
print("Jesse100 eternal vigilance | XRPEASY.CO.UK | Intelligent Pivot Guardian")
