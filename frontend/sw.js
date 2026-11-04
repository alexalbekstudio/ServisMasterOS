const CACHE_NAME = "servismaster-cache-v23";

const STATIC_ASSETS = [
    "/",
    "/orders",
    "/dashboard",
    "/inventory",
    "/reminders",
    "/static/css/style.css",
    "/static/css/app.css",
    "/static/js/api.js",
    "/static/js/reception.js",
    "/static/js/orders.js",
    "/static/js/dashboard.js",
    "/static/js/inventory.js",
    "/static/js/reminders.js",
    "/static/js/status.js",
    "/manifest.json"
];

// Instalacija — keširanje statičkih resursa
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return Promise.allSettled(
                STATIC_ASSETS.map((asset) =>
                    cache.add(asset).catch((err) => {
                        console.warn(`[SW] Nije keširan: ${asset}`, err);
                    })
                )
            );
        })
    );
    self.skipWaiting();
});

// Aktivacija — čišćenje starih keševa
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch — Network First za API, Cache First za statiku
self.addEventListener("fetch", (event) => {
    const req = event.request;

    // Ne keširaj API pozive
    if (req.url.includes("/api/")) {
        return;
    }

    // HTML navigacija — Network First
    if (req.mode === "navigate") {
        event.respondWith(
            fetch(req)
                .then((networkRes) => {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(req, networkRes.clone());
                        return networkRes;
                    });
                })
                .catch(() => caches.match(req))
        );
        return;
    }

    // Statički fajlovi — Cache First
    event.respondWith(
        caches.match(req).then((cachedRes) => {
            return cachedRes || fetch(req);
        })
    );
});