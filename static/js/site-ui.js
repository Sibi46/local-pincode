(() => {
  function start() {
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'opc-theme-toggle';
    function update() {
      const dark = document.documentElement.dataset.theme === 'dark';
      toggle.setAttribute('aria-pressed', String(dark));
      toggle.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      toggle.title = toggle.getAttribute('aria-label');
      toggle.innerHTML = '<i class="fas fa-' + (dark ? 'sun' : 'moon') + '" aria-hidden="true"></i>';
    }
    toggle.addEventListener('click', () => {
      const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = theme;
      try { localStorage.setItem('opc-theme', theme); } catch (error) { /* Storage may be disabled. */ }
      update();
    });
    const header = document.querySelector('.tb-right,.dash-topbar-right,.nav-links,.bp-topbar,.msg-topnav,.sp-topnav,.pj-nav');
    if (header) header.append(toggle);
    else { toggle.classList.add('opc-theme-floating'); document.body.append(toggle); }
    update();
    // Let CSS reserve room only on pages which actually render primary navigation.
    document.body.classList.toggle('opc-has-nav', !!document.querySelector('.opc-bottom-nav'));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
