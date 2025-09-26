/**
 * Base Component Class
 * Foundation for all UI components with lifecycle management
 */
class BaseComponent {
  constructor(options = {}) {
    this.options = options;
    this.element = null;
    this.initialized = false;
    this.mobile = this.detectMobile();
  }

  async init() {
    if (this.initialized) return;

    try {
      await this.loadDependencies();
      await this.render();
      this.attachEventListeners();
      this.initialized = true;
    } catch (error) {
      console.error(`Failed to initialize ${this.constructor.name}:`, error);
      throw error;
    }
  }

  async loadDependencies() {
    // Override in subclasses for async dependency loading
  }

  async render() {
    // Override in subclasses for rendering logic
  }

  attachEventListeners() {
    // Override in subclasses for event handling
  }

  destroy() {
    if (this.element) {
      // Remove all event listeners
      const clone = this.element.cloneNode(true);
      this.element.parentNode.replaceChild(clone, this.element);
      this.element = null;
    }
    this.initialized = false;
  }

  detectMobile() {
    return window.innerWidth <= 768 ||
           'ontouchstart' in window ||
           navigator.maxTouchPoints > 0;
  }

  // Utility method for safe DOM queries
  $(selector, context = document) {
    return context.querySelector(selector);
  }

  $$(selector, context = document) {
    return Array.from(context.querySelectorAll(selector));
  }
}

// Export for ES6 modules and global
export default BaseComponent;
window.BaseComponent = BaseComponent;