/* ============================================================================
 * SIGNHIFY.STUDIO — KINETIC TYPE JS  (renderer/reels_shared/kinetic_type.js)
 * Vanilla, dependency-free. Exposes window.KineticText. Deterministic and
 * seekable-compatible: every animation is a GSAP tween placed on a timeline
 * the caller passes in (no requestAnimationFrame loops), so HyperFrames can
 * seek to any frame.
 *
 * Usage (see _kinetic_head.html.jinja2 + kinetic_demo.html.jinja2):
 *   <h1 class="kinetic-text kt-3d kt-size-xl" data-kinetic="letters"
 *       data-start="0" data-duration="4">AI IS CHANGING</h1>
 *   <script>
 *     window.__timelines = window.__timelines || {};
 *     const tl = gsap.timeline({paused: true});
 *     window.KineticText.applyKineticText(document.getElementById('stage'), tl);
 *     window.__timelines.my_comp = tl;
 *   </script>
 * ========================================================================== */
(function () {
  'use strict';

  // --- letter splitting (preserves nested .g gradient spans) -----------
  function splitLetters(el) {
    if (!el || el.dataset.__ktSplit) return;
    el.dataset.__ktSplit = '1';
    var nodes = Array.prototype.slice.call(el.childNodes);
    el.innerHTML = '';
    nodes.forEach(function (node) {
      if (node.nodeType === 1 && node.classList && node.classList.contains('g')) {
        // keep the gradient wrapper intact; split its text into .ch.g
        var g = node;
        var gNodes = Array.prototype.slice.call(g.childNodes);
        g.innerHTML = '';
        gNodes.forEach(function (gn) {
          String(gn.textContent).split('').forEach(function (c) {
            var s = document.createElement('span');
            s.className = 'ch g';
            s.innerHTML = c === ' ' ? '\u00A0' : c;
            g.appendChild(s);
          });
        });
        el.appendChild(g);
        return;
      }
      String(node.textContent).split('').forEach(function (c) {
        var s = document.createElement('span');
        s.className = 'ch';
        s.innerHTML = c === ' ' ? '\u00A0' : c;
        el.appendChild(s);
      });
    });
  }

  // --- word splitting ----------------------------------------------------
  function splitWords(el) {
    if (!el || el.dataset.__ktSplit) return;
    el.dataset.__ktSplit = '1';
    var text = (el.textContent || '').replace(/\s+/g, ' ').trim();
    el.innerHTML = '';
    text.split(' ').forEach(function (w) {
      var s = document.createElement('span');
      s.className = 'word';
      s.textContent = w + ' ';
      el.appendChild(s);
    });
  }

  // --- layered duplicates ------------------------------------------------
  function buildLayers(el, layerCount) {
    if (!el || el.dataset.__ktSplit) return;
    el.dataset.__ktSplit = '1';
    var text = el.textContent;
    var copy = el.cloneNode(false);
    copy.textContent = text;
    copy.className = el.className + ' layer layer-back';
    var mid = el.cloneNode(false);
    mid.textContent = text;
    mid.className = el.className + ' layer layer-mid';
    el.className = el.className + ' layer-front';
    el.textContent = text;
    el.appendChild(mid);
    el.appendChild(copy);
  }

  // --- animate: place tweens on the timeline at absolute time `at` -----
  // opts: {kind: 'letters'|'words'|'layers', start, duration, popWords:[...]}
  function animate(el, timeline, at, opts) {
    if (!timeline || !el) return;
    var kind = opts.kind || 'letters';
    var dur = opts.duration || 2;
    var start = at == null ? parseFloat(el.dataset.start || 0) : at;
    if (start == null || isNaN(start)) start = 0;

    if (kind === 'letters') {
      splitLetters(el);
      var chars = el.querySelectorAll('.ch');
      if (chars.length) {
        timeline.from(chars, {
          y: 46, rotationX: -75, opacity: 0,
          stagger: Math.min(0.05, (dur * 0.3) / chars.length),
          duration: dur * 0.22,
          ease: 'back.out(1.6)'
        }, start + dur * 0.05);
      }
    } else if (kind === 'words') {
      splitWords(el);
      var words = el.querySelectorAll('.word');
      if (words.length) {
        timeline.from(words, {
          y: 24, opacity: 0, scale: 0.94,
          stagger: Math.min(0.06, (dur * 0.35) / words.length),
          duration: dur * 0.2,
          ease: 'power3.out'
        }, start + dur * 0.05);
      }
      // pop the emphasized words (scale + glow via .pop class)
      var pops = opts.popWords || [];
      words.forEach(function (w, i) {
        if (pops.indexOf(i) !== -1) {
          timeline.to(w, {
            scale: 1.18, duration: dur * 0.14,
            ease: 'back.out(2.2)'
          }, start + dur * 0.25);
          w.classList.add('pop');
        }
      });
    } else if (kind === 'layers') {
      buildLayers(el, 3);
      timeline.from(el.querySelectorAll('.layer-back'), { opacity: 0, duration: dur * 0.25, ease: 'power2.out' }, start);
      timeline.from(el.querySelectorAll('.layer-mid'), { opacity: 0, duration: dur * 0.25, ease: 'power2.out' }, start + dur * 0.08);
      timeline.from(el, { y: 20, opacity: 0, duration: dur * 0.2, ease: 'power3.out' }, start + dur * 0.05);
    }
  }

  // --- applyKineticText: scan [data-kinetic] and animate each -----------
  function applyKineticText(root, timeline) {
    root = root || document;
    if (!timeline) return;
    var els = root.querySelectorAll('[data-kinetic]');
    Array.prototype.forEach.call(els, function (el) {
      var kind = el.getAttribute('data-kinetic');
      var start = parseFloat(el.getAttribute('data-start') || 0);
      var dur = parseFloat(el.getAttribute('data-duration') || 2);
      var popWords = [];
      var popAttr = el.getAttribute('data-pop-words');
      if (popAttr) {
        popAttr.split(',').forEach(function (i) {
          var n = parseInt(i.trim(), 10);
          if (!isNaN(n)) popWords.push(n);
        });
      }
      animate(el, timeline, isNaN(start) ? 0 : start, { kind: kind, duration: dur, popWords: popWords });
    });
  }

  window.KineticText = {
    splitLetters: splitLetters,
    splitWords: splitWords,
    buildLayers: buildLayers,
    animate: animate,
    applyKineticText: applyKineticText
  };
})();
