#!/usr/bin/env python3
"""Baut site/ aus app/ für GitHub Pages (PWA: manifest, sw, icons, pwa-bar)."""
import hashlib, json, pathlib, re, shutil, struct, zlib

ROOT = pathlib.Path(__file__).resolve().parent
APP = ROOT / "app"
SITE = ROOT / "site"

PWA_JS = """(() => {
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
      const msg = (error && (error.message || error.reason)) ? (error.message || error.reason) : String(error);
      setStatus('Offline-Speicher nicht verfügbar: ' + msg);
      console.warn('Service Worker:', error);
      setTimeout(() => {
        navigator.serviceWorker.register('./sw.js', {scope: './', updateViaCache: 'none'})
          .then(() => networkStatus().catch(() => setStatus('Offline bereit')))
          .catch(() => {});
      }, 4000);
    });
})();
"""

SW_JS = """'use strict';
const VERSION = '__VERSION__';
const PREFIX = 'zeitreise-' + encodeURIComponent(self.registration.scope) + '-';
const CACHE = PREFIX + VERSION;
const FILES = '__FILES__';
const URLS = new Set(FILES.map(path => new URL(path, self.registration.scope).href));
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES.map(path => new Request(new URL(path, self.registration.scope), {cache: 'reload'}))).then(() => self.skipWaiting())));
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) {
      if (name.startsWith(PREFIX) && name !== CACHE) await caches.delete(name);
    }
    await self.clients.claim();
  })());
});
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  url.search = ''; url.hash = '';
  if (!URLS.has(url.href)) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    return (await cache.match(url.href)) || fetch(event.request);
  })());
});
"""

FILES = ['./', './index.html', './styles.css', './app.js', './questions.js',
         './pwa.js', './update.js', './version.json', './cache-version.js',
         './manifest.webmanifest', './icons/icon.svg', './icons/icon-192.png',
         './icons/icon-512.png', './icons/apple-touch-icon.png']

def build():
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "icons").mkdir(parents=True)

    html = (APP / "index.html").read_text(encoding="utf-8")
    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        '  <link rel="stylesheet" href="./styles.css">\n'
        '  <link rel="manifest" href="./manifest.webmanifest">\n'
        '  <link rel="icon" href="./icons/icon.svg" type="image/svg+xml">\n'
        '  <link rel="apple-touch-icon" href="./icons/apple-touch-icon.png">\n'
        '  <meta name="apple-mobile-web-app-capable" content="yes">\n'
        '  <meta name="apple-mobile-web-app-title" content="Zeitreise">', 1)
    html = html.replace(
        '  <main id="app"',
        '  <aside class="pwa-bar" aria-label="App und Offline-Status"><span id="offlineStatus" role="status">Offline-Speicher wird vorbereitet …</span><button id="installBtn" type="button">Als App installieren</button><button id="updateBtn" type="button" hidden>Update laden</button></aside>\n  <main id="app"', 1)
    html = html.replace(
        '  <script src="app.js"></script>',
        '  <script src="app.js"></script>\n  <script src="./cache-version.js"></script>\n  <script src="./pwa.js"></script>', 1)
    (SITE / "index.html").write_text(html, encoding="utf-8")

    for name in ["styles.css", "app.js", "questions.js", "update.js", "version.json"]:
        shutil.copy2(APP / name, SITE / name)

    (SITE / "pwa.js").write_text(PWA_JS, encoding="utf-8")

    icons = SITE / "icons"
    glyphs = {'Z': ['11111', '00001', '00010', '00100', '01000', '10000', '11111'],
              'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001']}
    def png(size):
        def chunk(name, data):
            return struct.pack('!I', len(data)) + name + data + struct.pack('!I', zlib.crc32(name + data) & 0xffffffff)
        rows = []
        for y in range(size):
            row = bytearray()
            for x in range(size):
                ux, uy = x / size, y / size
                color = (20, 40, 35)
                if .12 <= ux < .88 and .12 <= uy < .88:
                    color = (237, 107, 53) if uy < .4 else ((245, 187, 67) if uy < .6 else (29, 133, 128))
                gx = int((ux - .225) / .05)
                gy = int((uy - .325) / .05)
                if 0 <= gy < 7:
                    if 0 <= gx < 5 and glyphs['Z'][gy][gx] == '1': color = (255, 250, 240)
                    if 6 <= gx < 11 and glyphs['R'][gy][gx - 6] == '1': color = (255, 250, 240)
                row.extend(color)
            rows.append(b'\x00' + row)
        return (b'\x89PNG\r\n\x1a\n'
                + chunk(b'IHDR', struct.pack('!IIBBBBB', size, size, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(b''.join(rows), 9))
                + chunk(b'IEND', b''))
    for size, filename in [(192, 'icon-192.png'), (512, 'icon-512.png'), (180, 'apple-touch-icon.png')]:
        (icons / filename).write_bytes(png(size))
    (icons / 'icon.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<rect width="512" height="512" fill="#142823"/>'
        '<path d="M62 62h388v143H62z" fill="#ed6b35"/>'
        '<path d="M62 205h388v102H62z" fill="#f5bb43"/>'
        '<path d="M62 307h388v143H62z" fill="#1d8580"/>'
        '<text x="256" y="329" text-anchor="middle" fill="#fffaf0" font-family="sans-serif" font-weight="900" font-size="206">ZR</text></svg>',
        encoding="utf-8")

    manifest = {
        'id': './', 'name': 'Zeitreise – Das 70er bis 00er Quiz', 'short_name': 'Zeitreise',
        'description': 'Das nostalgische Quiz mit Fragen aus den 70ern bis 00ern.',
        'lang': 'de', 'start_url': './', 'scope': './', 'display': 'standalone',
        'theme_color': '#f4b942', 'background_color': '#f4eddf',
        'icons': [
            {'src': './icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': './icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'},
        ],
    }
    (SITE / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    digest = hashlib.sha256(''.join(
        f"{p.name}{hashlib.sha256(p.read_bytes()).hexdigest()}"
        for p in sorted(SITE.rglob('*')) if p.is_file()
    ).encode()).hexdigest()[:16]
    (SITE / 'cache-version.js').write_text(
        "window.ZEITREISE_CACHE = 'zeitreise-' + encodeURIComponent(new URL('./', document.baseURI).href) + '-" + digest + "';\n",
        encoding="utf-8")
    (SITE / 'sw.js').write_text(
        SW_JS.replace('__FILES__', json.dumps(FILES)).replace('__VERSION__', digest),
        encoding="utf-8")
    (SITE / '.nojekyll').touch()
    print("site/ gebaut. SW-Version:", digest)

if __name__ == "__main__":
    build()
