#!/usr/bin/env python3
print("UVDM 10.0 IMMORTAL HEXERS")
print("Position: 0x9f1a2b3c4d5e6f78910a11b12c13d14e15f16a17b18c19d20e21f22a23b24c25d26e27f28")
print("Livermore Guardian + Wyckoff ACTIVE")

asset = input("Asset (XLM/HEX/XRP): ")
price = float(input("Current price: "))

pivot = 0.16214
if price > pivot * 1.05:
    print("LIVMORE PIVOT BREAKOUT - BUY STRENGTH")
elif price < pivot * 0.95:
    print("PIVOT BREAKDOWN - PROTECT CAPITAL")
else:
    print("Range - Wait for pivot")

prev_price = float(input("Previous candle close: "))
if prev_price > price * 1.02 and price < pivot:
    print("WYCKOFF DIP THRUST - ADD if funds available")
else:
    print("Monitor for thrust")

input("Press Enter...")
