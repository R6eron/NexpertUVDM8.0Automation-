#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

HOME = Path.home()
SIGNALS_PATH = HOME / "wyckoff_trend_feed.json"
OUT_CSV = HOME / "amm_instructions.csv"
AUDIT_LOG = HOME / "wingman_audit.log"

BASE = "XLM"
QUOTE = "USDT"
NOTIONAL_PER_SIGNAL = 500.0
TRADEABLE_GRADES = ["high", "medium"]

DOCTRINE = [
    "I do not predict; I wait for proof.",
    "I do not chase; I position at levels.",
    "I do not hope; I define invalidation first.",
    "Tape truth: Obey. Do not argue.",
    "Process over outcome.",
    "No revenge trading.",
    "Markets are never wrong; opinions often are.",
    "Enter only after market action confirms the thesis.",
    "Continue with trades that show profit; end trades that show loss.",
    "Never average losses.",
    "Trade in the direction of the dominant market condition.",
    "Predefine the risk of every trade.",
    "An edge is a probability, not certainty.",
    "Anything can happen.",
    "Every moment in the market is unique.",
]

GRADE_MULTIPLIER = {"high": 1.25, "medium": 1.0, "low": 0.5}
CONF_MULTIPLIER = {4: 1.15, 3: 1.0, 2: 0.85, 1: 0.65, 0: 0.5}


def print_banner() -> None:
    print("=" * 52)
    print("Jesse Livermore Immortal Wingman at your service")
    print("The UVDM Wingman")
    print("=" * 52)
    print()


def print_doctrine() -> None:
    print("Doctrine")
    for line in DOCTRINE:
        print(f"  {line}")
    print()


def load_feed(path: Path = SIGNALS_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Signal feed not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_signals(path: Path = SIGNALS_PATH) -> pd.DataFrame:
    feed = load_feed(path)
    signals = feed.get("signals", [])
    if not signals:
        return pd.DataFrame()
    return pd.DataFrame(signals)


def classify_tradeable(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df[df["grade"].isin(TRADEABLE_GRADES)].copy()
    sort_cols = [c for c in ("confidence", "time") if c in out.columns]
    if sort_cols:
        out = out.sort_values(sort_cols, ascending=[False, True][: len(sort_cols)])
    return out


def infer_invalidation(row) -> str:
    kind = row.get("kind", "")
    price = float(row.get("price", 0.0))
    phase = str(row.get("phase", "unknown"))
    if price <= 0:
        return "Invalidation: price feed invalid (<= 0)."
    if kind == "bullish":
        level = round(price * 0.965, 6)
        return f"Invalid if acceptance below {level} or bullish phase fails ({phase})."
    level = round(price * 1.035, 6)
    return f"Invalid if acceptance above {level} or bearish phase fails ({phase})."


def build_trades(
    df: pd.DataFrame,
    base: str = BASE,
    quote: str = QUOTE,
    notional_per_signal: float = NOTIONAL_PER_SIGNAL,
) -> pd.DataFrame:
    trades = []
    for _, row in df.iterrows():
        side = "buy" if row.get("kind") == "bullish" else "sell"
        price = float(row.get("price", 0.0))
        grade = str(row.get("grade", "medium"))
        confidence = int(row.get("confidence", 0))

        g_mult = GRADE_MULTIPLIER.get(grade, 1.0)
        c_mult = CONF_MULTIPLIER.get(confidence, 0.5)
        weighted_notional = notional_per_signal * g_mult * c_mult
        qty = 0.0 if price <= 0 else weighted_notional / price

        trades.append(
            {
                "time": row.get("time") or row.get("timestamp"),
                "side": side,
                "base": base,
                "quote": quote,
                "price": round(price, 6),
                "qty": round(qty, 6),
                "phase": row.get("phase"),
                "trend_role": row.get("trend_role"),
                "phase_hint": row.get("phase_hint"),
                "grade": grade,
                "confidence": confidence,
                "invalidation": infer_invalidation(row),
            }
        )
    return pd.DataFrame(trades)


def summarize(feed, sigs: pd.DataFrame, tradeable: pd.DataFrame) -> None:
    meta = feed.get("meta", {}) if isinstance(feed, dict) else {}
    print("Market state")
    print(f"  Source            : {meta.get('source', 'unknown')}")
    print(f"  Symbol            : {meta.get('symbol', 'unknown')}")
    print(f"  Generated at      : {meta.get('generated_at', 'unknown')}")
    print()
    print("Signal summary")
    print(f"  Raw divergences   : {meta.get('raw_divergences', 'n/a')}")
    print(f"  Filtered signals  : {meta.get('filtered_signals', len(sigs))}")
    print(f"  Tradeable signals : {meta.get('tradeable_signals', len(tradeable))}")
    print()


def save_outputs(
    trades: pd.DataFrame,
    out_csv: Path = OUT_CSV,
    audit_log: Path = AUDIT_LOG,
) -> None:
    trades.to_csv(out_csv, index=False)
    stamp = datetime.now(timezone.utc).isoformat()
    with audit_log.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] rows={len(trades)} csv={out_csv}")


def main() -> None:
    print_banner()
    print_doctrine()

    feed = load_feed()
    sigs = load_signals()
    tradeable = classify_tradeable(sigs)

    summarize(feed, sigs, tradeable)

    trades = build_trades(tradeable)

    print("Tradeable signals")
    if tradeable.empty:
        print("  No tradeable signals. Stand down.")
    else:
        cols = [
            c
            for c in (
                "time",
                "kind",
                "price",
                "phase",
                "trend_role",
                "phase_hint",
                "grade",
                "confidence",
            )
            if c in tradeable.columns
        ]
        print(tradeable[cols].to_string(index=False))

    print()
    print("AMM instructions")
    if trades.empty:
        print("  No instructions emitted.")
    else:
        print(trades.to_string(index=False))

    print()
    print("Risk / invalidation notes")
    if trades.empty:
        print("  None.")
    else:
        for _, row in trades.iterrows():
            print(
                f"  - {row['time']} {row['side'].upper()} "
                f"{row['base']}/{row['quote']}: {row['invalidation']}"
            )

    save_outputs(trades)

    print()
    print("Files written to disk")
    print(f"  CSV      : {OUT_CSV}")
    print(f"  Audit log: {AUDIT_LOG}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Wingman halted.")
        print(f"Operator error: {e}")
        raise SystemExit(1)
