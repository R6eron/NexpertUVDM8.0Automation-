#!/usr/bin/env python3
"""
Medium-Frequency Monitor with Volume Analysis + Speaking
"""

import sys
import time
import json
import urllib.request
import subprocess
from decimal import Decimal
from pathlib import Path

RUNTIME = Path.home() / ".config" / "uvdm" / "runtime"
RUNTIME.mkdir(parents=True, exist_ok=True)

def speak(text: str):
    """Termux TTS"""
    try:
        subprocess.run(["termux-tts-speak", text], check=False, timeout=5)
    except:
        pass

def get_price_and_volume():
    try:
        req_price = urllib.request.Request("https://api.binance.com/api/v3/ticker/price?symbol=XLMUSDT")
        with urllib.request.urlopen(req_price, timeout=10) as r:
            price = Decimal(json.loads(r.read().decode())["price"])

        req_vol = urllib.request.Request("https://api.binance.com/api/v3/ticker/24hr?symbol=XLMUSDT")
        with urllib.request.urlopen(req_vol, timeout=10) as r:
            vol = Decimal(json.loads(r.read().decode())["volume"])

        return price, vol
    except:
        return Decimal("0.19"), Decimal("1000000")

def main():
    print("Medium-Frequency Monitor Started (Speaking Enabled)")
    print("Press Ctrl+C to stop.\n")

    last_price, last_volume = get_price_and_volume()
    speak(f"Monitor started for XLM at ${last_price}")

    while True:
        price, volume = get_price_and_volume()
        price_change = ((price - last_price) / last_price) * 100
        volume_change = ((volume - last_volume) / last_volume) * 100 if last_volume > 0 else 0

        status = f"XLM ${price:.6f} | {price_change:.2f}% | Vol {volume_change:+.1f}%"
        print(status)

        if price_change <= Decimal("-0.5") and volume_change > Decimal("20"):
            msg = f"Strong pullback detected with volume. Price ${price:.6f}."
            speak(msg)
            print("🔴 STRONG SIGNAL - Consider ladder")

        last_price = price
        last_volume = volume
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Monitor stopped.")
        print("\nMonitor stopped.")
