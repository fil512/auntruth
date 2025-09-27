/**
 * Mobile Performance Optimization for AuntieRuth.com
 * Implements service worker, lazy loading, and mobile-specific optimizations
 */

class MobilePerformanceManager {
    constructor() {
        this.isMobile = this.detectMobile();
        this.connectionType = this.getConnectionType();
        this.prefersReducedData = this.prefersReducedData();

        this.init();
    }

    init() {
        if (!this.isMobile) return;

        this.optimizeForMobile();
        this.setupLazyLoading();
        this.setupServiceWorker();
        this.optimizeImages();
        this.setupOfflineSupport();

        console.log('Mobile performance optimizations applied');
    }

    detectMobile() {
        return window.innerWidth <= 768 ||
               'ontouchstart' in window ||
               navigator.maxTouchPoints > 0;
    }

    getConnectionType() {
        if ('connection' in navigator) {
            return navigator.connection.effectiveType;
        }
        return 'unknown';
    }

    prefersReducedData() {
        if ('connection' in navigator) {
            return navigator.connection.saveData === true;
        }
        return false;
    }

    optimizeForMobile() {
        // Reduce cache size for mobile (following data-manager.js pattern)
        if (window.DataManager) {
            const dataManager = new DataManager();
            dataManager.maxCacheSize = 3; // Mobile-optimized cache
        }

        // Increase debounce delays on slow connections
        if (this.connectionType === 'slow-2g' || this.connectionType === '2g') {
            this.adjustDebounceDelays(300); // Increase from 150ms
        }

        // Disable animations on low-end devices
        if (this.prefersReducedData) {
            document.body.classList.add('reduced-motion');
        }
    }

    setupLazyLoading() {
        // Enhanced lazy loading for genealogy images
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;

                    // Load appropriate image size for mobile
                    if (img.dataset.mobileSrc && this.isMobile) {
                        img.src = img.dataset.mobileSrc;
                    } else if (img.dataset.src) {
                        img.src = img.dataset.src;
                    }

                    img.classList.remove('lazy');
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        }, {
            // Load images 100px before they come into view
            rootMargin: '100px'
        });

        // Apply to existing images
        document.querySelectorAll('img[data-src], img[loading="lazy"]').forEach(img => {
            img.classList.add('lazy');
            imageObserver.observe(img);
        });

        // Apply to future images
        const mutationObserver = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) {
                        const images = node.querySelectorAll ?
                            node.querySelectorAll('img[data-src], img[loading="lazy"]') : [];
                        images.forEach(img => {
                            img.classList.add('lazy');
                            imageObserver.observe(img);
                        });
                    }
                });
            });
        });

        mutationObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    async setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered:', registration);

                // Update on new service worker
                registration.addEventListener('updatefound', () => {
                    console.log('New service worker version available');
                });
            } catch (error) {
                console.warn('Service Worker registration failed:', error);
            }
        }
    }

    optimizeImages() {
        // Convert images to appropriate format and size for mobile
        const images = document.querySelectorAll('#right img, #singleImage img');

        images.forEach(img => {
            // Add responsive image attributes
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }

            // Optimize image quality for mobile
            if (this.prefersReducedData) {
                img.style.imageRendering = 'optimizeQuality';
            }

            // Add error handling
            img.addEventListener('error', () => {
                img.style.display = 'none';
                console.warn('Failed to load image:', img.src);
            });
        });
    }

    setupOfflineSupport() {
        // Basic offline support for genealogy browsing
        window.addEventListener('online', () => {
            document.body.classList.remove('offline');
            this.showConnectionStatus('Back online');
        });

        window.addEventListener('offline', () => {
            document.body.classList.add('offline');
            this.showConnectionStatus('Offline mode - limited functionality');
        });

        // Cache critical genealogy data
        this.cacheEssentialData();
    }

    async cacheEssentialData() {
        if ('caches' in window) {
            try {
                const cache = await caches.open('genealogy-v1');

                // Cache current lineage data
                const currentLineage = this.getCurrentLineage();
                if (currentLineage) {
                    const dataUrl = `/auntruth/new/js/data/lineages/L${currentLineage}.json`;
                    await cache.add(dataUrl);
                }

                // Cache main data file
                await cache.add('/auntruth/new/js/data.json');

            } catch (error) {
                console.warn('Failed to cache essential data:', error);
            }
        }
    }

    adjustDebounceDelays(newDelay) {
        // Update search debounce for slow connections
        const searchComponent = window.SearchComponent;
        if (searchComponent && searchComponent.prototype) {
            searchComponent.prototype.debounceDelay = newDelay;
        }
    }

    showConnectionStatus(message) {
        const toast = document.createElement('div');
        toast.className = 'connection-toast';
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    getCurrentLineage() {
        const match = window.location.pathname.match(/\/L(\d+)\//);
        return match ? match[1] : null;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new MobilePerformanceManager();
});

window.MobilePerformanceManager = MobilePerformanceManager;