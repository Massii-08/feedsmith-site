/* Feedsmith — motion layer. Vanilla, no build step, no dependency.
   Three things: the hero machine (canvas), scroll reveals, and pointer
   feedback on the primary buttons. Everything degrades to a static,
   fully readable page when JavaScript or motion is unavailable. */
(function () {
  'use strict';

  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------
     1. THE MACHINE
     Raw public web on the left (broken markup, 403s, empty bodies)
     travels right, crosses the forge gate, and locks into clean rows
     on the right. The rows carry real field names from the sample feed.
     --------------------------------------------------------------- */
  function machine(canvas) {
    var ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    var W = 0, H = 0, dpr = 1;
    var GATE = 0.44;              // gate position, share of width
    var rows = [], junk = [], sparks = [];
    var last = 0, acc = 0;

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

    function resize() {
      var r = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = Math.max(320, r.width); H = Math.max(180, r.height);
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      build();
    }

    function build() {
      rows = [];
      var top = 26, rh = Math.max(22, Math.min(30, (H - 52) / 8));
      var n = Math.max(4, Math.floor((H - 52) / rh));
      for (var i = 0; i < n && i < FIELDS.length; i++) {
        rows.push({ y: top + i * rh, h: rh, on: 0, data: FIELDS[i] });
      }
      junk = [];
      for (var j = 0; j < 18; j++) junk.push(spawn(true));
    }

    function spawn(seed) {
      return {
        x: seed ? Math.random() * W * GATE : -Math.random() * 90 - 20,
        y: 20 + Math.random() * (H - 44),
        v: 14 + Math.random() * 26,
        t: JUNK[(Math.random() * JUNK.length) | 0],
        bad: Math.random() < 0.28,
        a: 0.28 + Math.random() * 0.4,
        rot: (Math.random() - 0.5) * 0.14
      };
    }

    function convert(p) {
      var free = [], i;
      for (i = 0; i < rows.length; i++) if (rows[i].on < 0.05) free.push(i);
      var idx = free.length ? free[(Math.random() * free.length) | 0] : (Math.random() * rows.length) | 0;
      rows[idx].on = 0.001;
      for (i = 0; i < 7; i++) {
        sparks.push({
          x: W * GATE, y: p.y,
          vx: 30 + Math.random() * 150, vy: (Math.random() - 0.5) * 190,
          life: 1
        });
      }
    }

    function step(dt) {
      var i, p;
      for (i = junk.length - 1; i >= 0; i--) {
        p = junk[i];
        p.x += p.v * dt;
        if (p.x >= W * GATE) { convert(p); junk[i] = spawn(false); }
      }
      while (junk.length < 18) junk.push(spawn(false));

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

      for (i = sparks.length - 1; i >= 0; i--) {
        var s = sparks[i];
        s.x += s.vx * dt; s.y += s.vy * dt; s.vy += 60 * dt; s.life -= dt * 1.5;
        if (s.life <= 0) sparks.splice(i, 1);
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

      // raw side
      ctx.font = '12px "IBM Plex Mono", ui-monospace, Menlo, monospace';
      ctx.textBaseline = 'middle';
      for (i = 0; i < junk.length; i++) {
        var p = junk[i];
        if (p.x > gx) continue;
        var fade = Math.min(1, (gx - p.x) / 90);
        ctx.save();
        ctx.translate(p.x, p.y); ctx.rotate(p.rot);
        ctx.globalAlpha = p.a * fade;
        ctx.fillStyle = p.bad ? '#FF4A17' : '#8A8299';
        ctx.fillText(p.t, 0, 0);
        ctx.restore();
      }
      ctx.globalAlpha = 1;

      // the gate
      var g = ctx.createLinearGradient(gx - 26, 0, gx + 26, 0);
      g.addColorStop(0, 'rgba(255,74,23,0)');
      g.addColorStop(0.5, 'rgba(255,74,23,.5)');
      g.addColorStop(1, 'rgba(255,74,23,0)');
      ctx.fillStyle = g;
      ctx.fillRect(gx - 26, 8, 52, H - 16);
      ctx.fillStyle = '#FF4A17';
      ctx.fillRect(gx - 1, 8, 2, H - 16);

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
        ctx.fillStyle = '#F2EDE7';
        ctx.textAlign = 'left';
        ctx.fillText(ellipsis(r.data[0], w - pw - 34), x0 + 12, y);
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
      for (i = 0; i < sparks.length; i++) {
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

    var running = false;
    function start() { if (running) return; running = true; last = 0; requestAnimationFrame(frame); }
    function stop() { running = false; }

    resize();
    if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas);
    else window.addEventListener('resize', resize);

    if (reduced) {
      // one composed, static frame: half the rows already delivered
      for (var i = 0; i < rows.length; i++) rows[i].on = i % 2 ? 0 : 1;
      draw();
      return;
    }

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else start();
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) { e.isIntersecting && !document.hidden ? start() : stop(); });
      }, { threshold: 0.05 }).observe(canvas);
    } else start();
  }

  /* ---------------------------------------------------------------
     2. SCROLL REVEALS
     --------------------------------------------------------------- */
  function reveals() {
    var els = document.querySelectorAll('[data-rise]');
    if (!els.length) return;
    if (reduced || !('IntersectionObserver' in window)) {
      for (var i = 0; i < els.length; i++) els[i].classList.add('in');
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    for (var j = 0; j < els.length; j++) io.observe(els[j]);
  }

  /* ---------------------------------------------------------------
     3. POINTER LIGHT ON PRIMARY BUTTONS
     --------------------------------------------------------------- */
  function buttons() {
    if (reduced) return;
    document.addEventListener('pointermove', function (e) {
      var b = e.target.closest ? e.target.closest('.btn') : null;
      if (!b) return;
      var r = b.getBoundingClientRect();
      b.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      b.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }

  function boot() {
    var c = document.getElementById('machine');
    if (c) {
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { machine(c); });
      else machine(c);
    }
    reveals();
    buttons();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
