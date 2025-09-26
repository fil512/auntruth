# Component Integration Patterns

## Inter-Component Communication

### Event-Based Communication
Components should communicate through events rather than direct coupling:

```javascript
// Event naming convention: 'auntruth:componentname:action'
class ComponentEventSystem {
  // Fire events for other components to listen to
  firePersonSelected(personData) {
    const event = new CustomEvent('auntruth:person:selected', {
      detail: { person: personData },
      bubbles: true
    });
    document.dispatchEvent(event);
  }

  fireSearchCompleted(results) {
    const event = new CustomEvent('auntruth:search:completed', {
      detail: { results },
      bubbles: true
    });
    document.dispatchEvent(event);
  }

  fireTimelineFiltered(dateRange, lineage) {
    const event = new CustomEvent('auntruth:timeline:filtered', {
      detail: { dateRange, lineage },
      bubbles: true
    });
    document.dispatchEvent(event);
  }
}
```

### Component Registry Pattern
```javascript
class ComponentRegistry {
  constructor() {
    this.components = new Map();
    this.eventBus = new EventBus();
  }

  register(name, component) {
    this.components.set(name, component);
    component.eventBus = this.eventBus;
  }

  get(name) {
    return this.components.get(name);
  }

  broadcast(eventName, data) {
    this.eventBus.emit(eventName, data);
  }
}
```

## Common Integration Patterns

### Search → Family Tree
```javascript
// Search component integration
class SearchComponent extends BaseComponent {
  onResultClick(person) {
    // Fire event for family tree to focus on this person
    this.fireEvent('person:selected', {
      personId: person.id,
      context: 'search',
      intent: 'view-family-tree'
    });

    // Optionally navigate to family tree page
    if (this.options.autoNavigateToTree) {
      window.location.href = `/family-tree/?person=${person.id}`;
    }
  }
}

// Family tree component listens for search selections
class FamilyTreeComponent extends BaseComponent {
  attachEventListeners() {
    super.attachEventListeners();

    document.addEventListener('auntruth:person:selected', (e) => {
      if (e.detail.intent === 'view-family-tree') {
        this.focusOnPerson(e.detail.personId);
      }
    });
  }
}
```

### Navigation → All Components
```javascript
// Navigation provides context to all components
class NavigationComponent extends BaseComponent {
  navigateToLineage(lineageId) {
    // Notify all components of lineage context change
    this.fireEvent('context:lineage-changed', {
      lineageId,
      lineageName: this.getLineageName(lineageId)
    });
  }

  navigateToPerson(personId) {
    // Provide navigation context to all components
    this.fireEvent('context:person-changed', {
      personId,
      context: this.buildNavigationContext(personId)
    });
  }
}
```

### Timeline → Search Integration
```javascript
// Timeline can trigger searches based on time periods
class TimelineComponent extends BaseComponent {
  onTimeRangeSelected(startYear, endYear) {
    // Fire event that search can respond to
    this.fireEvent('timeline:range-selected', {
      startYear,
      endYear,
      intent: 'search-time-range'
    });
  }
}

// Search component can respond to timeline selections
class SearchComponent extends BaseComponent {
  attachEventListeners() {
    super.attachEventListeners();

    document.addEventListener('auntruth:timeline:range-selected', (e) => {
      if (e.detail.intent === 'search-time-range') {
        this.setDateRangeFilter(e.detail.startYear, e.detail.endYear);
        this.performSearch();
      }
    });
  }
}
```

## Data Sharing Patterns

### Shared Data Manager
```javascript
class DataManager {
  constructor() {
    this.cache = new Map();
    this.metadata = null;
    this.subscribers = new Map();
  }

  // Subscribe to data changes
  subscribe(dataType, callback) {
    if (!this.subscribers.has(dataType)) {
      this.subscribers.set(dataType, []);
    }
    this.subscribers.get(dataType).push(callback);
  }

  // Notify subscribers of data changes
  notifySubscribers(dataType, data) {
    const callbacks = this.subscribers.get(dataType) || [];
    callbacks.forEach(callback => callback(data));
  }

  async getPersonData(personId) {
    const cacheKey = `person-${personId}`;

    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Load person data and notify subscribers
    const personData = await this.fetchPersonData(personId);
    this.cache.set(cacheKey, personData);
    this.notifySubscribers('person-loaded', personData);

    return personData;
  }
}
```

