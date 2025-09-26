/**
 * Main Application Controller
 * Initializes and manages all components
 */

class AuntieRuthApp {
  constructor() {
    this.components = new Map();
    this.dataManager = null;
    this.initialized = false;
  }

  async init() {
    if (this.initialized) return;

    console.log('Initializing AuntieRuth.com modernization...');

    try {
      // Initialize data manager
      this.dataManager = new DataManager();

      // Initialize navigation (critical path)
      await this.initNavigation();

      // Progressive enhancement based on page type
      const pageType = this.detectPageType();

      if (pageType === 'person') {
        await this.initPersonPageEnhancements();
      }

      // Initialize mobile optimizations if needed
      if (this.isMobile()) {
        await this.initMobileEnhancements();
      }

      this.initialized = true;
      console.log('Application initialized successfully');

    } catch (error) {
      console.error('Failed to initialize application:', error);
      // Site should still work without JavaScript enhancements
    }
  }

  async initNavigation() {
    try {
      // Dynamic import for code splitting
      const NavigationModule = await this.loadComponent('navigation-enhanced');

      if (NavigationModule) {
        const nav = new NavigationModule.default({
          dataManager: this.dataManager
        });

        await nav.init();
        this.components.set('navigation', nav);
      }
    } catch (error) {
      console.error('Failed to initialize navigation:', error);
      // Fall back to basic navigation if enhanced fails
      this.initFallbackNavigation();
    }
  }

  async initPersonPageEnhancements() {
    // Additional enhancements for person pages
    console.log('Enhancing person page experience...');
  }

  async initMobileEnhancements() {
    // Mobile-specific optimizations
    console.log('Applying mobile optimizations...');

    // Add mobile class to body for CSS hooks
    document.body.classList.add('mobile-device');
  }

  async loadComponent(name) {
    try {
      // Dynamic import for progressive loading
      const module = await import(`../components/${name}.js`);
      return module;
    } catch (error) {
      console.warn(`Component ${name} not found, using fallback`);
      return null;
    }
  }

  initFallbackNavigation() {
    // Basic navigation without JavaScript enhancements
    console.log('Using fallback navigation');
  }

  detectPageType() {
    const filename = window.location.pathname.split('/').pop() || '';

    if (filename.startsWith('XF')) return 'person';
    if (filename.startsWith('THF')) return 'thumbnail';
    if (filename.startsWith('XI')) return 'image';
    if (filename.includes('index')) return 'index';

    return 'unknown';
  }

  isMobile() {
    return window.innerWidth <= 768 ||
           'ontouchstart' in window ||
           navigator.maxTouchPoints > 0;
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.auntieRuthApp = new AuntieRuthApp();
    window.auntieRuthApp.init();
  });
} else {
  // DOM already loaded
  window.auntieRuthApp = new AuntieRuthApp();
  window.auntieRuthApp.init();
}