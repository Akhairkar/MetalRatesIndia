const CACHE_NAME = 'mri-cache-v1';
const SHELL_ASSETS = [
  './',
  './index.html',
  './css/styles.css',
  './js/script.js',
  './js/charts.js',
  './data/metals.json',
  './data/goldsilver.json',
  './manifest.json',
  './offline.html'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Network-first for JSON data so rates stay fresh, falling back to cache offline
  if(req.url.includes('/data/') && req.url.endsWith('.json')){
    event.respondWith(
      fetch(req).then((res) => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
        return res;
      }).catch(() => caches.match(req))
    );
    return;
  }

  // Cache-first for shell assets, network fallback, offline page for navigations
  event.respondWith(
    caches.match(req).then((cached) => {
      return cached || fetch(req).then((res) => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
        return res;
      }).catch(() => {
        if(req.mode === 'navigate') return caches.match('./offline.html');
      });
    })
  );
});
