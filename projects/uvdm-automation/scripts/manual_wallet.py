#!/usr/bin/env python3
from xrpl.wallet import Wallet
w = Wallet.create()
print("🧠 BREATH WALLET:")
print(f"Address: {w.classic_address}")
print(f"Seed:    {w.seed}")
print("💾 SAVE SEED SECURELY")
