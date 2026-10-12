(() => {
  const form = document.querySelector('[data-news-upload]');
  if (!form || !window.XMLHttpRequest || !window.FormData) return;
  const button = form.querySelector('[type="submit"]');
  const panel = document.createElement('div');
  panel.hidden = true;
  panel.innerHTML = '<progress max="100" value="0" aria-label="News upload progress" style="width:100%;height:16px"></progress><p role="status" aria-live="polite"></p>';
  button.before(panel);
  const bar = panel.querySelector('progress'), status = panel.querySelector('p');
  const original = button.textContent;
  let busy = false;
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (busy || !form.reportValidity()) return;
    const data = new FormData(form);
    busy = true; button.disabled = true; button.textContent = 'Uploading…';
    panel.hidden = false; bar.value = 0; status.textContent = 'Uploading: 0%';
    form.setAttribute('aria-busy', 'true');
    const xhr = new XMLHttpRequest();
    xhr.open('POST', form.action || window.location.href);
    xhr.timeout = 300000;
    const finish = message => {
      busy = false; button.disabled = false; button.textContent = original;
      form.removeAttribute('aria-busy'); status.textContent = message;
    };
    xhr.upload.onprogress = event => {
      if (event.lengthComputable) {
        const percent = Math.round(event.loaded / event.total * 100);
        bar.hidden = false; bar.value = percent;
        status.textContent = `Uploading: ${percent}%`;
      } else { bar.removeAttribute('value'); status.textContent = 'Uploading…'; }
    };
    xhr.upload.onload = () => {
      bar.removeAttribute('value'); button.textContent = 'Saving story…';
      status.textContent = 'Upload complete (100%). Saving and checking your story…';
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300 && xhr.responseURL && new URL(xhr.responseURL).pathname !== window.location.pathname) {
        window.location.assign(xhr.responseURL); return;
      }
      if (xhr.status === 400) {
        const doc = new DOMParser().parseFromString(xhr.responseText, 'text/html');
        const errors = Array.from(doc.querySelectorAll('.errorlist li')).map(node => {
          const label = node.closest('.nd-field')?.querySelector('label')?.textContent || '';
          return `${label} ${node.textContent}`.trim();
        });
        finish(errors.length ? errors.join(' · ') : 'Please check your fields and try again.');
      } else if (xhr.status === 413) {
        finish('The uploaded files are too large for the server. Choose smaller files.');
      } else if (xhr.status === 403) {
        finish('Your session or permission may have changed. Open News Desk in another tab and sign in before trying again.');
      } else {
        finish('The server could not confirm saving. Check My desk before submitting again to avoid duplicates.');
      }
    };
    xhr.onerror = xhr.ontimeout = () => finish('Connection interrupted or server timed out. Your form is still here. Check My desk before retrying.');
    xhr.send(data);
  });
})();
