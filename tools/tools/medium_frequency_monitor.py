#!/usr/bin/env python3
import sys, time, json, urllib.request, subprocess
from decimal import Decimal
from pathlib import Path

RUNTIME = Path.home() / ".config" / "uvdm" / "runtime"
RUNTIME.mkdir(parents=True, exist_ok=True)

def c(code): return chr(27) + "[" + code + "m"
C_YELLOW = c("1;33"); C_GREEN = c("1;32"); C_MAGENTA = c("1;35"); C_CYAN = c("36"); C_RESET = c("0")

def speak(text):
    try: subprocess.run(["termux-tts-speak", text], check=False, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def get_market_data():
    try:
        req = urllib.request.Request("https://api.binance.com/api/v3/ticker/24hr?symbol=XLMUSDT")
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return Decimal(data["lastPrice"]), Decimal(data["volume"])
    except: return Decimal("0.19"), Decimal("1000000")

def main():
    print("⚡ UVDM Monitor: Smart Trail & Demand Zones")
    print("Press Ctrl+C or type 'uvkill' in a new tab to stop.")
    print("")

    last_price, last_volume = get_market_data()
    speak(f"Smart trail monitor live. XLM at ${last_price:.4f}")

    local_low = last_price
    hunting = False
    
    DROP_TRIGGER = Decimal("-0.01")
    TRAIL_TRIGGER = Decimal("0.01")
    
    USDT_BUDGET = "20"
    ASSET = "XLM"
    MODE = "futures"
    LEVERAGE = "3x"
    STRATEGY = "2"

    while True:
        price, volume = get_market_data()

        if last_price == 0: last_price = price
        if last_volume == 0: last_volume = volume

        price_change = ((price - last_price) / last_price) * 100
        volume_change = ((volume - last_volume) / last_volume) * 100

        if price < local_low: local_low = price

        if not hunting and price_change <= DROP_TRIGGER and volume_change > Decimal("5"):
            hunting = True
            local_low = price
            speak("Liquidity drop detected. Hunting mode engaged.")
            print("")
            print(f"{C_YELLOW}🎯 HUNTING MODE: Tracking for bottom. Local low locked at ${local_low:.6f}{C_RESET}")

        abs_change = abs(price_change)
        sleep_time = 10 if hunting else (15 if abs_change >= Decimal("0.25") else (60 if abs_change < Decimal("0.05") else 30))
        pace = "HUNT" if hunting else ("FAST" if sleep_time == 15 else ("SLOW" if sleep_time == 60 else "NORM"))

        status = f"XLM ${price:.6f} | {price_change:+.2f}% | Vol {volume_change:+.1f}% | {pace}"
        
        if hunting:
            bounce = ((price - local_low) / local_low) * 100
            status += f" | {C_MAGENTA}Trail: {bounce:+.2f}% / {TRAIL_TRIGGER}%{C_RESET}"
            
            if bounce >= TRAIL_TRIGGER:
                speak("Demand zone bounce confirmed. Executing ladder.")
                print("")
                print(f"{C_GREEN}✅ DEMAND ZONE CONFIRMED! Bounced {bounce:.2f}% off ${local_low:.6f}{C_RESET}")
                print(f"{C_CYAN}Auto-Deploying: {USDT_BUDGET} {ASSET} {MODE} {LEVERAGE} (Ladder){C_RESET}")
                print("")
                
                subprocess.run(["deploy", USDT_BUDGET, ASSET, MODE, LEVERAGE, STRATEGY])
                
                hunting = False
                local_low = price

        print(status)
        last_price = price
        last_volume = volume
        time.sleep(sleep_time)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        speak("Monitor stopped.")
        print("")
        print("Monitor stopped.")
