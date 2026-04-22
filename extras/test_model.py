def predict_with_model(features):
    return {
        "p_continue": 0.67,
        "p_reversal": 0.21,
        "p_stopout": 0.18,
        "recommended_stop_pct": 0.08
    }

print(predict_with_model({"x": 1}))
