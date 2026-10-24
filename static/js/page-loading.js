(function () {
  'use strict';
  var bar = document.getElementById('opc-bar');
  var loader = document.getElementById('opc-loader');
  if (!bar || !loader) return;
  var overlayTimer, recoveryTimer;
  function finish() {
    clearTimeout(overlayTimer);
    clearTimeout(recoveryTimer);
    loader.style.display = 'none';
    loader.setAttribute('aria-hidden', 'true');
    bar.style.opacity = '0';
    bar.style.width = '0%';
  }
  function start() {
    finish();
    bar.style.opacity = '1';
    bar.style.width = '70%';
    overlayTimer = setTimeout(function () {
      loader.style.display = 'flex';
      loader.setAttribute('aria-hidden', 'false');
    }, 400);
    // A failed download/navigation must never leave the page blocked indefinitely.
    recoveryTimer = setTimeout(function () {
      finish();
      var error = document.getElementById('opc-loading-error');
      if (!error) {
        error = document.createElement('p');
        error.id = 'opc-loading-error';
        error.setAttribute('role', 'alert');
        error.style.cssText = 'position:fixed;bottom:85px;left:16px;right:16px;z-index:99999;padding:14px;background:#fff7ed;color:#7c2d12;border:1px solid #fdba74;border-radius:12px';
        document.body.appendChild(error);
      }
      error.textContent = 'This is taking longer than expected. Check your connection and try again.';
    }, 15000);
  }
  document.addEventListener('click', function (event) {
    var link = event.target.closest('a');
    if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    if (link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
    var url = new URL(link.href, location.href);
    if (!/^https?:$/.test(url.protocol) || url.origin !== location.origin) return;
    if (url.pathname === location.pathname && url.search === location.search && url.hash) return;
    start();
  });
  document.addEventListener('submit', function (event) {
    if (!event.defaultPrevented && event.target.method !== 'dialog' && !event.target.target) start();
  });
  window.addEventListener('pageshow', finish);
  finish();
})();
