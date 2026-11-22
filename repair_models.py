from pathlib import Path
import ast
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
mp = base / "apps/resources/models.py"
src = mp.read_text(encoding="utf-8")
fixed = []
changed = False
for ln in src.splitlines():
    if "provenance_tier" in ln and "\\n" in ln:
        fixed.extend([q for q in ln.split("\\n") if q.strip()])
        changed = True
    else:
        fixed.append(ln)
if changed:
    mp.write_text("\n".join(fixed) + "\n", encoding="utf-8")
    print("REPAIRED")
else:
    print("ALREADY CLEAN")
ast.parse(mp.read_text(encoding="utf-8"))
print("MODELS SYNTAX OK")
cp = base / "apps/resources/management/commands/import_curriculum_pack.py"
ast.parse(cp.read_text(encoding="utf-8"))
print("COMMAND SYNTAX OK")
