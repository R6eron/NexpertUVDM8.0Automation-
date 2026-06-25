#!/usr/bin/env python3
import os, time, json, requests
from urllib.parse import quote

WHATSAPP_TO = os.getenv('WHATSAPP_TO', '447856297362')
CALLMEBOT_APIKEY = os.getenv('CALLMEBOT_APIKEY', '')
STATE_FILE = 'runtime/favorite_setup_state_bitrue_ftso.json'
MIN_SCORE_TO_ALERT = 70
INTERVALS = ['15m', '30m', '1h']
LIMIT = 120

ASSETS = {
    'XLMUSDT': {'asset':'XLM','symbol':'XLMUSDT'},
    'XRPUSDT': {'asset':'XRP','symbol':'XRPUSDT'},
    'HBARUSDT': {'asset':'HBAR','symbol':'HBARUSDT'},
    'XDCUSDT': {'asset':'XDC','symbol':'XDCUSDT'},
    'FLRUSDT': {'asset':'FLR','symbol':'FLRUSDT'},
    'SGBUSDT': {'asset':'SGB','symbol':'SGBUSDT'},
}

BITRUE_KLINES = 'https://openapi.bitrue.com/api/v1/klines'
BITRUE_TICKER = 'https://openapi.bitrue.com/api/v1/ticker/price'

def ema(values, n):
    k = 2/(n+1)
    out, e = [], None
    for v in values:
        e = v if e is None else (v*k + e*(1-k))
        out.append(e)
    return out

def sma(values, n):
    out, s = [], 0.0
    for i, v in enumerate(values):
        s += v
        if i >= n:
            s -= values[i-n]
        out.append(s/n if i >= n-1 else None)
    return out

def stddev(values, n):
    out = []
    for i in range(len(values)):
        if i < n-1:
            out.append(None)
            continue
        w = values[i-n+1:i+1]
        m = sum(w)/n
        out.append((sum((x-m)**2 for x in w)/n)**0.5)
    return out

def rsi(values, n=14):
    gains, losses = [0.0], [0.0]
    for i in range(1, len(values)):
        d = values[i] - values[i-1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    ag = sma(gains, n)
    al = sma(losses, n)
    out = []
    for g, l in zip(ag, al):
        if g is None or l is None:
            out.append(None)
        elif l == 0:
            out.append(100.0)
        else:
            rs = g/l
            out.append(100 - (100/(1+rs)))
    return out

def macd(values, fast=12, slow=26, signal=9):
    ef = ema(values, fast)
    es = ema(values, slow)
    line = [a-b for a, b in zip(ef, es)]
    sig = ema(line, signal)
    hist = [a-b for a, b in zip(line, sig)]
    return line, sig, hist

def get_bitrue_klines(symbol, interval, limit=LIMIT):
    r = requests.get(BITRUE_KLINES, params={'symbol':symbol, 'interval':interval, 'limit':limit}, timeout=20)
    r.raise_for_status()
    rows = r.json()
    return {
        'open': [float(x[1]) for x in rows],
        'high': [float(x[2]) for x in rows],
        'low': [float(x[3]) for x in rows],
        'close': [float(x[4]) for x in rows],
        'vol': [float(x[5]) for x in rows],
    }

def get_bitrue_spot(symbol):
    r = requests.get(BITRUE_TICKER, params={'symbol':symbol}, timeout=20)
    r.raise_for_status()
    return float(r.json()['price'])

def analyze(symbol, interval):
    d = get_bitrue_klines(symbol, interval)
    c, h, l, v = d['close'], d['high'], d['low'], d['vol']
    last = c[-1]
    s20 = sma(c, 20)
    sd20 = stddev(c, 20)
    lower = s20[-1] - 2*sd20[-1]
    upper = s20[-1] + 2*sd20[-1]
    band_pos = 0.5 if upper == lower else (last - lower) / (upper - lower)
    rrsi = rsi(c, 14)[-1]
    _, _, mhist = macd(c)
    trend_ema = ema(c, 20)[-1]
    recent_low = min(l[-5:])
    recent_high = max(h[-5:])
    score, tags = 0, []

    if band_pos <= 0.18:
        score += 25; tags.append('lower_bollinger_tag')
    if rrsi is not None and rrsi < 38:
        score += 20; tags.append('rsi_soft_oversold')
    if last > c[-2] and c[-2] <= recent_low * 1.01:
        score += 15; tags.append('bounce_from_recent_low')
    if mhist[-1] > mhist[-2]:
        score += 10; tags.append('macd_hist_improving')
    if abs(last - trend_ema) / trend_ema < 0.015:
        score += 10; tags.append('ema20_reclaim_zone')
    if abs(recent_high - last) / last < 0.01:
        score += 10; tags.append('near_breakout_pressure')

    setup = 'watch'
    if score >= 80:
        setup = 'high_probability_reclaim'
    elif score >= 70:
        setup = 'probable_bounce'
    elif score <= 20 and band_pos > 0.65:
        setup = 'avoid_chase'

    return {
        'symbol': symbol,
        'interval': interval,
        'last': last,
        'lower_bb': lower,
        'upper_bb': upper,
        'band_pos': band_pos,
        'rsi14': rrsi,
        'ema20': trend_ema,
        'recent_low': recent_low,
        'recent_high': recent_high,
        'score': int(score),
        'setup': setup,
        'tags': tags,
    }

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
                print('ANALYZE_FAIL', meta['symbol'], tf, repr(e))
        return {'last_alerts': {}}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def send_whatsapp(text):
    if not CALLMEBOT_APIKEY:
        return False
    url = f'https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_TO}&text={quote(text)}&apikey={CALLMEBOT_APIKEY}'
    requests.get(url, timeout=20)
    return True

def format_alert(item):
    return (
        f"{item['asset']} {item['interval']} {item['setup']} | score {item['score']} | "
        f"Bitrue {item['spot']} | bb_low {item['lower_bb']:.6f} | rsi {item['rsi14']:.1f} | "
        f"tags: {', '.join(item['tags'])}"
    )

def rank_setups():
    ranked = []
    for symbol, meta in ASSETS.items():
        best = None
        try:
            spot = get_bitrue_spot(meta['symbol'])
        except Exception as e:
                print('ANALYZE_FAIL', meta['symbol'], tf, repr(e))
            spot = None
        for tf in INTERVALS:
            try:
                a = analyze(meta['symbol'], tf)
            except Exception as e:
                print('ANALYZE_FAIL', meta['symbol'], tf, repr(e))
                continue
            if best is None or a['score'] > best['score']:
                best = a
        if best:
            best['asset'] = meta['asset']
            best['spot'] = spot
            ranked.append(best)
    ranked.sort(key=lambda x: -x['score'])
    return ranked

def main():
    ranked = rank_setups()
    state = load_state()
    print('Top setups:')
    for item in ranked:
        line = format_alert(item)
        print(line)
        key = f"{item['symbol']}:{item['interval']}"
        prev = state['last_alerts'].get(key, {})
        if item['score'] >= MIN_SCORE_TO_ALERT and (prev.get('score') != item['score'] or prev.get('setup') != item['setup']):
            send_whatsapp(line)
            state['last_alerts'][key] = {'score': item['score'], 'setup': item['setup'], 'ts': int(time.time())}
    save_state(state)

if __name__ == '__main__':
    main()
