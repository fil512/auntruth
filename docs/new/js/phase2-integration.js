/**
 * Phase 2 Integration Layer
 * Connects Enhanced Search, Family Tree, and Information Disclosure components
 * Manages cross-component communication and URL state
 */

import EnhancedSearchComponent from './components/enhanced-search.js';
import FamilyTreeComponent from './components/family-tree.js';
import InformationDisclosureComponent from './components/information-disclosure.js';
import DataManager from './core/data-manager.js';

class Phase2Integration {
  constructor() {
    this.components = {
      search: null,
      tree: null,
      disclosure: null
    };

    this.dataManager = new DataManager();
    this.urlState = this.parseUrlState();
    this.initialized = false;

    // Component communication events
    this.events = {
      PERSON_SELECTED: 'person-selected',
      SEARCH_RESULT_SELECTED: 'search-result-selected',
      TREE_PERSON_SELECTED: 'tree-person-selected',
      DISCLOSURE_LOADED: 'disclosure-loaded'
    };
  }

  async init() {
    if (this.initialized) return;

    try {
      console.log('Initializing Phase 2 integration...');

      // Load CSS dependencies
      await this.loadStylesheets();

      // Initialize components based on page context
      await this.initializeComponents();

      // Setup cross-component communication
      this.setupEventHandlers();

      // Setup URL state management
      this.setupUrlStateManagement();

      // Apply initial URL state
      this.applyUrlState();

      this.initialized = true;
      console.log('Phase 2 integration initialized successfully');

    } catch (error) {
      console.error('Failed to initialize Phase 2 integration:', error);
      throw error;
    }
  }

  async loadStylesheets() {
    const stylesheets = [
      '/auntruth/new/css/enhanced-search.css',
      '/auntruth/new/css/family-tree.css',
      '/auntruth/new/css/information-disclosure.css'
    ];

    const loadPromises = stylesheets.map(href => {
      return new Promise((resolve, reject) => {
        // Check if already loaded
        if (document.querySelector(`link[href="${href}"]`)) {
          resolve();
          return;
        }

        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.onload = resolve;
        link.onerror = reject;
        document.head.appendChild(link);
      });
    });

    await Promise.all(loadPromises);
    console.log('Phase 2 stylesheets loaded');
  }

  async initializeComponents() {
    const pageType = this.detectPageType();
    console.log(`Detected page type: ${pageType}`);

    switch (pageType) {
      case 'search':
        await this.initializeSearchPage();
        break;
      case 'person':
        await this.initializePersonPage();
        break;
      case 'tree':
        await this.initializeTreePage();
        break;
      case 'index':
        await this.initializeIndexPage();
        break;
      default:
        await this.initializeDefaultComponents();
    }
  }

  detectPageType() {
    const path = window.location.pathname;
    const params = new URLSearchParams(window.location.search);

    // Check for tree view parameter
    if (params.has('tree') || params.has('family-tree')) {
      return 'tree';
    }

    // Check for search parameter
    if (params.has('search') || params.has('q')) {
      return 'search';
    }

    // Check file patterns
    if (path.includes('/XF') && path.endsWith('.htm')) {
      return 'person'; // Person detail page
    }

    if (path.includes('/THF') && path.endsWith('.htm')) {
      return 'person'; // Person thumbnail page
    }

    if (path.includes('index.htm') || path.endsWith('/')) {
      return 'index';
    }

    return 'default';
  }

  async initializeSearchPage() {
    // Initialize enhanced search
    this.components.search = new EnhancedSearchComponent({
      dataManager: this.dataManager
    });
    await this.components.search.init();

    // Auto-perform search if query in URL
    const query = this.urlState.search || this.urlState.q;
    if (query) {
      this.components.search.searchInput.value = query;
      this.components.search.performSearch(query);
    }
  }

  async initializePersonPage() {
    // Initialize information disclosure for person pages
    this.components.disclosure = new InformationDisclosureComponent();
    await this.components.disclosure.init();

    // Initialize mini search widget
    await this.initializeMiniSearch();

    // Initialize family tree if person ID available
    const personId = this.extractPersonIdFromUrl();
    if (personId) {
      await this.initializeFamilyTreeForPerson(personId);
    }
  }

