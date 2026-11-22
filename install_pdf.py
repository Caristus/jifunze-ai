import urllib.request
from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
vendor = base / "static/js/vendor"
vendor.mkdir(parents=True, exist_ok=True)
LIBS = {
    "jspdf.umd.min.js": "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
    "jspdf.plugin.autotable.min.js": "https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js",
}
local = {}
for name, url in LIBS.items():
    dest = vendor / name
    if not dest.exists():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                dest.write_bytes(r.read())
        except Exception:
            pass
    local[name] = dest.exists() and dest.stat().st_size > 10000
EXPORTER = r'''
(function () {
  var INDIGO = [27, 31, 75], GREEN = [16, 185, 129], AMBER = [245, 158, 11], CHAMP = [201, 162, 39],
      INK = [15, 23, 42], MUT = [100, 116, 139], LINE = [228, 225, 214], SOFT = [246, 244, 236],
      RED = [220, 38, 38], WHITE = [255, 255, 255];
  var W = 210, H = 297, M = 16, CW = W - 2 * M;
  var doc = null, y = 0, L = null;
  var FALLBACK_L = { out: "Learning Outcomes", intro: "By the end of this lesson, learners will be able to:", flow: "Lesson Flow", res: "Teaching Resources", diff: "Differentiation", ass: "Assessment & Rubric", notes: "Teacher Notes", plan: "Lesson Plan", dur: "Duration", subj: "Subject", grade: "Grade", wt: "Week / Term", marks: "Total marks", instr: "Instructions", wb: "Word bank", ext: "Extension", rub: "Rubric", ex: "Exemplar answers", err: "Common errors", obj: "Objective", mat: "Materials", grp: "Grouping", safe: "Safety", chk: "Success checklist", ans: "Answer", pts: "Marking points", q: "Question", task: "Task" };
  function toast(msg, tone) {
    var t = document.createElement("div");
    t.textContent = msg;
    t.style.cssText = "position:fixed;right:22px;bottom:22px;z-index:9999;padding:12px 18px;border-radius:12px;font:600 13px Inter,sans-serif;color:#fff;box-shadow:0 12px 30px -10px rgba(27,31,75,.6);opacity:0;transform:translateY(10px);transition:.25s;background:" + (tone === "err" ? "#DC2626" : "#1B1F4B");
    document.body.appendChild(t);
    requestAnimationFrame(function () { t.style.opacity = "1"; t.style.transform = "none"; });
    setTimeout(function () { t.style.opacity = "0"; t.style.transform = "translateY(10px)"; setTimeout(function () { t.remove(); }, 300); }, 2800);
  }
  function contHeader() {
    doc.setFillColor(INDIGO[0], INDIGO[1], INDIGO[2]); doc.rect(0, 0, W, 10, "F");
    doc.setFillColor(CHAMP[0], CHAMP[1], CHAMP[2]); doc.rect(0, 10, W, 0.8, "F");
    doc.setTextColor(255, 255, 255); doc.setFont("helvetica", "bold"); doc.setFontSize(8);
    doc.text("JIFUNZE AI  ·  " + String(doc.__title).toUpperCase().slice(0, 70), M, 6.5);
    y = 18;
  }
  function ensure(h) { if (y + h > H - 20) { doc.addPage(); contHeader(); } }
  function setBody(size, color, style) {
    doc.setFont("helvetica", style || "normal"); doc.setFontSize(size || 10);
    var c = color || INK; doc.setTextColor(c[0], c[1], c[2]);
  }
  function para(text, opt) {
    opt = opt || {};
    var indent = opt.indent || 0, size = opt.size || 10;
    setBody(size, opt.color || INK, opt.style || "normal");
    var lines = doc.splitTextToSize(String(text == null ? "" : text), CW - indent);
    for (var i = 0; i < lines.length; i++) { ensure(6); setBody(size, opt.color || INK, opt.style || "normal"); doc.text(lines[i], M + indent, y); y += size * 0.52; }
    y += (opt.after == null ? 2.5 : opt.after);
  }
  function section(t) {
    ensure(16);
    doc.setFillColor(GREEN[0], GREEN[1], GREEN[2]); doc.rect(M, y - 3.4, 2.6, 4.8, "F");
    setBody(12.5, INDIGO, "bold"); doc.text(String(t), M + 5.5, y);
    y += 3.2; doc.setDrawColor(LINE[0], LINE[1], LINE[2]); doc.setLineWidth(0.3);
    doc.line(M, y, M + CW, y); y += 6.5;
  }
  function chipRow(items) {
    var x = M;
    for (var i = 0; i < items.length; i++) {
      var t = String(items[i] || ""); if (!t) continue;
      setBody(8, INDIGO, "bold");
      var w = doc.getTextWidth(t) + 7;
      if (x + w > M + CW) { x = M; y += 8; ensure(9); }
      doc.setFillColor(SOFT[0], SOFT[1], SOFT[2]); doc.setDrawColor(LINE[0], LINE[1], LINE[2]); doc.setLineWidth(0.25);
      doc.roundedRect(x, y - 4.2, w, 6.4, 3.2, 3.2, "FD");
      setBody(8, INDIGO, "bold"); doc.text(t, x + 3.5, y);
      x += w + 3;
    }
    y += 9;
  }
  function metaGrid(pairs) {
    var gap = 4, bw = (CW - gap * 3) / 4, bh = 15; ensure(bh + 6);
    for (var i = 0; i < 4; i++) {
      var x = M + i * (bw + gap);
      doc.setFillColor(SOFT[0], SOFT[1], SOFT[2]); doc.setDrawColor(LINE[0], LINE[1], LINE[2]); doc.setLineWidth(0.25);
      doc.roundedRect(x, y, bw, bh, 2, 2, "FD");
      setBody(6.5, MUT, "bold"); doc.text(String(pairs[i][0]).toUpperCase(), x + 3, y + 5);
      setBody(9.5, INK, "bold");
      var v = doc.splitTextToSize(String(pairs[i][1] || "—"), bw - 6);
      doc.text(v[0], x + 3, y + 11);
    }
    y += bh + 8;
  }
  function numbered(i, text) {
    setBody(10, INK, "normal");
    var lines = doc.splitTextToSize(String(text), CW - 11);
    ensure(Math.max(9, lines.length * 5.4 + 4));
    doc.setFillColor(GREEN[0], GREEN[1], GREEN[2]); doc.circle(M + 3.4, y - 1.3, 3.4, "F");
    setBody(8, WHITE, "bold"); doc.text(String(i), M + 3.4, y + 0.4, { align: "center" });
    setBody(10, INK, "normal");
    for (var k = 0; k < lines.length; k++) { ensure(6); setBody(10, INK, "normal"); doc.text(lines[k], M + 10, y); y += 5.4; }
    y += 3.4;
  }
  function toneBox(label, text, tone) {
    var c = tone === "danger" ? RED : (tone === "warn" ? AMBER : GREEN);
    var fill = tone === "danger" ? [254, 242, 242] : (tone === "warn" ? [255, 251, 235] : [240, 253, 246]);
    setBody(9.5, INK, "normal");
    var lines = doc.splitTextToSize(String(text || ""), CW - 12);
    var h = 10 + lines.length * 5.0;
    ensure(h + 4);
    doc.setFillColor(fill[0], fill[1], fill[2]); doc.roundedRect(M, y - 4, CW, h, 2, 2, "F");
    doc.setFillColor(c[0], c[1], c[2]); doc.rect(M, y - 4, 1.6, h, "F");
    setBody(8.5, c, "bold"); doc.text(String(label).toUpperCase(), M + 6, y + 1);
    setBody(9.5, INK, "normal");
    var yy = y + 7;
    for (var i = 0; i < lines.length; i++) { doc.text(lines[i], M + 6, yy); yy += 5.0; }
    y = yy + 3;
  }
  function stepBlock(idx, step, duration, content) {
    setBody(9.5, MUT, "normal");
    var lines = doc.splitTextToSize(String(content || ""), CW - 24);
    var h = 13 + lines.length * 5.0;
    ensure(h + 5);
    doc.setFillColor(255, 255, 255); doc.setDrawColor(LINE[0], LINE[1], LINE[2]); doc.setLineWidth(0.3);
    doc.roundedRect(M + 8, y - 4, CW - 8, h, 2.5, 2.5, "FD");
    doc.setFillColor(INDIGO[0], INDIGO[1], INDIGO[2]); doc.circle(M + 3.4, y + 1.5, 4.2, "F");
    setBody(8, WHITE, "bold"); doc.text(("0" + idx).slice(-2), M + 3.4, y + 3, { align: "center" });
    setBody(11, INDIGO, "bold"); doc.text(String(step), M + 13, y + 2);
    setBody(8, MUT, "bold"); doc.text(String(duration || ""), M + CW - 4, y + 2, { align: "right" });
    setBody(9.5, MUT, "normal");
    var yy = y + 8.5;
    for (var i = 0; i < lines.length; i++) { doc.text(lines[i], M + 13, yy); yy += 5.0; }
    y = y - 4 + h + 6;
  }
  function ruled(n) {
    for (var i = 0; i < n; i++) { ensure(8); doc.setDrawColor(LINE[0], LINE[1], LINE[2]); doc.setLineWidth(0.25); doc.line(M + 2, y, M + CW - 2, y); y += 7.5; }
    y += 2;
  }
  function question(q, withAnswers) {
    ensure(16);
    setBody(9, INDIGO, "bold"); doc.text(L.q + " " + q.no, M, y);
    setBody(8.5, MUT, "bold"); doc.text(q.marks + (q.marks > 1 ? " marks" : " mark"), M + CW, y, { align: "right" });
    y += 6;
    para(q.stem, { size: 10.5, style: "bold", after: 2 });
    (q.options || []).forEach(function (o, i) {
      setBody(9.5, INK, "normal");
      var ls = doc.splitTextToSize(String(o), CW - 12);
      ensure(6 + ls.length * 5);
      doc.setDrawColor(LINE[0], LINE[1], LINE[2]); doc.setFillColor(SOFT[0], SOFT[1], SOFT[2]); doc.setLineWidth(0.25);
      doc.circle(M + 3.2, y - 1.2, 3.0, "FD");
      setBody(7.5, INDIGO, "bold"); doc.text(String.fromCharCode(65 + i), M + 3.2, y + 0.2, { align: "center" });
      setBody(9.5, INK, "normal");
      for (var k = 0; k < ls.length; k++) { ensure(6); setBody(9.5, INK, "normal"); doc.text(ls[k], M + 9, y); y += 5.0; }
      y += 2.4;
    });
    if (withAnswers) {
      toneBox(L.ans, String(q.answer || "") + (q.explain ? "  —  " + q.explain : ""), "ok");
      if (q.points && q.points.length) para(L.pts + ": " + q.points.join(" · "), { size: 8.5, color: MUT, after: 3 });
    }
    y += 3;
  }
  function build() {
    var raw = window.currentContent || "";
    if (!raw) { toast("Generate a document first, then download it.", "err"); return; }
    var d;
    try { d = JSON.parse(raw); } catch (e) { window.print(); return; }
    if (!window.jspdf || !window.jspdf.jsPDF) { toast("PDF engine unavailable — opening print dialog.", "err"); window.print(); return; }
    L = (window.I18N && window.I18N[d.language === "sw" ? "sw" : "en"]) || FALLBACK_L;
    var withAnswers = document.getElementById("doc").classList.contains("show-answers");
    var kind = d.kind || "lesson_plan";
    var kindLabel = { lesson_plan: L.plan, quiz: "Quiz", worksheet: "Worksheet", marking_guide: "Marking Guide", activity: "Learning Activity" }[kind] || L.plan;
    doc = new window.jspdf.jsPDF({ unit: "mm", format: "a4", compress: true });
    doc.__title = d.title || "Teaching Material";
    doc.setProperties({ title: doc.__title, subject: kindLabel + " · " + (d.curriculum || ""), author: "JIFUNZE AI Teacher Studio", creator: "JIFUNZE AI" });
    doc.setFont("helvetica", "bold"); doc.setFontSize(17);
    var titleLines = doc.splitTextToSize(doc.__title, CW - 8).slice(0, 2);
    var headH = 22 + titleLines.length * 8;
    doc.setFillColor(INDIGO[0], INDIGO[1], INDIGO[2]); doc.rect(0, 0, W, headH, "F");
    doc.setFillColor(CHAMP[0], CHAMP[1], CHAMP[2]); doc.rect(0, headH, W, 1.6, "F");
    doc.setTextColor(255, 255, 255); doc.setFont("helvetica", "bold"); doc.setFontSize(8.5);
    doc.text("JIFUNZE AI  ·  TEACHER STUDIO", M, 11);
    doc.setFontSize(17);
    for (var i = 0; i < titleLines.length; i++) doc.text(titleLines[i], M, 21 + i * 8);
    doc.setFontSize(9); doc.setFont("helvetica", "normal");
    doc.text(kindLabel + "  ·  " + (d.duration || ""), M, headH - 4);
    y = headH + 12;
    chipRow([d.curriculum, d.grade_level, d.subject, d.difficulty, d.language === "sw" ? "Kiswahili" : "English"]);
    metaGrid([[L.dur, d.duration], [L.subj, d.subject], [L.grade, d.grade_level], [L.wt, (d.week || "—") + " / " + (d.term || "—")]]);
    if (kind === "lesson_plan") {
      section(L.out); para(L.intro, { size: 9.5, color: MUT, after: 4 });
      (d.outcomes || []).forEach(function (o, i) { numbered(i + 1, o); });
      y += 2; section(L.flow);
      (d.flow || []).forEach(function (s, i) { stepBlock(i + 1, s.step, s.duration, s.content); });
      section(L.res); para(d.resources, { size: 9.5, color: MUT });
      section(L.diff); para(d.differentiation, { size: 9.5, color: MUT });
      section(L.ass); para(d.assessment, { size: 9.5, color: MUT });
      toneBox(L.notes, d.teacher_notes, "warn");
    } else if (kind === "quiz") {
      section(L.instr); para(d.instructions, { size: 9.5, color: MUT });
      para(L.marks + ": " + d.total_marks, { size: 11, style: "bold", color: INDIGO, after: 5 });
      (d.questions || []).forEach(function (q) { question(q, withAnswers); });
    } else if (kind === "worksheet") {
      section(L.instr); para(d.instructions, { size: 9.5, color: MUT });
      section(L.wb); para((d.word_bank || []).join("  ·  "), { size: 9.5, style: "bold", color: INDIGO, after: 5 });
      (d.tasks || []).forEach(function (t) {
        ensure(16);
        setBody(9, INDIGO, "bold"); doc.text(L.task + " " + t.no, M, y);
        setBody(8, MUT, "bold"); doc.text(String(t.type || ""), M + CW, y, { align: "right" });
        y += 6; para(t.prompt, { size: 10.5, after: 3 });
        ruled(t.lines || 3);
        if (withAnswers) toneBox(L.ans, t.answer, "ok");
        y += 3;
      });
      toneBox(L.ext, d.extension, "ok");
    } else if (kind === "marking_guide") {
      para(L.marks + ": " + d.total_marks, { size: 11, style: "bold", color: INDIGO, after: 5 });
      section(L.rub);
      var head = [["Criteria"].concat(d.levels || [])];
      var body = (d.rubric || []).map(function (r) { return [r.name + "  (/" + r.max + ")"].concat(r.descriptors || []); });
      if (typeof doc.autoTable === "function") {
        doc.autoTable({
          startY: y, head: head, body: body, margin: { left: M, right: M, top: 18 },
          styles: { font: "helvetica", fontSize: 8, cellPadding: 2.6, lineColor: LINE, lineWidth: 0.2, textColor: INK, valign: "top" },
          headStyles: { fillColor: INDIGO, textColor: WHITE, fontStyle: "bold", fontSize: 8.5 },
          alternateRowStyles: { fillColor: SOFT },
          columnStyles: { 0: { cellWidth: 40, fontStyle: "bold" } }
        });
        y = (doc.lastAutoTable ? doc.lastAutoTable.finalY : y) + 9;
      } else {
        (d.rubric || []).forEach(function (r) {
          para(r.name + " (/" + r.max + ")", { style: "bold", size: 10 });
          (r.descriptors || []).forEach(function (x, i) { para(((d.levels || [])[i] || "") + ": " + x, { size: 9, color: MUT, indent: 5, after: 1 }); });
          y += 3;
        });
      }
      section(L.ex);
      (d.exemplars || []).forEach(function (e) { para(e.q, { size: 10.5, style: "bold", after: 2 }); toneBox(L.ans, e.answer + "  (" + e.marks + " marks)", "ok"); });
      section(L.err);
      (d.common_errors || []).forEach(function (x, i) { numbered(i + 1, x); });
      toneBox(L.notes, d.notes, "warn");
    } else if (kind === "activity") {
      section(L.obj); para(d.objective, { size: 10, color: MUT });
      section(L.mat); para((d.materials || []).join("  ·  "), { size: 9.5, style: "bold", color: INDIGO, after: 5 });
      section(L.flow);
      (d.steps || []).forEach(function (s, i) { stepBlock(i + 1, s.step, s.duration, s.content); });
      section(L.grp); para(d.grouping, { size: 9.5, color: MUT });
      section(L.diff); para(d.differentiation, { size: 9.5, color: MUT });
      toneBox(L.safe, d.safety, "danger");
      section(L.chk);
      (d.checklist || []).forEach(function (c, i) { numbered(i + 1, c); });
    }
    var stamp = new Date().toLocaleDateString();
    var copy = (kind === "quiz" || kind === "worksheet") ? (withAnswers ? "Teacher copy · answers included" : "Student copy · answers hidden") : "Teacher copy";
    var n = doc.getNumberOfPages();
    for (var p = 1; p <= n; p++) {
      doc.setPage(p);
      doc.setDrawColor(LINE[0], LINE[1], LINE[2]); doc.setLineWidth(0.3);
      doc.line(M, H - 14, M + CW, H - 14);
      setBody(7.5, MUT, "normal");
      doc.text("Generated by JIFUNZE AI Teacher Studio  ·  " + stamp, M, H - 9.5);
      doc.text(copy, M + CW / 2, H - 9.5, { align: "center" });
      doc.text("Page " + p + " of " + n, M + CW, H - 9.5, { align: "right" });
    }
    var name = ((d.topic || d.title || "material") + "_" + kind).replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "") + ".pdf";
    doc.save(name);
    toast("PDF saved · " + name);
  }
  function wire() {
    var b = document.getElementById("dlBtn");
    if (!b) return;
    b.innerHTML = '<i data-lucide="file-down"></i> Download PDF';
    b.onclick = function () {
      var original = b.innerHTML;
      b.disabled = true;
      b.innerHTML = '<i data-lucide="loader"></i> Preparing PDF…';
      if (window.lucide) lucide.createIcons();
      setTimeout(function () {
        try { build(); }
        catch (e) { console.error(e); toast("PDF failed — opening print dialog.", "err"); window.print(); }
        finally { b.disabled = false; b.innerHTML = original; if (window.lucide) lucide.createIcons(); }
      }, 60);
    };
    if (window.lucide) lucide.createIcons();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();
})();
'''
(base / "static/js/studio_pdf.js").write_text(EXPORTER, encoding="utf-8")
p = base / "templates/teacher_studio/studio.html"
html = p.read_text(encoding="utf-8")
marker = "var INDIGO=[27,31,75]"
if marker in html:
    i = html.index(marker)
    start = html.rfind("<script>", 0, i)
    end = html.find("</script>", i)
    if start != -1 and end != -1:
        html = html[:start] + html[end + len("</script>"):]
for tag in list(LIBS.keys()):
    html = html.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>\n', "")
    html = html.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>\n', "")
html = html.replace('<script src="/static/js/studio_pdf.js"></script>\n', "")
def tag(name, cdn):
    if local.get(name):
        return '<script src="/static/js/vendor/%s" onerror="this.onerror=null;this.src=\'%s\'"></script>' % (name, cdn)
    return '<script src="%s"></script>' % cdn
tags = tag("jspdf.umd.min.js", LIBS["jspdf.umd.min.js"]) + "\n" + \
       tag("jspdf.plugin.autotable.min.js", LIBS["jspdf.plugin.autotable.min.js"]) + "\n" + \
       '<script src="/static/js/studio_pdf.js"></script>\n'
idx = html.rfind("{% endblock %}")
html = html[:idx] + tags + html[idx:]
p.write_text(html, encoding="utf-8")
print("PDF ENGINE LOCAL:", local)
print("PDF DOWNLOAD READY")
