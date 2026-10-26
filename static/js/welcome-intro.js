(() => {
  'use strict';
  const dialog = document.getElementById('welcomeIntro');
  const key = 'opc-welcome-local-v2';
  if (!dialog || typeof dialog.showModal !== 'function') return;
  for (const storage of ['localStorage', 'sessionStorage']) {
    try { if (window[storage].getItem(key)) return; } catch (_) { /* Storage may be unavailable. */ }
  }
  if (location.search || location.hash) return;
  const previousFocus = document.activeElement;
  function complete() {
    for (const storage of ['localStorage', 'sessionStorage']) {
      try { window[storage].setItem(key, 'done'); } catch (_) { /* Keep navigation available. */ }
    }
    dialog.close();
    document.documentElement.classList.remove('welcome-open');
    if (previousFocus && previousFocus !== document.body) previousFocus.focus();
  }
  dialog.querySelector('[data-welcome-skip]').addEventListener('click', complete);
  dialog.querySelector('[data-welcome-complete]').addEventListener('click', complete);
  dialog.querySelectorAll('.local-card-cta').forEach(link => link.addEventListener('click', complete));
  dialog.addEventListener('cancel', event => { event.preventDefault(); complete(); });
  dialog.showModal();
  document.documentElement.classList.add('welcome-open');
  window.dispatchEvent(new Event('welcomeintro:opened'));
})();