  async initializeTreePage() {
    // Initialize family tree component
    const personId = this.urlState.focus || this.extractPersonIdFromUrl();
    this.components.tree = new FamilyTreeComponent({
      dataManager: this.dataManager,
      focusPersonId: personId,
      generations: parseInt(this.urlState.generations) || 3
    });
    await this.components.tree.init();

    // Initialize search for tree navigation
    await this.initializeMiniSearch();
  }

  async initializeIndexPage() {
    // Initialize search for main navigation
    this.components.search = new EnhancedSearchComponent({
      dataManager: this.dataManager
    });
    await this.components.search.init();

    // Show search interface by default
    if (this.components.search.searchContainer) {
      this.components.search.searchContainer.classList.add('active');
    }
  }

  async initializeDefaultComponents() {
    // Initialize components that enhance existing pages
    await this.initializeMiniSearch();

    // Initialize disclosure if table present
    const table = document.querySelector('table#List') || document.querySelector('table');
    if (table) {
      this.components.disclosure = new InformationDisclosureComponent();
      await this.components.disclosure.init();
    }
  }

  async initializeMiniSearch() {
    // Create a smaller search widget for navigation
    this.components.search = new EnhancedSearchComponent({
      dataManager: this.dataManager,
      compact: true
    });
    await this.components.search.init();
  }

  async initializeFamilyTreeForPerson(personId) {
    // Create family tree widget for person pages
    this.components.tree = new FamilyTreeComponent({
      dataManager: this.dataManager,
      focusPersonId: personId,
      generations: 2,
      container: this.createTreeContainer()
    });
    await this.components.tree.init();
  }

  createTreeContainer() {
    // Create a container for the family tree on person pages
    const container = document.createElement('div');
    container.id = 'person-family-tree';
    container.style.marginTop = '2rem';

    // Insert after main content
    const main = document.querySelector('main, .main-content, body');
    if (main) {
      main.appendChild(container);
    }

    return container;
  }

  setupEventHandlers() {
    // Search -> Tree workflow
    document.addEventListener(this.events.SEARCH_RESULT_SELECTED, (event) => {
      this.handleSearchResultSelected(event);
    });

    // Tree -> Person workflow
    document.addEventListener(this.events.TREE_PERSON_SELECTED, (event) => {
      this.handleTreePersonSelected(event);
    });

    // Person selection coordination
    document.addEventListener(this.events.PERSON_SELECTED, (event) => {
      this.handlePersonSelected(event);
    });

    // Enhanced search result clicks
    document.addEventListener('click', (event) => {
      const resultItem = event.target.closest('.search-result-item.enhanced-result');
      if (resultItem) {
        event.preventDefault();
        const personId = this.extractPersonIdFromResultItem(resultItem);
        if (personId) {
          this.selectPerson(personId);
        }
      }
    });

    // Family tree navigation
    document.addEventListener('click', (event) => {
      if (event.target.matches('.show-family-tree')) {
        event.preventDefault();
        const personId = event.target.dataset.personId;
        if (personId) {
          this.showFamilyTree(personId);
        }
      }
    });
  }

  setupUrlStateManagement() {
    // Handle browser back/forward
    window.addEventListener('popstate', (event) => {
      if (event.state) {
        this.urlState = event.state;
        this.applyUrlState();
      }
    });

    // Update URL when state changes
    document.addEventListener('state-change', (event) => {
      this.updateUrlState(event.detail);
    });
  }

  handleSearchResultSelected(event) {
    const { personId, person } = event.detail;

    // Update tree if present
    if (this.components.tree) {
      this.components.tree.focusOnPerson(personId);
    }

    // Navigate to person page or show tree
    if (this.urlState.view === 'tree') {
      this.showFamilyTree(personId);
    } else {
      this.navigateToPersonPage(personId);
    }
  }

  handleTreePersonSelected(event) {
    const { personId, person } = event.detail;

    // Update search results if present
    if (this.components.search) {
      // Highlight in search results if visible
      this.highlightPersonInSearch(personId);
    }

    // Update URL state
    this.updateUrlState({ focus: personId });
  }

  handlePersonSelected(event) {
    const { personId } = event.detail;

    // Coordinate all components
    if (this.components.tree) {
      this.components.tree.focusOnPerson(personId);
    }

    if (this.components.disclosure) {
      // Disclosure might need to reload for different person
      // This would require extending the component
    }

    // Update URL state
    this.updateUrlState({ focus: personId });
  }

