// 0. Spatial 5-Theme Preset Engine
const THEME_MAP = {
  'dark':        { icon: '🌙', label: 'QUANTUM' },
  'cyberpunk':   { icon: '⚡', label: 'CYBER' },
  'neumorphic':  { icon: '🫧', label: 'NEO' },
  'swiss-light': { icon: '📰', label: 'SWISS' },
  'bento-grid':  { icon: '🧱', label: 'BENTO' },
  'light':       { icon: '☀️', label: 'DAY' }
};

window.applyTheme = function(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  try { localStorage.setItem('autogram_theme', theme); } catch (e) {}
  const meta = THEME_MAP[theme] || THEME_MAP['dark'];
  const icon = document.getElementById('theme-toggle-icon');
  const label = document.getElementById('theme-toggle-label');
  if (icon) icon.textContent = meta.icon;
  if (label) label.textContent = meta.label;
  document.querySelectorAll('.theme-pick').forEach(b => {
    b.classList.toggle('active', b.dataset.theme === theme);
  });
  const dd = document.getElementById('theme-picker-dropdown');
  if (dd) dd.classList.remove('open');
};

window.toggleThemePicker = function() {
  const dd = document.getElementById('theme-picker-dropdown');
  if (dd) dd.classList.toggle('open');
};

window.toggleTheme = function() {
  const cur = document.documentElement.getAttribute('data-theme') || 'dark';
  window.applyTheme(cur === 'light' ? 'dark' : 'light');
};

// Close theme picker on outside click
document.addEventListener('click', (e) => {
  const picker = document.getElementById('theme-picker');
  const dd = document.getElementById('theme-picker-dropdown');
  if (picker && dd && !picker.contains(e.target)) dd.classList.remove('open');
});

