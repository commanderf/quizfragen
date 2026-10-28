(() => {
  'use strict';
  const APP_VERSION = '2026-10-28.4';
  const SEEN_KEY = 'zrVersion';
  const DISMISS_KEY = 'zrUpdateDismissed';
  const banner = document.getElementById('updateBanner');
  const btn = document.getElementById('updateNowBtn');
  const later = document.getElementById('updateLaterBtn');
  if (!banner || !btn || !later) return;
  let current = '';
  let visible = false;

  try {
    localStorage.setItem(SEEN_KEY, APP_VERSION);
  } catch {}

  function show() {
    try {
      if (localStorage.getItem(DISMISS_KEY) === current) return;
    } catch {}
    if (!visible) {
      visible = true;
      banner.hidden = false;
    }
  }

  function hide() {
    visible = false;
    banner.hidden = true;
  }

  async function clearCaches() {
    try {
      if ('caches' in window) {
        const keys = await caches.keys();
        await Promise.all(keys.map(k => caches.delete(k)));
      }
    } catch {}
  }

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    later.disabled = true;
    btn.textContent = 'Wird aktualisiert …';
    try {
      localStorage.setItem(DISMISS_KEY, '');
      localStorage.setItem(SEEN_KEY, current);
    } catch {}
    try {
      if ('serviceWorker' in navigator) {
        const reg = await navigator.serviceWorker.getRegistration();
        if (reg && reg.waiting) {
          navigator.serviceWorker.addEventListener('controllerchange', () => location.reload(), {once: true});
          reg.waiting.postMessage({type: 'SKIP_WAITING'});
          setTimeout(() => clearCaches().then(() => location.reload()), 1500);
          return;
        }
      }
    } catch {}
    await clearCaches();
    location.reload();
  });

  later.addEventListener('click', () => {
    try {
      localStorage.setItem(DISMISS_KEY, current);
    } catch {}
    hide();
  });

  async function check() {
    try {
      const res = await fetch(new URL('version.json', document.baseURI), {cache: 'no-store'});
      if (!res.ok) return;
      const data = await res.json();
      if (data.version && data.version !== APP_VERSION) {
        current = data.version;
        show();
      } else {
        current = '';
        hide();
      }
    } catch {}
  }

  check();
  setInterval(check, 2 * 60 * 1000);
})();
