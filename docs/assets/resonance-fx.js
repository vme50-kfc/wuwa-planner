(() => {
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ------------------------------------------------------------------------
     1. Hero Resonance Soundwave & Tacet Stardust Canvas
     ------------------------------------------------------------------------ */
  const canvas = document.querySelector('#resonance-canvas');
  const hero = document.querySelector('.hero');

  if (canvas && hero) {
    const ctx = canvas.getContext('2d');
    let width = 0;
    let height = 0;
    let dpr = 1;
    let rafId = 0;
    let heroVisible = true;
    let particles = [];
    let pointerX = 0.5;

    function createParticles(count) {
      const list = [];
      for (let i = 0; i < count; i++) {
        const isGold = i % 3 !== 0;
        list.push({
          x: Math.random(),
          y: Math.random(),
          vy: 0.00018 + Math.random() * 0.00038,
          vx: (Math.random() - 0.5) * 0.00014,
          size: isGold ? 1.4 + Math.random() * 2.2 : 1.1 + Math.random() * 1.8,
          phase: Math.random() * Math.PI * 2,
          star: i % 5 === 0,
          gold: isGold,
        });
      }
      return list;
    }

    function resize() {
      const rect = hero.getBoundingClientRect();
      width = Math.max(320, Math.round(rect.width));
      height = Math.max(240, Math.round(rect.height));
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const targetCount = width < 640 ? 22 : 42;
      if (particles.length !== targetCount) particles = createParticles(targetCount);
      if (prefersReduced) drawFrame(1200);
    }

    function drawDiamondStar(x, y, r, alpha, color) {
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(x, y - r * 2.3);
      ctx.lineTo(x + r * 0.62, y - r * 0.62);
      ctx.lineTo(x + r * 2.3, y);
      ctx.lineTo(x + r * 0.62, y + r * 0.62);
      ctx.lineTo(x, y + r * 2.3);
      ctx.lineTo(x - r * 0.62, y + r * 0.62);
      ctx.lineTo(x - r * 2.3, y);
      ctx.lineTo(x - r * 0.62, y - r * 0.62);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    function drawWave(t, baseY, amp, freq, speed, strokeStyle, lineWidth, fillAlpha) {
      ctx.save();
      ctx.beginPath();
      const step = Math.max(8, Math.round(width / 96));
      for (let x = 0; x <= width + step; x += step) {
        const nx = x / width;
        const envelope = Math.sin(nx * Math.PI);
        const focusBoost = 1 + 0.45 * Math.exp(-Math.pow((nx - pointerX) * 3.4, 2));
        const y =
          baseY +
          Math.sin(nx * Math.PI * freq + t * speed) * amp * envelope * focusBoost +
          Math.sin(nx * Math.PI * (freq * 1.9) - t * speed * 1.35) * (amp * 0.36) * envelope;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = strokeStyle;
      ctx.lineWidth = lineWidth;
      ctx.stroke();

      if (fillAlpha > 0) {
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        const grad = ctx.createLinearGradient(0, baseY - amp * 2, 0, height);
        grad.addColorStop(0, `rgba(230, 200, 138, ${fillAlpha})`);
        grad.addColorStop(1, 'rgba(7, 12, 18, 0)');
        ctx.fillStyle = grad;
        ctx.fill();
      }
      ctx.restore();
    }

    function drawFrame(now) {
      const t = now * 0.001;
      ctx.clearRect(0, 0, width, height);

      // Resonance frequency waves along lower hero horizon
      const horizon = height * 0.84;
      drawWave(t, horizon, 16, 3.2, 0.9, 'rgba(230, 200, 138, 0.42)', 1.5, 0.075);
      drawWave(t + 1.4, horizon + 6, 11, 4.6, -0.72, 'rgba(103, 212, 255, 0.34)', 1.1, 0);
      drawWave(t + 2.8, horizon - 5, 7, 6.2, 1.15, 'rgba(246, 225, 180, 0.2)', 0.9, 0);

      // Subtle rising stardust & 4-point Astrite glints
      for (const p of particles) {
        if (!prefersReduced) {
          p.y -= p.vy;
          p.x += p.vx + Math.sin(t * 0.7 + p.phase) * 0.00008;
          if (p.y < -0.05) {
            p.y = 1.05;
            p.x = Math.random();
          }
          if (p.x < -0.02) p.x = 1.02;
          if (p.x > 1.02) p.x = -0.02;
        }
        const px = p.x * width;
        const py = p.y * height;
        const twinkle = 0.28 + 0.52 * (0.5 + 0.5 * Math.sin(t * 2.1 + p.phase));
        const color = p.gold ? '#f4dca8' : '#7ae0ff';
        if (p.star) {
          drawDiamondStar(px, py, p.size, twinkle * 0.82, color);
        } else {
          ctx.save();
          ctx.globalAlpha = twinkle * 0.65;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(px, py, p.size, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }
      }
    }

    function loop(now) {
      if (!heroVisible || document.hidden) {
        rafId = 0;
        return;
      }
      drawFrame(now);
      rafId = requestAnimationFrame(loop);
    }

    function start() {
      if (prefersReduced || rafId || !heroVisible || document.hidden) return;
      rafId = requestAnimationFrame(loop);
    }

    function stop() {
      if (rafId) {
        cancelAnimationFrame(rafId);
        rafId = 0;
      }
    }

    resize();
    window.addEventListener('resize', resize, { passive: true });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stop();
      else start();
    });

    if ('IntersectionObserver' in window) {
      const heroObs = new IntersectionObserver(
        (entries) => {
          heroVisible = entries[0]?.isIntersecting ?? true;
          if (heroVisible) start();
          else stop();
        },
        { threshold: 0.02 }
      );
      heroObs.observe(hero);
    }

    if (!prefersReduced) {
      start();
      hero.addEventListener(
        'pointermove',
        (ev) => {
          const rect = hero.getBoundingClientRect();
          const rx = (ev.clientX - rect.left) / rect.width;
          const ry = (ev.clientY - rect.top) / rect.height;
          pointerX = rx;
          hero.style.setProperty('--px', `${((rx - 0.5) * -14).toFixed(1)}px`);
          hero.style.setProperty('--py', `${((ry - 0.5) * -10).toFixed(1)}px`);
        },
        { passive: true }
      );
      hero.addEventListener('pointerleave', () => {
        pointerX = 0.5;
        hero.style.setProperty('--px', '0px');
        hero.style.setProperty('--py', '0px');
      });
    }
  }

  /* ------------------------------------------------------------------------
     2. Delegated Spotlight Hover Glow on .spotlight-card
     ------------------------------------------------------------------------ */
  if (!prefersReduced) {
    document.addEventListener(
      'pointermove',
      (ev) => {
        const card = ev.target && ev.target.closest ? ev.target.closest('.spotlight-card') : null;
        if (!card) return;
        const rect = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${(ev.clientX - rect.left).toFixed(1)}px`);
        card.style.setProperty('--my', `${(ev.clientY - rect.top).toFixed(1)}px`);
      },
      { passive: true }
    );
  }

  /* ------------------------------------------------------------------------
     3. Reading Progress Gold Line & Nav Scroll Spy
     ------------------------------------------------------------------------ */
  const progressBar = document.querySelector('#scroll-progress-bar');
  const navLinks = [...document.querySelectorAll('.main-nav a[data-nav]')];
  const sections = navLinks
    .map((link) => ({ link, el: document.getElementById(link.dataset.nav) }))
    .filter((entry) => entry.el);

  let scrollTicking = false;
  function updateScrollUI() {
    scrollTicking = false;
    const docEl = document.documentElement;
    const maxScroll = Math.max(1, docEl.scrollHeight - window.innerHeight);
    const ratio = Math.min(1, Math.max(0, window.scrollY / maxScroll));
    if (progressBar) {
      progressBar.style.transform = `scaleX(${ratio.toFixed(4)})`;
    }

    const probe = window.scrollY + 140;
    let activeId = null;
    for (const { el } of sections) {
      if (el.offsetTop <= probe) activeId = el.id;
    }
    for (const { link, el } of sections) {
      link.classList.toggle('is-active', el.id === activeId);
    }
  }

  window.addEventListener(
    'scroll',
    () => {
      if (!scrollTicking) {
        scrollTicking = true;
        requestAnimationFrame(updateScrollUI);
      }
    },
    { passive: true }
  );
  updateScrollUI();

  /* ------------------------------------------------------------------------
     4. Scroll Reveal & Count-Up Numbers
     ------------------------------------------------------------------------ */
  const reveals = [...document.querySelectorAll('.reveal')];
  if (prefersReduced || !('IntersectionObserver' in window)) {
    for (const el of reveals) el.classList.add('is-visible');
  } else {
    const revObs = new IntersectionObserver(
      (entries, obs) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            obs.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.01, rootMargin: '0px 0px 120px 0px' }
    );
    for (const el of reveals) revObs.observe(el);
  }

  const counters = [...document.querySelectorAll('[data-count-to]')];
  if (!prefersReduced && counters.length && 'IntersectionObserver' in window) {
    const countObs = new IntersectionObserver(
      (entries, obs) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          const el = entry.target;
          const target = Number(el.dataset.countTo || 0);
          if (!Number.isFinite(target) || target <= 0) {
            obs.unobserve(el);
            continue;
          }
          const duration = 760;
          const t0 = performance.now();
          const tick = (now) => {
            const p = Math.min(1, (now - t0) / duration);
            const eased = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(target * eased).toLocaleString('en-US');
            if (p < 1) requestAnimationFrame(tick);
            else el.textContent = target.toLocaleString('en-US');
          };
          requestAnimationFrame(tick);
          obs.unobserve(el);
        }
      },
      { threshold: 0.35 }
    );
    for (const el of counters) countObs.observe(el);
  }
})();
