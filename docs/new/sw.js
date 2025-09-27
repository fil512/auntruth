/**
 * Service Worker for AuntieRuth.com Mobile Performance
 * Provides offline functionality and performance optimization
 */

const CACHE_NAME = 'auntieruth-v1';
const STATIC_CACHE = 'auntieruth-static-v1';
const DATA_CACHE = 'auntieruth-data-v1';

// Critical files to cache for offline functionality
const STATIC_FILES = [
    '/auntruth/new/',
    '/auntruth/new/css/main.css',
    '/auntruth/new/css/foundation.css',
    '/auntruth/new/css/navigation.css',
    '/auntruth/new/css/mobile-enhancements.css',
    '/auntruth/new/js/navigation.js',
    '/auntruth/new/js/mobile-gestures.js',
    '/auntruth/new/js/mobile-performance.js'
];

// Install event - cache static files
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => cache.addAll(STATIC_FILES))
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (!cacheName.startsWith('auntieruth-')) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Handle genealogy data requests
    if (url.pathname.includes('/js/data/') || url.pathname.includes('data.json')) {
        event.respondWith(cacheFirstStrategy(event.request, DATA_CACHE));
        return;
    }

    // Handle static files
    if (STATIC_FILES.some(file => url.pathname.includes(file))) {
        event.respondWith(cacheFirstStrategy(event.request, STATIC_CACHE));
        return;
    }

    // Handle HTML pages - network first with fallback
    if (url.pathname.endsWith('.htm') || url.pathname.endsWith('.html')) {
        event.respondWith(networkFirstStrategy(event.request));
        return;
    }

    // Default: try cache first
    event.respondWith(cacheFirstStrategy(event.request, CACHE_NAME));
});

// Cache first strategy - good for static files
async function cacheFirstStrategy(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
        return cachedResponse;
    }

    try {
        const networkResponse = await fetch(request);
        if (networkResponse.status === 200) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.warn('Network request failed:', request.url);
        return new Response('Offline - content unavailable', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Network first strategy - good for dynamic content
async function networkFirstStrategy(request) {
    const cache = await caches.open(CACHE_NAME);

    try {
        const networkResponse = await fetch(request);
        if (networkResponse.status === 200) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        const cachedResponse = await cache.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        return new Response('Offline - page unavailable', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}