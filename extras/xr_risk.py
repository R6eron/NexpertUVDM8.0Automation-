import time
from dataclasses import dataclass

R_PCT = 0.008  # 0.8% of equity, same as your Bash helpers


@dataclass
class Position:
    symbol: str
    size: float
    entry: float
    stop: float
    equity: float


def compute_r_view(pos: Position):
    loss = (pos.stop - pos.entry) * pos.size
    if loss < 0:
        loss = -loss
    R = R_PCT * pos.equity
    R_used = loss / R if R > 0 else 0.0
    price_move_pct = (pos.stop - pos.entry) / pos.entry * 100

    line = (
        f"R_VIEW | port_eq={pos.equity:.2f} "
        f"loss_at_stop={loss:.4f} "
        f"R={R:.4f} "
        f"R_used={R_used:.6f}R "
        f"price_move={price_move_pct:.6f}pct"
    )
    return {
        "loss": loss,
        "R": R,
        "R_used": R_used,
        "price_move_pct": price_move_pct,
        "line": line,
    }


def reason_trail(symbol, size, entry, highest, trail_pct, equity):
    stop = highest * (1 - trail_pct / 100.0)
    pos = Position(symbol=symbol, size=size, entry=entry, stop=stop, equity=equity)
    r = compute_r_view(pos)
    mode = "GREEN_SAFE" if r["R_used"] < 0.5 else "AMBER"

    reason = (
        f"{symbol} TRAIL | high={highest:.4f} trail={trail_pct:.1f}% "
        f"→ stop={stop:.5f} | {mode} | "
        f"{r['R_used']:.2f}R for {r['price_move_pct']:.2f}% excursion"
    )
    return reason, r["line"]


def reason_ladder(symbol, total_usdt, equity, stop, levels):
    slice_usdt = total_usdt / len(levels)
    total_R = 0.0
    lines = []

    for lvl in levels:
        size = slice_usdt / lvl
        pos = Position(symbol=symbol, size=size, entry=lvl, stop=stop, equity=equity)
        r = compute_r_view(pos)
        total_R += r["R_used"]
        lines.append(
            f"BID | {lvl:.4f} slice={slice_usdt:.2f}USDT "
            f"size={size:.0f}{symbol} "
            f"{r['R_used']:.3f}R for {r['price_move_pct']:.2f}%"
        )

    header = (
        f"{symbol} LADDER | budget={total_usdt:.2f}USDT stop={stop:.4f} "
        f"levels={','.join(f'{x:.4f}' for x in levels)} "
        f"total_R={total_R:.3f}R"
    )
    return header, lines


def poll_once():
    # For now, hard-code what you already use in Termux / Bitrue
    symbol = "XLM"
    equity = 21_000.0        # port_eq
    size = 149_715           # current perp size
    entry = 0.1650
    highest = 0.1760
    trail_pct = 6.0

    # 1) Trail reasoning
    reason, r_line = reason_trail(symbol, size, entry, highest, trail_pct, equity)
    print(reason)
    print(r_line)

    # 2) Ladder reasoning (0.168 / 0.164 / 0.160, 3000 USDT, cut 0.150)
    header, ladder_lines = reason_ladder(
        symbol=symbol,
        total_usdt=3000.0,
        equity=equity,
        stop=0.1500,
        levels=[0.1680, 0.1640, 0.1600],
    )
    print(header)
    for ln in ladder_lines:
        print("  " + ln)


def main():
    # Simple polling loop; adjust interval as needed
    while True:
        print("=" * 60)
        poll_once()
        time.sleep(30)


if __name__ == "__main__":
    main()
