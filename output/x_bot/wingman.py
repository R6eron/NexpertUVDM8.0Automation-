import sys
import time

def render():
    pass

if __name__ == '__main__':
    if '--once' in sys.argv:
        render()
    else:
        while True:
            render()
            time.sleep(2)python3 wingman.py --onceimport sys
import time

def render():
    pass

if __name__ == '__main__':
    if '--once' in sys.argv:
        render()
    else:
        while True:
            render()
            time.sleep(2)python3 wingman.py --once
import sys
import time

def render():
    pass

o
if __name__ == '__main__':
    if '--once' in sys.argv:
        render()
    else:
        while True:
            render()
            time.sleep(2)
python3 wingman.py --once
import sys
import time

def render():
    pass  # replace with your actual render logic

if __name__ == '__main__':
    if '--once' in sys.argv:
        render()
    else:
        while True:
            render()
            time.sleep(2)python3 wingman.py --once
ONBOARDING
Preserve the Accelerator Fund at all times; deploy only surplus capital into spot growth and balance-sheet repair.

STANDBY
Keep the Accelerator Fund intact; use only surplus for spot growth and de-leveraging.

LIVE
Accelerator Fund first, spot growth second, de-leverage always.#!/usr/bin/env python3
import json, os, sys, time
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
LEVELS = BASE / 'levels.json'
RESET='\u001B[0m'
C={'green':'\u001B[92m','yellow':'\u001B[93m','red':'\u001B[91m','cyan':'\u001B[96m','white':'\u001B[97m'}

def color(s, c='white'):
    return f"{C.get(c,'')}{s}{RESET}"

def clear():
    os.system('clear')

def ensure_levels():
    if not LEVELS.exists():
        LEVELS.write_text(json.dumps([
            {"asset":"XLM","spot":"108.5k","tp1":"109k","tp2":"110k","pivot":"Piv","status":"Accumulate","phase":"II","volume":"High","direction":"Up"},
            {"asset":"XRP","spot":"0.60","tp1":"0.62","tp2":"0.65","pivot":"Guard","status":"Secondary Test","phase":"II","volume":"Mix","direction":"Sideways"},
            {"asset":"BTC","spot":"65000","tp1":"68000","tp2":"70000","pivot":"Piv","status":"Distribution","phase":"III","volume":"Mixed","direction":"Down"}
        ], indent=2))

def load_levels():
    ensure_levels()
    return json.loads(LEVELS.read_text())

def palette(item):
    phase = str(item.get('phase','')).upper().replace('PHASE ','').replace('PHASE','').strip()
    direction = str(item.get('direction','')).lower()
    status = str(item.get('status','')).lower()
    if 'accumulate' in status or direction in ('up','bullish') or phase == 'II':
        return 'green'
    if 'distribution' in status or direction in ('down','bearish') or phase == 'III':
        return 'red'
    if 'secondary' in status or direction in ('sideways','mixed','flat','range') or phase in ('I','IV'):
        return 'yellow'
    return 'white'

def short_phase(p):
    p = str(p or '').strip().upper()
    if not p:
        return ''
    return p if p.startswith('P') else f'P{p}'

def row(a):
    return [
        f"║ {a.get('asset','UNK'):<4} {a.get('pivot',''):<5} {a.get('status','')[:12]:<12} ║",
        f"║ {a.get('spot',''):<6} TP1 {a.get('tp1',''):<7} TP2 {a.get('tp2',''):<7} ║",
        f"║ {short_phase(a.get('phase','')):<4} Vol {a.get('volume',''):<6} Dir {a.get('direction',''):<9} ║"
    ]

def render():
    clear()
    ts = datetime.now().strftime('%H:%M:%S')
    top = '╔' + '═'*29 + '╗'
    mid = '╠' + '═'*29 + '╣'
    bot = '╚' + '═'*29 + '╝'
    print(color(top,'cyan'))
    print(color('║ WINGMAN WYCKOFF LIVE       ║','cyan'))
    print(color(f'║ LIVE {ts:<23}║','white'))
    print(color(mid,'cyan'))
    rows = load_levels()
    for i, a in enumerate(rows):
        pal = palette(a)
        for line in row(a):
            print(color(line, pal))
        if i != len(rows)-1:
            print(color(mid,'cyan'))
    print(color(bot,'cyan'))
    print(color('Status: active levels only.','white'))

def main():
    if '--once' in sys.argv:
        render()
        return
    while True:
        render()
        time.sleep(2)

if __name__ == '__main__':
    main()
