from pathlib import Path
import subprocess
import os
import sys

repo = Path("/data/data/com.termux/files/home/NexpertUVDM-Automation")
p = repo / "uvdm_master.py"

def run(cmd, env=None):
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=str(repo), env=env)

def patch_file():
    text = p.read_text(encoding="utf-8")

    start = text.find("#!/usr/bin/env python3")
    if start != -1:
        text = text[start:]

    lines = text.splitlines()
    out = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.strip() == "<<<<<<< HEAD" or line.strip() == "=======" or line.startswith(">>>>>>> "):
            i += 1
            continue

        if 'f.write(json.dumps(event) + "")' in line:
            out.append('            f.write(json.dumps(event) + "\
")')
            i += 1
            continue

        if 'f.write(json.dumps(event) + "' in line and '\
")' not in line:
            out.append('            f.write(json.dumps(event) + "\
")')
            if i + 1 < len(lines) and lines[i + 1].strip() == '")':
                i += 2
            else:
                i += 1
            continue

        if 'f.write(json.dumps(event) + "\\' in line:
            out.append('            f.write(json.dumps(event) + "\
")')
            if i + 1 < len(lines) and lines[i + 1].strip() == '")':
                i += 2
            else:
                i += 1
            continue

        out.append(line)
        i += 1

    p.write_text(chr(10).join(out) + chr(10), encoding="utf-8")

patch_file()

r = run(["python", "-m", "py_compile", "uvdm_master.py"])
if r.returncode != 0:
    raise SystemExit(r.returncode)

r = run(["git", "add", "uvdm_master.py"])
if r.returncode != 0:
    raise SystemExit(r.returncode)

env = dict(os.environ)
env["GIT_EDITOR"] = "true"

r = run(["git", "rebase", "--continue"], env=env)
if r.returncode != 0:
    raise SystemExit(r.returncode)

r = run(["python", "-m", "py_compile", "uvdm_master.py"])
if r.returncode != 0:
    raise SystemExit(r.returncode)

r = run(["git", "push", "origin", "main"])
if r.returncode != 0:
    raise SystemExit(r.returncode)

print("DONE")
