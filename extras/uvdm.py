#!/usr/bin/env python3

POSITION = 109204
ENTRY = 0.16214
LIQUIDATION = 0.14617
TP1 = 0.25
TP2 = 0.50
TRAIL = 0.30

print("UVDM 9.0 - Jesse on.")
print(f"XLM Position: {POSITION} @ {ENTRY}")
print(f"Liquidation: {LIQUIDATION}")
print("---")

price = float(input("Enter current XLM price: "))

roe = ((price - ENTRY) / ENTRY) * 100
pnl = (price - ENTRY) * POSITION
print(f"Current ROE: {roe:.1f}%")
print(f"Unrealized PnL: {pnl:.2f}")

if roe >= TP2 * 100:
    print("SECOND TARGET HIT - Take another 33% now")
elif roe >= TP1 * 100:
    print("FIRST TARGET HIT - Take 33% profit now")
else:
    print("Hold - Let it run")

trail_stop = price * (1 - TRAIL)
print(f"30% trailing stop suggestion: {trail_stop:.5f}")

input("Press Enter to exit...")
