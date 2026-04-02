/* ═══════════════════════════════════════════════════════════
   GlobEd Consultancy — Main JavaScript
═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ─── Sticky Navbar Shadow ───────────────────────────────────
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    });
  }

  // ─── Mobile Nav Toggle ──────────────────────────────────────
  const toggle = document.getElementById('navToggle');
  const menu = document.getElementById('navMenu');
  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      menu.classList.toggle('open');
      const spans = toggle.querySelectorAll('span');
      if (menu.classList.contains('open')) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      }
    });
  }

  // ─── Chatbot Widget ─────────────────────────────────────────
  const chatToggle = document.getElementById('chatbotToggle');
  const chatPanel = document.getElementById('chatbotPanel');
  const chatClose = document.getElementById('chatbotClose');
  const chatBadge = document.querySelector('.chat-badge');

  if (chatToggle && chatPanel) {
    chatToggle.addEventListener('click', () => {
      chatPanel.classList.toggle('open');
      if (chatBadge) chatBadge.style.display = 'none';
    });
    if (chatClose) chatClose.addEventListener('click', () => chatPanel.classList.remove('open'));
  }

  // ─── Quick Lead Form ─────────────────────────────────────────
  const quickLeadForm = document.getElementById('quickLeadForm');
  if (quickLeadForm) {
    quickLeadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('qlName')?.value;
      const phone = document.getElementById('qlPhone')?.value;
      const country = document.getElementById('qlCountry')?.value;

      if (!name || !phone) {
        alert('Please fill in your name and phone number.');
        return;
      }

      try {
        const res = await fetch('/api/lead', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, phone, email: `${phone}@placeholder.com`, preferred_country: country })
        });
        const data = await res.json();
        if (data.success) {
          quickLeadForm.innerHTML = `
            <div style="color:white;font-weight:700;font-size:1rem;padding:10px 0;">
              ✅ ${data.message}
            </div>`;
        }
      } catch {
        alert('Thank you! We will contact you shortly.');
        quickLeadForm.reset();
      }
    });
  }

  // ─── Animate Numbers (Stats counter) ────────────────────────
  const statNums = document.querySelectorAll('.stat-num[data-count]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCount(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  statNums.forEach(el => observer.observe(el));

  function animateCount(el) {
    const target = parseInt(el.dataset.count);
    const duration = 1800;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        el.textContent = target.toLocaleString();
        clearInterval(timer);
      } else {
        el.textContent = Math.floor(current).toLocaleString();
      }
    }, 16);
  }

  // ─── Scroll Reveal (lightweight) ────────────────────────────
  const revealEls = document.querySelectorAll('.dest-card, .uni-card, .news-card, .blog-card, .testimonial-card');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, i * 60);
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  revealEls.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    revealObserver.observe(el);
  });

});

// ─── Chatbot Functions (global) ────────────────────────────
async function sendChat() {
  const input = document.getElementById('chatInput');
  if (!input || !input.value.trim()) return;

  const msg = input.value.trim();
  input.value = '';

  appendChatMsg(msg, 'user');
  const typing = appendChatMsg('Typing...', 'bot');

  try {
    const res = await fetch('/api/chatbot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    typing.querySelector('.msg-bubble').textContent = data.response;
  } catch {
    typing.querySelector('.msg-bubble').textContent = 'Sorry, I\'m having trouble responding. Please call us at +91 98765 43210.';
  }
}

function sendQuickMsg(msg) {
  const input = document.getElementById('chatInput');
  if (input) input.value = msg;
  sendChat();
}

function appendChatMsg(text, type) {
  const messages = document.getElementById('chatbotMessages');
  if (!messages) return {};
  const div = document.createElement('div');
  div.className = type === 'user' ? 'user-msg' : 'bot-msg';
  div.innerHTML = `<div class="msg-bubble">${text}</div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

// Allow Enter key in chat input
document.addEventListener('DOMContentLoaded', () => {
  const chatInput = document.getElementById('chatInput');
  if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendChat();
    });
  }
});
