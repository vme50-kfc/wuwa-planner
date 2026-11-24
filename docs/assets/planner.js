(() => {
  /* ========================================================================
     1. 22-Team Interactive Rotation Deck
     ======================================================================== */
  const search = document.querySelector('#team-search');
  const groupButtons = [...document.querySelectorAll('[data-filter]')];
  const elementButtons = [...document.querySelectorAll('[data-el-filter]')];
  const links = [...document.querySelectorAll('[data-team]')];
  const panels = new Map(
    links.map((link) => [link.dataset.team, document.querySelector(link.getAttribute('href'))])
  );
  const empty = document.querySelector('.no-result');
  const matchCountEl = document.querySelector('#team-match-count');
  const clearBtn = document.querySelector('#clear-team-filters');

  let group = 'all';
  let element = 'all';
  let activeTeam = links[0]?.dataset.team || '01';

  function requestedTeam() {
    const m = location.hash.match(/^#team-(\d{2}|P\d+)$/i);
    if (!m) return null;
    const raw = m[1];
    return raw.toUpperCase();
  }

  function setGroup(next) {
    group = next;
    for (const btn of groupButtons) {
      btn.setAttribute('aria-pressed', String(btn.dataset.filter === group));
    }
  }

  function setElement(next) {
    element = next;
    for (const btn of elementButtons) {
      btn.setAttribute('aria-pressed', String(btn.dataset.elFilter === element));
    }
  }

  function updateTeams(keepSelected = true) {
    const query = (search?.value || '').trim().toLowerCase();
    const numeric = /^\d{1,2}$/.test(query) ? query.padStart(2, '0') : null;
    const plannedCode = /^p\d+$/i.test(query) ? query.toUpperCase() : null;

    const matches = links.filter((link) => {
      const okGroup = group === 'all' || group === link.dataset.group;
      const okElement = element === 'all' || element === link.dataset.element;
      let okQuery = true;
      if (numeric) okQuery = link.dataset.team === numeric;
      else if (plannedCode) okQuery = link.dataset.team === plannedCode;
      else if (query) okQuery = (link.dataset.search || '').toLowerCase().includes(query);
      return okGroup && okElement && okQuery;
    });

    const preferred = requestedTeam() || activeTeam;
    const nextActive =
      keepSelected && matches.some((link) => link.dataset.team === preferred)
        ? preferred
        : matches[0]?.dataset.team || null;

    if (nextActive) activeTeam = nextActive;

    for (const link of links) {
      const visible = matches.includes(link);
      const selected = link.dataset.team === nextActive;
      link.hidden = !visible;
      if (selected) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
      const panel = panels.get(link.dataset.team);
      if (panel) panel.hidden = !selected;
    }

    if (empty) empty.hidden = matches.length > 0;
    if (matchCountEl) {
      matchCountEl.textContent =
        matches.length === links.length
          ? `共 ${links.length} 支队伍`
          : `筛选出 ${matches.length} / ${links.length} 支队伍`;
    }
    if (clearBtn) {
      const hasFilter = group !== 'all' || element !== 'all' || query.length > 0;
      clearBtn.hidden = !hasFilter;
    }
  }

  function selectTeam(teamId, scrollToPanel = false) {
    if (!panels.has(teamId)) return;
    const link = links.find((c) => c.dataset.team === teamId);
    if (link && link.hidden) {
      setGroup('all');
      setElement('all');
      if (search) search.value = '';
    }
    activeTeam = teamId;
    if (location.hash !== `#team-${teamId}`) {
      history.replaceState(null, '', `#team-${teamId}`);
    }
    updateTeams(true);
    if (link) link.scrollIntoView({ block: 'nearest' });
    if (scrollToPanel) {
      const panel = panels.get(teamId);
      panel?.focus({ preventScroll: true });
      panel?.scrollIntoView({ block: 'start' });
    }
  }

  function followTeamHash(scroll = true) {
    const target = requestedTeam();
    if (!target || !panels.has(target)) return;
    selectTeam(target, scroll);
  }

  const filtersWrap = document.querySelector('.filters');
  if (filtersWrap) filtersWrap.hidden = false;

  search?.addEventListener('input', () => updateTeams(true));

  for (const btn of groupButtons) {
    btn.addEventListener('click', () => {
      setGroup(btn.dataset.filter);
      updateTeams(true);
    });
  }

  for (const btn of elementButtons) {
    btn.addEventListener('click', () => {
      setElement(btn.dataset.elFilter);
      updateTeams(true);
    });
  }

  clearBtn?.addEventListener('click', () => {
    setGroup('all');
    setElement('all');
    if (search) search.value = '';
    updateTeams(true);
  });

  const stackedTeams = window.matchMedia('(max-width: 860px)');
  for (const link of links) {
    link.addEventListener('click', (ev) => {
      ev.preventDefault();
      selectTeam(link.dataset.team, stackedTeams.matches);
    });
  }

  // Intercept external jump chips (Tower 1+3+5 bar, Build cards, Inline team refs, Overview target)
  document.addEventListener('click', (ev) => {
    const anchor = ev.target && ev.target.closest ? ev.target.closest('a[href^="#team-"]') : null;
    if (anchor && !anchor.classList.contains('team-link')) {
      const m = anchor.getAttribute('href').match(/^#team-(\d{2}|P\d+)$/i);
      if (m && panels.has(m[1].toUpperCase())) {
        ev.preventDefault();
        selectTeam(m[1].toUpperCase(), true);
        return;
      }
    }

    const sharedBtn = ev.target && ev.target.closest ? ev.target.closest('[data-quick-search]') : null;
    if (sharedBtn && search) {
      setGroup('all');
      setElement('all');
      search.value = sharedBtn.dataset.quickSearch || '';
      updateTeams(true);
      search.focus();
    }
  });

  // Keyboard shortcuts: "/" to search, ArrowUp/ArrowDown to step through teams
  document.addEventListener('keydown', (ev) => {
    const tag = document.activeElement?.tagName;
    const isTyping = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';

    if (ev.key === '/' && !isTyping && !ev.ctrlKey && !ev.metaKey && !ev.altKey) {
      ev.preventDefault();
      search?.focus();
      search?.select();
      return;
    }

    if (ev.key === 'Escape' && document.activeElement === search && search.value) {
      search.value = '';
      updateTeams(true);
      return;
    }

    if ((ev.key === 'ArrowDown' || ev.key === 'ArrowUp') && (!isTyping || document.activeElement === search)) {
      const visible = links.filter((l) => !l.hidden);
      if (visible.length <= 1) return;
      const idx = visible.findIndex((l) => l.dataset.team === activeTeam);
      const step = ev.key === 'ArrowDown' ? 1 : -1;
      const next = visible[(idx + step + visible.length) % visible.length];
      if (next && (document.activeElement === search || ev.target.closest('.team-layout'))) {
        ev.preventDefault();
        selectTeam(next.dataset.team, false);
      }
    }
  });

  window.addEventListener('hashchange', () => followTeamHash(true));
  updateTeams(true);
  followTeamHash(false);

  /* ========================================================================
     2. Weekly Build Execution Checklist (localStorage persisted)
     ======================================================================== */
  const CHECK_KEY = 'wuwa-checklist-v1';
  const checkboxes = [...document.querySelectorAll('input[data-check-id]')];
  const checkCountEl = document.querySelector('#checklist-count');
  const checkPctEl = document.querySelector('#checklist-pct');
  const checkBarEl = document.querySelector('#checklist-bar');
  const checkResetBtn = document.querySelector('#checklist-reset');

  function loadChecklist() {
    try {
      const raw = localStorage.getItem(CHECK_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch {
      return {};
    }
  }

  function saveChecklist(state) {
    try {
      localStorage.setItem(CHECK_KEY, JSON.stringify(state));
    } catch {
      // Ignore storage errors in private mode.
    }
  }

  function renderChecklistStats() {
    const total = checkboxes.length;
    const done = checkboxes.filter((cb) => cb.checked).length;
    const pct = total ? Math.round((done / total) * 100) : 0;
    if (checkCountEl) checkCountEl.textContent = `${done} / ${total}`;
    if (checkPctEl) checkPctEl.textContent = `${pct}%`;
    if (checkBarEl) checkBarEl.style.width = `${pct}%`;
  }

  if (checkboxes.length) {
    const savedChecks = loadChecklist();
    for (const cb of checkboxes) {
      cb.checked = Boolean(savedChecks[cb.dataset.checkId]);
      cb.addEventListener('change', () => {
        savedChecks[cb.dataset.checkId] = cb.checked;
        saveChecklist(savedChecks);
        renderChecklistStats();
      });
    }
    checkResetBtn?.addEventListener('click', () => {
      for (const cb of checkboxes) {
        cb.checked = false;
        delete savedChecks[cb.dataset.checkId];
      }
      saveChecklist(savedChecks);
      renderChecklistStats();
    });
    renderChecklistStats();
  }

  /* ========================================================================
     3. Live Suoming Convene Budget Calculator
     ======================================================================== */
  const CALC_KEY = 'wuwa-convene-v1';
  const snapScript = document.querySelector('#snapshot-data');
  const snapshot = snapScript ? JSON.parse(snapScript.textContent) : {
    astrite: 150,
    lunite: 5738,
    radiant: 0,
    forging: 5,
    charPity: 5,
    weapPity: 19,
    guaranteed: false,
    afterglow: 28,
  };

  const defaults = {
    target: 'c0',
    astrite: snapshot.astrite,
    lunite: snapshot.lunite,
    radiant: snapshot.radiant,
    forging: snapshot.forging,
    charPity: snapshot.charPity,
    weapPity: snapshot.weapPity,
    coral: snapshot.afterglow,
    guarantee: snapshot.guaranteed ? 'guaranteed' : '5050',
    useLunite: true,
    useCoral: false,
  };

  const calcEl = document.querySelector('#convene-calc');
  if (calcEl) {
    const targetBtns = [...calcEl.querySelectorAll('[data-calc-target]')];
    const inAstrite = calcEl.querySelector('#in-astrite');
    const inLunite = calcEl.querySelector('#in-lunite');
    const inRadiant = calcEl.querySelector('#in-radiant');
    const inForging = calcEl.querySelector('#in-forging');
    const inCharPity = calcEl.querySelector('#in-char-pity');
    const inWeapPity = calcEl.querySelector('#in-weap-pity');
    const inCoral = calcEl.querySelector('#in-coral');
    const inGuarantee = calcEl.querySelector('#in-guarantee');
    const optLunite = calcEl.querySelector('#opt-lunite');
    const optCoral = calcEl.querySelector('#opt-coral');
    const coralPreview = calcEl.querySelector('#coral-pulls-preview');
    const savedBadge = calcEl.querySelector('#calc-saved-state');
    const resetBtn = calcEl.querySelector('#calc-reset');

    const ringEl = calcEl.querySelector('#calc-ring');
    const pctEl = calcEl.querySelector('#calc-pct');
    const labelEl = calcEl.querySelector('#calc-target-label');
    const deficitEl = calcEl.querySelector('#calc-deficit');
    const needPullsEl = calcEl.querySelector('#calc-need-pulls');
    const totalPullsEl = calcEl.querySelector('#calc-total-pulls');
    const noteEl = calcEl.querySelector('#calc-status-note');

    const CIRCUMFERENCE = 2 * Math.PI * 56;
    let state = { ...defaults };

    try {
      const raw = localStorage.getItem(CALC_KEY);
      if (raw) {
        state = { ...defaults, ...JSON.parse(raw) };
      }
    } catch {
      // Fallback to snapshot defaults.
    }

    function clampInt(val, min, max = 9999999) {
      const n = Math.floor(Number(val));
      if (!Number.isFinite(n)) return min;
      return Math.min(max, Math.max(min, n));
    }

    function syncInputsFromState() {
      inAstrite.value = state.astrite;
      inLunite.value = state.lunite;
      inRadiant.value = state.radiant;
      inForging.value = state.forging;
      inCharPity.value = state.charPity;
      inWeapPity.value = state.weapPity;
      inCoral.value = state.coral;
      inGuarantee.value = state.guarantee;
      optLunite.checked = Boolean(state.useLunite);
      optCoral.checked = Boolean(state.useCoral);
      for (const btn of targetBtns) {
        btn.setAttribute('aria-pressed', String(btn.dataset.calcTarget === state.target));
      }
    }

    function readInputsToState() {
      state.astrite = clampInt(inAstrite.value, 0);
      state.lunite = clampInt(inLunite.value, 0);
      state.radiant = clampInt(inRadiant.value, 0);
      state.forging = clampInt(inForging.value, 0);
      state.charPity = clampInt(inCharPity.value, 0, 79);
      state.weapPity = clampInt(inWeapPity.value, 0, 79);
      state.coral = clampInt(inCoral.value, 0);
      state.guarantee = inGuarantee.value === 'guaranteed' ? 'guaranteed' : '5050';
      state.useLunite = optLunite.checked;
      state.useCoral = optCoral.checked;
    }

    function isDefaultState() {
      return Object.keys(defaults).every((k) => state[k] === defaults[k]);
    }

    function computeAndRender(persist = false) {
      const charCap = state.target === 'next5' ? 80 : (state.guarantee === 'guaranteed' ? 80 : 160);
      const charNeedPulls = Math.max(0, charCap - state.charPity - state.radiant);
      const weapNeedPulls = state.target === 'c0r1' ? Math.max(0, 80 - state.weapPity - state.forging) : 0;

      const totalPullsAfterTides = charNeedPulls + weapNeedPulls;
      const totalAstriteNeed = totalPullsAfterTides * 160;
      const coralPulls = Math.floor(state.coral / 8);
      if (coralPreview) coralPreview.textContent = String(coralPulls);

      const walletAstrite =
        state.astrite +
        (state.useLunite ? state.lunite : 0) +
        (state.useCoral ? coralPulls * 160 : 0);

      const deficit = Math.max(0, totalAstriteNeed - walletAstrite);
      const needPulls = Math.ceil(deficit / 160);
      const readyPct =
        totalAstriteNeed === 0
          ? 100
          : Math.min(100, Math.max(0, Math.round(((totalAstriteNeed - deficit) / totalAstriteNeed) * 100)));

      const targetTitles = {
        c0: '锁暝 0 链 · 最坏情况还差',
        c0r1: '锁暝 0 链 + 专武沉冥 · 最坏情况还差',
        next5: '角色池下一次五星 · 最坏情况还差',
      };

      if (labelEl) labelEl.textContent = targetTitles[state.target] || targetTitles.c0;
      if (deficitEl) deficitEl.textContent = deficit.toLocaleString('en-US');
      if (needPullsEl) needPullsEl.textContent = String(needPulls);
      if (totalPullsEl) totalPullsEl.textContent = String(totalPullsAfterTides);
      if (pctEl) pctEl.textContent = `${readyPct}%`;

      if (ringEl) {
        const offset = CIRCUMFERENCE * (1 - readyPct / 100);
        ringEl.style.strokeDasharray = `${CIRCUMFERENCE.toFixed(2)}`;
        ringEl.style.strokeDashoffset = `${offset.toFixed(2)}`;
        ringEl.style.stroke = deficit === 0 ? 'var(--el-aero)' : 'var(--gold)';
      }

      if (noteEl) {
        if (deficit === 0) {
          const surplus = walletAstrite - totalAstriteNeed;
          noteEl.textContent = `当前库存已稳保目标！最坏情况下还可结余 ${surplus.toLocaleString('en-US')} 星声（约 ${Math.floor(surplus / 160)} 抽）。`;
        } else {
          const extras = [];
          if (state.useLunite) extras.push('月相');
          if (state.useCoral) extras.push(`珊瑚换 ${coralPulls} 抽`);
          const includeText = extras.length ? `已计入星声与${extras.join('、')}` : '仅计入现有星声与波纹';
          noteEl.textContent = `${includeText}；按每抽 160 星声最坏保底折算。`;
        }
      }

      if (savedBadge) {
        savedBadge.textContent = isDefaultState() ? '2026.11.24 基准快照' : '已自动保存自定义试算';
      }

      if (persist) {
        try {
          localStorage.setItem(CALC_KEY, JSON.stringify(state));
        } catch {
          // Ignore storage errors.
        }
      }
    }

    for (const btn of targetBtns) {
      btn.addEventListener('click', () => {
        state.target = btn.dataset.calcTarget;
        syncInputsFromState();
        computeAndRender(true);
      });
    }

    for (const ctrl of [inAstrite, inLunite, inRadiant, inForging, inCharPity, inWeapPity, inCoral, inGuarantee, optLunite, optCoral]) {
      ctrl.addEventListener('input', () => {
        readInputsToState();
        computeAndRender(true);
      });
      ctrl.addEventListener('change', () => {
        readInputsToState();
        computeAndRender(true);
      });
    }

    resetBtn?.addEventListener('click', () => {
      state = { ...defaults };
      syncInputsFromState();
      try {
        localStorage.removeItem(CALC_KEY);
      } catch {
        // Ignore storage errors.
      }
      computeAndRender(false);
    });

    syncInputsFromState();
    computeAndRender(false);
  }
})();
