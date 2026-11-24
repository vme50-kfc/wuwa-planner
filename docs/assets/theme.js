(() => {
  const key = 'wuwa-theme';
  const valid = ['system', 'light', 'dark'];
  let theme = 'system';

  try {
    const saved = localStorage.getItem(key);
    if (valid.includes(saved)) theme = saved;
  } catch {
    // The picker still works for this page if storage is unavailable.
  }

  function apply() {
    document.documentElement.dataset.theme = theme;
  }

  apply();
  document.addEventListener('DOMContentLoaded', () => {
    const picker = document.querySelector('#theme');
    picker.value = theme;
    picker.closest('.theme-control').hidden = false;
    picker.addEventListener('change', () => {
      theme = picker.value;
      apply();
      try {
        localStorage.setItem(key, theme);
      } catch {
        // Keep the selected theme for the current page.
      }
    });
  });
})();
