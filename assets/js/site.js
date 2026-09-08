(function(){
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine   = matchMedia('(hover: hover) and (pointer: fine)').matches;

  function go(){ document.body.classList.add('ready'); }
  if (reduce) { go(); }
  else if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(go); setTimeout(go, 1200);
  } else { go(); }

  /* masthead + scroll progress, one passive listener */
  var mast = document.querySelector('.mast'), prog = document.querySelector('.prog');
  function onScroll(){
    mast.classList.toggle('stuck', scrollY > 24);
    var max = document.documentElement.scrollHeight - innerHeight;
    prog.style.transform = 'scaleX(' + (max > 0 ? scrollY / max : 0) + ')';
  }
  addEventListener('scroll', onScroll, {passive:true}); onScroll();

  /* mobile nav */
  var burger = document.querySelector('.burger'), nav = document.getElementById('nav');

  /* pill indicator slides to the item under the pointer */
  var ind = document.querySelector('.nav-ind');
  if (ind) {
    nav.querySelectorAll('.nav-i').forEach(function(item){
      item.addEventListener('mouseenter', function(){
        if (innerWidth <= 1080) return;
        var a = item.querySelector('a');
        var r = a.getBoundingClientRect(), nr = nav.getBoundingClientRect();
        ind.style.left  = (r.left - nr.left) + 'px';
        ind.style.width = r.width + 'px';
        nav.classList.add('hot');
      });
    });
    nav.addEventListener('mouseleave', function(){ nav.classList.remove('hot'); });
  }
  burger.addEventListener('click', function(){
    var open = nav.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
  });
  nav.addEventListener('click', function(e){
    if (e.target.tagName === 'A') {
      nav.classList.remove('open'); burger.setAttribute('aria-expanded','false');
    }
  });

  /* ambient aurora follows the cursor — the hero is alive before you scroll */
  if (!reduce && fine) {
    var auras = document.querySelectorAll('.aura');
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
    addEventListener('mousemove', function(e){
      tx = (e.clientX / innerWidth  - .5) * 70;
      ty = (e.clientY / innerHeight - .5) * 70;
      if (!raf) raf = requestAnimationFrame(loop);
    }, {passive:true});
    function loop(){
      cx += (tx - cx) * .06; cy += (ty - cy) * .06;
      auras.forEach(function(a){
        a.style.setProperty('--px', cx.toFixed(2));
        a.style.setProperty('--py', cy.toFixed(2));
      });
      raf = (Math.abs(tx-cx) > .1 || Math.abs(ty-cy) > .1)
        ? requestAnimationFrame(loop) : null;
    }

  }

  /* ── THE FIELD ──────────────────────────────────────────────────────
     Organic forms on one canvas. Each blob is a closed curve through N
     radial points whose radius is modulated by summed sines. The sine
     frequencies are INTEGER multiples of the angle, which is what makes
     the deformation seamless where the curve wraps at 2*pi — with
     non-integer frequencies you get a visible kink at the seam.
     One path per blob, one paint per frame, however many there are.
     ------------------------------------------------------------------ */
  var cv = document.querySelector('.field');
  if (cv) (function(){
    var ctx = cv.getContext('2d');
    var hero = cv.parentNode, blobs = [], W = 0, H = 0, dpr = 1, raf = null;

    var INK  = '23,20,18';
    var HUES = ['236,64,8','240,115,26','219,162,46','200,30,20'];

    function rnd(a,b){ return a + Math.random()*(b-a); }

    function build(){
      /* Few and large beats many and small. Fifteen hairline outlines read as
         scribble; a handful of big soft masses reads as depth. All filled —
         hollow rings drew attention to their own edges. */
      var count = W < 760 ? 4 : 6;
      var pal = HUES.concat([INK]);
      blobs = [];
      for (var i=0; i<count; i++){
        blobs.push({
          x: rnd(-0.05,1.05)*W, y: rnd(-0.05,1.05)*H,
          r: rnd(W<760 ? 110 : 190, W<760 ? 200 : 340),
          /* elongation + rotation, so they are not six of the same circle */
          sx: rnd(.72,1.34), sy: rnd(.72,1.34), rot: rnd(0, Math.PI*2),
          pts: 18,
          amp: rnd(.12,.28),
          spd: rnd(.035,.10),                     /* slower than before */
          ph: [rnd(0,99), rnd(0,99), rnd(0,99)],
          vx: rnd(-.055,.055), vy: rnd(-.04,.04),
          col: pal[i % pal.length],
          alpha: (i % pal.length === pal.length-1) ? rnd(.050,.070)  /* ink reads darker */
                                                   : rnd(.085,.135)
        });
      }
    }

    /* Rasterising 15 large paths at full resolution cost ~7fps and 14 dropped
       frames per 2s (measured). These shapes are soft, out-of-focus background
       at 10-17% opacity, so they are drawn into a REDUCED-resolution buffer and
       upscaled by CSS — invisible at this blur level, and it cuts the rasterised
       pixel count by roughly half. */
    var RES = 0.62;
    function size(){
      var r = hero.getBoundingClientRect();
      W = r.width; H = r.height;
      dpr = Math.min(devicePixelRatio || 1, 2) * RES;
      cv.width = Math.round(W*dpr); cv.height = Math.round(H*dpr);
      ctx.setTransform(dpr,0,0,dpr,0,0);
      ctx.lineJoin = 'round';
      build();
    }

    function shape(b, t){
      var N = b.pts, pts = [], i, a, n, rr, px, py;
      var cr = Math.cos(b.rot), sr = Math.sin(b.rot);
      for (i=0; i<N; i++){
        a = i/N * Math.PI*2;
        n = Math.sin(a*2 + t*b.spd       + b.ph[0]) * .50
          + Math.sin(a*3 - t*b.spd*0.77  + b.ph[1]) * .32
          + Math.sin(a*5 + t*b.spd*0.53  + b.ph[2]) * .18;
        rr = b.r * (1 + n*b.amp);
        px = Math.cos(a)*rr*b.sx; py = Math.sin(a)*rr*b.sy;
        pts.push([b.x + px*cr - py*sr, b.y + px*sr + py*cr]);
      }
      ctx.beginPath();
      var last = pts[N-1], first = pts[0];
      ctx.moveTo((last[0]+first[0])/2, (last[1]+first[1])/2);
      for (i=0; i<N; i++){
        var q = pts[i], w = pts[(i+1)%N];
        ctx.quadraticCurveTo(q[0], q[1], (q[0]+w[0])/2, (w[1]+q[1])/2);
      }
      ctx.closePath();
    }

    function frame(now){
      var t = now/1000, m = 420;
      ctx.clearRect(0,0,W,H);
      for (var i=0; i<blobs.length; i++){
        var b = blobs[i];
        if (!reduce){
          b.x += b.vx; b.y += b.vy;
          if (b.x < -m) b.x = W+m; else if (b.x > W+m) b.x = -m;
          if (b.y < -m) b.y = H+m; else if (b.y > H+m) b.y = -m;
        }
        shape(b, reduce ? 0 : t);
        /* Filled flat, the path edge reads as a cut-out. Filling with a radial
           falloff that reaches zero at the silhouette keeps the organic form
           while removing the hard boundary — soft mass, not sticker. */
        var R = b.r * (1 + b.amp) * Math.max(b.sx, b.sy);
        var gr = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, R);
        gr.addColorStop(0,   'rgba('+b.col+','+b.alpha+')');
        gr.addColorStop(0.55,'rgba('+b.col+','+(b.alpha*0.72).toFixed(4)+')');
        gr.addColorStop(1,   'rgba('+b.col+',0)');
        ctx.fillStyle = gr;
        ctx.fill();
      }
      if (!reduce) raf = requestAnimationFrame(frame);
    }

    var ro = window.ResizeObserver ? new ResizeObserver(size) : null;
    if (ro) ro.observe(hero); else addEventListener('resize', size);
    size();

    if (reduce) { frame(0); return; }            /* one static frame, no loop */

    /* stop drawing once the hero has scrolled away — no point burning
       battery animating something nobody can see */
    new IntersectionObserver(function(es){
      es.forEach(function(e){
        if (e.isIntersecting){ if (!raf) raf = requestAnimationFrame(frame); }
        else if (raf){ cancelAnimationFrame(raf); raf = null; }
      });
    }, {threshold:0}).observe(hero);
  })();

  /* Stagger group children before observing. Counted PER CONTAINER, not per
     selector — a page with three .cells blocks would otherwise carry the cap
     (540ms) into every group after the first, and the later ones would sit
     visibly waiting after they had already scrolled in. */
  ['.cohorts', '.index', '.cells', '.events'].forEach(function(sel){
    document.querySelectorAll(sel).forEach(function(group){
      var kids = group.children, i = 0;
      for (var k = 0; k < kids.length; k++){
        if (!kids[k].hasAttribute('data-rv')) continue;
        kids[k].style.setProperty('--d', Math.min(i,9) * 60 + 'ms');
        i++;
      }
    });
  });

  /* A clip-path:inset(0 100% 0 0) element has ZERO visible area, and
     IntersectionObserver measures visible area — so a masked element can never
     trigger its own reveal. Masked nodes are watched via their unclipped parent. */
  var proxied = new Map();
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if (!en.isIntersecting) return;
      (proxied.get(en.target) || [en.target]).forEach(function(el){
        el.classList.add('in');
      });
      io.unobserve(en.target);
    });
  }, {threshold:.15, rootMargin:'0px 0px -8% 0px'});

  document.querySelectorAll('[data-rv], .people article').forEach(function(el){
    var masked = el.getAttribute('data-rv') === 'mask';
    var target = masked && el.parentElement ? el.parentElement : el;
    if (target === el) { io.observe(el); return; }
    if (proxied.has(target)) { proxied.get(target).push(el); return; }
    proxied.set(target, [el]); io.observe(target);
  });

  /* IntersectionObserver samples once per frame. Flick-scroll fast enough and an
     element can be below the fold on one sample and above it on the next — it
     never reports as intersecting, and would stay invisible for good. Sweep
     anything already past the fold once scrolling settles. */
  var sweepT;
  function sweep(){
    document.querySelectorAll('[data-rv]:not(.in), .people article:not(.in)')
      .forEach(function(el){
        if (el.getBoundingClientRect().top < innerHeight) el.classList.add('in');
      });
  }
  addEventListener('scroll', function(){
    clearTimeout(sweepT); sweepT = setTimeout(sweep, 140);
  }, {passive:true});
  addEventListener('load', sweep);

  /* counters — markup already holds the real value, so no-JS reads correctly */
  if (!reduce) {
    var cio = new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if (!en.isIntersecting) return;
        var box = en.target, out = box.querySelector('b');
        var suffix = out.querySelector('em');
        var suf = suffix ? suffix.outerHTML : '';
        var end = +box.dataset.count, t0 = performance.now(), dur = 2400;
        cio.unobserve(box);
        requestAnimationFrame(function tick(now){
          var p = Math.min((now - t0) / dur, 1);
          var e = 1 - Math.pow(1 - p, 3);
          out.innerHTML = Math.round(end * e) + (p === 1 ? suf : '');
          if (p < 1) requestAnimationFrame(tick);
        });
      });
    }, {threshold:.5});
    document.querySelectorAll('[data-count]').forEach(function(el){ cio.observe(el); });
  }
})();
