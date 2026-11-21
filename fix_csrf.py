import os
os.chdir(r"C:\Users\ESTHER M\Documents\jifunze_ai")
html_content = """{% extends "base.html" %}
{% load static %}
{% block title %}Teacher Studio{% endblock %}
{% block content %}
<div class="max-w-4xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold mb-6">Teacher Studio</h1>
  <div id="error-box" class="hidden bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"></div>
  <div class="grid md:grid-cols-2 gap-8">
    <div class="bg-white p-6 rounded-lg shadow">
      <form id="genform" class="space-y-4">
        <!-- FOOLPROOF DJANGO CSRF TOKEN -->
        {% csrf_token %}
        <div>
          <label class="block text-sm font-bold mb-1">Topic</label>
          <input id="topic" value="Photosynthesis" class="w-full border rounded px-3 py-2" required>
        </div>
        <div>
          <label class="block text-sm font-bold mb-1">Grade</label>
          <input id="grade" value="Form 2" class="w-full border rounded px-3 py-2">
        </div>
        <div>
          <label class="block text-sm font-bold mb-1">Curriculum</label>
          <select id="curr" class="w-full border rounded px-3 py-2">
            <option>CBC/CBE</option>
            <option selected>Cambridge IGCSE</option>
          </select>
        </div>
        <button type="submit" id="generateBtn" class="w-full bg-indigo-900 text-white font-bold py-3 rounded hover:bg-indigo-800">
          Generate Material
        </button>
      </form>
    </div>
    <div>
      <div id="empty-state" class="bg-white p-12 rounded-lg shadow text-center text-gray-500 border-2 border-dashed">
        Generated content will appear here.
      </div>
      <div id="output-container" class="hidden bg-white p-6 rounded-lg shadow">
        <h2 class="text-xl font-bold mb-4">Generated Content</h2>
        <div id="output-html" class="whitespace-pre-wrap"></div>
      </div>
    </div>
  </div>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('genform');
    const btn = document.getElementById('generateBtn');
    const errBox = document.getElementById('error-box');
    const emptyState = document.getElementById('empty-state');
    const outputContainer = document.getElementById('output-container');
    const outputHtml = document.getElementById('output-html');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        errBox.classList.add('hidden');
        btn.disabled = true;
        btn.innerText = 'Generating...';
        // OFFICIAL DJANGO WAY TO GET CSRF TOKEN
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const body = {
            artifact_type: 'lesson_plan',
            topic: document.getElementById('topic').value,
            grade_level: document.getElementById('grade').value,
            curriculum: document.getElementById('curr').value
        };
        fetch('/api/teacher/artifacts/generate/', {
            method: 'POST',
            headers: { 
                'X-CSRFToken': csrfToken, 
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(body)
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error('HTTP ' + response.status + ': ' + text.substring(0, 300)); });
            }
            return response.json();
        })
        .then(data => {
            emptyState.classList.add('hidden');
            outputContainer.classList.remove('hidden');
            outputHtml.innerText = data.content || "Success!";
        })
        .catch(error => {
            errBox.textContent = error.message;
            errBox.classList.remove('hidden');
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerText = 'Generate Material';
        });
    });
});
</script>
{% endblock %}"""
with open("templates/teacher_studio/studio.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Template fixed with official Django CSRF handling.")
