'use strict';
const VERSION = '022051cb75040d8c';
const PREFIX = 'zeitreise-' + encodeURIComponent(self.registration.scope) + '-';
const CACHE = PREFIX + VERSION;
const FILES = '["./", "./index.html", "./styles.css", "./app.js", "./questions.js", "./pwa.js", "./update.js", "./version.json", "./cache-version.js", "./manifest.webmanifest", "./icons/icon.svg", "./icons/icon-192.png", "./icons/icon-512.png", "./icons/apple-touch-icon.png"]';
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
