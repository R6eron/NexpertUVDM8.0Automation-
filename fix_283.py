from pathlib import Path
p = Path("tools/uvdm_voice_watch.py")
lines = p.read_text(encoding="utf-8").splitlines()
lines[282] = '    append_text(path, json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\
")'
del lines[283]
p.write_text("
".join(lines) + "
", encoding="utf-8")
