import os
import requests

k = os.getenv("NEXO_API_KEY", "")
if not k:
    raise RuntimeError("NEXO_API_KEY not set in environment")

headers = {"X-NEXO-API-KEY": k}
r = requests.get("https://api.nexo.io/v1/balances", headers=headers)

print("Status:", r.status_code)
print("✅ LIVE" if r.status_code == 200 else "❌ ERROR:", r.text[:300])