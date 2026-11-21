import os
import django
import sys
# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
from django.core.management import call_command
print("=== STEP 1: NUKING BROKEN DATABASE TABLE ===")
with connection.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS teacher_studio_teachingartifact;")
    print("Table dropped.")
print("=== STEP 2: RECREATING SCHEMA ===")
call_command('makemigrations', 'teacher_studio', verbosity=0)
call_command('migrate', 'teacher_studio', verbosity=0)
print("Schema recreated cleanly.")
print("=== STEP 3: WRITING PREMIUM TEMPLATE ===")
template_content = r'''
{% extends "base.html" %}
{% load static %}
{% block title %}Teacher Studio — JIFUNZE AI{% endblock %}
{% block content %}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lucide@latest"></script>
<style>
  :root {
    --royal-indigo: #1B1F4B;
    --indigo-hover: #262b63;
    --champagne: #C9A227;
    --learning-green: #10B981;
    --bg-canvas: #FDFCF8;
    --surface: #FFFFFF;
    --text-main: #0F172A;
    --text-muted: #64748B;
    --border: #E2E8F0;
  }
  body { font-family: 'Inter', sans-serif; background: var(--bg-canvas); color: var(--text-main); }
  .font-display { font-family: 'Manrope', sans-serif; }
  .jf-card { background: var(--surface); border: 1px solid var(--border); border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
  /* Timeline */
  .timeline { position: relative; padding-left: 2rem; }
  .timeline::before { content: ''; position: absolute; left: 15px; top: 24px; bottom: 0; width: 2px; background: var(--border); }
  .tl-item { position: relative; margin-bottom: 2rem; }
  .tl-dot { position: absolute; left: -2rem; top: 0; width: 32px; height: 32px; border-radius: 50%; background: var(--surface); border: 2px solid var(--border); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem; color: var(--royal-indigo); z-index: 2; }
  .tl-item.active .tl-dot { background: var(--royal-indigo); color: white; border-color: var(--royal-indigo); }
  .outcome-badge { width: 2rem; height: 2rem; border-radius: 50%; background: var(--learning-green); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }
</style>
<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-display font-extrabold text-[var(--royal-indigo)] mb-6">Teacher Studio</h1>
  <div id="error-box" class="hidden bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6"></div>
  <div class="grid lg:grid-cols-12 gap-8">
    <!-- LEFT: Form -->
    <div class="lg:col-span-4">
      <div class="jf-card p-6 sticky top-8">
        <form id="genform" class="space-y-4">
          <input type="hidden" id="csrf-token" value="{{ csrf_token }}">
          <div>
            <label class="block text-sm font-semibold mb-1">Artifact Type</label>
            <select id="atype" class="w-full border rounded-lg px-3 py-2 bg-white">
              <option value="lesson_plan">Lesson Plan</option>
              <option value="quiz">Quiz</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-semibold mb-1">Topic</label>
            <input id="topic" value="Photosynthesis" class="w-full border rounded-lg px-3 py-2" required>
          </div>
          <div>
            <label class="block text-sm font-semibold mb-1">Subtopic</label>
            <input id="subtopic" class="w-full border rounded-lg px-3 py-2" placeholder="e.g. Light Reactions">
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-semibold mb-1">Grade</label>
              <input id="grade" value="Form 2" class="w-full border rounded-lg px-3 py-2">
            </div>
            <div>
              <label class="block text-sm font-semibold mb-1">Curriculum</label>
              <select id="curr" class="w-full border rounded-lg px-3 py-2 bg-white">
                <option>CBC/CBE</option>
                <option selected>Cambridge IGCSE</option>
                <option>IB</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-semibold mb-1">Week</label>
              <input id="week" class="w-full border rounded-lg px-3 py-2" placeholder="Week 3">
            </div>
            <div>
              <label class="block text-sm font-semibold mb-1">Term</label>
              <input id="term" class="w-full border rounded-lg px-3 py-2" placeholder="Term 1">
            </div>
          </div>
          <button type="submit" id="generateBtn" class="w-full bg-[var(--royal-indigo)] hover:bg-[var(--indigo-hover)] text-white font-semibold rounded-lg py-3 shadow-md transition-all flex items-center justify-center gap-2">
            <i data-lucide="sparkles" class="w-5 h-5"></i> Generate Material
          </button>
        </form>
      </div>
    </div>
    <!-- RIGHT: Output -->
    <div class="lg:col-span-8">
      <div id="empty-state" class="jf-card p-16 text-center border-2 border-dashed">
        <div class="inline-flex w-16 h-16 rounded-full bg-slate-100 mb-4 items-center justify-center">
          <i data-lucide="file-text" class="w-8 h-8 text-slate-400"></i>
        </div>
        <h3 class="text-lg font-display font-bold">Your generated material will appear here</h3>
      </div>
      <div id="output-container" class="hidden">
        <div class="flex gap-3 mb-6">
          <button id="printBtn" class="flex-1 bg-[var(--royal-indigo)] text-white rounded-lg py-2 font-medium">Print</button>
          <button id="copyBtn" class="flex-1 bg-white border rounded-lg py-2 font-medium">Copy</button>
        </div>
        <div id="document-paper" class="jf-card p-8 md:p-12">
          <div class="border-b-2 border-[var(--royal-indigo)] pb-6 mb-8">
            <div class="flex items-center gap-2 mb-2">
              <span class="bg-[var(--royal-indigo)] text-white text-xs font-bold px-2 py-1 rounded uppercase">AI Generated</span>
              <span id="doc-curriculum" class="bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-1 rounded uppercase"></span>
            </div>
            <h1 id="doc-title" class="text-4xl font-display font-extrabold text-[var(--royal-indigo)] mb-2"></h1>
            <p id="doc-subtitle" class="text-lg text-[var(--text-muted)]"></p>
            <div class="grid grid-cols-3 gap-4 mt-6">
              <div class="bg-slate-50 rounded-lg p-3 border"><p class="text-xs uppercase text-[var(--text-muted)]">Duration</p><p id="doc-duration" class="text-lg font-display font-bold"></p></div>
              <div class="bg-slate-50 rounded-lg p-3 border"><p class="text-xs uppercase text-[var(--text-muted)]">Subject</p><p id="doc-subject" class="text-lg font-display font-bold"></p></div>
              <div class="bg-slate-50 rounded-lg p-3 border"><p class="text-xs uppercase text-[var(--text-muted)]">Level</p><p id="doc-grade" class="text-lg font-display font-bold"></p></div>
            </div>
          </div>
          <div class="mb-10">
            <h2 class="text-xl font-display font-bold text-[var(--royal-indigo)] mb-4 flex items-center gap-2"><i data-lucide="target" class="w-5 h-5 text-[var(--learning-green)]"></i> Learning Outcomes</h2>
            <div id="doc-outcomes" class="space-y-3"></div>
          </div>
          <div class="mb-10">
            <h2 class="text-xl font-display font-bold text-[var(--royal-indigo)] mb-6 flex items-center gap-2"><i data-lucide="clock" class="w-5 h-5 text-[var(--learning-green)]"></i> Lesson Flow</h2>
            <div class="timeline" id="doc-flow"></div>
          </div>
          <div class="grid md:grid-cols-2 gap-8 mb-10">
            <div><h2 class="text-lg font-display font-bold text-[var(--royal-indigo)] mb-2">Resources</h2><p id="doc-resources" class="text-sm bg-slate-50 p-4 rounded-lg border"></p></div>
            <div><h2 class="text-lg font-display font-bold text-[var(--royal-indigo)] mb-2">Differentiation</h2><p id="doc-differentiation" class="text-sm bg-slate-50 p-4 rounded-lg border"></p></div>
          </div>
          <div class="mb-10">
            <h2 class="text-lg font-display font-bold text-[var(--royal-indigo)] mb-2">Assessment</h2>
            <p id="doc-assessment" class="text-sm"></p>
          </div>
          <div class="bg-amber-50 border-l-4 border-amber-400 p-5 rounded-r-lg">
            <h2 class="text-sm font-display font-bold text-amber-900 mb-2">Teacher Notes</h2>
            <p id="doc-notes" class="text-amber-800 text-sm"></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<script>
lucide.createIcons();
const csrf = document.getElementById('csrf-token').value;
document.getElementById('genform').addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('generateBtn');
    const errBox = document.getElementById('error-box');
    const emptyState = document.getElementById('empty-state');
    const outputContainer = document.getElementById('output-container');
    btn.disabled = true;
    btn.innerHTML = 'Generating...';
    errBox.classList.add('hidden');
    const body = {
        artifact_type: document.getElementById('atype').value,
        topic: document.getElementById('topic').value,
        subtopic: document.getElementById('subtopic').value,
        grade_level: document.getElementById('grade').value,
        curriculum: document.getElementById('curr').value,
        week: document.getElementById('week').value,
        term: document.getElementById('term').value
    };
    try {
        const resp = await fetch('/api/teacher/artifacts/generate/', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        const d = JSON.parse(data.content); // Parse the JSON string from backend
        // Render Header
        document.getElementById('doc-title').textContent = d.title;
        document.getElementById('doc-subtitle').textContent = `Lesson Plan · ${d.duration}`;
        document.getElementById('doc-curriculum').textContent = d.curriculum;
        document.getElementById('doc-duration').textContent = d.duration;
        document.getElementById('doc-subject').textContent = d.subject;
        document.getElementById('doc-grade').textContent = body.grade_level;
        // Render Outcomes
        const oc = document.getElementById('doc-outcomes');
        oc.innerHTML = d.outcomes.map((o, i) => `
            <div class="flex items-start gap-4 bg-emerald-50/30 p-4 rounded-lg border border-emerald-100">
                <div class="outcome-badge">${i+1}</div>
                <p class="font-medium pt-1">${o}</p>
            </div>
        `).join('');
        // Render Flow
        const fl = document.getElementById('doc-flow');
        fl.innerHTML = d.flow.map((item, i) => `
            <div class="tl-item ${i===0?'active':''}">
                <div class="tl-dot">${String(i+1).padStart(2,'0')}</div>
                <div class="bg-white rounded-xl p-5 border shadow-sm">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="font-display font-bold text-lg text-[var(--royal-indigo)]">${item.step}</h3>
                        <span class="bg-slate-100 text-slate-600 text-xs font-bold px-2 py-1 rounded-full">${item.duration}</span>
                    </div>
                    <p class="text-[var(--text-muted)] text-sm">${item.content}</p>
                </div>
            </div>
        `).join('');
        document.getElementById('doc-resources').textContent = d.resources;
        document.getElementById('doc-differentiation').textContent = d.differentiation;
        document.getElementById('doc-assessment').textContent = d.assessment;
        document.getElementById('doc-notes').textContent = d.teacher_notes;
        emptyState.classList.add('hidden');
        outputContainer.classList.remove('hidden');
        lucide.createIcons();
    } catch (err) {
        errBox.textContent = "Error: " + err.message;
        errBox.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="sparkles" class="w-5 h-5"></i> Generate Material';
        lucide.createIcons();
    }
});
document.getElementById('printBtn').onclick = () => window.print();
document.getElementById('copyBtn').onclick = () => navigator.clipboard.writeText(document.getElementById('document-paper').innerText);
</script>
{% endblock %}
'''
with open('templates/teacher_studio/studio.html', 'w', encoding='utf-8') as f:
    f.write(template_content)
