#!/usr/bin/env python3
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent
PROMPT_PATH = REPO_ROOT / "prompts" / "wingman_master_prompt.md"

def load_wingman_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Missing prompt file: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8").strip()

def read_snapshot() -> str:
    if len(sys.argv) > 1:
        snap_path = Path(sys.argv[1])
        if not snap_path.exists():
            raise FileNotFoundError(f"Missing snapshot file: {snap_path}")
        return snap_path.read_text(encoding="utf-8").strip()
    return sys.stdin.read().strip()

def main() -> None:
    canon = load_wingman_prompt()
    snapshot = read_snapshot()

    full = canon
    if snapshot:
        full = canon + "

" + snapshot

    sys.stdout.write(full)
    if not full.endswith("
"):
        sys.stdout.write("
")

if __name__ == "__main__":
    main()
