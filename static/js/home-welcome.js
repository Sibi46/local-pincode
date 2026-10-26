(() => {
  const track = document.getElementById('local-welcome-cards');
  if (!track) return;
  const cards = [...track.querySelectorAll('.local-card')];
  const dots = [...document.querySelectorAll('[data-local-card]')];
  const previous = document.querySelector('[data-local-prev]');
  const next = document.querySelector('[data-local-next]');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let active = 0;
  function update() {
    const start = track.getBoundingClientRect().left;
    active = cards.reduce((nearest, card, index) =>
      Math.abs(card.getBoundingClientRect().left - start) < Math.abs(cards[nearest].getBoundingClientRect().left - start) ? index : nearest, 0);
    dots.forEach((dot, index) => {
      if (index === active) dot.setAttribute('aria-current', 'true');
      else dot.removeAttribute('aria-current');
    });
    previous.disabled = active === 0;
    next.disabled = active === cards.length - 1;
  }
  function goTo(index) {
    const card = cards[Math.max(0, Math.min(index, cards.length - 1))];
    track.scrollTo({left: track.scrollLeft + card.getBoundingClientRect().left - track.getBoundingClientRect().left - 2,
      behavior: motion.matches ? 'instant' : 'smooth'});
  }
  dots.forEach((dot, index) => dot.addEventListener('click', () => goTo(index)));
  previous.addEventListener('click', () => goTo(active - 1));
  next.addEventListener('click', () => goTo(active + 1));
  track.addEventListener('keydown', event => {
    if (event.target !== track || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    goTo(event.key === 'Home' ? 0 : event.key === 'End' ? cards.length - 1 : active + (event.key === 'ArrowRight' ? 1 : -1));
  });
  track.addEventListener('scroll', update, {passive:true});
  window.addEventListener('resize', update);
  window.addEventListener('welcomeintro:opened', () => requestAnimationFrame(update));
  update();
})();
