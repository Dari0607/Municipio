const CACHE_NAME = 'municipio-v2';
const URLS_CACHE = [
  '/',
  '/login/',
  '/static/assets/css/main.css',
  '/static/assets/vendor/bootstrap/css/bootstrap.min.css',
  '/static/assets/vendor/bootstrap-icons/bootstrap-icons.css',
  '/static/assets/vendor/bootstrap/js/bootstrap.bundle.min.js',
  '/static/assets/vendor/jquery/jquery.min.js',
  '/static/assets/vendor/sweetalert2/sweetalert2.all.min.js',
  '/static/assets/vendor/sweetalert2/sweetalert2.min.css',
  '/static/manifest.json',
];

// Instalación — guarda en cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(URLS_CACHE))
  );
  self.skipWaiting();
});

// Activación — limpia caches viejos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Fetch — sirve desde cache si hay, si no va a la red
self.addEventListener('fetch', event => {
  // Solo cachear GET, ignorar peticiones POST y admin
  if (event.request.method !== 'GET') return;
  if (event.request.url.includes('/admin/')) return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      return cached || fetch(event.request).then(response => {
        // Cachear solo respuestas válidas de assets estáticos
        if (
          response.ok &&
          event.request.url.includes('/static/')
        ) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => cached);
    })
  );
});
