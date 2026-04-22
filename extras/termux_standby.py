#!/usr/bin/env python3
import os
import time
from dataclasses import dataclass

@dataclass
class Asset:
    name: str
    stage: str
    volume: str
    direction: str
    color: str

assets = [
    Asset('BTC', 'Wyckoff dip/thrust fade detection: Accumulation', 'Volume surge: rising', 'Direction: up', 'green'),
    Asset('XLM', 'Wyckoff dip/thrust fade detection: Markup', 'Volume surge: moderate', 'Direction: up', 'green'),
    Asset('XRP', 'Wyckoff dip/thrust fade detection: Re-accumulation', 'Volume surge: steady', 'Direction: sideways/up', 'yellow'),
    Asset('FLR', 'Wyckoff dip/thrust fade detection: Distribution', 'Volume surge: elevated', 'Direction: down', 'red'),
    Asset('NEXO', 'Wyckoff dip/thrust fade detection: Markdown', 'Volume surge: falling', 'Direction: down', 'red'),
    Asset('SGB', 'Wyckoff dip/thrust fade detection: Re-accumulation', 'Volume surge: mixed', 'Direction: sideways', 'yellow'),
]

RESET='\u001B[0m'
COLORS={'green':'\u001B[92m','yellow':'\u001B[93m','red':'\u001B[91m','cyan':'\u001B[96m','white':'\u001B[97m'}

def c(text, color='white'):
    return f"{COLORS.get(color,'')}{text}{RESET}"

def clear():
    os.system('clear')

def render():
    clear()
    print(c('XRPeasy Digital Ltd | Termux Standby', 'cyan'))
    print(c('Wyckoff dip/thrust fade detection / volume / direction dashboard', 'white'))
    print('-' * 40)
    for a in assets:
        print(c(f'{a.name:<5} | {a.stage}', a.color))
        print(c(f'        {a.volume} | {a.direction}', a.color))
    print('-' * 40)
    print(c('Color key: green=up, yellow=neutral, red=down', 'cyan'))
    print(c('Standby mode active. Press Ctrl+C to exit.', 'white'))

if __name__ == '__main__':
    try:
        while True:
            render()
            time.sleep(2)
    except KeyboardInterrupt:
        pass
