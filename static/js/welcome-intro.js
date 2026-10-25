(() => {
  'use strict';
  const dialog = document.getElementById('welcomeIntro');
  const key = 'opc-welcome-v1';
  if (!dialog || typeof dialog.showModal !== 'function') return;
  let dismissed = false;
  for (const storage of ['localStorage', 'sessionStorage']) {
    try { dismissed = dismissed || Boolean(window[storage].getItem(key)); } catch (error) { /* Private browsing can disable storage. */ }
  }
  if (dismissed) return;
  // Keep account recovery, campaign and signup links on their requested journey.
  if (location.search || location.hash) return;
  const slides = [
    {eyebrow:'01 / YOUR BUSINESS', title:'Register your business.\nReach more customers.', text:'Bring your shop or service closer to the people around you. Create a business profile, share what you offer, and help local customers discover you.', icon:'store', badge:'GROW LOCAL', accent:'#126452', soft:'#d9ede3', action:'Register your business', href:'/register/?type=company'},
    {eyebrow:'02 / YOUR COMMUNITY', title:'Your neighbourhood.\nYour kind of people.', text:'Find communities around you, join conversations, share updates and celebrate local moments. Build stronger connections with the people who make your area feel like home.', icon:'users', badge:'BELONG HERE', accent:'#6551a1', soft:'#e8e1f4', action:'Explore communities', href:'/community/'},
    {eyebrow:'03 / LOCAL NEWS', title:'Stay close to\nwhat is happening.', text:'Discover published stories and updates for your area. Explore local news by PIN code and stay connected to the places and people that matter to you.', icon:'newspaper', badge:'STAY INFORMED', accent:'#215f98', soft:'#dcebf6', action:'Read local news', href:'/news/'},
    {eyebrow:'04 / NEARBY OFFERS', title:'Great finds.\nCloser to home.', text:'Explore offers from local businesses, discover something new and share a good find with friends. See available deals and visit the businesses behind them.', icon:'tags', badge:'DISCOVER LOCAL', accent:'#a04d28', soft:'#f5e2d5', action:'Discover offers', href:'/advertise/'},
    {eyebrow:'05 / WELCOME HOME', title:'One PIN code.\nSo many possibilities.', text:'Businesses, communities, news, offers and everyday local services — all in one place. Start exploring OURPINCODE and discover what is around you.', icon:'map-marker-alt', badge:'YOUR LOCAL WORLD', accent:'#126452', soft:'#d9ede3', action:'', href:''}
  ];
  const title = document.getElementById('welcomeTitle');
  const description = document.getElementById('welcomeDescription');
  const action = document.getElementById('welcomeAction');
  const next = document.getElementById('welcomeNext');
  const back = document.getElementById('welcomeBack');
  const dots = [...dialog.querySelectorAll('[data-welcome-slide]')];
  let current = 0;
  const previousFocus = document.activeElement;
  function complete() {
    try { localStorage.setItem(key, 'done'); } catch (error) { /* Fall back to the current session. */ }
    try { sessionStorage.setItem(key, 'done'); } catch (error) { /* Navigation still works without storage. */ }
    dialog.close();
    document.documentElement.classList.remove('welcome-open');
    if (previousFocus && previousFocus !== document.body) previousFocus.focus();
  }
  function render(index) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    const slide = slides[current];
    title.replaceChildren(...slide.title.split('\n').flatMap((line, index) => index ? [document.createElement('br'), document.createTextNode(line)] : [document.createTextNode(line)]));
    description.textContent = slide.text;
    document.getElementById('welcomeEyebrow').textContent = slide.eyebrow;
    document.getElementById('welcomeIcon').className = 'fas fa-' + slide.icon;
    document.getElementById('welcomeBadge').textContent = slide.badge;
    document.getElementById('welcomeCount').textContent = `${current + 1} of ${slides.length}`;
    dialog.style.setProperty('--welcome-accent', slide.accent);
    dialog.style.setProperty('--welcome-soft', slide.soft);
    action.hidden = !slide.action;
    action.textContent = slide.action;
    action.href = slide.href || '/';
    back.disabled = current === 0;
    next.textContent = current === slides.length - 1 ? 'Explore home →' : 'Next →';
    dots.forEach((dot, index) => index === current ? dot.setAttribute('aria-current', 'step') : dot.removeAttribute('aria-current'));
    dialog.scrollTop = 0;
  }
  next.addEventListener('click', () => current === slides.length - 1 ? complete() : render(current + 1));
  back.addEventListener('click', () => render(current - 1));
  dialog.querySelector('[data-welcome-skip]').addEventListener('click', complete);
  action.addEventListener('click', complete);
  dots.forEach((dot, index) => dot.addEventListener('click', () => render(index)));
  dialog.addEventListener('cancel', event => { event.preventDefault(); complete(); });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight') { event.preventDefault(); render(current + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); render(current - 1); }
  });
  render(0);
  dialog.showModal();
  document.documentElement.classList.add('welcome-open');
})();
