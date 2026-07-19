#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class Config:
    initial_capital: float = 10000.0
    consolidation_bars: int = 20
    pivot_left: int = 3
    pivot_right: int = 3
    breakout_buffer_atr: float = 0.5
    atr_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    max_adds: int = 3
    add_sizes: tuple = (0.4, 0.3, 0.3)
    min_add_atr_spacing: float = 1.0
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    futures_mode: bool = False
    leverage: float = 1.0
    funding_bps_per_8h: float = 0.0
    compare_trailing_stop: bool = True
    trailing_stop_pct: float = 8.2


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}
    required = ["timestamp", "open", "high", "low", "close", "volume"]
    for col in required:
        if col not in cols:
            raise ValueError(f"Missing required column: {col}")
    df = df.rename(columns={cols[k]: k for k in required})
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    return df


def add_indicators(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    out = df.copy()
    ema_fast = out["close"].ewm(span=cfg.macd_fast, adjust=False).mean()
    ema_slow = out["close"].ewm(span=cfg.macd_slow, adjust=False).mean()
    out["macd"] = ema_fast - ema_slow
    out["macd_signal"] = out["macd"].ewm(span=cfg.macd_signal, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]

    prev_close = out["close"].shift(1)
    tr = pd.concat([
        out["high"] - out["low"],
        (out["high"] - prev_close).abs(),
        (out["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    out["atr"] = tr.rolling(cfg.atr_period).mean()
    out["rolling_high"] = out["high"].rolling(cfg.consolidation_bars).max().shift(1)
    out["rolling_low"] = out["low"].rolling(cfg.consolidation_bars).min().shift(1)
    return out


def find_pivots(series: pd.Series, left: int = 3, right: int = 3):
    highs = np.full(len(series), False)
    lows = np.full(len(series), False)
    vals = series.values
    for i in range(left, len(series) - right):
        window = vals[i - left:i + right + 1]
        center = vals[i]
        if np.isnan(center) or np.isnan(window).any():
            continue
        if center == window.max() and np.sum(window == center) == 1:
            highs[i] = True
        if center == window.min() and np.sum(window == center) == 1:
            lows[i] = True
    return pd.Series(highs, index=series.index), pd.Series(lows, index=series.index)


def apply_pivots(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    out = df.copy()
    ph, pl = find_pivots(out["close"], cfg.pivot_left, cfg.pivot_right)
    mh, ml = find_pivots(out["macd"], cfg.pivot_left, cfg.pivot_right)
    out["price_pivot_high"] = ph
    out["price_pivot_low"] = pl
    out["macd_pivot_high"] = mh
    out["macd_pivot_low"] = ml
    return out


def detect_divergences(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bearish_divergence"] = False
    out["bullish_divergence"] = False

    high_idx = list(out.index[out["price_pivot_high"]])
    low_idx = list(out.index[out["price_pivot_low"]])

    for i in range(1, len(high_idx)):
        prev_idx = high_idx[i - 1]
        curr_idx = high_idx[i]
        if out.loc[curr_idx, "close"] > out.loc[prev_idx, "close"] and out.loc[curr_idx, "macd"] < out.loc[prev_idx, "macd"]:
            out.loc[curr_idx, "bearish_divergence"] = True

    for i in range(1, len(low_idx)):
        prev_idx = low_idx[i - 1]
        curr_idx = low_idx[i]
        if out.loc[curr_idx, "close"] < out.loc[prev_idx, "close"] and out.loc[curr_idx, "macd"] > out.loc[prev_idx, "macd"]:
            out.loc[curr_idx, "bullish_divergence"] = True

    return out


def position_mark_to_market(side, units, avg_entry, close_price):
    if units == 0:
        return 0.0
    if side == "long":
        return units * (close_price - avg_entry)
    return units * (avg_entry - close_price)


def trading_cost(notional: float, cfg: Config) -> float:
    fee_rate = cfg.fee_bps / 10000.0
    slip_rate = cfg.slippage_bps / 10000.0
    return notional * (fee_rate + slip_rate)


def run_backtest(df: pd.DataFrame, cfg: Config, exit_mode: str = "divergence"):
    cash = cfg.initial_capital
    equity_curve = []
    trades = []
    position = None
    last_price_pivot_low = np.nan
    last_price_pivot_high = np.nan
    pending_bearish_div = False
    pending_bullish_div = False

    start_bar = max(cfg.consolidation_bars + 5, cfg.atr_period + 5, cfg.macd_slow + cfg.macd_signal)

    for i in range(start_bar, len(df)):
        row = df.iloc[i]
        ts = row["timestamp"]
        close = float(row["close"])
        atr = float(row["atr"]) if pd.notna(row["atr"]) else np.nan
        rolling_high = float(row["rolling_high"]) if pd.notna(row["rolling_high"]) else np.nan
        rolling_low = float(row["rolling_low"]) if pd.notna(row["rolling_low"]) else np.nan

        if row["price_pivot_low"]:
            last_price_pivot_low = close
        if row["price_pivot_high"]:
            last_price_pivot_high = close
        if row["bearish_divergence"]:
            pending_bearish_div = True
        if row["bullish_divergence"]:
            pending_bullish_div = True

        if position is not None:
            mtm = position_mark_to_market(position["side"], position["units"] * (cfg.leverage if cfg.futures_mode else 1.0), position["avg_entry"], close)
            mark = cash + mtm
        else:
            mark = cash
        equity_curve.append({"timestamp": ts, "equity": mark})

        if np.isnan(atr) or np.isnan(rolling_high) or np.isnan(rolling_low):
            continue

        if position is None:
            long_trigger = close > rolling_high + cfg.breakout_buffer_atr * atr and row["macd_hist"] > 0
            short_trigger = close < rolling_low - cfg.breakout_buffer_atr * atr and row["macd_hist"] < 0

            if long_trigger:
                alloc = cfg.add_sizes[0]
                notional = cash * alloc
                units = notional / close if close > 0 else 0
                cost = trading_cost(notional, cfg)
                cash -= cost
                position = {
                    "side": "long",
                    "units": units,
                    "avg_entry": close,
                    "entries": [{"ts": ts, "price": close, "units": units}],
                    "adds": 0,
                    "highest_close": close,
                    "lowest_close": close,
                    "last_add_price": close,
                    "entry_ts": ts,
                }
                pending_bearish_div = False
                pending_bullish_div = False
                continue

            if short_trigger:
                alloc = cfg.add_sizes[0]
                notional = cash * alloc
                units = notional / close if close > 0 else 0
                cost = trading_cost(notional, cfg)
                cash -= cost
                position = {
                    "side": "short",
                    "units": units,
                    "avg_entry": close,
                    "entries": [{"ts": ts, "price": close, "units": units}],
                    "adds": 0,
                    "highest_close": close,
                    "lowest_close": close,
                    "last_add_price": close,
                    "entry_ts": ts,
                }
                pending_bearish_div = False
                pending_bullish_div = False
                continue

        else:
            position["highest_close"] = max(position["highest_close"], close)
            position["lowest_close"] = min(position["lowest_close"], close)

            if position["adds"] < cfg.max_adds - 1:
                next_alloc = cfg.add_sizes[position["adds"] + 1]
                if position["side"] == "long" and close >= position["last_add_price"] + cfg.min_add_atr_spacing * atr:
                    notional = cash * next_alloc
                    units = notional / close if close > 0 else 0
                    cost = trading_cost(notional, cfg)
                    new_total_units = position["units"] + units
                    position["avg_entry"] = ((position["avg_entry"] * position["units"]) + (close * units)) / new_total_units
                    position["units"] = new_total_units
                    position["adds"] += 1
                    position["last_add_price"] = close
                    position["entries"].append({"ts": ts, "price": close, "units": units})
                    cash -= cost
                elif position["side"] == "short" and close <= position["last_add_price"] - cfg.min_add_atr_spacing * atr:
                    notional = cash * next_alloc
                    units = notional / close if close > 0 else 0
                    cost = trading_cost(notional, cfg)
                    new_total_units = position["units"] + units
                    position["avg_entry"] = ((position["avg_entry"] * position["units"]) + (close * units)) / new_total_units
                    position["units"] = new_total_units
                    position["adds"] += 1
                    position["last_add_price"] = close
                    position["entries"].append({"ts": ts, "price": close, "units": units})
                    cash -= cost

            exit_reason = None
            if position["side"] == "long":
                structural_stop = close < last_price_pivot_low if pd.notna(last_price_pivot_low) else False
                divergence_exit = pending_bearish_div and exit_mode == "divergence"
                trailing_exit = cfg.compare_trailing_stop and close <= position["highest_close"] * (1 - cfg.trailing_stop_pct / 100.0)
                if structural_stop:
                    exit_reason = "pivot_break"
                elif divergence_exit:
                    exit_reason = "bearish_divergence"
                elif trailing_exit:
                    exit_reason = "trailing_stop"
            else:
                structural_stop = close > last_price_pivot_high if pd.notna(last_price_pivot_high) else False
                divergence_exit = pending_bullish_div and exit_mode == "divergence"
                trailing_exit = cfg.compare_trailing_stop and close >= position["lowest_close"] * (1 + cfg.trailing_stop_pct / 100.0)
                if structural_stop:
                    exit_reason = "pivot_break"
                elif divergence_exit:
                    exit_reason = "bullish_divergence"
                elif trailing_exit:
                    exit_reason = "trailing_stop"

            if exit_reason is not None:
                exit_notional = position["units"] * close
                cost = trading_cost(exit_notional, cfg)
                gross_pnl = position_mark_to_market(position["side"], position["units"] * (cfg.leverage if cfg.futures_mode else 1.0), position["avg_entry"], close)
                net_pnl = gross_pnl - cost
                cash += net_pnl
                trades.append({
                    "entry_ts": str(position["entry_ts"]),
                    "exit_ts": str(ts),
                    "side": position["side"],
                    "units": round(position["units"], 8),
                    "avg_entry": round(position["avg_entry"], 6),
                    "exit_price": round(close, 6),
                    "gross_pnl": round(gross_pnl, 2),
                    "net_pnl": round(net_pnl, 2),
                    "adds": position["adds"],
                    "exit_reason": exit_reason,
                })
                position = None
                pending_bearish_div = False
                pending_bullish_div = False

    if position is not None:
        close = float(df.iloc[-1]["close"])
        ts = df.iloc[-1]["timestamp"]
        exit_notional = position["units"] * close
        cost = trading_cost(exit_notional, cfg)
        gross_pnl = position_mark_to_market(position["side"], position["units"] * (cfg.leverage if cfg.futures_mode else 1.0), position["avg_entry"], close)
        net_pnl = gross_pnl - cost
        cash += net_pnl
        trades.append({
            "entry_ts": str(position["entry_ts"]),
            "exit_ts": str(ts),
            "side": position["side"],
            "units": round(position["units"], 8),
            "avg_entry": round(position["avg_entry"], 6),
            "exit_price": round(close, 6),
            "gross_pnl": round(gross_pnl, 2),
            "net_pnl": round(net_pnl, 2),
            "adds": position["adds"],
            "exit_reason": "end_of_data",
        })

    equity_df = pd.DataFrame(equity_curve)
    trades_df = pd.DataFrame(trades)
    total_return_pct = ((cash / cfg.initial_capital) - 1.0) * 100.0
    summary = {
        "initial_capital": cfg.initial_capital,
        "final_equity": round(cash, 2),
        "total_return_pct": round(total_return_pct, 2),
        "trade_count": int(len(trades_df)),
        "wins": int((trades_df["net_pnl"] > 0).sum()) if not trades_df.empty else 0,
        "losses": int((trades_df["net_pnl"] <= 0).sum()) if not trades_df.empty else 0,
        "avg_trade_pnl": round(float(trades_df["net_pnl"].mean()), 2) if not trades_df.empty else 0.0,
    }
    return summary, trades_df, equity_df


def main() -> None:
    parser = argparse.ArgumentParser(description="Livermore-style breakout backtest with pivots, MACD divergence, and trailing stop comparison")
    parser.add_argument("csv_path", help="Path to OHLCV CSV with timestamp, open, high, low, close, volume")
    parser.add_argument("--exit-mode", choices=["divergence", "trailing_only"], default="divergence")
    parser.add_argument("--initial-capital", type=float, default=10000.0)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    cfg = Config(initial_capital=args.initial_capital)
    df = load_data(args.csv_path)
    df = add_indicators(df, cfg)
    df = apply_pivots(df, cfg)
    df = detect_divergences(df)

    summary, trades_df, equity_df = run_backtest(df, cfg, exit_mode=args.exit_mode)

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    trades_path = outdir / "livermore_backtest_trades.csv"
    equity_path = outdir / "livermore_backtest_equity.csv"
    summary_path = outdir / "livermore_backtest_summary.json"

    trades_df.to_csv(trades_path, index=False)
    equity_df.to_csv(equity_path, index=False)
    summary_payload = {"config": asdict(cfg), "summary": summary}
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    print(json.dumps(summary_payload, indent=2))


if __name__ == "__main__":
    main()