from pathlib import Path
import py_compile

p = Path('tools/uvdm_live.py')
s = p.read_text()

debug_line = "DEBUG_MODE = os.getenv('UVDM_DEBUG', '0') == '1'"

if debug_line not in s:
    lines = s.splitlines(True)
    insert_at = 1 if lines and lines[0].startswith('#!') else 0
    body = ''.join(lines[insert_at:])
    if 'import os
' in body:
        body = body.replace('import os
', 'import os
' + debug_line + '
', 1)
    elif 'import os
' in body:
        body = body.replace('import os
', 'import os
' + debug_line + '
', 1)
    else:
        body = 'import os
' + debug_line + '
' + body
    s = ''.join(lines[:insert_at]) + body

repls = [
    ('Source:', 'Feed  : Binance'),
    ('api.binance.com/api/v3/ticker/price?symbol=', ''),
    ('print("Order:")', 'print("Debug  : dry_run order ready" if not DEBUG_MODE else "Order:")'),
    ('print(order_json)', 'print(order_json) if DEBUG_MODE else None'),
    ('print("")
print("ENTRY BAND")', 'print("\
ENTRY BAND")'),
]

for a, b in repls:
    s = s.replace(a, b)

p.write_text(s)
py_compile.compile(str(p), doraise=True)
print('Patched and syntax-checked tools/uvdm_live.py')
