from pathlib import Path
import ast
p = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai\config\urls.py")
text = p.read_bytes().decode("utf-8-sig")
text = text.replace("\ufeff", "")
if "from apps.resources import library_views" not in text:
    text = "from apps.resources import library_views\n" + text
seen = False
out = []
for ln in text.splitlines():
    if ln.strip() == "from apps.resources import library_views":
        if seen:
            continue
        seen = True
    out.append(ln)
text = "\n".join(out) + "\n"
ast.parse(text)
p.write_text(text, encoding="utf-8")
print("URLS FIXED - BOM removed, syntax OK")
print("library route present:", 'library_views.library_page' in text)
