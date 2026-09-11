// 0. Day / Night Mode Toggle
window.applyTheme = function(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  try { localStorage.setItem('autogram_theme', theme); } catch (e) {}
  const icon = document.getElementById('theme-toggle-icon');
  const label = document.getElementById('theme-toggle-label');
  if (icon) icon.textContent = theme === 'light' ? '☀️' : '🌙';
  if (label) label.textContent = theme === 'light' ? 'LIGHT' : 'DARK';
};

window.toggleTheme = function() {
  const cur = document.documentElement.getAttribute('data-theme') || 'dark';
  window.applyTheme(cur === 'light' ? 'dark' : 'light');
};

// Cross-tab sync between landing page and dashboard
window.addEventListener('storage', (e) => {
  if (e.key === 'autogram_theme' && e.newValue) {
    window.applyTheme(e.newValue);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('autogram_theme') || 'dark';
  window.applyTheme(savedTheme);
  // 1. Pricing Annual / Monthly Switch Toggle
  const switchPill = document.getElementById('pricing-switch');
  const monthlyLabel = document.getElementById('monthly-toggle-label');
  const annualLabel = document.getElementById('annual-toggle-label');

  const priceStarter = document.getElementById('price-starter');
  const priceGrowth = document.getElementById('price-growth');
  const priceEnterprise = document.getElementById('price-enterprise');

  let isAnnual = false;

  function updatePricing() {
    if (!switchPill) return;
    if (isAnnual) {
      switchPill.classList.add('annual');
      if (annualLabel) annualLabel.classList.add('active');
      if (monthlyLabel) monthlyLabel.classList.remove('active');

      if (priceStarter) priceStarter.textContent = '$397';
      if (priceGrowth) priceGrowth.textContent = '$797';
      if (priceEnterprise) priceEnterprise.textContent = '$1,997';
    } else {
      switchPill.classList.remove('annual');
      if (monthlyLabel) monthlyLabel.classList.add('active');
      if (annualLabel) annualLabel.classList.remove('active');

      if (priceStarter) priceStarter.textContent = '$497';
      if (priceGrowth) priceGrowth.textContent = '$997';
      if (priceEnterprise) priceEnterprise.textContent = '$2,497';
    }
  }

  if (switchPill) {
    switchPill.addEventListener('click', () => {
      isAnnual = !isAnnual;
      updatePricing();
    });
  }

  if (monthlyLabel) monthlyLabel.addEventListener('click', () => { isAnnual = false; updatePricing(); });
  if (annualLabel) annualLabel.addEventListener('click', () => { isAnnual = true; updatePricing(); });

  // 2. Interactive Terminal Console
  const terminalBody = document.getElementById('terminal-body');
  const terminalBtns = document.querySelectorAll('.t-cmd-btn');

  function appendTerminal(text, type = '') {
    if (!terminalBody) return;
    const line = document.createElement('div');
    line.className = `terminal-line ${type}`;
    line.textContent = text;
    terminalBody.appendChild(line);
    terminalBody.scrollTop = terminalBody.scrollHeight;
  }

  const CMD_OUTPUTS = {
    'status': [
      '> autogram --status',
      '[SYS] System Kernel: v2.4-STABLE',
      '[NET] Instagram Graph API: CONNECTED (Quota: 1/50)',
      '[AI] LLM Pipeline: READY (Gemini / Groq / Free Engine)',
      '[RENDER] Playwright Headless Chromium: 1080x1350 READY',
      '[LOG] Recent memory: 4 items loaded. Anti-repetition active.'
    ],
    'generate': [
      '> autogram --generate',
      '[LAYER-A] Fetching fresh research feeds (ArXiv, TechCrunch)...',
      '[LAYER-B] Top candidate: "Compound AI Systems in Production"',
      '[LAYER-C] Generating 8-slide structured narrative JSON...',
      '[LAYER-C] Fact-Check Audit: 8/8 Claims VERIFIED',
      '[LAYER-C] Quality Gate: PASSED (Score: 100/100)',
      '[RENDER] Capturing 8 high-res JPEG slides...',
      '[SUCCESS] Staged at output/2026-09-09. Zero human intervention needed.'
    ],
    'verify': [
      '> autogram --verify',
      '[AUDIT] Dimension check: 1080x1350 px (4:5 portrait) - OK',
      '[AUDIT] Typography bounding box check: 0 overflow - OK',
      '[AUDIT] Banned phrase check: 0 violations detected - OK',
      '[AUDIT] Meta Content Publishing Limit: 49 slots available today',
      '[AUDIT] All automated guardrails green.'
    ],
    'pricing': [
      '> autogram --pricing',
      'STARTER: $497/mo (15 bespoke carousels, 1 pillar)',
      'GROWTH AUTOPILOT: $997/mo (30 daily carousels, full 6-pillar rotation, Meta publishing)',
      'ENTERPRISE SWARM: $2,497/mo (Multi-account network, custom MCP, dedicated SLA)',
      'Run: Click [Deploy My Autopilot] to lock in launch pricing.'
    ]
  };

  terminalBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.getAttribute('data-cmd');
      const lines = CMD_OUTPUTS[cmd] || [`Unknown command: ${cmd}`];
      lines.forEach((l, idx) => {
        setTimeout(() => {
          appendTerminal(l, l.includes('SUCCESS') ? 'success' : (l.includes('>') ? 'info' : ''));
        }, idx * 100);
      });
    });
  });

  // 3. Client UPI Payment & WhatsApp Confirmation Modal
  const modal = document.getElementById('booking-modal');
  const modalClose = document.getElementById('modal-close-btn');
  const openModalBtns = document.querySelectorAll('.trigger-booking-modal');
  const portalModal = document.getElementById('portal-modal');

  const planPrices = {
    'Starter Autopilot': { inr: '₹39,999 / mo', usd: '$497 USD equivalent', amt: '39999' },
    'Growth Autopilot': { inr: '₹79,999 / mo', usd: '$997 USD equivalent', amt: '79999' },
    'Enterprise Swarm': { inr: '₹1,99,999 / mo', usd: '$2,497 USD equivalent', amt: '199999' }
  };

  openModalBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const planName = btn.getAttribute('data-plan') || 'Growth Autopilot';
      const planTitle = document.getElementById('modal-plan-title');
      const planPriceInr = document.getElementById('modal-plan-price-inr');
      const planPriceUsd = document.getElementById('modal-plan-price-usd');
      const qrImg = document.getElementById('upi-qr-image');

      if (planTitle) planTitle.textContent = planName;
      const details = planPrices[planName] || planPrices['Growth Autopilot'];
      if (planPriceInr) planPriceInr.innerHTML = `${details.inr.split(' ')[0]}<span style="font-size: 12px; color: var(--text-muted);"> / mo</span>`;
      if (planPriceUsd) planPriceUsd.textContent = details.usd;

      if (qrImg) {
        const upiUri = `upi://pay?pa=6202442690@jio&pn=Autogram%20AI&am=${details.amt}&cu=INR`;
        qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(upiUri)}`;
      }

      if (portalModal) portalModal.classList.remove('active');
      if (modal) modal.classList.add('active');
    });
  });

  if (modalClose) {
    modalClose.addEventListener('click', () => {
      if (modal) modal.classList.remove('active');
    });
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }

  // Copy UPI ID Button
  const copyUpiBtn = document.getElementById('copy-upi-btn');
  const upiIdInput = document.getElementById('upi-id-input');
  if (copyUpiBtn && upiIdInput) {
    copyUpiBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(upiIdInput.value).then(() => {
        const originalText = copyUpiBtn.textContent;
        copyUpiBtn.textContent = '✓ Copied!';
        copyUpiBtn.style.borderColor = 'var(--neon-green)';
        copyUpiBtn.style.color = 'var(--neon-green)';
        setTimeout(() => {
          copyUpiBtn.textContent = originalText;
          copyUpiBtn.style.borderColor = '';
          copyUpiBtn.style.color = '';
        }, 2000);
      });
    });
  }

  // WhatsApp Screenshot Confirmation Button
  const whatsappSubmitBtn = document.getElementById('whatsapp-submit-btn');
  if (whatsappSubmitBtn) {
    whatsappSubmitBtn.addEventListener('click', () => {
      const clientName = (document.getElementById('checkout-client-name')?.value || '').trim() || 'Valued Client';
      const igHandle = (document.getElementById('checkout-ig-handle')?.value || '').trim() || '@instagram';
      const planTitle = document.getElementById('modal-plan-title')?.textContent || 'Growth Autopilot';
      const details = planPrices[planTitle] || planPrices['Growth Autopilot'];

      const msg = `Hi Piyush, I have completed the UPI payment for Autogram AI.\n\n` +
        `📦 Plan: ${planTitle}\n` +
        `💰 Price: ${details.inr} (${details.usd})\n` +
        `🏢 Name / Company: ${clientName}\n` +
        `📸 Instagram Handle: ${igHandle}\n\n` +
        `Attached is my payment screenshot for verification. Please send my Client License Key to activate my Autogram Studio!`;

      const waUrl = `https://wa.me/916202442690?text=${encodeURIComponent(msg)}`;
      window.open(waUrl, '_blank');

      alert("Opening WhatsApp (+91 6202442690) to send your payment screenshot. Piyush will verify the transaction and send your license key within 15 minutes!");
      if (modal) modal.classList.remove('active');
    });
  }
});