  selectPerson(personId) {
    // Central method to handle person selection
    document.dispatchEvent(new CustomEvent(this.events.PERSON_SELECTED, {
      detail: { personId }
    }));
  }

  async showFamilyTree(personId) {
    // Navigate to tree view or initialize tree component
    if (!this.components.tree) {
      await this.initializeFamilyTreeForPerson(personId);
    } else {
      this.components.tree.focusOnPerson(personId);
    }

    // Update URL to tree view
    this.updateUrlState({ view: 'tree', focus: personId });
  }

  navigateToPersonPage(personId) {
    // Navigate to person detail page
    // This requires knowledge of URL structure
    const person = this.dataManager.getPersonData(personId);
    if (person) {
      const url = `/auntruth/new/htm/L${person.lineage || '0'}/${person.filename || personId}.htm`;
      window.location.href = url;
    }
  }

  highlightPersonInSearch(personId) {
    const searchResults = document.querySelectorAll('.search-result-item');
    searchResults.forEach(item => {
      const itemPersonId = this.extractPersonIdFromResultItem(item);
      item.classList.toggle('highlighted', itemPersonId === personId);
    });
  }

  extractPersonIdFromUrl() {
    const path = window.location.pathname;

    // Extract from XF### pattern
    const xfMatch = path.match(/XF(\d+)\.htm/);
    if (xfMatch) return xfMatch[1];

    // Extract from THF### pattern
    const thfMatch = path.match(/THF(\d+)\.htm/);
    if (thfMatch) return thfMatch[1];

    // Extract from URL parameter
    const params = new URLSearchParams(window.location.search);
    return params.get('person') || params.get('id');
  }

  extractPersonIdFromResultItem(item) {
    const url = item.dataset.url || item.getAttribute('data-url');
    if (url) {
      const match = url.match(/[XTH]F(\d+)\.htm/);
      return match ? match[1] : null;
    }
    return null;
  }

  parseUrlState() {
    const params = new URLSearchParams(window.location.search);
    return {
      search: params.get('search') || params.get('q'),
      focus: params.get('focus') || params.get('person'),
      view: params.get('view'),
      generations: params.get('generations'),
      lineage: params.get('lineage')
    };
  }

  applyUrlState() {
    if (this.urlState.search && this.components.search) {
      this.components.search.performSearch(this.urlState.search);
    }

    if (this.urlState.focus && this.components.tree) {
      this.components.tree.focusOnPerson(this.urlState.focus);
    }

    if (this.urlState.view === 'tree' && !this.components.tree) {
      this.showFamilyTree(this.urlState.focus);
    }
  }

  updateUrlState(newState) {
    // Merge new state with existing
    this.urlState = { ...this.urlState, ...newState };

    // Update URL
    const params = new URLSearchParams();
    Object.entries(this.urlState).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      }
    });

    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState(this.urlState, '', newUrl);
  }

  // Public API for external integration
  async openSearch() {
    if (!this.components.search) {
      await this.initializeMiniSearch();
    }
    if (this.components.search.searchContainer) {
      this.components.search.searchContainer.classList.add('active');
      this.components.search.searchInput.focus();
    }
  }

  async showPersonTree(personId) {
    await this.showFamilyTree(personId);
  }

  getComponent(type) {
    return this.components[type];
  }

  destroy() {
    // Clean up all components
    Object.values(this.components).forEach(component => {
      if (component && component.destroy) {
        component.destroy();
      }
    });

    // Remove event listeners
    window.removeEventListener('popstate', this.handlePopstate);
  }
}

// Auto-initialize on DOM ready
let phase2Integration = null;

document.addEventListener('DOMContentLoaded', async () => {
  // Only initialize in the new site structure
  if (window.location.pathname.includes('/new/') ||
      document.querySelector('[data-phase2-enabled]')) {

    try {
      phase2Integration = new Phase2Integration();
      await phase2Integration.init();

      // Make available globally for debugging
      window.Phase2 = phase2Integration;

    } catch (error) {
      console.error('Phase 2 initialization failed:', error);
    }
  }
});

// Global search trigger
document.addEventListener('keydown', (event) => {
  // Ctrl/Cmd + K to open search
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault();
    if (phase2Integration) {
      phase2Integration.openSearch();
    }
  }
});

export default Phase2Integration;