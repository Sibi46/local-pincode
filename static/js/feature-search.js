(() => {
  const form = document.getElementById('featureSearchForm');
  if (!form) return;
  const input = document.getElementById('homeSearchInput');
  const results = document.getElementById('featureSearchResults');
  const features = JSON.parse(document.getElementById('feature-catalog').textContent);
  function search() {
    const query = input.value.trim().toLowerCase();
    results.replaceChildren(); results.hidden = !query;
    if (!query) return;
    const matches = features.filter(item => query.split(/\s+/).every(word => (item.name + ' ' + item.keywords).toLowerCase().includes(word)));
    matches.forEach(item => {
      const link = document.createElement('a'); link.href = item.url;
      const title = document.createElement('strong'); title.textContent = item.name;
      link.append(title); results.append(link);
    });
    if (!matches.length) { const empty = document.createElement('p'); empty.textContent = 'No features found. Try jobs, quiz, offers or health.'; results.append(empty); }
  }
  input.addEventListener('input', search);
  input.addEventListener('keydown', event => { if (event.key === 'Escape') { input.value = ''; search(); } });
  form.addEventListener('submit', event => { event.preventDefault(); search(); const first = results.querySelector('a'); if (first) first.focus(); });
})();
