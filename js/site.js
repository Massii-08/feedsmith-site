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
   7. active section in the nav                                              */
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
