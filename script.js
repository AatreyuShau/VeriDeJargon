window.onload = () => {
  // Show modal on load
  const modal = document.getElementById('modal-overlay');
  modal.style.display = 'grid';
};

function closeModal() {
  const modal = document.getElementById('modal-overlay');
  modal.style.display = 'none';
}

// Add loading overlay logic
function showLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  const bar = document.getElementById('progress-bar');
  overlay.style.display = 'flex';
  bar.style.width = '0%';
  let progress = 0;
  // Animate progress bar to 90% over 3 seconds, then wait for completion
  window.loadingInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 5 + 2; // randomize for effect
      if (progress > 90) progress = 90;
      bar.style.width = progress + '%';
    }
  }, 200);
}

function hideLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  const bar = document.getElementById('progress-bar');
  if (window.loadingInterval) clearInterval(window.loadingInterval);
  bar.style.width = '100%';
  setTimeout(() => {
    overlay.style.display = 'none';
    bar.style.width = '0%';
  }, 400);
}

document.getElementById('summarizer-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const inputBox = document.getElementById('raw_in');
    const inputText = inputBox.value;
    showLoadingOverlay();
    fetch('/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
    })
    .then(res => res.json())
    .then(data => {
        inputBox.value = data.summary || data.output;
        // Show definitions below the textbox if present
        let defsDiv = document.getElementById('definitions-box');
        if (data.definitions) {
            if (!defsDiv) {
                defsDiv = document.createElement('div');
                defsDiv.id = 'definitions-box';
                inputBox.parentNode.appendChild(defsDiv);
            }
            let html = '<b>Key Terms:</b><ul>';
            for (const [word, def] of Object.entries(data.definitions)) {
                html += `<li><b>${word}:</b> ${def}</li>`;
            }
            html += '</ul>';
            defsDiv.innerHTML = html;
        } else if (defsDiv) {
            defsDiv.innerHTML = '';
        }
        hideLoadingOverlay();
    })
    .catch(err => {
        inputBox.value = 'Error: ' + err;
        hideLoadingOverlay();
    });
});

// Research mode tab logic
const researchTab = document.createElement('button');
researchTab.textContent = 'Research Mode';
researchTab.id = 'research-tab';
document.body.insertBefore(researchTab, document.body.firstChild);

researchTab.addEventListener('click', function() {
    let topic = prompt('Enter a research topic:');
    if (!topic) return;
    const inputBox = document.getElementById('raw_in');
    inputBox.value = '⏳ Researching... Please wait.';
    fetch('/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
    })
    .then(res => res.json())
    .then(data => {
        // Expecting { definition, overview, history, derivation, deepdive }
        let result = '';
        if (data.definition) result += `Definition:\n${data.definition}\n\n`;
        if (data.overview) result += `Overview:\n${data.overview}\n\n`;
        if (data.history) result += `History:\n${data.history}\n\n`;
        if (data.derivation) result += `Derivation:\n${data.derivation}\n\n`;
        if (data.deepdive) result += `Simplified Deep Dive:\n${data.deepdive}`;
        inputBox.value = result;
    })
    .catch(err => {
        inputBox.value = 'Error: ' + err;
    });
});
