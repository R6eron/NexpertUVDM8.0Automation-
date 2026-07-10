from pathlib import Path
import json
import sys

RUNTIME = Path.home() / ".config" / "uvdm" / "runtime"

def generate_tp_levels(asset: str, size: int):
    raw_levels = [
        {"level": 0.25,  "fraction": 0.10},
        {"level": 0.275, "fraction": 0.10},
        {"level": 0.31,  "fraction": 0.50},
    ]

    levels = []
    allocated = 0

    for spec in raw_levels:
        amount = int(size * spec["fraction"])
        levels.append({
            "level": spec["level"],
            "amount": amount
        })
        allocated += amount

    remainder = size - allocated
    if remainder != 0 and levels:
        levels[-1]["amount"] += remainder

    out = {
        "asset": asset,
        "total_size": size,
        "levels": levels,
    }

    RUNTIME.mkdir(parents=True, exist_ok=True)
    tmp = RUNTIME / "tp_levels_live.tmp"
    final = RUNTIME / "tp_levels_live.json"
    
    tmp.write_text(json.dumps(out, indent=2) + "\n")
    tmp.replace(final)

    print(f"TP levels generated for {asset} ({size} units)")
    print(json.dumps(out, indent=2))
    return out


def load_tp_levels():
    """Load the latest TP levels from JSON"""
    final = RUNTIME / "tp_levels_live.json"
    if not final.exists():
        print("No TP levels file found. Generate first.")
        return None
    
    try:
        data = json.loads(final.read_text())
        print(f"Loaded TP levels for {data['asset']} ({data['total_size']} units)")
        print(json.dumps(data, indent=2))
        return data
    except Exception as e:
        print(f"Error loading TP levels: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Generate: python3 tools/tp_levels_live.py <ASSET> <SIZE>")
        print("  Load:     python3 tools/tp_levels_live.py load")
        sys.exit(1)

    if sys.argv[1] == "load":
        load_tp_levels()
    else:
        asset = sys.argv[1]
        size = int(sys.argv[2])
        generate_tp_levels(asset, size)