print("Template written successfully.")
print("=== STEP 4: FIXING MOCK PROVIDER ===")
provider_content = r'''
from .base import BaseProvider
import json
class MockProvider(BaseProvider):
    provider_name = "mock"
    def generate(self, prompt, system_prompt=None, **kwargs):
        if kwargs.get("mode") == "teacher" and kwargs.get("artifact_type") == "lesson_plan":
            topic = kwargs.get("topic", "Topic")
            cur = kwargs.get("curriculum", "CBC")
            lesson = {
                "title": topic.title(),
                "subject": "Biology",
                "curriculum": cur,
                "duration": "50 minutes",
                "outcomes": [
                    f"Explain {topic.lower()} using correct terminology.",
                    f"Apply knowledge of {topic.lower()} to real life.",
                    f"Demonstrate critical thinking competencies."
                ],
                "flow": [
                    {"step": "Introduction", "duration": "5 min", "content": f"Engage learners with a question about {topic.lower()}."},
                    {"step": "Main Activity", "duration": "25 min", "content": f"Guided exploration of {topic.lower()} using school resources."},
                    {"step": "Assessment", "duration": "10 min", "content": f"Formative check on {topic.lower()}."}
                ],
                "resources": "Textbook Ch 4, Whiteboard.",
                "differentiation": "Support: Sentence starters. Extension: Case study.",
                "assessment": "1. Define process. 2. Label diagram.",
                "teacher_notes": "Ensure safety protocols."
            }
            return json.dumps(lesson)
        return "Generated content."
'''
with open('apps/ai_gateway/providers/mock_provider.py', 'w', encoding='utf-8') as f:
    f.write(provider_content)
print("Mock provider fixed.")
print("\n=== ALL DONE ===")
print("1. Run: .\\jifunze runserver")
print("2. Go to: http://127.0.0.1:8000/studio/")
print("3. Click Generate Material.")
