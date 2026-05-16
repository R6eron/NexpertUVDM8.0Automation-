#!/usr/bin/env python3
import argparse
import json
from dataclasses import dataclass
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
        prev_price = out.loc[prev_idx, "close"]
        curr_price = out.loc[curr_idx, "close"]
        prev_macd = out.loc[prev_idx, "macd"]
        curr_macd = out.loc[curr_idx, "macd"]
        if curr_price > prev_price and curr_macd < prev_macd:
            out.loc[curr_idx, "bearish_divergence"] = True

    for i in range(1, len(low_idx)):
        prev_idx = low_idx[i - 1]
        curr_idx = low_idx[i]
        prev_price = out.loc[prev_idx, "close"]
        curr_price = out.loc[curr_idx, "close"]
        prev_macd = out.loc[prev_idx, "macd"]
        curr_macd = out.loc[curr_idx, "macd"]
        if curr_price < prev_price and curr_macd > prev_macd:
            out.loc[curr_idx, "bullish_divergence"] = True

    return out


def position_mark_to_market(side, units, avg_entry, close_price):
    if units == 0:
        return 0.0
    if side == "long":
        return units * (close_price - avg_entry)
    return units * (avg_entry - close_price)


def run_backtest(df: pd.DataFrame, cfg: Config, exit_mode: str = "divergence"):
    cash = cfg.initial_capital
    equity_curve = []
    trades = []
    position = None
    last_price_pivot_low = np.nan
    last_price_pivot_high = np.nan
    pending_bearish_div = False
    pending_bullish_div = False
    trailing_anchor = None

    fee_rate = cfg.fee_bps / 10000.0
    slip_rate = cfg.slippage_bps / 10000.0
    mult = cfg.leverage if cfg.futures_mode else 1.0

    start_bar = max(
        cfg.consolidation_bars + 5,
        cfg.atr_period + 5,
        cfg.macd_slow + cfg.macd_signal
    )

    for i in range(start_bar, len(df)):
        row = df.iloc[i]
        ts = row["timestamp"]
        close = row["close"]
        atr = row["atr"]

        if row["price_pivot_low"]:
            last_price_pivot_low = close
        if row["price_pivot_high"]:
            last_price_pivot_high = close
        if row["bearish_divergence"]:
            pending_bearish_div = True
        if row["bullish_divergence"]:
            pending_bullish_div = True

        if position is not None:
            if position["side"] == "long":
                mark = cash + position_mark_to_market("long", position["units"] * mult, position["avg_entry"], close)
            else:
                mark = cash + position_mark_to_market("short", position["units"] * mult, position["avg_entry"], close)
        else:
            mark = cash
        equity_curve.append({"timestamp": ts, "equity": mark})


        if position is
