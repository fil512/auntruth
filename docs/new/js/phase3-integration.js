/**
 * Phase 3 Integration Layer
 * Orchestrates Relationship Navigator, Timeline, and URL Router components
 * Manages cross-component communication and advanced features
 */

import RelationshipNavigatorComponent from './components/relationship-navigator.js';
import TimelineComponent from './components/timeline.js';
import URLRouter from './utils/url-router.js';
import DataManager from './core/data-manager.js';

class Phase3Integration {
  constructor() {
    this.components = {
      relationshipNavigator: null,
      timeline: null,
      urlRouter: null
    };

    this.dataManager = new DataManager();
    this.initialized = false;

    // Component communication events
    this.events = {
      PERSON_SELECTED: 'person-selected',
      TIMELINE_EVENT_SELECTED: 'timeline-event-selected',
      RELATIONSHIP_FOUND: 'relationship-found',
      ROUTER_COMPONENTS_REQUESTED: 'router-components-requested',
      ROUTER_PERSON_SELECTED: 'router-person-selected',
      ROUTER_TIMELINE_FOCUS: 'router-timeline-focus',
      URL_CHANGED: 'url-changed'
    };

    // Router integration
    this.currentRoute = null;
    this.pendingComponentLoads = new Set();
  }

  async init() {
    if (this.initialized) return;

    try {
      console.log('Initializing Phase 3 integration...');

      // Load CSS dependencies
      await this.loadStylesheets();

      // Initialize URL Router first (it coordinates everything)
      this.urlRouter = new URLRouter();
      this.urlRouter.init();
      this.components.urlRouter = this.urlRouter;

      // Setup cross-component communication
      this.setupEventHandlers();

      // Setup URL routing events
      this.setupUrlRouting();

      this.initialized = true;
      console.log('Phase 3 integration initialized successfully');

    } catch (error) {
      console.error('Failed to initialize Phase 3 integration:', error);
      throw error;
    }
  }

