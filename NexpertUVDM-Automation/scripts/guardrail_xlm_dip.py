API_KEY=a6c6c86e-274d-4fc3-ae22-de5b481effd4

API_KEY = "YOUR_32_CHAR_KEY"
API_SECRET = "YOUR_64_CHAR_SECRET"

headers = {
    'X-NEXO-API-KEY': API_KEY,
    'X-NEXO-API-SIGNATURE': API_SECRET,
    'Content-Type': 'application/json'
}

resp = requests.get("https://api.nexo.io/v1/balances", headers=headers)
print("Status: " + str(resp.status_code))

if resp.status_codeimport requests
API_KEY = "PASTE_YOUR_32_CHAR_KEY_HERE"
API_SECRET = "PASTE_YOUR_64_CHAR_SECRET_HERE"

headers = {
    'X-NEXO-API-KEY': API_KEY,
    'X-NEXO-API-SIGNATURE': API_SECRET,
    'Content-Type': 'application/json'
}

resp = requests.get("https://api.nexo.io/v1/balances", headers=headers)
print("Status: " + str(resp.status_code))

if resp.status_code == 200:
    print("LIVE - 5907 XLM PROTECTED")
else:
    print("ERROR - check keys")a6c6c86e-274d-4fc3-ae22-de5b481effd4d528c5ec-4d67-494b-a7ab-3ccd49f910fb
