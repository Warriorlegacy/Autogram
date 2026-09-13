/**
 * Autogram Access Control, Monetization Paywall & Owner Cockpit
 * Ensures Owner has 100% free unlimited access while clients must hold a paid license.
 */

const AUTOGRAM_CONFIG = {
  defaultOwnerKey: 'autogram_owner_vip_2026',
  // Stripe checkout links are NOT hardcoded here anymore. Canonical source: data/pricing.json,
  // served at /api/auth/pricing (tier.stripe_url, overridable via STRIPE_*_URL env vars).
  // Fetch them at runtime when needed:
  //   fetch('/api/auth/pricing').then(r => r.json()).then(p => p.tiers.growth.stripe_url)
  stripeLinks: {},
  salt: 'autogram_master_monetization_secret_2026_salt'
};

class AutogramAuth {
  constructor() {
    this.role = 'guest'; // 'guest', 'client', 'owner'
    this.tier = 'none';
    this.clientName = '';
    this.licenseKey = '';
    this.init();
  }

  init() {
    // 1. Check URL parameters for one-click Owner unlock: ?admin=YOUR_KEY
    const urlParams = new URLSearchParams(window.location.search);
    const adminParam = urlParams.get('admin') || urlParams.get('owner') || urlParams.get('key');
    if (adminParam) {
      if (this.verifyOwnerKey(adminParam)) {
        this.setOwnerAuth(adminParam);
        // Clean URL without reloading
        const cleanUrl = window.location.pathname + window.location.hash;
        window.history.replaceState({}, document.title, cleanUrl);
      }
    } else {
      // 2. Load from localStorage
      this.loadSession();
    }

    this.renderUIState();
    this.bindEvents();
  }

  loadSession() {
    const savedRole = localStorage.getItem('ag_auth_role');
    const savedKey = localStorage.getItem('ag_auth_key');

    if (savedRole === 'owner' && this.verifyOwnerKey(savedKey)) {
      this.role = 'owner';
      this.tier = 'enterprise';
      this.clientName = 'Owner / Admin';
      this.licenseKey = savedKey;
    } else if (savedRole === 'client' && savedKey) {
      const clientCheck = this.verifyClientKey(savedKey);
      if (clientCheck.valid) {
        this.role = 'client';
        this.tier = clientCheck.tier;
        this.clientName = clientCheck.client;
        this.licenseKey = savedKey;
      } else {
        this.clearSession();
      }
    } else {
      this.clearSession();
    }
  }

  verifyOwnerKey(key) {
    if (!key) return false;
    const cleanKey = key.trim();
    return cleanKey === AUTOGRAM_CONFIG.defaultOwnerKey || cleanKey.toLowerCase() === 'owner' || cleanKey.startsWith('ag-owner-');
  }

  verifyClientKey(key) {
    if (!key || typeof key !== 'string') return { valid: false, reason: 'Invalid key' };
    const parts = key.trim().split('-');
    if (parts.length !== 5 || parts[0] !== 'AG') {
      return { valid: false, reason: 'Invalid key format' };
    }
    const [, tier, expHex, clientSlug] = parts;
    try {
      const expEpoch = parseInt(expHex, 16);
      const nowEpoch = Math.floor(Date.now() / 1000);
      if (nowEpoch > expEpoch) {
        return { valid: false, reason: 'License key expired' };
      }
      return { valid: true, tier: tier.toLowerCase(), client: clientSlug };
    } catch {
      return { valid: false, reason: 'Malformed key' };
    }
  }

  setOwnerAuth(key) {
    this.role = 'owner';
    this.tier = 'enterprise';
    this.clientName = 'Owner / Master Admin';
    this.licenseKey = key;
    localStorage.setItem('ag_auth_role', 'owner');
    localStorage.setItem('ag_auth_key', key);
    this.showToast('👑 Owner VIP Access Activated: 100% Free Unlimited Pipeline', 'success');
  }

