# Component Architecture Pattern

## Base Component Pattern

All major components should extend a common BaseComponent class that provides:

### Core Component Structure
```javascript
class BaseComponent {
  constructor(options = {}) {
    this.options = options;
    this.element = null;
    this.initialized = false;
    this.mobile = this.detectMobile();
  }

  async init() {
    if (this.initialized) return;
    await this.render();
    this.attachEventListeners();
    this.initialized = true;
  }

  async render() {
    // Override in subclasses
  }

  attachEventListeners() {
    // Override in subclasses
  }

  destroy() {
    if (this.element) {
      this.element.removeEventListeners();
      this.element = null;
    }
    this.initialized = false;
  }

  detectMobile() {
    return window.innerWidth <= 768 || 'ontouchstart' in window;
  }
}
```

## Component Integration Patterns

### Data Manager Integration
Components should use a shared DataManager for accessing genealogy data:

```javascript
class ComponentExample extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
  }

  async loadPersonData(personId) {
    return await this.dataManager.getPersonData(personId);
  }
}
```

### Page Detection Pattern
Components need to detect current page context:

```javascript
detectCurrentPage() {
  const path = window.location.pathname;
  const filename = path.split('/').pop() || 'index.html';

  let pageType = 'unknown';
  let pageId = null;

  if (filename.startsWith('XF')) {
    pageType = 'person';
    pageId = filename.replace('.htm', '').replace('XF', '');
  } else if (filename.startsWith('XI')) {
    pageType = 'image';
    pageId = filename.replace('.htm', '').replace('XI', '');
  } else if (filename.startsWith('THF')) {
    pageType = 'thumbnail';
    pageId = filename.replace('.htm', '').replace('THF', '');
  }

  return { path, filename, type: pageType, pageId };
}
```

### Lineage Detection Pattern
Components need to detect current lineage context:

```javascript
detectCurrentLineage() {
  const path = window.location.pathname;
  const lineageMatch = path.match(/\/L(\d+)\//);

  if (lineageMatch) {
    const lineageNumber = lineageMatch[1];
    const lineageNames = {
      '1': 'Hagborg-Hansson',
      '2': 'Nelson',
      '3': 'Pringle-Hambley',
      // ... etc
    };

    return {
      number: lineageNumber,
      name: lineageNames[lineageNumber],
      path: `/auntruth/new/htm/L${lineageNumber}/`
    };
  }

  return null;
}
```

## Component Loading Strategy

### Progressive Component Loading
```javascript
class ComponentLoader {
  async loadComponent(componentName, options = {}) {
    try {
      const module = await import(`./components/${componentName}.js`);
      const ComponentClass = module.default;
      const component = new ComponentClass(options);
      await component.init();
      return component;
    } catch (error) {
      console.error(`Failed to load component ${componentName}:`, error);
      return null;
    }
  }
}
```

### Component Registration Pattern
```javascript
class ComponentRegistry {
  constructor() {
    this.components = new Map();
  }

  register(name, component) {
    this.components.set(name, component);
  }

  get(name) {
    return this.components.get(name);
  }

  initializeForPage(pageType) {
    // Initialize components appropriate for page type
    switch (pageType) {
      case 'person':
        this.loadComponent('navigation');
        this.loadComponent('relationship-navigator');
        this.loadComponent('information-disclosure');
        break;
      case 'index':
        this.loadComponent('navigation');
        this.loadComponent('search');
        break;
    }
  }
}
```

## Event Communication Pattern

### Component Events
Components should communicate via events rather than direct coupling:

```javascript
class ComponentWithEvents extends BaseComponent {
  fireEvent(eventName, data) {
    const event = new CustomEvent(`auntruth:${eventName}`, {
      detail: data,
      bubbles: true
    });
    document.dispatchEvent(event);
  }

  attachEventListeners() {
    super.attachEventListeners();

    // Listen for events from other components
    document.addEventListener('auntruth:person-selected', (e) => {
      this.handlePersonSelected(e.detail);
    });
  }
}
```

## Error Handling Pattern

### Graceful Degradation
```javascript
class RobustComponent extends BaseComponent {
  async init() {
    try {
      await super.init();
    } catch (error) {
      console.error(`Component ${this.constructor.name} failed to initialize:`, error);
      this.showFallbackContent();
    }
  }

  showFallbackContent() {
    // Provide basic functionality even if enhanced features fail
    if (this.element) {
      this.element.innerHTML = '<p>Basic functionality available</p>';
    }
  }
}
```