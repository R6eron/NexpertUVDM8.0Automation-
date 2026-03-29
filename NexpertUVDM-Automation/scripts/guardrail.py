import requests
k = "a6c6c86e-274d-4fc3-ae22-de5b481effd4"
headers = {"X-NEXO-API-KEY": k}
r = requests.get("https://api.nexo.io/v1/balances", headers=headers)
print("Status:", r.status_code)
print("✅ LIVE" if r.status_code == 200 else "❌ ERROR:", r.text[:300])
