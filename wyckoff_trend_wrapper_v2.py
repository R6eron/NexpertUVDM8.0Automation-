import json
import pandas as pd
from uvdm_modules.rsi_divergence_module import detect_rsi_divergence, rsi


def compute_features(df):
    d = df.copy().reset_index(drop=True)
    d["bar_index"] = d.index
    d["ema"] = d["close"].ewm(span=200, adjust=False).mean()
    d["hh"] = d["high"].rolling(50).max()
    d["ll"] = d["low"].rolling(50).min()
    d["range_width"] = (d["hh"] - d["ll"]) / d["close"]
    d["above_ema"] = d["close"] > d["ema"]
    d["rsi"] = rsi(d["close"], 14)
    return d


def label_phase(df):
    d = df.copy()
    in_range = d["range_width"] < 0.10
    near_low = d["close"] < (d["ll"] + 0.45 * (d["hh"] - d["ll"]))
    near_top = d["close"] > (d["ll"] + 0.55 * (d["hh"] - d["ll"]))
    from_tr_low = (d["close"] - d["ll"]) / d["ll"]
    strong_above_ema = d["above_ema"].rolling(20).mean() > 0.55

    phase = pd.Series("unknown", index=d.index)
    phase[(in_range) & (near_low) & (~d["above_ema"])] = "accumulation"
    phase[(from_tr_low.between(0.10, 0.35)) & (strong_above_ema)] = "early_markup"
    phase[(from_tr_low > 0.35) & (strong_above_ema)] = "late_markup"
    phase[(d["range_width"] > 0.08) & (near_top) & (strong_above_ema)] = "distribution"
    d["phase"] = phase
    return d


def normalize_raw_div(raw_div):
    r = raw_div.copy()

    if "time" in r.columns and "bar_index" not in r.columns:
        if pd.api.types.is_numeric_dtype(r["time"]):
            r["bar_index"] = r["time"].astype(int)
        else:
            parsed = pd.to_numeric(r["time"], errors="coerce")
            if parsed.notna().all():
                r["bar_index"] = parsed.astype(int)
            else:
                r["bar_index"] = np.arange(len(r), dtype=int)
    elif "bar_index" not in r.columns:
        r["bar_index"] = np.arange(len(r), dtype=int)

    if "price" in r.columns and "close" not in r.columns:
        r["close"] = pd.to_numeric(r["price"], errors="coerce")
    if "regularBearish" not in r.columns:
        r["regularBearish"] = False
    if "hiddenBearish" not in r.columns:
        r["hiddenBearish"] = False

    r["regularBearish"] = r["regularBearish"].fillna(False).astype(bool)
    r["hiddenBearish"] = r["hiddenBearish"].fillna(False).astype(bool)

    keep = [c for c in ["bar_index", "close", "regularBearish", "hiddenBearish"] if c in r.columns]
    r = r[keep].copy()
    r["bar_index"] = pd.to_numeric(r["bar_index"], errors="coerce")
    r["close"] = pd.to_numeric(r["close"], errors="coerce")
    r = r.dropna(subset=["bar_index", "close"]).sort_values("bar_index").drop_duplicates("bar_index", keep="last")
    r["bar_index"] = r["bar_index"].astype(int)
    return r.reset_index(drop=True)


def find_nearest_divergence(divs, bar_index, max_gap=12):
    if divs is None or divs.empty:
        return None
    m = (divs["bar_index"] - int(bar_index)).abs() <= int(max_gap)
    c = divs.loc[m]
    if c.empty:
        return None
    c = c.assign(dist=(c["bar_index"] - int(bar_index)).abs())
    reg = c[c["regularBearish"]]
    hid = c[c["hiddenBearish"]]
    if not reg.empty:
        return ("regularBearish", int(reg.sort_values("dist").iloc[0]["bar_index"]))
    if not hid.empty:
        return ("hiddenBearish", int(hid.sort_values("dist").iloc[0]["bar_index"]))
    return None