// Cross-tab sync between landing page and dashboard
window.addEventListener('storage', (e) => {
  if (e.key === 'autogram_theme' && e.newValue) {
    window.applyTheme(e.newValue);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('autogram_theme') || 'dark';
  window.applyTheme(savedTheme);
  // ─── 1. Pricing: single live state, hydrated from /api/auth/pricing (data/pricing.json) ───
  // Fallbacks mirror data/pricing.json; the fetch below overrides them when the API is up.
  window.AUTOGRAM_PRICING = {
    currency: 'USD',
    upi: { id: '6202442690@jio', payee_name: 'Autogram AI', whatsapp_number: '916202442690', whatsapp_display: '+91 6202442690' },
    tiers: {
      starter:    { key: 'starter',    name: 'Starter Autopilot',  price_monthly: 29,  price_annual: 290,  tagline: '15 Carousels/mo · 1 Core Pillar',        cta_label: 'Deploy My Autopilot',      checkout_style: 'upi',     stripe_url: null },
      growth:     { key: 'growth',     name: 'Growth Autopilot',   price_monthly: 79,  price_annual: 790,  tagline: '30 Daily Carousels · Full Rotation',     cta_label: 'Deploy My Autopilot',      checkout_style: 'upi',     stripe_url: null },
      agency_pro: { key: 'agency_pro', name: 'Enterprise Swarm',   price_monthly: 199, price_annual: 1990, tagline: 'Multi-Account · Dedicated SLA',          cta_label: 'Talk to Enterprise',       checkout_style: 'contact', stripe_url: null }
    },
    loaded: false
  };

  const tierByKey = (k) => window.AUTOGRAM_PRICING.tiers[k] || null;
  const legacyPlanToTier = { 'Starter Autopilot': 'starter', 'Growth Autopilot': 'growth', 'Enterprise Swarm': 'agency_pro' };

  function hydratePricingFromAPI() {
    return fetch('/api/auth/pricing')
      .then(r => r.json())
      .then(res => {
        if (!res || !res.ok || !res.tiers) return;
        const P = window.AUTOGRAM_PRICING;
        ['starter', 'growth', 'agency_pro'].forEach(k => {
          if (res.tiers[k]) P.tiers[k] = Object.assign({}, P.tiers[k], res.tiers[k], { key: k });
        });
        if (res.upi && res.upi.id) P.upi = Object.assign({}, P.upi, res.upi);
        if (res.currency) P.currency = res.currency;
        P.loaded = true;
      })
      .catch(() => { /* static hosting / API down — fallbacks above stay canonical */ });
  }

  function renderPricingUI() {
    const P = window.AUTOGRAM_PRICING;
    const isAnnual = P.isAnnual === true;

    // Every element with data-price-for="<tier>" gets the current number.
    document.querySelectorAll('[data-price-for]').forEach(el => {
      const t = tierByKey(el.getAttribute('data-price-for'));
      if (!t) return;
      const val = isAnnual ? Math.round(t.price_annual / 12) : t.price_monthly;
      el.textContent = `$${val}`;
    });
    document.querySelectorAll('[data-price-period]').forEach(el => {
      el.textContent = isAnnual ? '/mo billed annually' : '/mo';
    });
    document.querySelectorAll('[data-tagline-for]').forEach(el => {
      const t = tierByKey(el.getAttribute('data-tagline-for'));
      if (t && t.tagline) el.textContent = t.tagline;
    });
    document.querySelectorAll('[data-cta-for]').forEach(el => {
      const t = tierByKey(el.getAttribute('data-cta-for'));
      if (t && t.cta_label) el.textContent = t.cta_label;
    });

    // UPI details everywhere (paywall banner + checkout modal inputs)
    document.querySelectorAll('[data-upi-id]').forEach(el => { el.textContent = P.upi.id; });
    const upiInput = document.getElementById('upi-id-input');
    if (upiInput) upiInput.value = P.upi.id;
    const directUpi = document.getElementById('direct-upi-link');
    if (directUpi) directUpi.href = `upi://pay?pa=${encodeURIComponent(P.upi.id)}&pn=${encodeURIComponent(P.upi.payee_name || 'Autogram AI')}&cu=INR`;
    document.querySelectorAll('[data-upi-whatsapp]').forEach(el => { el.textContent = P.upi.whatsapp_display || P.upi.whatsapp_number; });

    if (switchPill) switchPill.classList.toggle('annual', isAnnual);
    if (monthlyLabel) monthlyLabel.classList.toggle('active', !isAnnual);
    if (annualLabel) annualLabel.classList.toggle('active', isAnnual);
  }

  const switchPill = document.getElementById('pricing-switch');
  const monthlyLabel = document.getElementById('monthly-toggle-label');
  const annualLabel = document.getElementById('annual-toggle-label');

  function setBillingPeriod(annual) {
    window.AUTOGRAM_PRICING.isAnnual = annual;
    renderPricingUI();
  }

  if (switchPill) {
    switchPill.addEventListener('click', () => setBillingPeriod(!window.AUTOGRAM_PRICING.isAnnual));
  }
  if (monthlyLabel) monthlyLabel.addEventListener('click', () => setBillingPeriod(false));
  if (annualLabel) annualLabel.addEventListener('click', () => setBillingPeriod(true));

  // Hydrate prices + UPI from the canonical source, then paint every pricing surface.
  hydratePricingFromAPI().then(renderPricingUI);

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
      () => {
        const t = window.AUTOGRAM_PRICING.tiers;
        return `STARTER: $${t.starter.price_monthly}/mo (30 carousels, 1 account)`;
      },
      () => {
        const t = window.AUTOGRAM_PRICING.tiers;
        return `GROWTH AUTOPILOT: $${t.growth.price_monthly}/mo (120 carousels + 40 reels, 7x scheduler, Meta publishing)`;
      },
      () => {
        const t = window.AUTOGRAM_PRICING.tiers;
        return `ENTERPRISE SWARM: $${t.agency_pro.price_monthly}/mo (Multi-account network, white-label, dedicated SLA)`;
      },
      'Run: Click [Deploy My Autopilot] to lock in launch pricing.'
    ]
  };

  terminalBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.getAttribute('data-cmd');
      const lines = CMD_OUTPUTS[cmd] || [`Unknown command: ${cmd}`];
    lines.forEach((l, idx) => {
      setTimeout(() => {
        const text = typeof l === 'function' ? l() : l;
        appendTerminal(text, text.includes('SUCCESS') ? 'success' : (text.includes('>') ? 'info' : ''));
      }, idx * 100);
    });
    });
  });

  // 3. Client Checkout Modal — keyed by tier key (starter/growth/agency_pro)
  const modal = document.getElementById('booking-modal');
  const modalClose = document.getElementById('modal-close-btn');
  const openModalBtns = document.querySelectorAll('.trigger-booking-modal');
  const portalModal = document.getElementById('portal-modal');

  openModalBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      // Accept data-tier (canonical) or legacy data-plan names
      const tierKey = btn.getAttribute('data-tier') || legacyPlanToTier[btn.getAttribute('data-plan')] || 'growth';
      openCheckoutModal(tierKey);
    });
  });

  function openCheckoutModal(tierKey) {
    const t = tierByKey(tierKey) || tierByKey('growth');
    const planTitle = document.getElementById('modal-plan-title');
    const planPriceInr = document.getElementById('modal-plan-price-inr');
    const planPriceUsd = document.getElementById('modal-plan-price-usd');
    const qrImg = document.getElementById('upi-qr-image');
    const step1 = document.getElementById('checkout-step-1');
    const step2 = document.getElementById('checkout-step-2');

    if (planTitle) {
      planTitle.textContent = t.name;
      planTitle.setAttribute('data-tier', t.key);
    }
    if (planPriceInr) planPriceInr.innerHTML = `$${t.price_monthly}<span style="font-size: 12px; color: var(--text-muted);"> / mo</span>`;
    if (planPriceUsd) planPriceUsd.textContent = 'billed monthly · cancel anytime';

    // Stripe-first checkout when a real Payment Link exists for this tier.
    if (t.stripe_url) {
      if (step1) step1.style.display = 'none';
      if (step2) step2.style.display = 'none';
      window.open(t.stripe_url, '_blank');
    } else {
      // Manual UPI + WhatsApp flow (default while stripe_url is empty)
      if (step1) step1.style.display = '';
      if (step2) step2.style.display = '';
      if (qrImg) {
        const upiUri = `upi://pay?pa=${encodeURIComponent(window.AUTOGRAM_PRICING.upi.id)}&pn=${encodeURIComponent(window.AUTOGRAM_PRICING.upi.payee_name || 'Autogram AI')}&am=${Math.round(t.price_monthly * 8300)}&cu=INR`;
        qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(upiUri)}`;
      }
    }

    if (portalModal) portalModal.classList.remove('active');
    if (modal) modal.classList.add('active');
  }
  window.openCheckoutModal = openCheckoutModal;

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
      const titleEl = document.getElementById('modal-plan-title');
      const tierKey = (titleEl && titleEl.getAttribute('data-tier')) || 'growth';
      const t = tierByKey(tierKey) || tierByKey('growth');

      const msg = `Hi Piyush, I have completed the UPI payment for Autogram AI.\n\n` +
        `📦 Plan: ${t.name}\n` +
        `💰 Price: $${t.price_monthly}/mo\n` +
        `🏢 Name / Company: ${clientName}\n` +
        `📸 Instagram Handle: ${igHandle}\n\n` +
        `Attached is my payment screenshot for verification. Please send my Client License Key to activate my Autogram Studio!`;

      const waUrl = `https://wa.me/${window.AUTOGRAM_PRICING.upi.whatsapp_number}?text=${encodeURIComponent(msg)}`;
      window.open(waUrl, '_blank');

      alert("Opening WhatsApp to send your payment screenshot. Your license key will arrive within 15 minutes of verification!");
      if (modal) modal.classList.remove('active');
    });
  }
});

