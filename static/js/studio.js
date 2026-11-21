console.log("JIFUNZE STUDIO JS LOADED");
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('genform');
    const btn = document.getElementById('generateBtn');
    const errBox = document.getElementById('error-box');
    const emptyState = document.getElementById('empty-state');
    const outputContainer = document.getElementById('output-container');
    const outputHtml = document.getElementById('output-html');
    if (!form) { console.error("Form not found!"); return; }
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log("FORM SUBMITTED");
        errBox.classList.add('hidden');
        btn.disabled = true;
        btn.innerText = 'Generating...';
        const csrfToken = document.getElementById('csrf-token').value;
        const body = {
            artifact_type: document.getElementById('atype').value,
            topic: document.getElementById('topic').value,
            subtopic: document.getElementById('subtopic').value,
            grade_level: document.getElementById('grade').value,
            curriculum: document.getElementById('curr').value,
            week: document.getElementById('week').value,
            term: document.getElementById('term').value
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
            console.log("Response status:", response.status);
            if (!response.ok) {
                return response.text().then(text => { throw new Error('Server Error ' + response.status + ': ' + text.substring(0, 300)); });
            }
            return response.json();
        })
        .then(data => {
            console.log("Success!", data);
            emptyState.classList.add('hidden');
            outputContainer.classList.remove('hidden');
            outputHtml.innerText = data.content || "Content generated.";
        })
        .catch(error => {
            console.error("Error:", error);
            errBox.textContent = error.message;
            errBox.classList.remove('hidden');
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerText = 'Generate Material';
        });
    });
});