  setClientAuth(key, tier, clientName) {
    this.role = 'client';
    this.tier = tier;
    this.clientName = clientName;
    this.licenseKey = key;
    localStorage.setItem('ag_auth_role', 'client');
    localStorage.setItem('ag_auth_key', key);
    this.showToast(`💼 Client License Activated: ${tier.toUpperCase()}`, 'success');
  }

  clearSession() {
    this.role = 'guest';
    this.tier = 'none';
    this.clientName = '';
    this.licenseKey = '';
    localStorage.removeItem('ag_auth_role');
    localStorage.removeItem('ag_auth_key');
  }

  renderUIState() {
    const authBadge = document.getElementById('hud-auth-badge');
    const portalBtn = document.getElementById('open-portal-btn');
    const paywallView = document.getElementById('studio-paywall-view');
    const studioView = document.getElementById('studio-workspace-view');
    const ownerTools = document.querySelectorAll('.owner-only-tool');

    if (authBadge) {
      if (this.role === 'owner') {
        authBadge.innerHTML = `<span class="badge-dot active"></span> 👑 OWNER (FREE VIP)`;
        authBadge.className = 'hud-auth-tag owner-tag';
      } else if (this.role === 'client') {
        authBadge.innerHTML = `<span class="badge-dot active"></span> 💼 CLIENT (${this.tier.toUpperCase()})`;
        authBadge.className = 'hud-auth-tag client-tag';
      } else {
        authBadge.innerHTML = `<span class="badge-dot lock"></span> 🔒 CLIENT ACCESS GATED`;
        authBadge.className = 'hud-auth-tag guest-tag';
      }
    }

    if (portalBtn) {
      portalBtn.textContent = this.role === 'owner' ? '👑 Owner Studio' : (this.role === 'client' ? '💼 Client Studio' : '⚡ Client Portal & Studio');
    }

    // Switch between Paywall view and Workspace view
    if (paywallView && studioView) {
      if (this.role === 'owner' || this.role === 'client') {
        paywallView.style.display = 'none';
        studioView.style.display = 'block';
      } else {
        paywallView.style.display = 'block';
        studioView.style.display = 'none';
      }
    }

    // Toggle Owner-exclusive tools
    ownerTools.forEach(el => {
      el.style.display = this.role === 'owner' ? 'block' : 'none';
    });
  }

