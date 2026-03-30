#!/usr/bin/env python3
from xrpl.wallet import Wallet
w = Wallet.create()
print("🧠 BREATH ISSUER WALLET:")
print(f"Address: {w.classic_address}")
print(f"Seed:    {w.seed}")
print("SAVE THIS SEED SECURELY - PAPER BACKUP")
