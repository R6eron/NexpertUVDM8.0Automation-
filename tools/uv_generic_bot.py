#!/usr/bin/env python3
"""
UVDM Generic Bot Launcher

Single unified entry for UV ticker commands.
If a dedicated bot exists for a ticker, it runs that.
Otherwise, it reports a clean placeholder status.
"""

import sys
import os
from pathlib import Path

ROOT = Path.home() / "NexpertUVDM-Automation"
TOOLS = ROOT / "tools"

def main():
    if len(sys.argv) < 2:
        print("Usage: uv_generic_bot.py <ticker>")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    safe = ticker.lower()

    possible = [
        TOOLS / f"uv_{safe}_bot.py",
        TOOLS / f"{safe}_bot.py",
    ]

    for candidate in possible:
        if candidate.is_file():
            os.execvp("python3", ["python3", str(candidate)])
            return

    print(f"UVDM {ticker} bot")
    print("Status: placeholder generic launcher active")
    print("Hint  : add a dedicated bot at:")
    print(f"  {TOOLS}/uv_{safe}_bot.py")
    print(f"  or {TOOLS}/{safe}_bot.py")

if __name__ == "__main__":
    main()
