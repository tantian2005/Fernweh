/* The page: network first (with a short wait), so updates arrive at once and the cache covers slow or no signal.
   Versioned data (?v=N) never changes under the same address: cache first.
   Photos and fine borders live in their own cache that updates never clear. Online map tiles are left alone. */
/* the About page shows this number as 0.N: raise APPV in fernweh.html together with it */
const CACHE = 'fernweh-v20';
const MEDIA = 'fernweh-media';
const SHELL = ['fernweh.html', 'data/core.js?v=3', 'data/rest.js?v=3', 'data/photos.js?v=8', 'manifest.webmanifest', 'icons/icon-192.png'];
/* photos come from the photo site (same origin on GitHub Pages: /fernweh-photos/png/...) */
const isMedia = url => url.pathname.includes('/png/') || url.pathname.includes('/data/geo/');

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

/* keep photos already viewed: move them out of older page caches before those are dropped */
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const media = await caches.open(MEDIA);
    for (const k of await caches.keys()) {
      if (k === CACHE || k === MEDIA) continue;
      const old = await caches.open(k);
      for (const req of await old.keys()) {
        if (isMedia(new URL(req.url)) && !(await media.match(req))) {
          const res = await old.match(req);
          if (res) await media.put(req, res);
        }
      }
      await caches.delete(k);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  const store = name => res => {
    if (res.ok) { const copy = res.clone(); caches.open(name).then(c => c.put(e.request, copy)); }
    return res;
  };
  if (isMedia(url)) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(store(MEDIA))));
    return;
  }
  if (url.searchParams.has('v')) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(store(CACHE))));
    return;
  }
  /* the page itself is checked with the server every time, so a new version shows on the next open and not ten minutes later */
  const net = (e.request.mode === 'navigate' ? fetch(url.href, { cache: 'no-cache' }) : fetch(e.request)).then(store(CACHE));
  const fallback = () => caches.match(e.request)
    .then(hit => hit || (e.request.mode === 'navigate' ? caches.match('fernweh.html') : undefined));
  e.respondWith(new Promise(resolve => {
    let done = false;
    const finish = r => { if (!done && r) { done = true; resolve(r); } };
    /* slow signal: show the cached page after 3s, the network copy still refreshes the cache */
    const t = setTimeout(() => fallback().then(finish), 3000);
    net.then(r => { clearTimeout(t); finish(r); })
      .catch(() => { clearTimeout(t); fallback().then(r => { if (r) finish(r); else if (!done) { done = true; resolve(Response.error()); } }); });
  }));
});
