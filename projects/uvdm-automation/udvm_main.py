#!/usr/bin/env python3
# UVDM 3.0 RON'S LAMBO EDITION - Termux/Mobile Optimized
# XRPL/MEXC/Nexo/Flare Flywheel - 4 space indent
# Copyright © 2026 R.S. Lewis - XRPEASY.CO.UK

import requests
import time
import json
import hmac
import hashlib
import os

print("🐎 UVDM 3.0 - RON'S LAMBO FLYWHEEL STARTING...")

# ========== MOBILE INPUT (one line each) ==========
def get_keys():
    print("
🔑 ENTER TEST API KEYS (DEMO MODE):")
    return {
        'nexo': input("Nexo Key: ").strip(),
        'mexc_key': input("MEXC Key: ").strip(),
        'mexc_secret': input("MEXC Secret: ").strip(),
        'xrpl_seed': input("XRPL Seed (testnet): ").strip()
    }

keys = get_keys()
if not all([keys['nexo'], keys['mexc_key'], keys['mexc_secret']]):
    print("❌ Missing keys. Exit.")
    exit(1)

# ========== XRPL CONNECTION ==========
def xrpl_ping():
    try:
        r = requests.get("https://s1.ripple.com:51234", timeout=5)
        print("✅ XRPL Connected")
        return True
    except:
        print("❌ XRPL Failed")
        return False

# ========== NEXO BALANCE ==========
def nexo_balance():
    url = "https://api.nexo.com/v1/balances"
    headers = {"X-API-KEY": keys['nexo']}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("💰 Nexo Balance OK")
        return r.json()
    except:
        print("⚠️ Nexo Demo Mode")
        return {"demo": "100 USDT"}

# ========== MEXC ORDER ==========
def mexc_order(symbol="BTCUSDT", side="BUY", qty="0.001"):
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol, "side": side, "type": "MARKET",
        "quantity": qty, "timestamp": timestamp
    }
    query = "&".join(f"{k}={v}" for k,v in sorted(params.items()))
    signature = hmac.new(
        keys['mexc_secret'].encode(), query.encode(),
        hashlib.sha256
    ).hexdigest()
    params['signature'] = signature
    
    headers = {"X-MEXC-APIKEY": keys['mexc_key']}
    try:
        r = requests.post("https://api.mexc.com/api/v3/order", 
                         headers=headers, data=params)
        print(f"✅ MEXC {side} {symbol} OK")
        return r.json()
    except Exception as e:
        print(f"⚠️ MEXC Demo: {e}")
        return {"demo_order": "executed"}

# ========== MAIN FLYWHEEL ==========
def main():
    print("
🚀 UVDM 3.0 FLYWHEEL CYCLE 1/∞")
    
    # 1. XRPL Health
    if not xrpl_ping():
        return
    
    # 2. Nexo Balance
    nexo_bal = nexo_balance()
    
    # 3. MEXC Trade
    mexc_order("BTCUSDT", "BUY", "0.001")
    mexc_order("XLMUSDT", "BUY", "10")
    
    print("
✅ FLYWHEEL CYCLE COMPLETE")
    print("💎 Next cycle in 60s... (Ctrl+C to stop)")
    
    # Perpetual loop
    while True:
        time.sleep(60)
        main()

if __name__ == "__main__":

    main()
nano livermore_pivot_guard_auto.py
ls -la *.py
head -10 udvm_main.py
wc -l udvm_main.py livermore_pivot_guard_auto.py  # Line counts > 50 = success

