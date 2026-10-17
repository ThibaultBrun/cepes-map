const V = 'cepes-v1';
const PRECACHE = ['/index.html', '/icon.svg'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== V).map(k => caches.delete(k)))
  ).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // Always network-first for push.json and external resources
  if (url.pathname.includes('push.json') || url.origin !== location.origin) return;
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request).then(res => {
      if (res.ok && url.pathname.endsWith('.html')) {
        const clone = res.clone();
        caches.open(V).then(c => c.put(e.request, clone));
      }
      return res;
    }))
  );
});
