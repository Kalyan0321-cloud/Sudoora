/* Homepage specific JS */
document.addEventListener('DOMContentLoaded', () => {

  // ─── Exchange Rate Display ──────────────────────────────────
  fetch('/api/exchange-rates')
    .then(r => r.json())
    .then(rates => {
      // Optionally display live rates somewhere
      console.log('Exchange rates loaded:', rates);
    })
    .catch(() => {});

  // ─── Destination Card Hover Effects ─────────────────────────
  document.querySelectorAll('.dest-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      const stripe = card.querySelector('.dest-stripe');
      if (stripe) {
        card.style.borderColor = stripe.style.background;
      }
    });
    card.addEventListener('mouseleave', () => {
      card.style.borderColor = '';
    });
  });

  // ─── Cost Calculator Bars Animation ─────────────────────────
  setTimeout(() => {
    document.querySelectorAll('.bar-fill').forEach(bar => {
      const width = bar.style.width;
      bar.style.width = '0';
      requestAnimationFrame(() => {
        setTimeout(() => bar.style.width = width, 100);
      });
    });
  }, 500);

  // ─── Hero Background Particle Effect ────────────────────────
  const hero = document.getElementById('hero');
  if (hero) {
    // Add subtle mouse parallax to shapes
    hero.addEventListener('mousemove', (e) => {
      const rect = hero.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      const shapes = hero.querySelectorAll('.shape');
      shapes.forEach((shape, i) => {
        const speed = (i + 1) * 12;
        shape.style.transform = `translate(${(x - 0.5) * speed}px, ${(y - 0.5) * speed}px)`;
      });
    });
  }

});
