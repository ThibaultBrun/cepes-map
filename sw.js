const V = 'cepes-v9';
// Précache : l'app + les sorties famille (dispo hors-ligne dans la forêt, sans réseau)
const PRECACHE = [
  '/index.html', '/icon.svg', '/manifest.json',
  '/sorties/ustaritz-famille.geojson', '/sorties/ustaritz-famille.gpx',
  '/sorties/espelette-famille.geojson', '/sorties/espelette-famille.gpx',
  '/sorties/pas-de-roland.geojson', '/sorties/pas-de-roland.gpx',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(V)
      .then(c => Promise.allSettled(PRECACHE.map(u => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== V).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  // push.json + ressources externes (tuiles IGN/Panoramax/CDN) : réseau direct
  if (url.pathname.includes('push.json') || url.origin !== location.origin) return;

  const isHtml = url.pathname.endsWith('.html') || url.pathname === '/';
  if (isHtml) {
    // network-first : toujours la dernière version quand on a du réseau, cache en secours hors-ligne
    e.respondWith(
      fetch(e.request).then(res => {
        if (res.ok) { const clone = res.clone(); caches.open(V).then(c => c.put('/index.html', clone)); }
        return res;
      }).catch(() => caches.match('/index.html'))
    );
    return;
  }
  // sortie + icônes : cache-first avec rafraîchissement en arrière-plan (offline-friendly)
  if (url.pathname.startsWith('/sorties/') || url.pathname.endsWith('.svg') || url.pathname.endsWith('manifest.json')) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        const net = fetch(e.request).then(res => {
          if (res.ok) { const clone = res.clone(); caches.open(V).then(c => c.put(e.request, clone)); }
          return res;
        }).catch(() => cached);
        return cached || net;
      })
    );
  }
  // reste (tuiles raster même origine, pmtiles…) : réseau direct, pas de cache
});