  async loadStylesheets() {
    const stylesheets = [
      '/auntruth/new/css/relationship-navigator.css',
      '/auntruth/new/css/timeline.css',
      '/auntruth/new/css/phase3-components.css'
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
        link.onerror = () => {
          console.warn(`Failed to load stylesheet: ${href}`);
          resolve(); // Don't fail the whole init
        };
        document.head.appendChild(link);
      });
    });

    await Promise.all(loadPromises);
    console.log('Phase 3 stylesheets loaded');
  }

  setupEventHandlers() {
    // URL Router requests components
    document.addEventListener(this.events.ROUTER_COMPONENTS_REQUESTED, (event) => {
      this.handleComponentsRequested(event);
    });

    // Router person selection
    document.addEventListener(this.events.ROUTER_PERSON_SELECTED, (event) => {
      this.handleRouterPersonSelected(event);
    });

    // Timeline event selection
    document.addEventListener(this.events.TIMELINE_EVENT_SELECTED, (event) => {
      this.handleTimelineEventSelected(event);
    });

    // Person selection coordination
    document.addEventListener(this.events.PERSON_SELECTED, (event) => {
      this.handlePersonSelected(event);
    });

    // Relationship Navigator person selection
    document.addEventListener('relationship-navigator-person-selected', (event) => {
      this.handlePersonSelected(event);
    });

    // Cross-component navigation requests
    document.addEventListener('router-search-requested', (event) => {
      this.handleSearchRequested(event);
    });

    document.addEventListener('router-tree-focus-requested', (event) => {
      this.handleTreeFocusRequested(event);
    });

    document.addEventListener('router-timeline-period-requested', (event) => {
      this.handleTimelinePeriodRequested(event);
    });
  }

  setupUrlRouting() {
    // Listen for URL changes to update components
    window.addEventListener('popstate', () => {
      this.handleUrlChange();
    });

    // Initial URL handling is done by URLRouter
    this.handleUrlChange();
  }

  async handleComponentsRequested(event) {
    const { components, route } = event.detail;
    console.log('Components requested:', components, route);

    this.currentRoute = route;

    // Initialize requested components
    for (const componentName of components) {
      if (!this.pendingComponentLoads.has(componentName)) {
        this.pendingComponentLoads.add(componentName);
        await this.initializeComponent(componentName);
        this.pendingComponentLoads.delete(componentName);
      }
    }
  }

  async initializeComponent(componentName) {
    console.log('Initializing component:', componentName);

    try {
      switch (componentName) {
        case 'relationship-navigator':
          if (!this.components.relationshipNavigator) {
            this.components.relationshipNavigator = new RelationshipNavigatorComponent({
              dataManager: this.dataManager
            });
            await this.components.relationshipNavigator.init();
          }
          break;

        case 'timeline':
          if (!this.components.timeline) {
            this.components.timeline = new TimelineComponent({
              dataManager: this.dataManager
            });
            await this.components.timeline.init();
          }
          break;

        case 'enhanced-search':
          // Enhanced search is handled by Phase 2 integration
          console.log('Enhanced search handled by Phase 2');
          break;

        case 'family-tree':
          // Family tree is handled by Phase 2 integration
          console.log('Family tree handled by Phase 2');
          break;

        default:
          console.warn('Unknown component requested:', componentName);
      }
    } catch (error) {
      console.error(`Failed to initialize ${componentName}:`, error);
    }
  }

  handleRouterPersonSelected(event) {
    const { personId, person } = event.detail;
    console.log('Router selected person:', personId, person?.name);

    // Update relationship navigator
    if (this.components.relationshipNavigator) {
      this.components.relationshipNavigator.selectPerson(personId);
    }

    // Focus timeline on person's events
    if (this.components.timeline && personId) {
      const personEvents = this.components.timeline.getEventsForPerson(personId);
      if (personEvents.length > 0) {
        // Focus timeline on person's birth year or first event
        const firstEvent = personEvents.sort((a, b) => a.year - b.year)[0];
        this.components.timeline.focusOnYear(firstEvent.year);
      }
    }
  }

  handlePersonSelected(event) {
    const { personId, person } = event.detail;
    console.log('Person selected:', personId, person?.name);

    // Update URL if not already reflecting this person
    if (this.urlRouter && person) {
      const currentRoute = this.urlRouter.getCurrentRoute();
      const expectedUrl = this.urlRouter.generatePersonURL(person);

      if (currentRoute?.path !== expectedUrl) {
        this.urlRouter.navigate(expectedUrl);
      }
    }

    // Coordinate all components
    if (this.components.relationshipNavigator &&
        this.components.relationshipNavigator.currentPerson?.id !== personId) {
      this.components.relationshipNavigator.selectPerson(personId);
    }

    // Focus timeline if available
    if (this.components.timeline && personId) {
      const personEvents = this.components.timeline.getEventsForPerson(personId);
      if (personEvents.length > 0) {
        const firstEvent = personEvents.sort((a, b) => a.year - b.year)[0];
        this.components.timeline.focusOnYear(firstEvent.year);
      }
    }
  }

  handleTimelineEventSelected(event) {
    const { event: timelineEvent, personId, person } = event.detail;
    console.log('Timeline event selected:', timelineEvent);

    // Update relationship navigator with the person from the event
    if (personId && this.components.relationshipNavigator) {
      this.components.relationshipNavigator.selectPerson(personId);
    }

    // Navigate to person page if we have person data
    if (person && this.urlRouter) {
      const personUrl = this.urlRouter.generatePersonURL(person);
      this.urlRouter.navigate(personUrl);
    }
  }

  async handleSearchRequested(event) {
    const { query } = event.detail;
    console.log('Search requested:', query);

    // Ensure search component is loaded (handled by Phase 2)
    document.dispatchEvent(new CustomEvent('phase3-search-requested', {
      detail: { query }
    }));
  }

  async handleTreeFocusRequested(event) {
    const { personId } = event.detail;
    console.log('Tree focus requested:', personId);

    // Ensure family tree is loaded and focused
    document.dispatchEvent(new CustomEvent('phase3-tree-focus-requested', {
      detail: { personId }
    }));

    // Also update relationship navigator
    if (this.components.relationshipNavigator) {
      this.components.relationshipNavigator.selectPerson(personId);
    }
  }

  async handleTimelinePeriodRequested(event) {
    const { period } = event.detail;
    console.log('Timeline period requested:', period);

    // Parse period and focus timeline
    if (this.components.timeline) {
      const periodInfo = this.parsePeriod(period);
      if (periodInfo) {
        this.components.timeline.setDateRange(periodInfo.start, periodInfo.end);
      }
    }
  }

  parsePeriod(period) {
    // Parse period strings like "1800s", "1900-1950", "1920"
    if (period.endsWith('s')) {
      // Decade: "1890s" -> 1890-1899
      const decade = parseInt(period.slice(0, -1));
      if (!isNaN(decade)) {
        return { start: decade, end: decade + 9 };
      }
    }

    if (period.includes('-')) {
      // Range: "1900-1950" -> 1900-1950
      const [start, end] = period.split('-').map(y => parseInt(y));
      if (!isNaN(start) && !isNaN(end)) {
        return { start, end };
      }
    }

    // Single year: "1920" -> 1920-1930
    const year = parseInt(period);
    if (!isNaN(year)) {
      return { start: year, end: year + 10 };
    }

    return null;
  }

  handleUrlChange() {
    if (!this.urlRouter) return;

    const currentRoute = this.urlRouter.getCurrentRoute();
    console.log('URL changed:', currentRoute);

    // Update components based on new route
    this.updateComponentsForRoute(currentRoute);
  }

  updateComponentsForRoute(route) {
    if (!route) return;

    // Extract person information from route
    if (route.pattern === '/person/:slug' || route.pattern === '/person/:slug/:section') {
      const personId = this.extractPersonIdFromSlug(route.params.slug);

      // Update relationship navigator
      if (this.components.relationshipNavigator && personId) {
        this.components.relationshipNavigator.selectPerson(personId);
      }
    }

    // Handle timeline routes
    if (route.pattern === '/timeline/:period') {
      const periodInfo = this.parsePeriod(route.params.period);
      if (this.components.timeline && periodInfo) {
        this.components.timeline.setDateRange(periodInfo.start, periodInfo.end);
      }
    }
  }

  extractPersonIdFromSlug(slug) {
    // Extract person ID from slug (format: name-123 or just 123)
    const match = slug.match(/-(\d+)$/) || slug.match(/^(\d+)$/);
    return match ? match[1] : null;
  }

  // Public API for external integration
  async showPersonRelationships(personId) {
    // Ensure relationship navigator is loaded
    await this.initializeComponent('relationship-navigator');

    if (this.components.relationshipNavigator) {
      this.components.relationshipNavigator.selectPerson(personId);

      // Show sidebar if hidden
      if (!this.components.relationshipNavigator.sidebarVisible) {
        this.components.relationshipNavigator.toggleSidebar();
      }
    }
  }

  async showPersonTimeline(personId) {
    // Ensure timeline is loaded
    await this.initializeComponent('timeline');

    if (this.components.timeline && personId) {
      const personEvents = this.components.timeline.getEventsForPerson(personId);
      if (personEvents.length > 0) {
        const firstEvent = personEvents.sort((a, b) => a.year - b.year)[0];
        this.components.timeline.focusOnYear(firstEvent.year);
      }
    }
  }

  async findRelationship(personId1, personId2) {
    // Ensure relationship navigator is loaded
    await this.initializeComponent('relationship-navigator');

    if (this.components.relationshipNavigator) {
      return await this.components.relationshipNavigator.findRelationship(personId1, personId2);
    }

    return null;
  }

  getComponent(type) {
    return this.components[type];
  }

  isComponentReady(type) {
    return this.components[type] !== null;
  }

  async waitForComponent(type, timeout = 10000) {
    const startTime = Date.now();

    while (!this.isComponentReady(type)) {
      if (Date.now() - startTime > timeout) {
        throw new Error(`Timeout waiting for component: ${type}`);
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    return this.components[type];
  }

  destroy() {
    // Clean up all components
    Object.values(this.components).forEach(component => {
      if (component && component.destroy) {
        component.destroy();
      }
    });

    // Clean up event listeners
    // (Browser will handle this on page unload)

    this.initialized = false;
  }
}

// Auto-initialize on DOM ready
let phase3Integration = null;

document.addEventListener('DOMContentLoaded', async () => {
  // Only initialize in the new site structure
  if (window.location.pathname.includes('/new/') ||
      document.querySelector('[data-phase3-enabled]') ||
      document.querySelector('[data-modern-routing]')) {

    try {
      phase3Integration = new Phase3Integration();
      await phase3Integration.init();

      // Make available globally for debugging and external use
      window.Phase3 = phase3Integration;

      // Integrate with Phase 2 if available
      if (window.Phase2) {
        console.log('Phase 3 integrated with Phase 2');
        // Phase 2 and Phase 3 can coexist and complement each other
      }

    } catch (error) {
      console.error('Phase 3 initialization failed:', error);
      // Don't prevent page load - graceful degradation
    }
  }
});

// Global keyboard shortcuts for Phase 3 features
document.addEventListener('keydown', (event) => {
  if (!phase3Integration) return;

  // Ctrl/Cmd + R to show relationships
  if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
    event.preventDefault();
    const relationshipNav = phase3Integration.getComponent('relationshipNavigator');
    if (relationshipNav && !relationshipNav.sidebarVisible) {
      relationshipNav.toggleSidebar();
    }
  }

  // Ctrl/Cmd + T to show timeline
  if ((event.ctrlKey || event.metaKey) && event.key === 't') {
    event.preventDefault();
    if (phase3Integration.urlRouter) {
      phase3Integration.urlRouter.navigate('/timeline');
    }
  }
});

export default Phase3Integration;