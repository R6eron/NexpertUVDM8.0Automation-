#!/usr/bin/env python3
import time
import json
import logging
from pathlib import Path

logger = logging.getLogger("uvdm_rotation_daemon")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

BASE_DIR = Path(__file__).resolve().parent

def dummy_profit_event():
    return {"id": "DUMMY_EVENT", "pnl_usdt": 0.0}

def get_latest_realized_pnl():
    """Read latest profit event from latest_profit_event.json if it exists."""
    import json
    event_file = BASE_DIR / "state" / "latest_profit_event.json"
    if not event_file.exists():
        return None
    try:
        return json.loads(event_file.read_text())
    except Exception as e:
        logger.warning("Failed to read profit event: %s", e)
        return None

def main():
    logger.info("UVDM Rotation Daemon starting")
    state_dir = BASE_DIR / "state"
    if not state_dir.exists():
        state_dir.mkdir(parents=True)

    last_event_raw = None

    while True:
        event = get_latest_realized_pnl()
        if event is None:
            logger.debug("No profit event yet")
        else:
            event_raw = json.dumps(event, sort_keys=True)
            if event_raw != last_event_raw:
                logger.info("New profit event: %s", event)
                last_event_raw = event_raw
                # TODO: call allocator here, e.g. rotate_portfolio(event)
            else:
                logger.debug("No change in profit event, skipping")

        time.sleep(10)

if __name__ == "__main__":
    main()

