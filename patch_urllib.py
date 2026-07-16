import re
from pathlib import Path
import py_compile

p = Path("tools/uvdm_live.py")
s = p.read_text()

old_block = """    try:
        headers = sign_headers("POST", "/fapi/v2/order", body)
        req = urllib.request.Request(
            "https://fapi.bitrue.com/fapi/v2/order",
            data=body_str.encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())"""

new_block = """    try:
        headers = sign_headers("POST", "/fapi/v2/order", body)
        req = urllib.request.Request(
            "https://fapi.bitrue.com/fapi/v2/order",
            data=body_str.encode(),
            headers=headers,
            method="POST",
        )
        import urllib.error
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode()
            print(f"\
❌ BITRUE API REJECTED REQUEST:\
Status: {e.code}\
Response: {err_msg}")
            return {"succ": False, "msg": err_msg}
        except Exception as e:
            print(f"\
❌ NETWORK ERROR: {e}")
            return {"succ": False, "msg": str(e)}"""

if "except urllib.error.HTTPError" not in s:
    s = s.replace(old_block, new_block)
    p.write_text(s)

py_compile.compile(str(p), doraise=True)
print("✅ Error handling patched.")
