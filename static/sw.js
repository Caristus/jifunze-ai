const CACHE_NAME = 'jifunze-v1';
const urlsToCache = ['/', '/static/manifest.json'];
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).catch(() => {
        if (event.request.mode === 'navigate') {
          return new Response('<h1>Offline</h1><p>JIFUNZE AI is currently offline. Cached resources are available.</p>', {
            headers: { 'Content-Type': 'text/html' }
          });
        }
      });
    })
  );
});
