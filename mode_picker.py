def choose_mode(token, regime):
    # regime: "leader", "normal", "laggard"
    if regime == "leader":
        return "10x"
    if regime == "normal":
        return "7x"
    return "5x"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python mode_picker.py TOKEN REGIME")
        print("Example: python mode_picker.py XLMUSDT leader")
        raise SystemExit(1)

    token = sys.argv[1]
    regime = sys.argv[2]
    mode = choose_mode(token, regime)
    print(f"[MODE] {token} | regime={regime} -> {mode}")