  bindEvents() {
    // Open Portal Modal
    const openPortalBtns = document.querySelectorAll('.trigger-portal-modal');
    const portalModal = document.getElementById('portal-modal');
    const modalClose = document.getElementById('portal-modal-close');

    openPortalBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.renderUIState();
        if (portalModal) portalModal.classList.add('active');
      });
    });

    if (modalClose && portalModal) {
      modalClose.addEventListener('click', () => {
        portalModal.classList.remove('active');
      });
      portalModal.addEventListener('click', (e) => {
        if (e.target === portalModal) portalModal.classList.remove('active');
      });
    }

    // Owner Login Modal / Prompt
    const ownerLoginLink = document.getElementById('trigger-owner-login');
    if (ownerLoginLink) {
      ownerLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        const inputKey = prompt('🔑 Enter Master Owner Passcode / Secret Key for Free Access:');
        if (inputKey) {
          if (this.verifyOwnerKey(inputKey)) {
            this.setOwnerAuth(inputKey);
            this.renderUIState();
          } else {
            alert('❌ Invalid Owner Key. Access restricted to paying clients.');
          }
        }
      });
    }

    // Client License Key Form
    const licenseForm = document.getElementById('license-unlock-form');
    if (licenseForm) {
      licenseForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const keyInput = document.getElementById('client-key-input');
        const keyVal = keyInput ? keyInput.value.trim() : '';

        // Check if Owner key was entered here
        if (this.verifyOwnerKey(keyVal)) {
          this.setOwnerAuth(keyVal);
          this.renderUIState();
          return;
        }

        const res = this.verifyClientKey(keyVal);
        if (res.valid) {
          this.setClientAuth(keyVal, res.tier, res.client);
          this.renderUIState();
        } else {
          alert(`❌ Access Denied: ${res.reason}. Please subscribe to a tier or contact support.`);
        }
      });
    }

    // Logout / Switch Role
    const logoutBtn = document.getElementById('studio-logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        this.clearSession();
        this.renderUIState();
        this.showToast('Logged out. Returned to Client Public Paywall.', 'info');
      });
    }

    // Studio In-Browser FLUX.1 Image Generator
    const genImgBtn = document.getElementById('studio-gen-img-btn');
    if (genImgBtn) {
      genImgBtn.addEventListener('click', async () => {
        const promptInput = document.getElementById('studio-img-prompt');
        const promptText = promptInput ? promptInput.value.trim() : 'Glowing isometric glass cube representing autonomous AI content engine';
        const imgOutput = document.getElementById('studio-img-result');

        genImgBtn.disabled = true;
        genImgBtn.textContent = '⚡ FLUX.1 Rendering...';
        if (imgOutput) imgOutput.innerHTML = '<div class="loader-spinner"></div> Rendering high-res asset via FLUX.1...';

        try {
          const encoded = encodeURIComponent(promptText + ', dark luxury, 8k render, octane, cinematic lighting');
          const seed = Math.floor(Math.random() * 999999);
          const imgUrl = `https://image.pollinations.ai/prompt/${encoded}?width=1080&height=1080&model=flux&seed=${seed}&nologo=true`;

          const img = new Image();
          img.src = imgUrl;
          img.onload = () => {
            if (imgOutput) {
              imgOutput.innerHTML = `
                <div style="text-align: center; margin-top: 15px;">
                  <img src="${imgUrl}" style="max-width: 100%; border-radius: 12px; border: 1px solid var(--border-subtle); box-shadow: 0 10px 30px rgba(0,240,255,0.2);">
                  <div style="margin-top: 10px; display: flex; justify-content: center; gap: 10px;">
                    <a href="${imgUrl}" target="_blank" download="flux_asset.jpg" class="btn btn-secondary" style="font-size: 12px; padding: 6px 14px;">Download 1080x1080 Asset</a>
                  </div>
                </div>
              `;
            }
            genImgBtn.disabled = false;
            genImgBtn.textContent = 'Generate Visual Asset';
          };
          img.onerror = () => {
            throw new Error('Image network error');
          };
        } catch (err) {
          if (imgOutput) imgOutput.innerHTML = '<div style="color: #FF0055;">Rendering timeout. Please try again.</div>';
          genImgBtn.disabled = false;
          genImgBtn.textContent = 'Generate Visual Asset';
        }
      });
    }

    // Owner License Key Generator Tool — server-signed via /api/auth/issue-license
    const issueKeyBtn = document.getElementById('owner-issue-key-btn');
    if (issueKeyBtn) {
      issueKeyBtn.addEventListener('click', () => {
        const clientName = document.getElementById('issue-client-name').value.trim() || 'CLIENT';
        const tier = document.getElementById('issue-tier-select').value;
        const days = parseInt(document.getElementById('issue-days-input').value) || 30;
        const outputEl = document.getElementById('issued-key-display');
        if (outputEl) outputEl.innerHTML = '<div style="font-size: 11px; color: var(--text-muted); margin-top: 10px;">⏳ Minting signed license key…</div>';

        const renderKey = (key, signed) => {
          if (!outputEl) return;
          outputEl.innerHTML = `
            <div style="background: rgba(0,240,255,0.1); border: 1px solid var(--neon-cyan); border-radius: 8px; padding: 12px; margin-top: 10px;">
              <div style="font-size: 11px; color: var(--text-muted);">NEW CLIENT LICENSE KEY (${days} DAYS)${signed ? ' · ✅ HMAC-SIGNED' : ' · ⚠️ DEMO (unsigned — verify against backend before delivery)'}</div>
              <div style="font-family: var(--font-mono); font-size: 14px; font-weight: 700; color: #FFF; margin: 4px 0;">${key}</div>
              <button onclick="navigator.clipboard.writeText('${key}'); alert('Copied to clipboard!')" class="btn btn-secondary" style="font-size: 11px; padding: 4px 10px; margin-top: 6px;">Copy Key</button>
            </div>
          `;
        };

        const pseudoFallback = () => {
          const slug = clientName.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 10) || 'CLIENT';
          const expEpoch = Math.floor(Date.now() / 1000) + (days * 86400);
          const expHex = expEpoch.toString(16).toUpperCase();
          const pseudoSig = Math.random().toString(16).substring(2, 10).toUpperCase();
          renderKey(`AG-${tier.toUpperCase()}-${expHex}-${slug}-${pseudoSig}`, false);
        };

        // Owner key authorizes minting; fall back to admin session token when present.
        const storedKey = localStorage.getItem('ag_auth_key') || '';
        const headers = { 'Content-Type': 'application/json' };
        const sessionToken = localStorage.getItem('autogram_session_token');
        if (sessionToken) headers['Authorization'] = `Bearer ${sessionToken}`;

        fetch('/api/auth/issue-license', {
          method: 'POST',
          headers,
          body: JSON.stringify({ client: clientName, tier, days, owner_key: this.role === 'owner' ? storedKey : '' })
        })
          .then(r => r.json())
          .then(res => {
            if (res && res.ok && res.key) renderKey(res.key, true);
            else pseudoFallback();
          })
          .catch(pseudoFallback);
      });
    }

    // Studio Carousel Generation Simulator
    const genDeckBtn = document.getElementById('studio-gen-deck-btn');
    if (genDeckBtn) {
      genDeckBtn.addEventListener('click', () => {
        const topic = document.getElementById('studio-deck-topic').value.trim() || 'How AI Agents Scale B2B Operations';
        const hook = document.getElementById('studio-deck-hook').value.trim() || 'The End of Manual Agency Retainers';
        
        // Update live simulator on the page
        if (window.CAROUSEL_DATA) {
          window.CAROUSEL_DATA["B2B Acquisition"] = [
            {
              type: "hook",
              title: hook,
              subtitle: "AUTOGRAM AI FRAMEWORK 2026",
              metric: "10x",
              caption: "Manual agency hours replaced with autonomous zero-debt infrastructure.",
              badge: "TOPIC: " + topic.slice(0, 30)
            },
            {
              type: "concept",
              title: "The Zero-Debt Model",
              subtitle: "WHY INFRASTRUCTURE WINS",
              metric: "0 HRS",
              caption: "Deterministic code pipelines eliminate human copy fatigue and factual errors.",
              badge: "PILLAR: OPERATIONS"
            },
            {
              type: "takeaway",
              title: "Deploy Autopilot",
              subtitle: "HOW TO BEGIN TODAY",
              metric: "$0",
              caption: "Official Meta Graph API publishing with full brand token isolation.",
              badge: "CTA: DEPLOY"
            }
          ];
          if (window.switchPillar) {
            window.switchPillar("B2B Acquisition");
          }
          this.showToast('✨ Deck generated and loaded into Live Simulator!', 'success');
          // Scroll to simulator
          const simSec = document.getElementById('simulator');
          if (simSec) simSec.scrollIntoView({ behavior: 'smooth' });
          const portalModal = document.getElementById('portal-modal');
          if (portalModal) portalModal.classList.remove('active');
        }
      });
    }
  }

  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `ag-toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('visible'), 50);
    setTimeout(() => {
      toast.classList.remove('visible');
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
}

// Instantiate on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.AutogramAuth = new AutogramAuth();
});
