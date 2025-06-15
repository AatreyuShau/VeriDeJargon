window.onload = () => {
  // Show modal on load
  const modal = document.getElementById('modal-overlay');
  modal.style.display = 'grid';
};

function closeModal() {
  const modal = document.getElementById('modal-overlay');
  modal.style.display = 'none';
}
