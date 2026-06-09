#!/usr/bin/env python3
import requests
import os
import time
from datetime import datetime, timezone

PIVOT = 0.1468
BUFFER = 0.0015
SYMBOL = 'FLRUSDT'
API_URL = f'https://api.mexc.com/api/v3/ticker/24hr?symbol={SYMBOL}'
STATE_PATH = os.path.expanduser('~/.flreasy_pivot_state')

print(f"[FLREASY] LIVERMORE PIVOT GUARD | {datetime.now().strftime('%H:%M GMT')}")

def fetch_xrp_stats():
    try:
        resp = requests.get(API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        price = float(data['lastPrice'])
        change = float(data['priceChangePercent'])
        return price, change
    except Exception as e:
        print(f'[ERROR] API ERROR: {e}')
        return None, None

def classify_pivot_state(price, change):
    if price is None:
        return 'API_ERROR', 'no_data'
    if price >= PIVOT + BUFFER:
        if change is not None and change > 3.0:
            return 'BULL_PIVOT_CONFIRMED', 'positive'
        return 'ABOVE_PIVOT_WEAK', 'positive_weak'
    if price <= PIVOT - BUFFER:
        if change is not None and change < -3.0:
            return 'BEAR_PIVOT_CONFIRMED', 'negative'
        return 'BELOW_PIVOT_WEAK', 'negative_weak'
    return 'AT_PIVOT_ZONE', 'neutral'

def classify_spring_conditions(price):
    if price is None:
        return 'unknown'
    if price <= PIVOT - BUFFER:
        return 'spring_conditions_active'
    if PIVOT - BUFFER < price < PIVOT + BUFFER:
        return 'spring_test_zone'
    return 'follow_through_zone'

def write_pivot_state(state, follow_through, spring_condition, price, change):
    ts = datetime.now(timezone.utc).isoformat()
    safe_price = price if price is not None else 0.0
    safe_change = change if change is not None else 0.0
    try:
        with open(STATE_PATH, 'w', encoding='utf-8') as f:
            f.write(f'{ts},{state},{follow_through},{spring_condition},{safe_price:.6f},{safe_change:+.2f}')
    except Exception as e:
        print(f'[WARN] STATE WRITE ERROR: {e}')

price, change = fetch_xrp_stats()
state, follow_through = classify_pivot_state(price, change)
spring_condition = classify_spring_conditions(price)

if price is not None:
    print(f'[DATA] FLR/USDT: ${price:.6f} | 24h: {change:+.2f}% | STATE: {state} | FOLLOW_THRU: {follow_through} | SPRING: {spring_condition}')
else:
    print('[ERROR] INITIAL API ERROR - RETRYING')

write_pivot_state(state, follow_through, spring_condition, price, change)
print('[LIVE] UVDM LIVERMORE SENTINEL LIVE - Ctrl+C to exit')

while True:
    time.sleep(60)
    price, change = fetch_xrp_stats()
    state, follow_through = classify_pivot_state(price, change)
    spring_condition = classify_spring_conditions(price)

    if price is not None:
        print(f"[{datetime.now().strftime('%H:%M')}] FLR: ${price:.6f} ({change:+.2f}%) -> {state} | FOLLOW_THRU: {follow_through} | SPRING: {spring_condition}")

    write_pivot_state(state, follow_through, spring_condition, price, change)
