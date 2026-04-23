CYAN  = "\u001B[36;1m"
YELLOW= "\u001B[33;1m"
RESET = "\u001B[0m"

def choose_mode(token, regime):
    if regime == "leader":
        return "10x"
    if regime == "normal":
        return "7x"
    return "5x"

def note_for(token, regime):
    if token == "XLMUSDT" and regime in ("leader", "normal"):
        return "XLM may be a 10x-capable asset; current second leg tuned to 7x."
    return ""

if __name__ == "__main__":
    import sys
    token = sys.argv[1]
    regime = sys.argv[2]
    mode = choose_mode(token, regime)
    print(f"{CYAN}[MODE]{RESET} {token} | regime={regime} -> {mode}")
    extra = note_for(token, regime)
    if extra:
        print(f"{YELLOW}[NOTE]{RESET} {extra}")
