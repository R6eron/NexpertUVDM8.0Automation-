#!/usr/bin/env python3
import ccxt, pandas as pd, pandas_ta as ta, time, os
from datetime import datetime

PAIR = 'XLM/USDT'
TF   = '1h'

API_KEY = os.getenv('MEXC_API_KEY')
API_SECRET = os.getenv('MEXC_SECRET')

exchange = ccxt.mexc({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

def lambo_upthrust(df, resistance):
    df['avg_vol'] = df['volume'].rolling(20).mean()
    df['rsi'] = ta.rsi(df['close'], 14)
    last = df.iloc[-1]
    up_break = last['high'] > resistance
    reject   = last['close'] <= resistance
    low_vol  = last['volume'] < last['avg_vol'] * 0.8
    wick     = (last['high'] - last['close']) > 2 * (last['close'] - last['open'])
    ob       = last['rsi'] > 75
    return up_break and reject and low_vol and wick and ob

print("🚀 LAMBO UVDM LIVE | XLM/USDT 1h | Upthrust fade engine")
while True:
    try:
        bars = exchange.fetch_ohlcv(PAIR, TF, limit=60)
        df = pd.DataFrame(bars, columns=['time','open','high','low','close','volume'])
        resistance = df['high'].rolling(10).max().iloc[-2]
        price = df['close'].iloc[-1]
        signal = lambo_upthrust(df, resistance)
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        line = f"{now} UTC | {PAIR} {price:.4f} | R={resistance:.4f}"
        if signal:
            print(line + " | 🚀 SHORT SIGNAL – FADE UPTHRUST")
            print("  → ACTION: CLOSE LONG / OPEN SHORT (max 3x)")
        else:
            print(line + " | no signal")
        time.sleep(300)
    except Exception as e:
        print(f"ERROR {datetime.utcnow().strftime('%H:%M')}: {e}")
        time.sleep(60)

        # PYRAMID LONG (markup phase)
        support = df['low'].rolling(10).min().iloc[-2]
        pullback = price <= support * 1.02  # 2% pullback
        vol_surge = df['volume'].iloc[-1] > df['avg_vol'] * 1.5
        rsi_oversold = df['rsi'].iloc[-1] < 35
        
        if pullback and vol_surge and rsi_oversold:
            print(f"📈 PYRAMID LONG | XLM ${price:.4f} | S:{support:.4f}")
            # LONG: 0.25% risk (safer than shorts)
            long_amount = (balance * 0.0025 / price) * 5
            long_order = ex.create_market_buy_order('XLM/USDT', long_amount)
            print(f"  🟢 LONG {long_amount:.0f}XLM @${price:.4f} | {long_order['id']}")

        # FLARE SPOT GROWTH (5% pullbacks)
        try:
            flr_price = ex.fetch_ticker('FLR/USDT')['last']
            if flr_price <= flr_sma * 0.95:  # 5% pullback
                flr_amount = balance * 0.1 / flr_price  # 10% allocation
                flr_order = ex.create_market_buy_order('FLR/USDT', flr_amount)
                print(f"🔥 FLARE SPOT BUY {flr_amount:.0f}FLR @${flr_price:.4f}")
        except:
            pass

        # XLM TOP-UP (profits → spot)
        if balance > start_balance * 1.05:  # 5% profit
            xlm_topup = (balance - start_balance) * 0.3 / price  # 30% to spot
            print(f"💰 XLM TOP-UP {xlm_topup:.0f}XLM → Nexo transfer")
