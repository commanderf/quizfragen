(() => {
  'use strict';
  const status = document.getElementById('offlineStatus');
  const installButton = document.getElementById('installBtn');
  const updateButton = document.getElementById('updateBtn');
  let installPrompt = null;
  let registration = null;
  let updating = false;
  const standalone = () => matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  function setStatus(text) { status.textContent = text; }
  function installVisibility() { installButton.hidden = standalone(); }
  installVisibility();
  matchMedia('(display-mode: standalone)').addEventListener('change', installVisibility);
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault(); installPrompt = event; installVisibility();
  });
  window.addEventListener('appinstalled', () => {
    installPrompt = null; installButton.hidden = true;
  });
  installButton.addEventListener('click', async () => {
    if (installPrompt) {
      try { await installPrompt.prompt(); await installPrompt.userChoice; }
      catch (error) { console.warn('App-Installation:', error); }
      installPrompt = null;
    } else {
      const ios = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
      alert(ios ? 'In Safari: Teilen → Zum Home-Bildschirm → Hinzufügen. Falls der Link in einer anderen App geöffnet wurde, zuerst in Safari öffnen.' : 'Im Browsermenü nach „App installieren" oder „Zum Startbildschirm hinzufügen" suchen. Nicht jeder Browser bietet eine Installation an. Das Quiz funktioniert auch ohne Installation.');
    }
  });
  updateButton.addEventListener('click', () => {
    if (!registration?.waiting) return;
    if (document.getElementById('quizView').classList.contains('active') && !confirm('Die Aktualisierung beendet die aktuelle Runde. Jetzt aktualisieren?')) return;
    updating = true;
    registration.waiting.postMessage({type: 'SKIP_WAITING'});
  });
  if (!('serviceWorker' in navigator) || !window.isSecureContext) {
    setStatus('Offline-Speicher benötigt HTTPS oder localhost'); return;
  }
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (updating) location.reload();
    else setStatus(navigator.onLine ? 'Offline bereit' : 'Offline · spielbereit');
  });
  async function networkStatus() {
    const ready = await caches.has(window.ZEITREISE_CACHE);
    setStatus(ready ? (navigator.onLine ? 'Offline bereit' : 'Offline · spielbereit') : (navigator.onLine ? 'Offline-Speicher wird vorbereitet …' : 'Offline-Speicher noch nicht bereit'));
  }
  addEventListener('online', () => networkStatus().catch(() => setStatus('Online')));
  addEventListener('offline', () => networkStatus().catch(() => setStatus('Offline')));
  function watchUpdate() {
    if (registration.waiting) registration.waiting.postMessage({type: 'SKIP_WAITING'});
    if (registration.waiting && navigator.serviceWorker.controller) updateButton.hidden = false;
  }
  let hadController = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (hadController) { location.reload(); return; }
    hadController = true;
    setStatus(navigator.onLine ? 'Offline bereit' : 'Offline · spielbereit');
  });
  navigator.serviceWorker.register('./sw.js', {scope: './', updateViaCache: 'none'})
    .then(reg => {
      registration = reg; watchUpdate();
      reg.addEventListener('updatefound', () => {
        const worker = reg.installing;
        worker?.addEventListener('statechange', () => {
          if (worker.state === 'installed') {
            watchUpdate();
            networkStatus().catch(() => {});
          }
        });
      });
      navigator.serviceWorker.ready.then(() => networkStatus()).catch(() => {});
      networkStatus().catch(() => {});
    })
    .catch(error => {
      setStatus('Offline-Speicher nicht verfügbar'); console.warn('Service Worker:', error);
    });
})();
