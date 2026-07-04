RESET = "\u001B[0m"
BOLD = "\u001B[1m"
CYAN = "\u001B[96m"
GREEN = "\u001B[92m"
YELLOW = "\u001B[93m"
RED = "\u001B[91m"
MAGENTA = "\u001B[95m"

PERCENT_EQUIVALENT = 0.05

def c(text, colour, bold=False):
    if bold:
        return BOLD + colour + str(text) + RESET
    return colour + str(text) + RESET

def stop_eq(high):
    return round(high * (1 - PERCENT_EQUIVALENT), 7)

def action(px, stop):
    if px > stop:
        return "HOLD"
    if px == stop:
        return "SET_STOP"
    return "EXIT_MKT"

def acol(act):
    if act == "HOLD":
        return GREEN
    if act == "SET_STOP":
        return YELLOW
    return RED

assets = {
    "XLM_FUTURES":   {"px": 0.1950000, "high": 0.2000000},
    "XLM_SPOT":      {"px": 0.1850000, "high": 0.1900000},
    "FLR_SPOT":      {"px": 0.0086270, "high": 0.0089500},
    "SGB_SPOT":      {"px": 0.0016870, "high": 0.0018000},
    "NEXO_SPOT":     {"px": 0.9018000, "high": 1.1000000},
    "XRPAYNET_XUMM": {"px": 0.0014500, "high": 0.0016000},
    "PAXG_SPOT":     {"px": 4701.2900000, "high": 4711.6100000},
}

print(c("Wingman TM", CYAN, True))
print(c("Digital Immortal 001", CYAN))
print()

print(c("LIVE INPUTS", CYAN, True))
print("FLR_SPOT  : 0.0086270")
print("SGB_SPOT  : 0.0016870")
print("NEXO_SPOT : 0.9018000")
print("PAXG_SPOT : 4701.2900000")
print()

print(c("MULTI-ASSET STATUS", CYAN, True))
for name in assets:
    a = assets[name]
    s = stop_eq(a["high"])
    act = action(a["px"], s)
    line = name
    line += " | px=" + format(a["px"], ".7f")
    line += " | high=" + format(a["high"], ".7f")
    line += " | stop=" + format(s, ".7f")
    line += " | action=" + act
    print(c(line, acol(act), act != "HOLD"))
print()

print(c("DOCTRINE", MAGENTA, True))
print(c("We read the tape first. Respect trend, direction, and volume.", MAGENTA))
print(c("If there is strength, we press with discipline. Protect capital first.", MAGENTA, True))
print(c("Tape truth: obey. Do not argue.", MAGENTA, True))
