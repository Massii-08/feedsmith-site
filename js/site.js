/* Feedsmith — motion layer. Vanilla, no build step, no dependency, no network.

   Everything here is hook-driven: a feature only runs where the markup
   carries its attribute (#machine, [data-split], [data-magnetic], [data-plx]),
   so a page that loads this file without the hooks simply gets nothing. The
   page is fully readable with JavaScript off, and every feature has a
   finished static state under prefers-reduced-motion.

   1. the hero machine (canvas, now pointer-reactive, with a delivered counter)
   2. the split headline
   3. scroll reveals
   4. pointer light on buttons
   5. magnetic actions
   6. scroll effects: parallax + belt velocity
   7. active section in the nav

   v3 — matter in the middle of the page. Same rule: a hook or nothing.
   8.  hero embers (canvas ambience behind the hero)      .hero-embers
   9.  the pipeline rail under "how it works"             [data-pipeline]
   10. prices that count up                               [data-count]
   11. the config that types itself                       [data-type]
   12. the CSV that arrives row by row                    [data-sweep]
   Page transitions are chantier 6 and live entirely in CSS.               */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var mqReduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  var reduced = !!(mqReduce && mqReduce.matches);
  var fine = !!(window.matchMedia && window.matchMedia('(pointer: fine)').matches);
  var hasIO = 'IntersectionObserver' in window;
  var stopMotion = [];          // callbacks to cut if the preference flips mid-visit

  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) {
    return Array.prototype.slice.call((c || doc).querySelectorAll(s));
  }

  /* ---------------------------------------------------------------
     1. THE MACHINE
     Raw public web on the left (broken markup, 403s, empty bodies)
     travels right, crosses the forge gate, and locks into clean rows
     on the right. The rows carry real field names from the sample feed.

     v2 adds the hand: junk gives way around the cursor, the gate flares
     when the cursor crosses it, a click throws sparks, and the foot
     counts what has actually been delivered.

     Budget: one rAF loop, no allocation inside it. Particles come from
     fixed pools, the gate gradients are pre-built per size, and each
     row caches the label width it was last trimmed to.
     --------------------------------------------------------------- */
  function machine(canvas) {
    var ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    var W = 0, H = 0, dpr = 1;
    var GATE = 0.44;              // gate position, share of width
    var rows = [], junk = [];
    var last = 0, acc = 0, running = false;

    var JUNK_N = 18;
    var SPARK_MAX = 160;
    var sparks = [], nSpark = 0;

    var delivered = 0, tickState = 0;
    var readout = doc.getElementById('rows-count');   // absent on pages without the hook

    /* the hand */
    var pt = { x: -9999, y: -9999, on: false };
    var PUSH_R = 60, PUSH_R2 = PUSH_R * PUSH_R, PUSH_F = 150, PUSH_MAX = 26;
    var gatePulse = 0;

    /* pre-built gate gradients: index 0 is at rest, the last is the flare */
    var GRAD_N = 6, GRAD_W = 26, GRAD_SPREAD = 0.22;
    var grads = [], gradHW = [];

    var JUNK = [
      '<div class="pr_">', '403 Forbidden', '&nbsp;&nbsp;&nbsp;', '</span></div>',
      'null', '<!-- empty -->', '429 Too Many', '{}', '<script>__NEXT', 'undefined',
      '<td class="v"/>', 'captcha?', '…', '<b></b>', 'ERR_EMPTY', '<tr><td>'
    ];
    var FIELDS = [
      ['A Light in the Attic', '51.77', 'In stock'],
      ['Tipping the Velvet', '53.74', 'In stock'],
      ['Soumission', '50.10', 'In stock'],
      ['Sharp Objects', '47.82', 'In stock'],
      ['Sapiens', '54.23', 'In stock'],
      ['The Requiem Red', '22.65', 'In stock'],
      ['Olio', '23.88', 'In stock'],
      ['Shakespeares Sonnets', '20.66', 'In stock']
    ];

    for (var si = 0; si < SPARK_MAX; si++) {
      sparks.push({ x: 0, y: 0, vx: 0, vy: 0, life: 0 });
    }

    function resize() {
      var r = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = Math.max(320, r.width); H = Math.max(180, r.height);
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      build();
      buildGrads();
      /* setting canvas.width wipes the bitmap, so whenever the loop is not
         the one repainting — first init, hidden tab, below the fold, reduced
         motion — the resting frame has to be re-composed here or the slab
         shows as a black rectangle. */
      if (!running) { compose(); draw(); }
    }

    /* the machine at rest: what it looks like before anyone has watched it */
    function compose() {
      var i;
      if (reduced) {
        var shown = 0;
        for (i = 0; i < rows.length; i++) {
          rows[i].on = i % 2 ? 0 : 1;
          if (rows[i].on) shown++;
        }
        readoutSet(shown);
        return;
      }
      var keep = delivered;               // a resize is not a delivery
      for (i = 0; i < 44; i++) step(0.05);
      delivered = keep;
      readoutSet(delivered);
      if (readout) readout.removeAttribute('data-t');
    }

    function buildGrads() {
      var gx = W * GATE, i, hw, g;
      grads.length = 0; gradHW.length = 0;
      for (i = 0; i < GRAD_N; i++) {
        hw = GRAD_W * (1 + GRAD_SPREAD * (i / (GRAD_N - 1)));
        g = ctx.createLinearGradient(gx - hw, 0, gx + hw, 0);
        g.addColorStop(0, 'rgba(255,74,23,0)');
        g.addColorStop(0.5, 'rgba(255,74,23,.5)');
        g.addColorStop(1, 'rgba(255,74,23,0)');
        grads.push(g); gradHW.push(hw);
      }
    }

    function build() {
      var top = 26, rh = Math.max(22, Math.min(30, (H - 52) / 8));
      var n = Math.max(4, Math.floor((H - 52) / rh)), i;
      rows.length = 0;
      for (i = 0; i < n && i < FIELDS.length; i++) {
        rows.push({ y: top + i * rh, h: rh, on: 0, data: FIELDS[i], label: '', lw: -1 });
      }
      /* junk is pooled: reset in place, never re-allocated */
      if (junk.length !== JUNK_N) {
        junk.length = 0;
        for (i = 0; i < JUNK_N; i++) junk.push(reset({}, true));
      } else {
        for (i = 0; i < JUNK_N; i++) reset(junk[i], true);
      }
    }

    function reset(p, seed) {
      p.x = seed ? Math.random() * W * GATE : -Math.random() * 90 - 20;
      p.y = 20 + Math.random() * (H - 44);
      p.v = 14 + Math.random() * 26;
      p.t = JUNK[(Math.random() * JUNK.length) | 0];
      p.bad = Math.random() < 0.28;
      p.a = 0.28 + Math.random() * 0.4;
      p.rot = (Math.random() - 0.5) * 0.14;
      p.ox = 0; p.oy = 0;         // displacement from the cursor, springs back to 0
      return p;
    }

    function emit(x, y, vx, vy) {
      if (nSpark >= SPARK_MAX) return;
      var s = sparks[nSpark++];
      s.x = x; s.y = y; s.vx = vx; s.vy = vy; s.life = 1;
    }

    function pad4(n) {
      var s = String(n);
      while (s.length < 4) s = '0' + s;
      return s;
    }

    function readoutSet(n) {
      if (!readout) return;
      readout.textContent = pad4(n);
    }

    function convert(p) {
      /* pick a free row by reservoir sampling: one pass, no array */
      var i, idx = -1, seen = 0;
      for (i = 0; i < rows.length; i++) {
        if (rows[i].on < 0.05) { seen++; if (Math.random() < 1 / seen) idx = i; }
      }
      if (idx < 0) idx = (Math.random() * rows.length) | 0;
      rows[idx].on = 0.001;
      for (i = 0; i < 7; i++) {
        emit(W * GATE, p.y + p.oy, 30 + Math.random() * 150, (Math.random() - 0.5) * 190);
      }
      delivered++;
      readoutSet(delivered);
      if (readout) {                       // two identical keyframes: the swap
        tickState = tickState ? 0 : 1;     // restarts the tick without a reflow
        readout.setAttribute('data-t', String(tickState));
      }
    }

    function step(dt) {
      var i, p, s, dx, dy, d2, d, g;
      var gx = W * GATE;
      var decay = 1 - Math.pow(0.0006, dt);   // one pow per frame, not per particle

      /* the gate flares while the cursor is crossing it */
      var want = (pt.on && Math.abs(pt.x - gx) < 40) ? 1 : 0;
      g = dt * 7; if (g > 1) g = 1;
      gatePulse += (want - gatePulse) * g;

      for (i = 0; i < junk.length; i++) {
        p = junk[i];
        p.x += p.v * dt;
        if (pt.on) {
          dx = (p.x + p.ox) - pt.x; dy = (p.y + p.oy) - pt.y;
          d2 = dx * dx + dy * dy;
          if (d2 < PUSH_R2 && d2 > 0.01) {
            d = Math.sqrt(d2);
            g = (1 - d / PUSH_R) * PUSH_F * dt;
            p.ox += dx / d * g; p.oy += dy / d * g;
          }
        }
        p.ox -= p.ox * decay; p.oy -= p.oy * decay;
        if (p.ox > PUSH_MAX) p.ox = PUSH_MAX; else if (p.ox < -PUSH_MAX) p.ox = -PUSH_MAX;
        if (p.oy > PUSH_MAX) p.oy = PUSH_MAX; else if (p.oy < -PUSH_MAX) p.oy = -PUSH_MAX;
        /* conversion still reads the true x: the hand moves the look, not the line */
        if (p.x >= gx) { convert(p); reset(p, false); }
      }

      for (i = 0; i < rows.length; i++) {
        if (rows[i].on > 0 && rows[i].on < 1) rows[i].on = Math.min(1, rows[i].on + dt * 1.7);
      }
      // the table stays mostly full: once delivered, rows retire one at a
      // time so the feed reads as continuous rather than as a reset loop
      var lit = 0;
      for (i = 0; i < rows.length; i++) if (rows[i].on >= 1) lit++;
      if (lit >= rows.length - 1) {
        acc += dt;
        if (acc > 0.5) {
          acc = 0;
          for (i = 0; i < rows.length; i++) if (rows[i].on >= 1) { rows[i].on = 0; break; }
        }
      }

      for (i = nSpark - 1; i >= 0; i--) {
        s = sparks[i];
        if (pt.on) {                       // fresh sparks lean toward the hand
          dx = pt.x - s.x; dy = pt.y - s.y;
          d2 = dx * dx + dy * dy;
          if (d2 < 40000 && d2 > 1) {
            d = Math.sqrt(d2); g = 70 * dt;
            s.vx += dx / d * g; s.vy += dy / d * g;
          }
        }
        s.x += s.vx * dt; s.y += s.vy * dt; s.vy += 60 * dt; s.life -= dt * 1.5;
        if (s.life <= 0) {                 // kill by swapping with the last live one
          sparks[i] = sparks[nSpark - 1];
          sparks[nSpark - 1] = s;
          nSpark--;
        }
      }
    }

    /* trim a label to the width its column actually has */
    function ellipsis(txt, max) {
      if (max <= 8) return '';
      if (ctx.measureText(txt).width <= max) return txt;
      var s = txt;
      while (s.length > 1 && ctx.measureText(s + '…').width > max) s = s.slice(0, -1);
      return s + '…';
    }

    function draw() {
      var gx = W * GATE, i;
      ctx.fillStyle = '#121016';
      ctx.fillRect(0, 0, W, H);

      // faint field grid on the clean side
      ctx.strokeStyle = 'rgba(255,255,255,.035)';
      ctx.lineWidth = 1;
      for (i = 1; i < 4; i++) {
        var x = gx + (W - gx) * (i / 4);
        ctx.beginPath(); ctx.moveTo(x, 14); ctx.lineTo(x, H - 14); ctx.stroke();
      }

      // raw side. Clipped at the gate: fillText draws rightward from its
      // origin, so a long fragment would otherwise spill over the clean table.
      ctx.font = '12px "IBM Plex Mono", ui-monospace, Menlo, monospace';
      ctx.textBaseline = 'middle';
      ctx.save();
      ctx.beginPath(); ctx.rect(0, 0, gx - 4, H); ctx.clip();
      for (i = 0; i < junk.length; i++) {
        var p = junk[i];
        if (p.x > gx) continue;
        var fade = Math.min(1, (gx - p.x) / 90);
        ctx.save();
        ctx.translate(p.x + p.ox, p.y + p.oy); ctx.rotate(p.rot);
        ctx.globalAlpha = p.a * fade;
        ctx.fillStyle = p.bad ? '#FF4A17' : '#8E837A';
        ctx.fillText(p.t, 0, 0);
        ctx.restore();
      }
      ctx.restore();
      ctx.globalAlpha = 1;

      // the gate, widening as the cursor crosses it
      var gi = (gatePulse * (GRAD_N - 1) + 0.5) | 0;
      if (gi < 0) gi = 0; else if (gi >= GRAD_N) gi = GRAD_N - 1;
      if (grads.length) {
        ctx.fillStyle = grads[gi];
        ctx.fillRect(gx - gradHW[gi], 8, gradHW[gi] * 2, H - 16);
      }
      ctx.fillStyle = '#FF4A17';
      ctx.fillRect(gx - 1 - gatePulse * 0.5, 8, 2 + gatePulse, H - 16);

      // clean side
      for (i = 0; i < rows.length; i++) {
        var r = rows[i], on = r.on, y = r.y + r.h / 2;
        var x0 = gx + 26, w = W - x0 - 18;
        ctx.fillStyle = 'rgba(255,255,255,.045)';
        ctx.fillRect(x0, r.y + 3, w, r.h - 6);
        if (on <= 0) continue;
        var k = on < 1 ? on : 1;
        ctx.save();
        ctx.beginPath(); ctx.rect(x0, r.y, w * k, r.h); ctx.clip();
        ctx.fillStyle = 'rgba(255,74,23,' + (0.16 * (1 - k)) + ')';
        ctx.fillRect(x0, r.y + 3, w, r.h - 6);
        ctx.font = '12px "IBM Plex Mono", ui-monospace, Menlo, monospace';
        var price = '£' + r.data[1];
        var pw = ctx.measureText(price).width;
        var maxw = w - pw - 34;
        /* the trim only changes when the column does: no per-frame string work */
        if (r.lw !== maxw) { r.lw = maxw; r.label = ellipsis(r.data[0], maxw); }
        ctx.fillStyle = '#F2EDE7';
        ctx.textAlign = 'left';
        ctx.fillText(r.label, x0 + 12, y);
        ctx.fillStyle = '#FF4A17';
        ctx.textAlign = 'right';
        ctx.fillText(price, x0 + w - 12, y);
        ctx.textAlign = 'left';
        ctx.restore();
        if (on < 1) {
          ctx.fillStyle = '#FF4A17';
          ctx.fillRect(x0 + w * k - 2, r.y + 3, 2, r.h - 6);
        }
      }

      // sparks
      for (i = 0; i < nSpark; i++) {
        var s = sparks[i];
        ctx.globalAlpha = Math.max(0, s.life) * 0.9;
        ctx.fillStyle = '#FFB08A';
        ctx.fillRect(s.x, s.y, 2, 2);
      }
      ctx.globalAlpha = 1;
    }

    function frame(now) {
      if (!running) return;
      var dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016;
      last = now;
      step(dt); draw();
      requestAnimationFrame(frame);
    }

    function start() { if (running) return; running = true; last = 0; requestAnimationFrame(frame); }
    function stop() { running = false; }

    resize();                 // builds, composes and paints the resting frame
    if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas);
    else window.addEventListener('resize', resize);

    // under reduced motion the resting frame is the whole animation
    if (reduced) return;

    /* the hand. Passive listeners, and the rect is only read on a real move. */
    canvas.addEventListener('pointermove', function (e) {
      var r = canvas.getBoundingClientRect();
      pt.x = e.clientX - r.left;
      pt.y = e.clientY - r.top;
      pt.on = true;
    }, { passive: true });
    canvas.addEventListener('pointerleave', function () {
      pt.on = false; pt.x = -9999; pt.y = -9999;
    }, { passive: true });
    canvas.addEventListener('pointerdown', function (e) {
      var r = canvas.getBoundingClientRect();
      var x = e.clientX - r.left, y = e.clientY - r.top;
      var n = 10 + ((Math.random() * 5) | 0), i, a, sp;
      for (i = 0; i < n; i++) {
        a = Math.random() * 6.2832;
        sp = 60 + Math.random() * 180;
        emit(x, y, Math.cos(a) * sp, Math.sin(a) * sp - 40);
      }
    }, { passive: true });

    doc.addEventListener('visibilitychange', function () {
      if (doc.hidden) stop(); else start();
    });
    if (hasIO) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) { e.isIntersecting && !doc.hidden ? start() : stop(); });
      }, { threshold: 0.05 }).observe(canvas);
    } else start();

    // preference flipped mid-visit: settle on the resting frame, not on
    // whatever half-drawn frame the loop happened to be on
    stopMotion.push(function () { stop(); compose(); draw(); });
  }

  /* ---------------------------------------------------------------
     2. THE SPLIT HEADLINE
     Wraps every word of an element in a mask at runtime, whatever the
     text and whatever inline markup it carries — the <em> keeps its own
     element, its words are simply wrapped inside it. Word order gives
     the sequence, so the emphasis at the end of a sentence naturally
     arrives last. Nothing is written to the DOM unless the element
     carries [data-split].
     --------------------------------------------------------------- */
  function splitWords(el) {
    if (el.getAttribute('data-split-done')) return;
    var idx = 0;

    function walk(node) {
      var kids = Array.prototype.slice.call(node.childNodes), i, n;
      for (i = 0; i < kids.length; i++) {
        n = kids[i];
        if (n.nodeType === 3) {
          var parts = n.nodeValue.split(/(\s+)/);
          if (parts.length === 1 && !parts[0]) continue;
          var frag = doc.createDocumentFragment();
          for (var j = 0; j < parts.length; j++) {
            var t = parts[j];
            if (!t) continue;
            if (!/\S/.test(t)) { frag.appendChild(doc.createTextNode(t)); continue; }
            var mask = doc.createElement('span');
            var inner = doc.createElement('span');
            mask.className = 'w';
            inner.className = 'wi';
            inner.style.setProperty('--i', String(idx++));
            inner.appendChild(doc.createTextNode(t));
            mask.appendChild(inner);
            frag.appendChild(mask);
          }
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.className !== 'w') {
          walk(n);
        }
      }
    }

    walk(el);
    el.setAttribute('data-split-done', '1');
  }

  /* ---------------------------------------------------------------
     3. SCROLL REVEALS
     The [data-rise] / .in contract is unchanged — 56 other pages
     depend on it. This only adds: an element that also carries
     [data-split] is lit at the same moment it is revealed.
     --------------------------------------------------------------- */
  function reveals() {
    var els = $$('[data-rise],[data-split]');
    if (!els.length) return;

    function show(el) {
      el.classList.add('in');
      if (el.hasAttribute('data-split')) el.classList.add('is-lit');
      onReveal(el);
    }

    if (reduced || !hasIO) {
      for (var i = 0; i < els.length; i++) show(els[i]);
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    for (var j = 0; j < els.length; j++) io.observe(els[j]);
    stopMotion.push(function () {
      io.disconnect();
      for (var k = 0; k < els.length; k++) show(els[k]);
    });
  }

  /* ---------------------------------------------------------------
     4. POINTER LIGHT ON PRIMARY BUTTONS
     --------------------------------------------------------------- */
  function buttons() {
    if (reduced) return;
    doc.addEventListener('pointermove', function (e) {
      var b = e.target.closest ? e.target.closest('.btn') : null;
      if (!b) return;
      var r = b.getBoundingClientRect();
      b.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      b.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }

  /* ---------------------------------------------------------------
     5. MAGNETIC ACTIONS
     6px of pull, then the button's own easing springs it home. The
     offset is handed to CSS as a custom property so the existing hover
     lift composes with it instead of being overwritten.
     --------------------------------------------------------------- */
  function magnetic() {
    if (reduced || !fine) return;
    var MAX = 6;
    $$('[data-magnetic]').forEach(function (el) {
      function release() {
        el.classList.remove('is-mag');
        el.style.setProperty('--mgx', '0px');
        el.style.setProperty('--mgy', '0px');
      }
      el.addEventListener('pointermove', function (e) {
        if (e.pointerType && e.pointerType !== 'mouse') return;
        var r = el.getBoundingClientRect();
        var mx = (e.clientX - (r.left + r.width / 2)) / (r.width / 2);
        var my = (e.clientY - (r.top + r.height / 2)) / (r.height / 2);
        if (mx > 1) mx = 1; else if (mx < -1) mx = -1;
        if (my > 1) my = 1; else if (my < -1) my = -1;
        el.classList.add('is-mag');
        el.style.setProperty('--mgx', (mx * MAX).toFixed(2) + 'px');
        el.style.setProperty('--mgy', (my * MAX).toFixed(2) + 'px');
      }, { passive: true });
      el.addEventListener('pointerleave', release, { passive: true });
      el.addEventListener('blur', release);
      stopMotion.push(release);
    });
  }

  /* ---------------------------------------------------------------
     6. SCROLL EFFECTS
     (a) parallax on [data-plx], clamped to ±24px, written as --plx so
         the reveal (which rides on `translate`) is never disturbed;
     (b) the belt reacts to scroll velocity: a lurch forward that eases
         back to the CSS animation's own pace. Modulating the animation
         duration instead would jump the track, since progress is
         elapsed/duration.
     --------------------------------------------------------------- */
  function scrollFx() {
    if (reduced) return;
    var layers = $$('[data-plx]');
    var track = $('.belt-track');
    var belt = $('.belt');
    if (!layers.length && !track) return;

    var CLAMP = 24;
    var vh = window.innerHeight;
    var vals = new Array(layers.length);       // read pass then write pass
    var ticking = false;
    var lastY = window.pageYOffset || root.scrollTop || 0;

    var target = 0, shift = 0, raf = null, hover = false;

    if (belt) {
      belt.addEventListener('pointerenter', function () { hover = true; }, { passive: true });
      belt.addEventListener('pointerleave', function () { hover = false; }, { passive: true });
    }

    function beltFrame() {
      raf = null;
      target *= 0.86;
      if (hover) target = 0;
      shift += (target - shift) * 0.18;
      if (Math.abs(shift) < 0.05 && Math.abs(target) < 0.05) {
        shift = 0; target = 0;
        track.style.translate = '';
        return;
      }
      track.style.translate = shift.toFixed(1) + 'px 0';
      raf = requestAnimationFrame(beltFrame);
    }

    function kick(d) {
      if (!track || hover) return;
      target -= d * 0.55;
      if (target > 70) target = 70; else if (target < -70) target = -70;
      if (raf === null && !doc.hidden) raf = requestAnimationFrame(beltFrame);
    }

    function update() {
      ticking = false;
      var y = window.pageYOffset || root.scrollTop || 0;
      var d = y - lastY;
      lastY = y;
      var i, el, r, f, mid, t;
      for (i = 0; i < layers.length; i++) {          // read
        el = layers[i];
        r = el.getBoundingClientRect();
        if (r.bottom < -240 || r.top > vh + 240) { vals[i] = null; continue; }
        f = parseFloat(el.getAttribute('data-plx')) || 0;
        mid = r.top + r.height / 2 - vh / 2;
        t = -mid * f;
        if (t > CLAMP) t = CLAMP; else if (t < -CLAMP) t = -CLAMP;
        vals[i] = t;
      }
      for (i = 0; i < layers.length; i++) {          // write
        if (vals[i] === null) continue;
        layers[i].style.setProperty('--plx', vals[i].toFixed(1) + 'px');
      }
      if (d) kick(d);
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    }

    function onResize() { vh = window.innerHeight; update(); }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize, { passive: true });
    doc.addEventListener('visibilitychange', function () {
      if (!doc.hidden) return;
      if (raf !== null) { cancelAnimationFrame(raf); raf = null; }
      target = 0; shift = 0;
      if (track) track.style.translate = '';
    });
    update();

    stopMotion.push(function () {
      window.removeEventListener('scroll', onScroll);
      if (raf !== null) { cancelAnimationFrame(raf); raf = null; }
      if (track) track.style.translate = '';
      for (var i = 0; i < layers.length; i++) layers[i].style.setProperty('--plx', '0px');
    });
  }

  /* ---------------------------------------------------------------
     7. ACTIVE SECTION IN THE NAV
     Silent on any page whose nav links do not resolve to a section
     that exists on it.
     --------------------------------------------------------------- */
  function activeNav() {
    if (!hasIO) return;
    var links = $$('.nav-links a:not(.btn)');
    if (!links.length) return;

    var map = [], i, href, h, id, el;
    for (i = 0; i < links.length; i++) {
      href = links[i].getAttribute('href') || '';
      h = href.indexOf('#');
      if (h < 0) continue;
      id = href.slice(h + 1);
      if (!id) continue;
      el = doc.getElementById(id);
      if (!el) continue;
      map.push({ a: links[i], el: el, vis: false });
    }
    if (!map.length) return;

    var io = new IntersectionObserver(function (entries) {
      var i, j;
      for (i = 0; i < entries.length; i++) {
        for (j = 0; j < map.length; j++) {
          if (map[j].el === entries[i].target) map[j].vis = entries[i].isIntersecting;
        }
      }
      var hit = -1;
      for (i = 0; i < map.length; i++) if (map[i].vis) { hit = i; break; }
      for (i = 0; i < map.length; i++) map[i].a.classList.toggle('is-active', i === hit);
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });

    for (i = 0; i < map.length; i++) io.observe(map[i].el);
  }

  /* ---------------------------------------------------------------
     8. HERO EMBERS
     A forge leaves something in the air. Forty-odd one and two pixel
     embers drift up through the hero, oscillating as they rise, cooling
     out and relighting at the floor. They give way, gently, around the
     cursor — the same hand the machine already answers to.

     This is ambience: at rest it should be felt rather than watched,
     which is why the alphas top out at .45 and the drift is slower than
     the eye tracks. Same budget rules as the machine: a fixed pool, no
     allocation in the loop, and the rAF cut when the hero leaves the
     screen or the tab goes away. Under reduced motion the canvas is not
     started at all — drifting embers have no meaningful still frame.
     --------------------------------------------------------------- */
  function embers(canvas) {
    var ctx = canvas.getContext('2d');
    if (!ctx) return;

    var W = 0, H = 0, dpr = 1, running = false, last = 0;
    var ps = [], N = 0;
    var COL = ['#FF4A17', '#C7300B', '#FFB08A'];

    var pt = { x: -9999, y: -9999, on: false };
    var PUSH_R = 96, PUSH_R2 = PUSH_R * PUSH_R, PUSH_F = 46, PUSH_MAX = 15;

    function want() {
      return (window.matchMedia && window.matchMedia('(max-width:720px)').matches) ? 21 : 42;
    }

    function seed(p, first) {
      p.x = Math.random() * W;
      p.y = first ? Math.random() * H : H + Math.random() * 26;
      p.vy = 9 + Math.random() * 17;          // px per second, upward
      p.amp = 3 + Math.random() * 11;         // sway, px
      p.w = 0.22 + Math.random() * 0.6;       // sway rate, rad/s
      p.ph = Math.random() * 6.2832;
      p.s = Math.random() < 0.26 ? 2 : 1;
      p.a = 0.12 + Math.random() * 0.33;
      p.c = COL[(Math.random() * 3) | 0];
      /* long enough that most of them cross the whole hero: a lifetime
         tuned to burn out mid-flight would pile every ember into the
         bottom third within a few seconds (measured). Only the slowest
         die on the way up, which is the handful that should. */
      p.ttl = 18 + Math.random() * 32;
      p.life = first ? Math.random() * p.ttl : p.ttl;
      p.ox = 0; p.oy = 0;
      return p;
    }

    function resize() {
      var r = canvas.getBoundingClientRect(), n = want(), i;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = Math.max(1, Math.round(r.width));
      H = Math.max(1, Math.round(r.height));
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (ps.length > n) ps.length = n;
      while (ps.length < n) ps.push(seed({}, true));
      N = ps.length;
      for (i = 0; i < N; i++) if (ps[i].x > W) ps[i].x = Math.random() * W;
      if (!running) draw();
    }

    function step(dt) {
      var i, p, dx, dy, d2, d, g;
      var decay = 1 - Math.pow(0.0009, dt);   // one pow per frame, not per ember
      for (i = 0; i < N; i++) {
        p = ps[i];
        p.y -= p.vy * dt;
        p.ph += p.w * dt;
        p.life -= dt;
        if (pt.on) {
          dx = (p.x + p.ox) - pt.x; dy = (p.y + p.oy) - pt.y;
          d2 = dx * dx + dy * dy;
          if (d2 < PUSH_R2 && d2 > 0.01) {
            d = Math.sqrt(d2);
            g = (1 - d / PUSH_R) * PUSH_F * dt;
            p.ox += dx / d * g; p.oy += dy / d * g;
          }
        }
        p.ox -= p.ox * decay; p.oy -= p.oy * decay;
        if (p.ox > PUSH_MAX) p.ox = PUSH_MAX; else if (p.ox < -PUSH_MAX) p.ox = -PUSH_MAX;
        if (p.oy > PUSH_MAX) p.oy = PUSH_MAX; else if (p.oy < -PUSH_MAX) p.oy = -PUSH_MAX;
        if (p.life <= 0 || p.y < -8) seed(p, false);
      }
    }

    function draw() {
      var i, p, age, e, a, x, y;
      ctx.clearRect(0, 0, W, H);
      for (i = 0; i < N; i++) {
        p = ps[i];
        /* absolute seconds, not a fraction of the lifetime: a long-lived
           ember should still catch and let go in about a second */
        age = p.ttl - p.life;
        e = Math.min(1, age / 1.2, p.life / 1.8);
        if (e <= 0) continue;
        a = p.a * e;
        if (a < 0.005) continue;
        x = p.x + Math.sin(p.ph) * p.amp + p.ox;
        if (x < -4 || x > W + 4) continue;
        y = p.y + p.oy;
        ctx.globalAlpha = a;
        ctx.fillStyle = p.c;
        ctx.fillRect(x | 0, y | 0, p.s, p.s);
      }
      ctx.globalAlpha = 1;
    }

    function frame(now) {
      if (!running) return;
      var dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016;
      last = now;
      step(dt); draw();
      requestAnimationFrame(frame);
    }
    function start() { if (running) return; running = true; last = 0; requestAnimationFrame(frame); }
    function stop() { running = false; }

    resize();
    if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas);
    else window.addEventListener('resize', resize);

    /* the canvas is pointer-transparent, so the hand is read on the hero */
    var hero = canvas.parentNode;
    if (hero && hero.addEventListener) {
      hero.addEventListener('pointermove', function (e) {
        var r = canvas.getBoundingClientRect();
        pt.x = e.clientX - r.left;
        pt.y = e.clientY - r.top;
        pt.on = true;
      }, { passive: true });
      hero.addEventListener('pointerleave', function () {
        pt.on = false; pt.x = -9999; pt.y = -9999;
      }, { passive: true });
    }

    doc.addEventListener('visibilitychange', function () {
      if (doc.hidden) stop(); else start();
    });
    if (hasIO) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) { e.isIntersecting && !doc.hidden ? start() : stop(); });
      }, { threshold: 0 }).observe(canvas);
    } else start();

    stopMotion.push(function () { stop(); ctx.clearRect(0, 0, W, H); });
  }

  /* ---------------------------------------------------------------
     9. THE PIPELINE RAIL
     The four steps stop being a list and become a route: a hairline bus
     under the cards, a tap under each one, and a packet that runs it —
     pausing under each step long enough to bring its number up to
     temperature, then carrying on. After the first pass it keeps
     circulating at reduced opacity, the way a line that is running does.

     The SVG is built here rather than in the markup so the only thing to
     replicate on the localized homes is one attribute. Geometry is read
     from the cards themselves (offsetLeft is layout, so the reveal's
     transform never disturbs it) and rebuilt on resize.

     Below 1040px the grid stacks: a horizontal rail would describe a
     route that no longer exists, so the numbers simply light in
     sequence instead. Under reduced motion the rail is drawn and every
     number is already lit.
     --------------------------------------------------------------- */
  function pipeline(grid) {
    var NS = 'http://www.w3.org/2000/svg';
    var cards = $$('.card', grid);
    if (cards.length < 2) return;

    var nums = [], i;
    for (i = 0; i < cards.length; i++) nums.push($('.step-num', cards[i]));

    var mqWide = window.matchMedia ? window.matchMedia('(min-width:1040px)') : null;
    var wide = mqWide ? mqWide.matches : true;

    function el(tag, cls) {
      var n = doc.createElementNS(NS, tag);
      if (cls) n.setAttribute('class', cls);
      return n;
    }
    function box(n, x, y, w, h) {
      n.setAttribute('x', x); n.setAttribute('y', y);
      n.setAttribute('width', w); n.setAttribute('height', h);
    }

    var svg = el('svg', 'pipe');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');

    var rail = el('rect', 'rail');
    svg.appendChild(rail);
    var taps = [];
    for (i = 0; i < cards.length; i++) { taps.push(el('rect', 'tap')); svg.appendChild(taps[i]); }

    /* the packet: a 5px head with three cooling embers behind it, all
       centred on the rail at y 19.5 */
    var pkg = el('g', 'pk-g');
    var trail = el('g', 'pk-t');
    var TR = [[-9, 3, 0.5], [-14, 2, 0.3], [-18, 2, 0.15]], t;
    for (i = 0; i < TR.length; i++) {
      t = el('rect', 'pk');
      box(t, TR[i][0], 19.5 - TR[i][1] / 2, TR[i][1], TR[i][1]);
      t.setAttribute('opacity', TR[i][2]);
      trail.appendChild(t);
    }
    pkg.appendChild(trail);
    var head = el('rect', 'pk');
    box(head, -2.5, 17, 5, 5);
    pkg.appendChild(head);
    svg.appendChild(pkg);
    grid.appendChild(svg);

    var TRAVEL = 4.2, DWELL = 0.42, TAIL = 3;      // ≈ 9s round
    var cx = [], kf = [], arrive = [], END = 0, PERIOD = 9;

    function layout() {
      var i, x0, x1, speed, tt, prev, W = grid.clientWidth;
      cx.length = 0;
      for (i = 0; i < cards.length; i++) cx.push(cards[i].offsetLeft + cards[i].offsetWidth / 2);
      box(rail, cx[0], 19, Math.max(0, cx[cx.length - 1] - cx[0]), 1);
      for (i = 0; i < taps.length; i++) box(taps[i], Math.round(cx[i]), 13, 1, 6);

      /* constant speed whatever the column widths, so the dwells read as
         deliberate stops rather than as a change of pace */
      x0 = -16; x1 = W + 16;
      speed = (x1 - x0) / TRAVEL;
      kf.length = 0; arrive.length = 0;
      tt = 0; prev = x0;
      kf.push({ t: 0, x: x0 });
      for (i = 0; i < cx.length; i++) {
        tt += (cx[i] - prev) / speed; prev = cx[i];
        kf.push({ t: tt, x: cx[i] });
        arrive.push(tt);
        tt += DWELL;
        kf.push({ t: tt, x: cx[i] });
      }
      tt += (x1 - prev) / speed;
      kf.push({ t: tt, x: x1 });
      END = tt;
      PERIOD = tt + TAIL;
    }

    var litN = 0, casc = false;
    function light(k) {
      var n = nums[k];
      if (!n || n.getAttribute('data-lit')) return;
      n.setAttribute('data-lit', '1');
      n.classList.add('is-lit');
      litN++;
    }
    function lightAll(stagger) {
      var i;
      if (!stagger) { for (i = 0; i < nums.length; i++) light(i); return; }
      if (casc) return;
      casc = true;
      for (i = 0; i < nums.length; i++) {
        (function (k) { window.setTimeout(function () { light(k); }, k * 130); })(i);
      }
    }

    var running = false, last = 0, elapsed = 0, vis = -1, onScreen = false;

    function frame(now) {
      if (!running) return;
      var dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016;
      last = now;
      elapsed += dt;
      var tt = elapsed % PERIOD, pass = (elapsed / PERIOD) | 0;
      var i, a, b, span, k, x = null, spd = 0, o;
      if (tt <= END) {
        for (i = 1; i < kf.length; i++) {
          if (tt <= kf[i].t) {
            a = kf[i - 1]; b = kf[i];
            span = b.t - a.t;
            k = span > 0 ? (tt - a.t) / span : 1;
            x = a.x + (b.x - a.x) * k;
            spd = span > 0 ? Math.abs(b.x - a.x) / span : 0;
            break;
          }
        }
      }
      if (x === null) {
        if (vis !== 0) { vis = 0; pkg.style.opacity = '0'; }
      } else {
        o = pass > 0 ? 2 : 1;                 // quieter once the route is known
        if (vis !== o) { vis = o; pkg.style.opacity = pass > 0 ? '.4' : '1'; }
        pkg.setAttribute('transform', 'translate(' + x.toFixed(1) + ',0)');
        /* the trail is speed: it collapses into the head at each stop */
        trail.setAttribute('opacity', (spd > 240 ? 1 : spd / 240).toFixed(2));
      }
      if (pass === 0) {
        for (i = 0; i < arrive.length; i++) if (tt >= arrive[i]) light(i);
      } else if (litN < nums.length) lightAll(false);
      requestAnimationFrame(frame);
    }

    function start() {
      if (running) return;
      if (!wide) { lightAll(true); return; }
      running = true; last = 0; requestAnimationFrame(frame);
    }
    function stop() { running = false; }

    function onResize() {
      var w = mqWide ? mqWide.matches : true;
      layout();
      if (w === wide) return;
      wide = w;
      if (!wide) { stop(); vis = 0; pkg.style.opacity = '0'; lightAll(false); }
      else if (onScreen && !doc.hidden) start();
    }

    layout();
    if (window.ResizeObserver) new ResizeObserver(onResize).observe(grid);
    else window.addEventListener('resize', onResize);

    if (reduced) { pkg.style.opacity = '0'; lightAll(false); return; }

    doc.addEventListener('visibilitychange', function () {
      if (doc.hidden) stop(); else if (onScreen) start();
    });
    if (hasIO) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          onScreen = e.isIntersecting;
          if (onScreen && !doc.hidden) start(); else stop();
        });
      }, { threshold: 0 }).observe(grid);
    } else { onScreen = true; start(); }

    stopMotion.push(function () {
      stop(); vis = 0; pkg.style.opacity = '0'; lightAll(false);
    });
  }

  /* ---------------------------------------------------------------
     10. PRICES COUNT UP
     The amount is found and wrapped at runtime, so the markup stays a
     plain price and the same code works on "€150" and on "150 €". Only
     the first number of the [data-count] element is touched: the note
     underneath ("to 1,500, one time") is prose and must not move.
     The final frame writes the original string back verbatim, so no
     formatting can drift.
     --------------------------------------------------------------- */
  var NUM = /\d{1,3}(?:[.,'\u202F\u00A0 ]\d{3})+|\d+/;

  function countUp(host) {
    if (reduced || host.getAttribute('data-cu')) return;
    host.setAttribute('data-cu', '1');

    var node = null, kids = host.childNodes, i, n;
    for (i = 0; i < kids.length; i++) {
      n = kids[i];
      if (n.nodeType === 3 && /\d/.test(n.nodeValue)) { node = n; break; }
    }
    if (!node) return;

    var m = node.nodeValue.match(NUM);
    if (!m) return;
    var raw = m[0];
    var to = parseInt(raw.replace(/\D/g, ''), 10);
    if (!isFinite(to) || to <= 0 || to > 9999999) return;
    var sm = raw.match(/[.,'\u202F\u00A0 ]/);
    var sep = sm ? sm[0] : '';

    function fmt(v) {
      var s = String(v), out = '', c = 0, i;
      if (!sep) return s;
      for (i = s.length - 1; i >= 0; i--) {
        out = s.charAt(i) + out;
        if (++c % 3 === 0 && i > 0) out = sep + out;
      }
      return out;
    }

    var span = doc.createElement('span');
    span.className = 'cu';
    span.textContent = fmt(0);
    var frag = doc.createDocumentFragment();
    var before = node.nodeValue.slice(0, m.index);
    var after = node.nodeValue.slice(m.index + raw.length);
    if (before) frag.appendChild(doc.createTextNode(before));
    frag.appendChild(span);
    if (after) frag.appendChild(doc.createTextNode(after));
    host.replaceChild(frag, node);

    var DUR = 700, t0 = 0, dead = false;
    function tick(now) {
      if (dead) return;
      if (!t0) t0 = now;
      var p = (now - t0) / DUR;
      if (p >= 1) { span.textContent = raw; return; }
      span.textContent = fmt(Math.round(to * (1 - Math.pow(1 - p, 3))));
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    stopMotion.push(function () { dead = true; span.textContent = raw; });
  }

  /* ---------------------------------------------------------------
     11. THE CONFIG TYPES ITSELF
     The <pre> carries coloured spans and, on the localized homes, its
     own translated comments — so the text is never re-written. Instead
     the element is revealed through a clip-path staircase: every line
     above the front at full width, the current line cut at the column
     the front has reached. The caret is a separate block outside the
     clipped element, riding that same front.

     Monospace makes the geometry exact: one probe gives the character
     width, the computed line-height gives the row. Runs once.
     --------------------------------------------------------------- */
  function clipTo(node, v) {
    if (v) {
      node.style.setProperty('-webkit-clip-path', v);
      node.style.setProperty('clip-path', v);
    } else {
      node.style.removeProperty('-webkit-clip-path');
      node.style.removeProperty('clip-path');
    }
  }
  function clipOK() {
    var s = root.style;
    return ('clipPath' in s) || ('webkitClipPath' in s) || ('WebkitClipPath' in s);
  }
  var HIDE_ALL = 'polygon(0 0, 100% 0, 100% 0, 0 0)';

  function stageType(pre) {
    if (reduced || !clipOK()) return;
    clipTo(pre, HIDE_ALL);
  }

  function typer(pre) {
    if (reduced || !clipOK() || pre.getAttribute('data-tw')) return;
    pre.setAttribute('data-tw', '1');
    var body = pre.parentNode;
    if (!body) { clipTo(pre, ''); return; }

    var cs = window.getComputedStyle(pre);
    var lh = parseFloat(cs.lineHeight);
    if (!(lh > 0)) lh = Math.round((parseFloat(cs.fontSize) || 13) * 1.65);

    var lines = pre.textContent.split('\n'), total = 0, i;
    for (i = 0; i < lines.length; i++) total += lines[i].length;
    if (!total) { clipTo(pre, ''); return; }

    /* measured inside the <pre>, so it inherits the exact face and size */
    var probe = doc.createElement('span');
    probe.textContent = '0000000000';
    probe.style.cssText = 'position:absolute;left:-9999px;top:0;white-space:pre;visibility:hidden';
    pre.appendChild(probe);
    var chW = probe.getBoundingClientRect().width / 10;
    pre.removeChild(probe);
    if (!(chW > 0)) { clipTo(pre, ''); return; }

    body.classList.add('has-caret');
    var caret = doc.createElement('i');
    caret.className = 'fs-caret';
    caret.style.width = chW.toFixed(2) + 'px';
    caret.style.height = lh.toFixed(1) + 'px';
    body.appendChild(caret);

    var ox = pre.offsetLeft, oy = pre.offsetTop;
    var DUR = 1400, t0 = 0, dead = false, over = false;

    function put(L, C) {
      var y0 = (L * lh).toFixed(1), y1 = ((L + 1) * lh).toFixed(1), x = (C * chW).toFixed(1);
      clipTo(pre, 'polygon(0 0, 100% 0, 100% ' + y0 + 'px, ' + x + 'px ' + y0 +
        'px, ' + x + 'px ' + y1 + 'px, 0 ' + y1 + 'px)');
      caret.style.transform = 'translate(' + (ox + C * chW).toFixed(1) + 'px,' +
        (oy + L * lh).toFixed(1) + 'px)';
    }

    function done() {
      if (over) return;
      over = true;
      clipTo(pre, '');
      caret.classList.add('is-done');
      window.setTimeout(function () {
        if (caret.parentNode) caret.parentNode.removeChild(caret);
        body.classList.remove('has-caret');
      }, 700);
    }

    function tick(now) {
      if (dead) return;
      if (!t0) t0 = now;
      var p = (now - t0) / DUR;
      if (p >= 1) { done(); return; }
      var k = Math.round(p * total), L = 0, C = 0, i;
      for (i = 0; i < lines.length; i++) {
        if (k <= lines[i].length) { L = i; C = k; break; }
        k -= lines[i].length;
        if (i === lines.length - 1) { L = i; C = lines[i].length; }
      }
      put(L, C);
      requestAnimationFrame(tick);
    }
    put(0, 0);
    requestAnimationFrame(tick);
    stopMotion.push(function () { dead = true; done(); });
  }

  /* ---------------------------------------------------------------
     12. THE CSV ARRIVES ROW BY ROW
     The same language as the machine's clean side: a hot wash that
     cools and a leading edge on the first cell. Both classes are taken
     off once the sweep has run — a filled animation would otherwise
     outrank the row hover for the rest of the visit.
     --------------------------------------------------------------- */
  function stageSweep(tb) {
    if (reduced) return;
    var rows = $$('tr', tb), i;
    if (!rows.length) return;
    for (i = 0; i < rows.length; i++) rows[i].style.setProperty('--i', String(i));
    tb.classList.add('fs-stage');
  }

  function sweep(tb) {
    if (reduced || tb.getAttribute('data-sw')) return;
    tb.setAttribute('data-sw', '1');
    var rows = $$('tr', tb), i;
    if (!rows.length) return;
    for (i = 0; i < rows.length; i++) rows[i].classList.add('is-in');

    function settle() {
      tb.classList.remove('fs-stage');
      for (var k = 0; k < rows.length; k++) {
        rows[k].classList.remove('is-in');
        rows[k].style.removeProperty('--i');
      }
    }
    window.setTimeout(settle, (rows.length - 1) * 90 + 420 + 140);
    stopMotion.push(settle);
  }

  /* every middle-of-page piece is triggered by the reveal that already
     brings its section in; each one is a no-op where its hook is absent */
  function onReveal(el) {
    var a, i;
    a = $$('[data-count]', el);
    for (i = 0; i < a.length; i++) countUp(a[i]);
    a = $$('[data-type]', el);
    for (i = 0; i < a.length; i++) typer(a[i]);
    a = $$('[data-sweep]', el);
    for (i = 0; i < a.length; i++) sweep(a[i]);
  }

  /* ---------------------------------------------------------------
     BOOT
     The headline and the reveals wait for the curtain. .fs-pl is set by
     the inline head script (first visit of the session, motion allowed)
     and cleared by that same script — so this only ever reads it.
     --------------------------------------------------------------- */
  function afterIntro(fn) {
    if (reduced || !root.classList.contains('fs-pl')) { fn(); return; }
    window.setTimeout(fn, 740);
  }

  function boot() {
    var splits = $$('[data-split]');
    if (!reduced) {
      for (var i = 0; i < splits.length; i++) splitWords(splits[i]);
    }
    /* the head script hid the split headline to avoid a flash between
       first paint and the wrap; it is safe to show it again now */
    root.classList.remove('fs-pre');

    var c = doc.getElementById('machine');
    if (c) {
      if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(function () { machine(c); });
      else machine(c);
    }

    /* v3. The staged states are set here, before any reveal can fire, and
       only ever by script — with JS off the config and the table are
       simply there. */
    var e = $('.hero-embers');
    if (e && !reduced) embers(e);
    var g = $('[data-pipeline]');
    if (g) pipeline(g);
    var st = $$('[data-type]'), k;
    for (k = 0; k < st.length; k++) stageType(st[k]);
    st = $$('[data-sweep]');
    for (k = 0; k < st.length; k++) stageSweep(st[k]);

    buttons();
    magnetic();
    scrollFx();
    activeNav();

    afterIntro(reveals);
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', boot);
  else boot();

  /* preference flipped mid-visit: cut the motion, leave every element in
     its finished state, without a reload that would lose a typed form */
  if (mqReduce) {
    var onPref = function (e) {
      if (!e.matches || reduced) return;
      reduced = true;
      for (var i = 0; i < stopMotion.length; i++) {
        try { stopMotion[i](); } catch (err) { /* ignored */ }
      }
      $$('[data-split]').forEach(function (el) { el.classList.add('is-lit'); });
    };
    if (mqReduce.addEventListener) mqReduce.addEventListener('change', onPref);
    else if (mqReduce.addListener) mqReduce.addListener(onPref);
  }
})();
