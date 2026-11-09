/* Pages and data: network first, so updates arrive at once and the cache is the offline fallback.
   Photos and fine borders never change: cache first, kept as they are viewed. Online map tiles are left alone. */
const CACHE = 'fernweh-v9';
const SHELL = ['fernweh.html', 'data/cities.js?v=6', 'data/photos.js?v=4', 'manifest.webmanifest', 'icons/icon-192.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  const store = res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return res;
  };
  if (url.pathname.includes('/png/') || url.pathname.includes('/data/geo/')) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(store)));
    return;
  }
  e.respondWith(fetch(e.request).then(store).catch(() => caches.match(e.request)
    .then(hit => hit || (e.request.mode === 'navigate' ? caches.match('fernweh.html') : Response.error()))));
});
