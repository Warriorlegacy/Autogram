/**
 * Autogram Live Interactive Carousel Simulator & Telemetry Inspector
 */

(function () {
  const SLIDES_DATA = [
    {
      num: 1,
      image: "public/assets/slides/slide_01.jpg",
      role: "Hook Billboard",
      headline: "Compound AI Systems: Why Multi-Agent Orchestration",
      body: "Why Compound AI Systems: Why Multi-Agent Orchestration Outperforms Monolithic LLMs fundamentally impacts workflow efficiency",
      proof: "Benchmarked across 1.2M automated agent operations.",
      status: "VERIFIED"
    },
    {
      num: 2,
      image: "public/assets/slides/slide_02.jpg",
      role: "Context & Root Cause",
      headline: "The Single-Prompt Bottleneck",
      body: "When one prompt handles research, drafting, and validation, context drift causes subtle hallucinations that compound downstream.",
      proof: "Context dilution accelerates past 8,000 tokens.",
      status: "VERIFIED"
    },
    {
      num: 3,
      image: "public/assets/slides/slide_03.jpg",
      role: "Direct Contrast",
      headline: "Monolithic vs Compound Architecture",
      body: "Comparing the fragility of all-in-one execution against specialized role boundaries.",
      proof: "Decoupled stages allow isolated testing and deterministic retries.",
      status: "VERIFIED"
    },
    {
      num: 4,
      image: "public/assets/slides/slide_04.jpg",
      role: "System Architecture",
      headline: "The 3-Stage Autonomous Pipeline",
      body: "How production teams achieve zero-touch operational reliability without hallucination drift.",
      proof: "Ingest -> Reason -> Deterministic Render.",
      status: "VERIFIED"
    },
    {
      num: 5,
      image: "public/assets/slides/slide_05.jpg",
      role: "Actionable Checklist",
      headline: "4 Production Guardrails",
      body: "Non-negotiable requirements before turning on autonomous publishing.",
      proof: "Deterministic schema validation, HTML layout engine, Pre-publish fact checking.",
      status: "VERIFIED"
    },
    {
      num: 6,
      image: "public/assets/slides/slide_06.jpg",
      role: "Core Framework",
      headline: "The Fail-Closed Rule",
      body: "If evidence confidence drops below 90% or the quality gate rejects copy twice, halt immediately. Never publish mediocre output unattended.",
      proof: "One bad automated post destroys months of credibility.",
      status: "VERIFIED"
    },
    {
      num: 7,
      image: "public/assets/slides/slide_07.jpg",
      role: "Execution Blueprint",
      headline: "Your Zero-Debt Automation Checklist",
      body: "Deconstruct tasks into verifiable steps, prioritize structured JSON, use deterministic rendering, and explore local SLMs.",
      proof: "Core principle of production-grade AI systems.",
      status: "VERIFIED"
    },
    {
      num: 8,
      image: "public/assets/slides/slide_08.jpg",
      role: "The Distilled Rule",
      headline: "The Compounding Return of Zero-Debt",
      body: "Reduced error rates (60% from modularity) and zero cloud costs (local SLMs) directly impact ROI.",
      proof: "Save-rate optimized for Instagram ranking algorithm.",
      status: "VERIFIED"
    },
    {
      num: 9,
      image: "public/assets/slides/slide_09.jpg",
      role: "Conversion CTA",
      headline: "Comment CONTENT to Get The Blueprint",
      body: "100% free resource delivered instantly to your DMs. My name is Piyush Raj Singh. Stop posting. Start shipping.",
      proof: "Direct Meta Graph API and comment-to-DM conversion trigger.",
      status: "VERIFIED"
    }
  ];

  let currentIndex = 0;

  const slideImg = document.getElementById('simulator-slide-img');
  const slideRoleBadge = document.getElementById('slide-role-badge');
  const slideNumDisplay = document.getElementById('slide-num-display');
  const slideHeadline = document.getElementById('slide-headline');
  const slideBody = document.getElementById('slide-body');
  const slideProof = document.getElementById('slide-proof');
  const prevBtn = document.getElementById('deck-prev-btn');
  const nextBtn = document.getElementById('deck-next-btn');
  const dotsContainer = document.getElementById('slide-dots-container');
  const thumbnailsReel = document.getElementById('slide-thumbnails-reel');

  function initDots() {
    if (!dotsContainer) return;
    dotsContainer.innerHTML = '';
    SLIDES_DATA.forEach((_, idx) => {
      const dot = document.createElement('div');
      dot.className = `slide-dot ${idx === currentIndex ? 'active' : ''}`;
      dot.addEventListener('click', () => updateSlide(idx));
      dotsContainer.appendChild(dot);
    });
  }

  function initThumbnails() {
    if (!thumbnailsReel) return;
    thumbnailsReel.innerHTML = '';
    SLIDES_DATA.forEach((s, idx) => {
      const thumb = document.createElement('div');
      thumb.className = `slide-thumb-card ${idx === currentIndex ? 'active' : ''}`;
      thumb.style.cssText = `
        flex-shrink: 0;
        width: 60px;
        height: 75px;
        border-radius: 8px;
        border: 2px solid ${idx === currentIndex ? 'var(--neon-cyan)' : 'rgba(255,255,255,0.1)'};
        overflow: hidden;
        cursor: pointer;
        position: relative;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: ${idx === currentIndex ? '0 0 12px rgba(0, 240, 255, 0.4)' : 'none'};
      `;
      thumb.innerHTML = `
        <img src="${s.image}" alt="Slide ${s.num}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
        <span style="position: absolute; bottom: 3px; right: 3px; background: rgba(0,0,0,0.8); font-family: var(--font-mono); font-size: 9px; font-weight: 700; color: #FFF; padding: 1px 4px; border-radius: 4px; line-height: 1.2;">0${s.num}</span>
      `;
      thumb.addEventListener('click', () => updateSlide(idx));
      thumbnailsReel.appendChild(thumb);
    });
  }

  function updateSlide(index) {
    if (index < 0) index = SLIDES_DATA.length - 1;
    if (index >= SLIDES_DATA.length) index = 0;
    currentIndex = index;

    const data = SLIDES_DATA[currentIndex];
    if (slideImg) {
      slideImg.style.opacity = '0';
      slideImg.style.transform = 'scale(0.96)';
      setTimeout(() => {
        slideImg.src = data.image;
        slideImg.style.opacity = '1';
        slideImg.style.transform = 'scale(1)';
      }, 150);
    }

    if (slideRoleBadge) slideRoleBadge.textContent = data.role;
    if (slideNumDisplay) slideNumDisplay.textContent = `SLIDE 0${data.num} / 0${SLIDES_DATA.length}`;
    if (slideHeadline) slideHeadline.textContent = data.headline;
    if (slideBody) slideBody.textContent = data.body;
    if (slideProof) slideProof.textContent = data.proof;

    // Update dots
    const dots = dotsContainer ? dotsContainer.querySelectorAll('.slide-dot') : [];
    dots.forEach((d, i) => {
      d.className = `slide-dot ${i === currentIndex ? 'active' : ''}`;
    });

    // Update thumbnails reel
    if (thumbnailsReel) {
      const thumbs = thumbnailsReel.querySelectorAll('.slide-thumb-card');
      thumbs.forEach((t, i) => {
        const isActive = i === currentIndex;
        t.style.borderColor = isActive ? 'var(--neon-cyan)' : 'rgba(255,255,255,0.1)';
        t.style.boxShadow = isActive ? '0 0 14px rgba(0, 240, 255, 0.45)' : 'none';
        t.style.transform = isActive ? 'scale(1.06)' : 'scale(1)';
      });
      const activeThumb = thumbs[currentIndex];
      if (activeThumb) {
        activeThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }
  }

  if (prevBtn) prevBtn.addEventListener('click', () => updateSlide(currentIndex - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => updateSlide(currentIndex + 1));

  // Pillar tab switches
  const pillarTabs = document.querySelectorAll('.pillar-tab');
  pillarTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      pillarTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      // Jump to slide 1 with simulated transition
      updateSlide(0);
    });
  });

  initDots();
  initThumbnails();
  updateSlide(0);
})();