### Context Sharing
```javascript
class ContextManager {
  constructor() {
    this.currentContext = {
      personId: null,
      lineageId: null,
      pageType: null,
      navigationHistory: []
    };
  }

  updateContext(newContext) {
    const oldContext = { ...this.currentContext };
    this.currentContext = { ...this.currentContext, ...newContext };

    // Notify all components of context change
    this.fireContextChange(oldContext, this.currentContext);
  }

  fireContextChange(oldContext, newContext) {
    document.dispatchEvent(new CustomEvent('auntruth:context:changed', {
      detail: { oldContext, newContext }
    }));
  }

  getContext() {
    return { ...this.currentContext };
  }
}
```

## URL State Integration

### URL Router Integration Pattern
```javascript
class URLRouter {
  constructor() {
    this.routes = new Map();
    this.componentRegistry = null;
  }

  setComponentRegistry(registry) {
    this.componentRegistry = registry;
  }

  // Route changes notify relevant components
  handleRoute(path, params) {
    // Parse URL and determine which components need updating
    const context = this.parseURLContext(path, params);

    // Update components based on URL
    if (context.personId) {
      this.updateComponentsForPerson(context.personId);
    }

    if (context.searchQuery) {
      this.updateComponentsForSearch(context.searchQuery, context.filters);
    }

    if (context.timelineRange) {
      this.updateComponentsForTimeline(context.timelineRange);
    }
  }

  updateComponentsForPerson(personId) {
    // Update family tree
    const familyTree = this.componentRegistry.get('family-tree');
    if (familyTree) {
      familyTree.focusOnPerson(personId);
    }

    // Update relationship navigator
    const relationshipNav = this.componentRegistry.get('relationship-navigator');
    if (relationshipNav) {
      relationshipNav.setCurrentPerson(personId);
    }
  }
}
```

## Component Lifecycle Integration

### Initialization Order
```javascript
class ApplicationInitializer {
  constructor() {
    this.initOrder = [
      'data-manager',
      'context-manager',
      'url-router',
      'navigation',
      'search',
      'family-tree',
      'timeline',
      'relationship-navigator',
      'information-disclosure'
    ];
  }

  async initializeApplication() {
    const componentRegistry = new ComponentRegistry();

    // Initialize components in dependency order
    for (const componentName of this.initOrder) {
      try {
        const component = await this.loadComponent(componentName);
        componentRegistry.register(componentName, component);
        await component.init();
      } catch (error) {
        console.error(`Failed to initialize ${componentName}:`, error);
        // Continue initialization of other components
      }
    }

    // Connect components after all are initialized
    this.connectComponents(componentRegistry);

    return componentRegistry;
  }

  connectComponents(registry) {
    // Connect URL router to component registry
    const router = registry.get('url-router');
    if (router) {
      router.setComponentRegistry(registry);
    }

    // Connect data manager to all components
    const dataManager = registry.get('data-manager');
    if (dataManager) {
      registry.components.forEach(component => {
        if (component.setDataManager) {
          component.setDataManager(dataManager);
        }
      });
    }
  }
}
```

## Error Handling Integration

### Cross-Component Error Recovery
```javascript
class ErrorRecoveryManager {
  constructor(componentRegistry) {
    this.componentRegistry = componentRegistry;
    this.setupGlobalErrorHandling();
  }

  setupGlobalErrorHandling() {
    document.addEventListener('auntruth:component:error', (e) => {
      this.handleComponentError(e.detail.componentName, e.detail.error);
    });
  }

  handleComponentError(componentName, error) {
    console.error(`Component ${componentName} error:`, error);

    // Try to recover dependent components
    const dependentComponents = this.getDependentComponents(componentName);

    dependentComponents.forEach(depComponent => {
      try {
        depComponent.handleDependencyError(componentName, error);
      } catch (recoveryError) {
        console.error(`Failed to recover dependent component:`, recoveryError);
      }
    });
  }

  getDependentComponents(componentName) {
    // Return components that depend on the failed component
    const dependencies = {
      'data-manager': ['search', 'family-tree', 'timeline', 'relationship-navigator'],
      'navigation': ['search', 'family-tree'],
      'search': ['family-tree'],
      // ... etc
    };

    return (dependencies[componentName] || [])
      .map(name => this.componentRegistry.get(name))
      .filter(Boolean);
  }
}
```