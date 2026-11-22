tpl = '''{% extends "base.html" %}
{% block title %}Teacher Studio — JIFUNZE AI{% endblock %}
{% block content %}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lucide@latest"></script>
<style>
  :root{--indigo:#1B1F4B;--indigo2:#2A3070;--champ:#C9A227;--green:#10B981;--green2:#0E9F6E;--bg:#FDFCF8;--card:#FFFFFF;--ink:#0F172A;--mut:#64748B;--line:#E4E1D6;--soft:#F6F4EC;--amber:#F59E0B;}
  *{scrollbar-width:thin;scrollbar-color:#C9C4B4 #EFEDE6;}
  *::-webkit-scrollbar{width:10px;height:10px;}
  *::-webkit-scrollbar-track{background:#EFEDE6;}
  *::-webkit-scrollbar-thumb{background:#C9C4B4;border-radius:8px;border:2px solid #EFEDE6;}
  *::-webkit-scrollbar-thumb:hover{background:var(--indigo);}
  .jf{font-family:Inter,sans-serif;color:var(--ink);background:
     radial-gradient(1100px 500px at 85% -10%, rgba(27,31,75,.06), transparent 60%),
     radial-gradient(900px 480px at -10% 110%, rgba(16,185,129,.07), transparent 60%),
     var(--bg);min-height:100vh;}
  .jf h1,.jf h2,.jf h3,.font-display{font-family:Manrope,sans-serif;}
  .jf-card{background:var(--card);border:1px solid var(--line);border-radius:1rem;box-shadow:0 6px 18px -8px rgba(27,31,75,.14);}
  .jf label{display:block;font-size:.8rem;font-weight:600;margin-bottom:.35rem;color:var(--ink);}
  .jf input,.jf select{width:100%;border:1px solid var(--line);border-radius:.6rem;padding:.6rem .7rem;background:#fff;font-size:.9rem;transition:border-color .15s, box-shadow .15s;}
  .jf input:focus,.jf select:focus{outline:none;border-color:var(--indigo);box-shadow:0 0 0 3px rgba(27,31,75,.14);}
  .jf-btn{background:var(--indigo);color:#fff;font-weight:600;border-radius:.7rem;padding:.85rem;width:100%;display:flex;align-items:center;justify-content:center;gap:.5rem;cursor:pointer;border:none;transition:background .18s, transform .12s, box-shadow .18s;box-shadow:0 8px 20px -10px rgba(27,31,75,.55);}
  .jf-btn:hover{background:var(--indigo2);transform:translateY(-1px);}
  .jf-btn:active{transform:translateY(0);}
  .jf-btn:disabled{opacity:.65;cursor:wait;transform:none;}
  .jf-btn.ghost{background:#fff;color:var(--ink);border:1px solid var(--line);box-shadow:none;}
  .jf-btn.ghost:hover{background:var(--soft);}
  .chip{font-size:.68rem;font-weight:700;letter-spacing:.04em;padding:.22rem .6rem;border-radius:9999px;background:#EEF0F6;color:#3B4270;}
  .tl{position:relative;padding-left:2.6rem;}
  .tl::before{content:"";position:absolute;left:15px;top:10px;bottom:10px;width:2px;background:linear-gradient(var(--indigo),var(--green));opacity:.35;}
  .tl-item{position:relative;margin-bottom:1.1rem;}
  .tl-dot{position:absolute;left:-2.6rem;top:2px;width:32px;height:32px;border-radius:50%;background:#fff;border:2px solid var(--line);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.72rem;color:var(--indigo);}
  .tl-item.active .tl-dot{background:var(--indigo);color:#fff;border-color:var(--indigo);box-shadow:0 0 0 4px rgba(27,31,75,.12);}
  .oc{display:flex;align-items:flex-start;gap:.9rem;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.22);padding:.9rem 1rem;border-radius:.7rem;}
  .oc b{width:1.9rem;height:1.9rem;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:.85rem;}
  .stat{background:var(--soft);border:1px solid var(--line);border-radius:.7rem;padding:.7rem .8rem;}
  .stat p:first-child{font-size:.62rem;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);font-weight:700;}
  .stat p:last-child{font-family:Manrope;font-weight:800;font-size:.95rem;margin-top:.15rem;}
  .fade{animation:fade .35s ease;}
  @keyframes fade{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
  @media print{.no-print{display:none!important;}.jf{background:#fff;}.jf-card{box-shadow:none;border:none;}.tl::before{background:#cbd5e1;opacity:1;}}
</style>
<div class="jf px-4 py-8">
 <div class="max-w-7xl mx-auto">
  <div class="flex items-end justify-between mb-6 no-print">
    <div>
      <h1 class="text-3xl font-extrabold" style="color:var(--indigo)">Teacher Studio</h1>
      <p class="mt-1" style="color:var(--mut)">Generate world-class, curriculum-aligned teaching materials.</p>
    </div>
    <span class="chip" style="background:var(--indigo);color:#fff">AI POWERED</span>
  </div>
  <div id="err" class="no-print hidden" style="background:#FEF2F2;border:1px solid #FECACA;color:#B91C1C;border-radius:.7rem;padding:1rem;margin-bottom:1.4rem;white-space:pre-wrap;font-size:.8rem"></div>
  <div class="grid lg:grid-cols-12 gap-8">
    <div class="lg:col-span-4 no-print">
      <div class="jf-card p-6" style="position:sticky;top:24px">
        <form id="genform" class="space-y-4">
          {% csrf_token %}
          <div><label>Artifact type</label>
            <select id="atype"><option value="lesson_plan">Lesson Plan</option><option value="quiz">Quiz</option><option value="worksheet">Worksheet</option><option value="marking_guide">Marking Guide</option><option value="activity">Learning Activity</option></select></div>
          <div><label>Topic</label><input id="topic" value="Photosynthesis"></div>
          <div><label>Subtopic / lesson title</label><input id="subtopic" placeholder="e.g. Light-dependent reactions"></div>
          <div><label>Curriculum</label>
            <select id="curr"><option>CBC/CBE</option><option>8-4-4</option><option selected>Cambridge IGCSE</option><option>IB</option><option>CAPS</option><option>NECTA</option><option>NCDC</option><option>NERDC</option><option>NaCCA</option><option>ZIMSEC</option><option>WAEC</option><option>Edexcel</option><option>Common Core</option></select></div>
          <div><label>Grade / level <span style="color:var(--green2);font-weight:700">· aligned to curriculum</span></label>
            <select id="grade"></select></div>
          <div class="grid grid-cols-2 gap-3">
            <div><label>Week</label><select id="week"><option value="">—</option></select></div>
            <div><label>Term</label><select id="term"><option value="">—</option><option>Term 1</option><option>Term 2</option><option>Term 3</option></select></div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label>Duration</label><select id="duration"><option>30</option><option>40</option><option selected>50</option><option>60</option><option>80</option></select></div>
            <div><label>Language</label><select id="language"><option value="en">English</option><option value="sw">Kiswahili</option></select></div>
          </div>
          <button type="submit" id="btn" class="jf-btn"><i data-lucide="sparkles"></i> Generate Material</button>
        </form>
      </div>
    </div>
    <div class="lg:col-span-8">
      <div id="empty" class="jf-card p-16 text-center" style="border:2px dashed var(--line);color:var(--mut)">Your generated lesson plan will appear here.</div>
      <div id="out" class="hidden fade">
        <div class="flex gap-3 mb-4 no-print">
          <button id="printBtn" class="jf-btn flex-1"><i data-lucide="printer"></i> Print</button>
          <button id="copyBtn" class="jf-btn ghost flex-1"><i data-lucide="copy"></i> Copy</button>
          <button id="dlBtn" class="jf-btn ghost flex-1"><i data-lucide="download"></i> Download</button>
        </div>
        <div id="doc" class="jf-card p-8 md:p-12"></div>
      </div>
    </div>
  </div>
 </div>
</div>
<script>
lucide.createIcons();
function seq(p,a,b){var r=[];for(var i=a;i<=b;i++)r.push(p+" "+i);return r;}
var GRADES={
 "CBC/CBE":[{g:"Pre-Primary",o:["PP1","PP2"]},{g:"Primary",o:seq("Grade",1,6)},{g:"Junior School",o:seq("Grade",7,9)},{g:"Senior School",o:seq("Grade",10,12)}],
 "8-4-4":[{g:"Primary",o:seq("Standard",1,8)},{g:"Secondary",o:seq("Form",1,4)}],
 "Cambridge IGCSE":[{g:"Primary",o:seq("Stage",1,6)},{g:"Lower Secondary",o:seq("Stage",7,9)},{g:"IGCSE",o:["Year 10","Year 11"]},{g:"Advanced",o:["AS Level (Year 12)","A Level (Year 13)"]}],
 "IB":[{g:"PYP",o:seq("PYP",1,5)},{g:"MYP",o:seq("MYP",1,5)},{g:"DP",o:["DP 1","DP 2"]}],
 "CAPS":[{g:"Foundation",o:["Grade R"].concat(seq("Grade",1,3))},{g:"Intermediate",o:seq("Grade",4,6)},{g:"Senior",o:seq("Grade",7,9)},{g:"FET",o:seq("Grade",10,12)}],
 "NECTA":[{g:"Primary",o:["Standard I","Standard II","Standard III","Standard IV","Standard V","Standard VI","Standard VII"]},{g:"O-Level",o:seq("Form",1,4)},{g:"A-Level",o:["Form 5","Form 6"]}],
 "NCDC":[{g:"Primary",o:seq("P",1,7)},{g:"O-Level",o:seq("S",1,4)},{g:"A-Level",o:["S5","S6"]}],
 "NERDC":[{g:"Primary",o:seq("Primary",1,6)},{g:"Junior Secondary",o:seq("JSS",1,3)},{g:"Senior Secondary",o:seq("SSS",1,3)}],
 "NaCCA":[{g:"KG & Primary",o:["KG 1","KG 2"].concat(seq("Basic",1,6))},{g:"JHS",o:seq("Basic",7,9)},{g:"SHS",o:seq("SHS",1,3)}],
 "ZIMSEC":[{g:"Primary",o:seq("Grade",1,7)},{g:"O-Level",o:seq("Form",1,4)},{g:"A-Level",o:["Form 5","Form 6"]}],
 "WAEC":[{g:"Junior",o:seq("JSS",1,3)},{g:"Senior",o:seq("SSS",1,3)}],
 "Edexcel":[{g:"Primary",o:seq("Stage",1,6)},{g:"Lower Secondary",o:seq("Stage",7,9)},{g:"IGCSE",o:["Year 10","Year 11"]},{g:"Advanced",o:["AS Level (Year 12)","A Level (Year 13)"]}],
 "Common Core":[{g:"Elementary",o:["Kindergarten"].concat(seq("Grade",1,5))},{g:"Middle",o:seq("Grade",6,8)},{g:"High",o:seq("Grade",9,12)}]
};
var DEF={"CBC/CBE":"Grade 8","8-4-4":"Form 2","Cambridge IGCSE":"Year 10","IB":"MYP 3","CAPS":"Grade 10","NECTA":"Form 2","NCDC":"S2","NERDC":"JSS 2","NaCCA":"Basic 8","ZIMSEC":"Form 2","WAEC":"SSS 2","Edexcel":"Year 10","Common Core":"Grade 8"};
var gradeSel=document.getElementById("grade"),currSel=document.getElementById("curr");
function populateGrades(){
  var groups=GRADES[currSel.value]||GRADES["CBC/CBE"];
  var prev=gradeSel.value;
  gradeSel.innerHTML=groups.map(function(g){return '<optgroup label="'+g.g+'">'+g.o.map(function(v){return '<option>'+v+'</option>';}).join("")+'</optgroup>';}).join("");
  var all=groups.reduce(function(a,g){return a.concat(g.o);},[]);
  var d=DEF[currSel.value]||all[0];
  gradeSel.value=all.indexOf(prev)>=0?prev:(all.indexOf(d)>=0?d:all[0]);
}
currSel.addEventListener("change",populateGrades);
populateGrades();
(function(){var w=document.getElementById("week");for(var i=1;i<=14;i++){var o=document.createElement("option");o.textContent="Week "+i;w.appendChild(o);}})();
var I18N={
 en:{out:"Learning Outcomes",intro:"By the end of this lesson, learners will be able to:",flow:"Lesson Flow",res:"Teaching Resources",diff:"Differentiation",ass:"Assessment & Rubric",notes:"Teacher Notes",plan:"Lesson Plan",dur:"Duration",subj:"Subject",grade:"Grade",wt:"Week / Term"},
 sw:{out:"Matokeo ya Kujifunza",intro:"Mwisho wa somo hili, wanafunzi wataweza:",flow:"Mtiririko wa Somo",res:"Nyenzo za Kufundisha",diff:"Utofautishaji",ass:"Tathmini na Rubriki",notes:"Maelezo ya Mwalimu",plan:"Mpango wa Somo",dur:"Muda",subj:"Somo",grade:"Darasa",wt:"Wiki / Muhula"}
};
var currentContent="";
function esc(s){return String(s==null?"":s).replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
var f=document.getElementById("genform"),btn=document.getElementById("btn"),err=document.getElementById("err");
f.addEventListener("submit",async function(e){
  e.preventDefault();err.classList.add("hidden");btn.disabled=true;btn.innerHTML="Generating...";
  var token=document.querySelector("[name=csrfmiddlewaretoken]").value;
  var body={artifact_type:document.getElementById("atype").value,topic:document.getElementById("topic").value,subtopic:document.getElementById("subtopic").value,grade_level:gradeSel.value,curriculum:currSel.value,week:document.getElementById("week").value,term:document.getElementById("term").value,duration:document.getElementById("duration").value,language:document.getElementById("language").value};
  try{
    var r=await fetch("/api/teacher/artifacts/generate/",{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":token,"Content-Type":"application/json"},body:JSON.stringify(body)});
    var raw=await r.text();
    if(!r.ok){throw new Error("HTTP "+r.status+": "+raw.slice(0,300));}
    var d=JSON.parse(raw);currentContent=d.content||"";
    var lesson=null;try{lesson=JSON.parse(d.content);}catch(_){lesson=null;}
    document.getElementById("empty").classList.add("hidden");
    var out=document.getElementById("out");out.classList.remove("hidden");out.classList.add("fade");
    document.getElementById("doc").innerHTML=lesson?renderDoc(lesson,body):('<pre style="white-space:pre-wrap">'+esc(d.content)+'</pre>');
    lucide.createIcons();
  }catch(ex){err.textContent=ex.message;err.classList.remove("hidden");}
  finally{btn.disabled=false;btn.innerHTML='<i data-lucide="sparkles"></i> Generate Material';lucide.createIcons();}
});
function renderDoc(d,b){
  var L=I18N[d.language==="sw"?"sw":"en"];
  var oc=(d.outcomes||[]).map(function(o,i){return '<div class="oc"><b>'+(i+1)+'</b><span>'+esc(o)+'</span></div>';}).join("");
  var flow=(d.flow||[]).map(function(x,i){return '<div class="tl-item '+(i===0?"active":"")+'"><div class="tl-dot">'+String(i+1).padStart(2,"0")+'</div><div class="jf-card p-4"><div class="flex justify-between items-center mb-1"><h3 class="font-bold" style="color:var(--indigo)">'+esc(x.step)+'</h3><span class="chip">'+esc(x.duration)+'</span></div><p style="color:var(--mut);font-size:.9rem">'+esc(x.content)+'</p></div></div>';}).join("");
  return '<div style="border-bottom:2px solid var(--indigo);padding-bottom:1.4rem;margin-bottom:2rem">'
   +'<div class="flex gap-2 mb-2"><span class="chip" style="background:var(--indigo);color:#fff">AI GENERATED</span><span class="chip" style="background:#DCFCE7;color:#166534">'+esc(d.curriculum)+'</span><span class="chip" style="background:#FEF3C7;color:#92400E">'+esc(d.grade_level||b.grade_level)+'</span></div>'
   +'<h2 class="text-3xl font-extrabold" style="color:var(--indigo)">'+esc(d.title)+'</h2>'
   +'<p style="color:var(--mut)">'+L.plan+' · '+esc(d.duration||"50 minutes")+(b.subtopic?' · '+esc(b.subtopic):'')+'</p>'
   +'<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">'
   +'<div class="stat"><p>'+L.dur+'</p><p>'+esc(d.duration||"50 minutes")+'</p></div>'
   +'<div class="stat"><p>'+L.subj+'</p><p>'+esc(d.subject||"—")+'</p></div>'
   +'<div class="stat"><p>'+L.grade+'</p><p>'+esc(d.grade_level||b.grade_level)+'</p></div>'
   +'<div class="stat"><p>'+L.wt+'</p><p>'+esc((d.week||b.week||"—")+" / "+(d.term||b.term||"—"))+'</p></div>'
   +'</div></div>'
   +'<h3 class="text-xl font-bold mb-2" style="color:var(--indigo)">'+L.out+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-3">'+L.intro+'</p><div class="space-y-2 mb-8">'+oc+'</div>'
   +'<h3 class="text-xl font-bold mb-4" style="color:var(--indigo)">'+L.flow+'</h3><div class="tl mb-8">'+flow+'</div>'
   +'<div class="grid md:grid-cols-2 gap-6 mb-8"><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.res+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.resources)+'</p></div><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.diff+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.differentiation)+'</p></div></div>'
   +'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.ass+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-6">'+esc(d.assessment)+'</p>'
   +'<div style="background:#FFFBEB;border-left:4px solid var(--amber);padding:1rem;border-radius:0 .6rem .6rem 0"><h3 class="font-bold text-sm mb-1" style="color:#92400E">'+L.notes+'</h3><p style="color:#92400E;font-size:.9rem">'+esc(d.teacher_notes)+'</p></div>';
}
document.getElementById("printBtn").onclick=function(){window.print();};
document.getElementById("copyBtn").onclick=function(){navigator.clipboard.writeText(document.getElementById("doc").innerText);};
document.getElementById("dlBtn").onclick=function(){var b=new Blob([currentContent],{type:"application/json"});var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download=(document.getElementById("topic").value||"lesson").replace(/\\s+/g,"_")+".json";a.click();};
</script>
{% endblock %}'''
views = '''import json
import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TeachingArtifact
from apps.institutions.models import Membership
@login_required(login_url="/accounts/login/")
def studio_page(request):
    return render(request, "teacher_studio/studio.html")
def _band(grade):
    g = (grade or "").lower()
    if any(k in g for k in ("pp1", "pp2", "kg", "grade r", "pre")):
        return "early"
    m = re.search(r"\\d+", g)
    n = int(m.group()) if m else 0
    if "form" in g:
        return "junior" if n <= 2 else "senior"
    if re.match(r"^s\\d", g):
        return "junior" if n <= 2 else "senior"
    if "jss" in g:
        return "junior"
    if "sss" in g or "shs" in g:
        return "senior"
    if "myp" in g:
        return "junior"
    if "dp" in g:
        return "senior"
    if "pyp" in g:
        return "primary"
    if "stage" in g:
        return "primary" if n <= 6 else "junior"
    if "year" in g:
        return "senior"
    if "standard" in g or "primary" in g:
        return "primary"
    if "basic" in g:
        return "primary" if n <= 6 else "junior"
    if "grade" in g:
        return "primary" if n <= 6 else ("junior" if n <= 9 else "senior")
    return "junior"
OUT = {
    "early": {"en": ["Identify and name the main parts of {t}.", "Describe {t} using simple everyday words.", "Ask one curious question about {t}."],
              "sw": ["Tambua na uitaje sehemu kuu za {t}.", "Eleza {t} kwa maneno rahisi ya kila siku.", "Uliza swali moja la udadisi kuhusu {t}."]},
    "primary": {"en": ["Describe {t} and its main parts correctly.", "Use simple scientific words to explain {t}.", "Give one real-life example of {t}."],
                "sw": ["Eleza {t} na sehemu zake kuu kwa usahihi.", "Tumia maneno rahisi ya kisayansi kueleza {t}.", "Toa mfano mmoja wa maisha halisi wa {t}."]},
    "junior": {"en": ["Explain {t} using correct scientific terminology.", "Apply knowledge of {t} to familiar real-life situations.", "Communicate findings clearly in pairs or groups."],
               "sw": ["Eleza {t} kwa istilahi sahihi za kisayansi.", "Tumia maarifa ya {t} katika hali za maisha halisi.", "Wasiliana matokeo kwa uwazi kwa wawili au vikundi."]},
    "senior": {"en": ["Explain {t} using precise scientific terminology.", "Apply and analyse {t} in unfamiliar real-life contexts.", "Evaluate evidence and demonstrate critical-thinking competencies."],
               "sw": ["Eleza {t} kwa istilahi za kisayansi zilizo sahihi kabisa.", "Tumia na uchambue {t} katika muktadha mpya wa maisha.", "Tathmini ushahidi na uonyeshe ujuzi wa kufikiri kwa kina."]},
}
FLOW = {
    "early": {"en": ["Sing, look and touch: explore {t} with pictures and real objects.", "Play-based sorting and drawing of {t} in small circles.", "Show-and-tell: each child names one part of {t}.", "Wrap up with a song and a goodbye question about {t}."],
              "sw": ["Imba, tazama na gusa: chunguza {t} kwa picha na vitu halisi.", "Mchezo wa kupanga na kuchora {t} katika vikundi vidogo.", "Onyesha-na-eleza: kila mtoto ataja sehemu moja ya {t}.", "Hitimisha kwa wimbo na swali la kuaga kuhusu {t}."]},
    "primary": {"en": ["Hook: a quick question or picture about {t} from daily life.", "Hands-on: observe, draw and label {t} using school resources.", "Two short questions on {t}; mark against a {cur} rubric.", "Recap key words and set a simple home task on {t}."],
                "sw": ["Kivutio: swali fupi au picha kuhusu {t} kutoka maisha ya kila siku.", "Kwa vitendo: chunguza, chora na weka lebo {t} kwa nyenzo za shule.", "Maswali mawili mafupi kuhusu {t}; sahihisha kwa rubriki ya {cur}.", "Rudia maneno muhimu na toa kazi nyepesi ya nyumbani kuhusu {t}."]},
    "junior": {"en": ["Engage learners with a question about {t} drawn from daily experience.", "Guided exploration of {t} using the school's approved resources; pair work.", "Formative check on {t} marked against a {cur} rubric; peer review.", "Summarise key ideas and assign follow-up practice on {t}."],
               "sw": ["Washirikishe wanafunzi kwa swali kuhusu {t} kutoka uzoefu wa kila siku.", "Uchunguzi wa kuongozwa wa {t} kwa nyenzo za shule; kazi ya wawili.", "Tathmini ya {t} kwa rubriki ya {cur}; mapitio ya rika.", "Fupisha mawazo makuu na toa mazoezi ya ufuatiliaji kuhusu {t}."]},
    "senior": {"en": ["Probe prior conceptions of {t} with a diagnostic question.", "Investigate and analyse {t} using approved sources and data; group discussion.", "Exam-style questions on {t} marked against a {cur} rubric with reasoning marks.", "Synthesise findings, link to the next topic and set extension reading on {t}."],
               "sw": ["Chunguza dhana za awali za {t} kwa swali la uchunguzi.", "Chunguza na uchambue {t} kwa vyanzo na data; mjadala wa kikundi.", "Maswali ya mtihani kuhusu {t} kwa rubriki ya {cur} na alama za hoja.", "unganisha matokeo, unganisha na mada ijayo na toa usomaji wa upanuzi kuhusu {t}."]},
}
STEPS = {"en": ["Introduction", "Main Activity", "Assessment", "Conclusion"],
         "sw": ["Utangulizi", "Shughuli Kuu", "Tathmini", "Hitimisho"]}
EXTRA = {
    "en": {"res": "School textbook, JIFUNZE AI uploaded documents, whiteboard and manipulatives.",
           "diff": "Support: sentence starters and guided prompts. Extension: an open-ended investigation or case study.",
           "ass": "Two short questions on {t}; rubric awards marks for accuracy, terminology and reasoning.",
           "notes": "Confirm prior knowledge before starting; check resource availability and pace for the level."},
    "sw": {"res": "Kitabu cha shule, nyenzo zilizopakiwa za JIFUNZE AI, ubao na vifaa vya kufundishia.",
           "diff": "Msaada: vianzo vya sentensi na miongozo. Upanuzi: uchunguzi wa wazi au utafiti wa kesi.",
           "ass": "Maswali mawili mafupi kuhusu {t}; rubriki hutoa alama kwa usahihi, istilahi na hoja.",
           "notes": "Thibitisha maarifa ya awali kabla ya kuanza; angalia upatikanaji wa nyenzo na kasi ya darasa."},
}
def build_lesson(data):
    topic = (data.get("topic") or "Lesson").strip()
    sub = (data.get("subtopic") or "").strip()
    grade = (data.get("grade_level") or "").strip()
    cur = (data.get("curriculum") or "CBC/CBE").strip()
    lang = "sw" if (data.get("language") or "en") == "sw" else "en"
    try:
        total = int(data.get("duration") or 50)
    except (TypeError, ValueError):
        total = 50
    low = topic.lower()
    if any(k in low for k in ("photo", "cell", "bio", "plant", "chlor", "genet")):
        subject = "Biology"
    elif any(k in low for k in ("algebra", "calcul", "geometr", "math", "fraction")):
        subject = "Mathematics"
    elif any(k in low for k in ("chem", "atom", "mole", "acid")):
        subject = "Chemistry"
    elif any(k in low for k in ("physic", "force", "energy", "motion")):
        subject = "Physics"
    else:
        subject = "General"
    b = _band(grade)
    weights = [0.1, 0.5, 0.2, 0.2]
    mins = [max(5, int(round(total * w))) for w in weights]
    mins[-1] += total - sum(mins)
    flow = []
    for i, step in enumerate(STEPS[lang]):
        flow.append({"step": step, "duration": str(mins[i]) + " min",
                     "content": FLOW[b][lang][i].replace("{t}", low).replace("{cur}", cur)})
    ex = EXTRA[lang]
    return {
        "title": (sub or topic).title(),
        "subject": subject,
        "curriculum": cur,
        "grade_level": grade,
        "week": (data.get("week") or "").strip(),
        "term": (data.get("term") or "").strip(),
        "duration": str(total) + " minutes",
        "language": lang,
        "band": b,
        "outcomes": [o.replace("{t}", low) for o in OUT[b][lang]],
        "flow": flow,
        "resources": ex["res"],
        "differentiation": ex["diff"],
        "assessment": ex["ass"].replace("{t}", low),
        "teacher_notes": ex["notes"],
    }
class TeachingArtifactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        m = Membership.objects.filter(user=self.request.user, is_active=True).first()
        return TeachingArtifact.objects.filter(institution=m.institution) if m else TeachingArtifact.objects.none()
    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response({"detail": "You must belong to an institution."}, status=400)
        atype = data.get("artifact_type", "lesson_plan")
        topic = (data.get("topic") or "Lesson").strip()
        if atype == "lesson_plan":
            content = json.dumps(build_lesson(data), indent=2)
        else:
            content = None
            try:
                from apps.ai_gateway.services import AIGateway
                content = AIGateway(institution=m.institution).generate_teacher_artifact(
                    artifact_type=atype, topic=topic,
                    grade_level=data.get("grade_level", ""), curriculum=data.get("curriculum", "CBC/CBE"))
            except Exception:
                content = None
            if not content or not str(content).strip():
                content = "# " + topic + "\\n\\nGenerated teaching material for " + str(data.get("curriculum", "CBC/CBE")) + "."
        content = str(content)
        kwargs = dict(institution=m.institution, created_by=request.user,
                      artifact_type=atype, topic=topic, content=content)
        existing = {fl.name for fl in TeachingArtifact._meta.fields}
        for fl in ("grade_level", "curriculum", "subtopic", "week", "term", "subject"):
            if fl in existing:
                kwargs[fl] = (data.get(fl) or "")
        artifact = TeachingArtifact.objects.create(**kwargs)
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user,
                action="TEACHER_ARTIFACT_GENERATED", resource_type="TeachingArtifact",
                resource_id=str(artifact.id), metadata={"type": atype})
        except Exception:
            pass
        return Response({"id": str(artifact.id), "content": content, "topic": topic,
                         "artifact_type": atype}, status=201)
'''
open("templates/teacher_studio/studio.html", "w", encoding="utf-8").write(tpl)
open("apps/teacher_studio/views.py", "w", encoding="utf-8").write(views)
print("GRADE-ALIGNED TEACHER STUDIO INSTALLED")
