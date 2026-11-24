(() => {
  const key = 'wuwa-theme';
  const valid = ['dark', 'light', 'system'];
  let theme = 'dark';

  try {
    const saved = localStorage.getItem(key);
    if (valid.includes(saved)) theme = saved;
  } catch {
    // Keep default dark theme when storage is unavailable.
  }

  const mql = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function resolveTheme(mode) {
    if (mode === 'system') {
      return mql && !mql.matches ? 'light' : 'dark';
    }
    return mode;
  }

  function apply() {
    const resolved = resolveTheme(theme);
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.resolvedTheme = resolved;
    document.documentElement.style.colorScheme = resolved;
    window.dispatchEvent(new CustomEvent('wuwa:themechange', { detail: { theme, resolved } }));
  }

  function syncButtons() {
    const buttons = document.querySelectorAll('[data-theme-set]');
    for (const btn of buttons) {
      btn.setAttribute('aria-pressed', String(btn.dataset.themeSet === theme));
    }
  }

  apply();

  if (mql) {
    const onMediaChange = () => {
      if (theme === 'system') apply();
    };
    if (mql.addEventListener) mql.addEventListener('change', onMediaChange);
    else if (mql.addListener) mql.addListener(onMediaChange);
  }

  document.addEventListener('DOMContentLoaded', () => {
    syncButtons();
    for (const btn of document.querySelectorAll('[data-theme-set]')) {
      btn.addEventListener('click', () => {
        const next = btn.dataset.themeSet;
        if (!valid.includes(next)) return;
        theme = next;
        apply();
        syncButtons();
        try {
          localStorage.setItem(key, theme);
        } catch {
          // Keep selected theme for current session.
        }
      });
    }
  });
})();
