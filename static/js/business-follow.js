document.addEventListener('submit', async event => {
  const form = event.target.closest('.business-follow-form');
  if (!form) return;
  event.preventDefault();
  const button = form.querySelector('button[name=action]');
  const endpoint = form.getAttribute('action');
  const data = new FormData(form);
  data.set('action', button.value);
  button.disabled = true;
  try {
    const response = await fetch(endpoint, {method:'POST', body:data, credentials:'same-origin', headers:{'X-Requested-With':'XMLHttpRequest'}});
    if (response.redirected) { location.assign(response.url); return; }
    if (!response.ok) throw new Error('Could not update follow');
    const result = await response.json();
    button.value = result.following ? 'unfollow' : 'follow';
    button.setAttribute('aria-pressed', String(result.following));
    button.textContent = result.following ? '✓ Following' : '+ Follow';
    document.querySelectorAll('[data-business-followers]').forEach(element => {
      if (element.dataset.businessFollowers === endpoint) element.textContent = result.followers;
    });
  } catch (_) { alert('Could not update your follow. Please try again.'); }
  finally { button.disabled = false; }
}, true);
