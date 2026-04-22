def dynamic_stop(entry, close, atr, bias, structure_low=None, structure_high=None, risk_mult=1.5):
    if bias == "bullish":
        structure_stop = structure_low if structure_low is not None else entry * 0.98
        vol_stop = close - risk_mult * atr
        return max(structure_stop, vol_stop, entry * 0.98)
    if bias == "bearish":
        structure_stop = structure_high if structure_high is not None else entry * 1.02
        vol_stop = close + risk_mult * atr
        return min(structure_stop, vol_stop, entry * 1.02)
    return entry
