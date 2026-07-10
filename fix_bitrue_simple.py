from pathlib import Path

p = Path("NexpertUVDM-Automation/bitrue_simple.py")
src = p.read_text(encoding="utf-8")

a = src.index("def log(msg):")
b = src.index("
def get_price():", a)

fixed = '''def log(msg):
    ts = datetime.now().strftime("%H:%M")
    line = f"[{ts}]{msg}"
    print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\
")
'''

src = src[:a] + fixed + src[b+1:]
p.write_text(src, encoding="utf-8")

print("patched", p)
