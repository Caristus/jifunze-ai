html = """{% extends \"base.html\" %}
{% block title %}Teacher Studio — JIFUNZE AI{% endblock %}
{% block content %}
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap\" rel=\"stylesheet\">
<script src=\"https://unpkg.com/lucide@latest\"></script>
<style>
  :root{--indigo:#1B1F4B;--indigo2:#262b63;--green:#10B981;--bg:#FDFCF8;--card:#fff;--ink:#0F172A;--mut:#64748B;--line:#E2E8F0;}
  .jf{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);}
  .jf h1,.jf h2,.jf h3{font-family:Manrope,sans-serif;}
  .jf-card{background:var(--card);border:1px solid var(--line);border-radius:1rem;box-shadow:0 4px 6px -1px rgba(0,0,0,.08);}
  .jf-btn{background:var(--indigo);color:#fff;font-weight:600;border-radius:.6rem;padding:.8rem;width:100%;display:flex;align-items:center;justify-content:center;gap:.5rem;cursor:pointer;border:none;transition:.2s;}
  .jf-btn:hover{background:var(--indigo2);}
  .jf-btn:disabled{opacity:.6;cursor:wait;}
  .tl{position:relative;padding-left:2.5rem;}
  .tl::before{content:\"\";position:absolute;left:15px;top:8px;bottom:8px;width:2px;background:var(--line);}
  .tl-item{position:relative;margin-bottom:1.25rem;}
  .tl-dot{position:absolute;left:-2.5rem;top:0;width:32px;height:32px;border-radius:50%;background:var(--card);border:2px solid var(--line);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.75rem;color:var(--indigo);}
  .tl-item.active .tl-dot{background:var(--indigo);color:#fff;border-color:var(--indigo);}
  .oc{display:flex;align-items:flex-start;gap:1rem;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.2);padding:1rem;border-radius:.6rem;}
  .oc b{width:2rem;height:2rem;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
  .chip{font-size:.7rem;font-weight:700;padding:.2rem .6rem;border-radius:9999px;background:#f1f5f9;color:#475569;}
  @media print{.no-print{display:none!important;}.jf-card{box-shadow:none;border:none;}.tl::before{background:#cbd5e1;}}
</style>
<div class=\"jf max-w-7xl mx-auto px-4 py-8\">
  <h1 class=\"text-3xl font-bold mb-1\" style=\"color:var(--indigo)\">Teacher Studio</h1>
  <p class=\"mb-6\" style=\"color:var(--mut)\">Generate world-class, curriculum-aligned teaching materials.</p>
  <div id=\"err\" class=\"no-print hidden\" style=\"background:#fef2f2;border:1px solid #fecaca;color:#b91c1c;border-radius:.6rem;padding:1rem;margin-bottom:1.5rem;white-space:pre-wrap;font-size:.8rem\"></div>
  <div class=\"grid lg:grid-cols-12 gap-8\">
    <div class=\"lg:col-span-4 no-print\">
      <div class=\"jf-card p-6\">
        <form id=\"genform\" class=\"space-y-4\">
          {% csrf_token %}
          <div><label class=\"block text-sm font-semibold mb-1\">Artifact type</label>
            <select id=\"atype\" class=\"w-full border rounded-lg px-3 py-2 bg-white\"><option value=\"lesson_plan\">Lesson Plan</option><option value=\"quiz\">Quiz</option></select></div>
          <div><label class=\"block text-sm font-semibold mb-1\">Topic</label><input id=\"topic\" value=\"Photosynthesis\" class=\"w-full border rounded-lg px-3 py-2\"></div>
          <div><label class=\"block text-sm font-semibold mb-1\">Subtopic</label><input id=\"subtopic\" placeholder=\"e.g. Light reactions\" class=\"w-full border rounded-lg px-3 py-2\"></div>
          <div class=\"grid grid-cols-2 gap-3\">
            <div><label class=\"block text-sm font-semibold mb-1\">Grade</label><input id=\"grade\" value=\"Form 2\" class=\"w-full border rounded-lg px-3 py-2\"></div>
            <div><label class=\"block text-sm font-semibold mb-1\">Curriculum</label><select id=\"curr\" class=\"w-full border rounded-lg px-3 py-2 bg-white\"><option>CBC/CBE</option><option selected>Cambridge IGCSE</option><option>IB</option><option>CAPS</option><option>NECTA</option><option>NCDC</option><option>NERDC</option><option>NaCCA</option><option>ZIMSEC</option><option>WAEC</option><option>Edexcel</option><option>Common Core</option></select></div>
          </div>
          <div class=\"grid grid-cols-2 gap-3\">
            <div><label class=\"block text-sm font-semibold mb-1\">Week</label><input id=\"week\" placeholder=\"Week 3\" class=\"w-full border rounded-lg px-3 py-2\"></div>
            <div><label class=\"block text-sm font-semibold mb-1\">Term</label><input id=\"term\" placeholder=\"Term 1\" class=\"w-full border rounded-lg px-3 py-2\"></div>
          </div>
          <button type=\"submit\" id=\"btn\" class=\"jf-btn\"><i data-lucide=\"sparkles\"></i> Generate Material</button>
        </form>
      </div>
    </div>
    <div class=\"lg:col-span-8\">
      <div id=\"empty\" class=\"jf-card p-16 text-center\" style=\"border:2px dashed var(--line)\">Your generated lesson plan will appear here.</div>
      <div id=\"out\" class=\"hidden\">
        <div class=\"flex gap-3 mb-4 no-print\">
          <button id=\"printBtn\" class=\"jf-btn flex-1\"><i data-lucide=\"printer\"></i> Print</button>
          <button id=\"copyBtn\" class=\"jf-btn flex-1\" style=\"background:#fff;color:var(--ink);border:1px solid var(--line)\"><i data-lucide=\"copy\"></i> Copy</button>
        </div>
        <div id=\"doc\" class=\"jf-card p-8 md:p-12\"></div>
      </div>
    </div>
  </div>
</div>
<script>
lucide.createIcons();
const f=document.getElementById('genform'),btn=document.getElementById('btn'),err=document.getElementById('err');
f.addEventListener('submit',async e=>{
  e.preventDefault();err.classList.add('hidden');btn.disabled=true;btn.innerHTML='Generating...';
  const token=document.querySelector('[name=csrfmiddlewaretoken]').value;
  const body={artifact_type:atype.value,topic:topic.value,subtopic:subtopic.value,grade_level:grade.value,curriculum:curr.value,week:week.value,term:term.value};
  try{
    const r=await fetch('/api/teacher/artifacts/generate/',{method:'POST',credentials:'same-origin',headers:{'X-CSRFToken':token,'Content-Type':'application/json'},body:JSON.stringify(body)});
    const raw=await r.text();
    if(!r.ok){throw new Error('HTTP '+r.status+': '+raw.slice(0,300));}
    const d=JSON.parse(raw);
    let lesson; try{lesson=JSON.parse(d.content);}catch(_){lesson=null;}
    document.getElementById('empty').classList.add('hidden');
    document.getElementById('out').classList.remove('hidden');
    document.getElementById('doc').innerHTML=lesson?renderDoc(lesson,body):('<pre style=\"white-space:pre-wrap\">'+d.content+'</pre>');
    lucide.createIcons();
  }catch(ex){err.textContent=ex.message;err.classList.remove('hidden');}
  finally{btn.disabled=false;btn.innerHTML='<i data-lucide=\"sparkles\"></i> Generate Material';lucide.createIcons();}
});
function renderDoc(d,b){
  const esc=s=>String(s==null?'':s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
  const flow=(d.flow||[]).map((x,i)=>`<div class=\"tl-item ${i===0?'active':''}\"><div class=\"tl-dot\">${String(i+1).padStart(2,'0')}</div><div class=\"jf-card p-4\"><div class=\"flex justify-between items-center mb-1\"><h3 class=\"font-bold\" style=\"color:var(--indigo)\">${esc(x.step)}</h3><span class=\"chip\">${esc(x.duration)}</span></div><p style=\"color:var(--mut);font-size:.9rem\">${esc(x.content)}</p></div></div>`).join('');
  const oc=(d.outcomes||[]).map((o,i)=>`<div class=\"oc\"><b>${i+1}</b><span>${esc(o)}</span></div>`).join('');
  return `<div style=\"border-bottom:2px solid var(--indigo);padding-bottom:1.5rem;margin-bottom:2rem\">
    <div class=\"flex gap-2 mb-2\"><span class=\"chip\" style=\"background:var(--indigo);color:#fff\">AI Generated</span><span class=\"chip\" style=\"background:#dcfce7;color:#166534\">${esc(d.curriculum)}</span></div>
    <h2 class=\"text-3xl font-bold\" style=\"color:var(--indigo)\">${esc(d.title)}</h2>
    <p style=\"color:var(--mut)\">Lesson Plan · ${esc(d.duration||'50 min')} · ${esc(b.subtopic||d.subtopic||'')}</p>
    <div class=\"grid grid-cols-4 gap-3 mt-4\">
      <div class=\"jf-card p-3\"><p class=\"text-xs uppercase\" style=\"color:var(--mut)\">Duration</p><p class=\"font-bold\">${esc(d.duration||'50 min')}</p></div>
      <div class=\"jf-card p-3\"><p class=\"text-xs uppercase\" style=\"color:var(--mut)\">Subject</p><p class=\"font-bold\">${esc(d.subject||'—')}</p></div>
      <div class=\"jf-card p-3\"><p class=\"text-xs uppercase\" style=\"color:var(--mut)\">Grade</p><p class=\"font-bold\">${esc(b.grade_level)}</p></div>
      <div class=\"jf-card p-3\"><p class=\"text-xs uppercase\" style=\"color:var(--mut)\">Week/Term</p><p class=\"font-bold\">${esc(b.week||'—')} / ${esc(b.term||'—')}</p></div>
    </div></div>
    <h3 class=\"text-xl font-bold mb-3\" style=\"color:var(--indigo)\">Learning Outcomes</h3><div class=\"space-y-2 mb-8\">${oc}</div>
    <h3 class=\"text-xl font-bold mb-4\" style=\"color:var(--indigo)\">Lesson Flow</h3><div class=\"tl mb-8\">${flow}</div>
    <div class=\"grid md:grid-cols-2 gap-6 mb-8\"><div><h3 class=\"font-bold mb-2\" style=\"color:var(--indigo)\">Resources</h3><p style=\"color:var(--mut);font-size:.9rem\">${esc(d.resources)}</p></div><div><h3 class=\"font-bold mb-2\" style=\"color:var(--indigo)\">Differentiation</h3><p style=\"color:var(--mut);font-size:.9rem\">${esc(d.differentiation)}</p></div></div>
    <h3 class=\"font-bold mb-2\" style=\"color:var(--indigo)\">Assessment</h3><p style=\"color:var(--mut);font-size:.9rem\" class=\"mb-6\">${esc(d.assessment)}</p>
    <div style=\"background:#fffbeb;border-left:4px solid #f59e0b;padding:1rem;border-radius:0 .5rem .5rem 0\"><h3 class=\"font-bold text-sm mb-1\" style=\"color:#92400e\">Teacher Notes</h3><p style=\"color:#92400e;font-size:.9rem\">${esc(d.teacher_notes)}</p></div>`;
}
document.getElementById('printBtn').onclick=()=>window.print();
document.getElementById('copyBtn').onclick=()=>navigator.clipboard.writeText(document.getElementById('doc').innerText);
</script>
{% endblock %}"""
open("templates/teacher_studio/studio.html","w",encoding="utf-8").write(html)
print("PREMIUM STUDIO + CSRF FIX WRITTEN")
