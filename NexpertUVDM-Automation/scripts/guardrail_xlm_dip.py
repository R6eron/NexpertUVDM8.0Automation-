API_KEY=a6c6c86e-274d-4fc3-ae22-de5b481effd4

import os
import requests

API_KEY = os.getenv("NEXO_API_KEY", "")
API_SECRET = os.getenv("NEXO_API_SECRET", "")

if not API_KEY or not API_SECRET:
    raise RuntimeError("Set NEXO_API_KEY and NEXO_API_SECRET in your environment")

headers = {
    "X-NEXO-API-KEY": API_KEY,
    "X-NEXO-API-SIGNATURE": API_SECRET,
    "Content-Type": "application/json",
}

resp = requests.get("https://api.nexo.io/v1/balances", headers=headers, timeout=20)
print("Status:", resp.status_code)

if resp.status_code == 200:
    print("✅ LIVE")
    print(resp.text[:300])
else:
    print("❌ ERROR:", resp.text[:300])