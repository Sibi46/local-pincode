(() => {
  const nav = document.querySelector('.offer-filters');
  const results = document.getElementById('offer-results');
  if (!nav || !results || !window.fetch || !window.AbortController) return;
  const status = document.getElementById('offer-filter-status');
  const error = document.getElementById('offer-filter-error');
  let controller;
  const activeLink = nav.querySelector('[aria-current]');
  let selected = activeLink ? new URL(activeLink.href).searchParams.get('cat') || '' : '';
  function highlight(category) {
    nav.querySelectorAll('a').forEach(link => {
      if ((new URL(link.href).searchParams.get('cat') || '') === category) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }
  async function load(url, updateHistory) {
    if (controller) controller.abort();
    const current = new AbortController();
    controller = current;
    const category = url.searchParams.get('cat') || '';
    highlight(category);
    error.hidden = true;
    status.textContent = 'Loading offers…';
    results.setAttribute('aria-busy', 'true');
    const endpoint = new URL(url);
    endpoint.searchParams.set('format', 'json');
    try {
      const response = await fetch(endpoint, {signal: current.signal, headers: {'Accept': 'application/json'}});
      if (!response.ok) throw new Error('Offer request failed');
      const data = await response.json();
      if (current.signal.aborted) return;
      results.innerHTML = data.html;
      window.OFFERS_DATA = data.offers;
      selected = data.category;
      highlight(selected);
      document.getElementById('offer-count').textContent = data.count + ' offers';
      status.textContent = data.count + (data.count === 1 ? ' offer found.' : ' offers found.');
      if (updateHistory) history.pushState(null, '', url.pathname + url.search);
    } catch (failure) {
      if (current.signal.aborted) return;
      highlight(selected);
      status.textContent = '';
      error.replaceChildren(document.createTextNode('Could not update offers. Check your connection. '));
      const retry = document.createElement('a');
      retry.href = url.pathname + url.search;
      retry.textContent = 'Try loading this category again';
      error.append(retry);
      error.hidden = false;
    } finally {
      if (controller === current) results.removeAttribute('aria-busy');
    }
  }
  document.addEventListener('click', event => {
    const link = event.target.closest('.offer-filters a, #offer-results .offers-empty a');
    if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    load(new URL(link.href), true);
  });
  window.addEventListener('popstate', () => load(new URL(location.href), false));
})();
