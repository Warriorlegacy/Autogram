/* ════════════════════════════════════════════════════════════════════════════
   AUTogram Premium — Scroll Reveals, Ambient Particles, 3D Parallax
   ════════════════════════════════════════════════════════════════════════════ */
(function() {
  'use strict';

  /* ─── Ambient Particles (CSS-animated, zero-dependency) ─── */
  function initParticles() {
    var canvas = document.getElementById('ambient-particles');
    if (!canvas) {
      canvas = document.createElement('div');
      canvas.id = 'ambient-particles';
      document.body.prepend(canvas);
    }
    var count = window.innerWidth < 768 ? 12 : 24;
    var colors = [
      'rgba(0, 240, 255, 0.4)',
      'rgba(138, 43, 226, 0.35)',
      'rgba(0, 255, 163, 0.3)',
      'rgba(99, 102, 241, 0.3)',
      'rgba(255, 184, 0, 0.25)'
    ];
    for (var i = 0; i < count; i++) {
      var p = document.createElement('div');
      p.className = 'particle';
      var size = Math.random() * 3 + 1.5;
      var dur = Math.random() * 20 + 15;
      var delay = Math.random() * -30;
      var left = Math.random() * 100;
      var color = colors[Math.floor(Math.random() * colors.length)];
      p.style.cssText =
        'width:' + size + 'px;height:' + size + 'px;' +
        'left:' + left + '%;' +
        'background:' + color + ';' +
        'box-shadow:0 0 ' + (size * 3) + 'px ' + color + ';' +
        'animation-duration:' + dur + 's;' +
        'animation-delay:' + delay + 's;';
      canvas.appendChild(p);
    }
  }

  /* ─── Scroll Reveal (IntersectionObserver) ─── */
  function initScrollReveal() {
    var reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
    if (!reveals.length) return;

    if (!('IntersectionObserver' in window)) {
      reveals.forEach(function(el) { el.classList.add('visible'); });
      return;
    }

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(function(el) { observer.observe(el); });
  }

  /* ─── 3D Tilt on Cards (mouse parallax) ─── */
  function initTiltCards() {
    var cards = document.querySelectorAll('.doppelrand-card, .arch-card, .pricing-card, .doppel-shell, .platform-tile, .template-card-tile');
    if (!cards.length) return;

    cards.forEach(function(card) {
      card.addEventListener('mousemove', function(e) {
        var rect = card.getBoundingClientRect();
        var x = (e.clientX - rect.left) / rect.width - 0.5;
        var y = (e.clientY - rect.top) / rect.height - 0.5;
        card.style.transform =
          'perspective(800px) rotateY(' + (x * 6) + 'deg) rotateX(' + (-y * 6) + 'deg) translateY(-4px) scale(1.01)';
      });
      card.addEventListener('mouseleave', function() {
        card.style.transform = '';
      });
    });
  }

  /* ─── Smooth Counter Animation (for ROI numbers) ─── */
  function animateCounters() {
    var counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var target = parseInt(el.getAttribute('data-count'), 10);
        var prefix = el.getAttribute('data-prefix') || '';
        var suffix = el.getAttribute('data-suffix') || '';
        var duration = 1200;
        var start = 0;
        var startTime = null;

        function step(ts) {
          if (!startTime) startTime = ts;
          var progress = Math.min((ts - startTime) / duration, 1);
          var eased = 1 - Math.pow(1 - progress, 3);
          el.textContent = prefix + Math.floor(eased * target).toLocaleString() + suffix;
          if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
        observer.unobserve(el);
      });
    }, { threshold: 0.5 });

    counters.forEach(function(el) { observer.observe(el); });
  }

  /* ─── Header Scroll Effect ─── */
  function initHeaderScroll() {
    var header = document.querySelector('.hud-header');
    if (!header) return;
    var lastScroll = 0;
    window.addEventListener('scroll', function() {
      var st = window.pageYOffset;
      if (st > 80) {
        header.style.boxShadow = '0 8px 48px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.06)';
      } else {
        header.style.boxShadow = '';
      }
      lastScroll = st;
    }, { passive: true });
  }

  /* ─── Smooth Anchor Links ─── */
  function initSmoothLinks() {
    document.querySelectorAll('a[href^="#"]').forEach(function(link) {
      link.addEventListener('click', function(e) {
        var id = link.getAttribute('href');
        if (id === '#') return;
        var target = document.querySelector(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  /* ─── Init All ─── */
  function init() {
    initParticles();
    initScrollReveal();
    initTiltCards();
    animateCounters();
    initHeaderScroll();
    initSmoothLinks();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
