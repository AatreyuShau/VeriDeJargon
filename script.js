window.onload = () => {
  // Show modal on load
  const modal = document.getElementById('modal-overlay');
  modal.style.display = 'grid';
};

function closeModal() {
  const modal = document.getElementById('modal-overlay');
  modal.style.display = 'none';
}

document.getElementById('summarizer-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const inputBox = document.getElementById('raw_in');
    const inputText = inputBox.value;
    // Show loading message
    inputBox.value = '⏳ Simplifying... Please wait.';
    fetch('/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
    })
    .then(res => res.json())
    .then(data => {
        // Display summary directly in the input box
        inputBox.value = data.output;
    })
    .catch(err => {
        inputBox.value = 'Error: ' + err;
    });
});
