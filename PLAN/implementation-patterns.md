# Implementation Patterns & Best Practices

## Development Workflow Patterns

### File Modification Guidelines
- **NEVER modify existing HTML files** - All enhancements must be through JavaScript/CSS injection
- **ALWAYS preserve URLs** - Existing genealogy URLs must continue working
- **PREFER editing existing files** to creating new ones when possible
- **FOLLOW progressive enhancement** - Site must work without JavaScript

### Code Organization Patterns
```
/docs/new/
├── js/
│   ├── core/
│   │   ├── app.js                 # Main application controller
│   │   ├── data-manager.js        # Centralized data access
│   │   └── base-component.js      # Base class for components
│   ├── components/
│   │   ├── navigation.js          # Navigation enhancements
│   │   ├── search.js              # Search functionality
│   │   ├── family-tree.js         # Tree visualization
│   │   └── [component-name].js    # Individual components
│   ├── utils/
│   │   ├── url-router.js          # URL routing utilities
│   │   └── performance.js         # Performance utilities
│   └── data/
│       ├── metadata.json          # Site metadata
│       └── lineages/              # Lineage-specific data
├── css/
│   ├── main.css                   # Base responsive styles
│   ├── components/                # Component-specific styles
│   └── [feature].css              # Feature-specific styles
```

## Performance Optimization Patterns

### Lazy Loading Pattern
```javascript
class LazyLoadManager {
  constructor() {
    this.loadingQueue = [];
    this.loadedComponents = new Set();
  }

  async loadComponent(componentName, options = {}) {
    if (this.loadedComponents.has(componentName)) {
      return this.getExistingComponent(componentName);
    }

    try {
      const module = await import(`./components/${componentName}.js`);
      const ComponentClass = module.default;
      const component = new ComponentClass(options);

      await component.init();
      this.loadedComponents.add(componentName);

      return component;
    } catch (error) {
      console.error(`Failed to lazy load ${componentName}:`, error);
      return null;
    }
  }

  preloadComponent(componentName) {
    // Preload component module without initializing
    import(`./components/${componentName}.js`);
  }
}
```

### Memory Management Pattern
```javascript
class ComponentMemoryManager {
  constructor() {
    this.activeComponents = new Map();
    this.inactiveComponents = new Map();
  }

  activateComponent(name, component) {
    // Deactivate previous if memory constrained
    if (this.isMemoryConstrained()) {
      this.deactivateOldestComponent();
    }

    this.activeComponents.set(name, {
      component,
      lastAccessed: Date.now()
    });
  }

  deactivateComponent(name) {
    const componentData = this.activeComponents.get(name);
    if (componentData) {
      componentData.component.deactivate();
      this.inactiveComponents.set(name, componentData);
      this.activeComponents.delete(name);
    }
  }

  isMemoryConstrained() {
    return performance.memory &&
           performance.memory.usedJSHeapSize > 50000000; // 50MB
  }
}
```

## Data Processing Patterns

### Genealogy Data Normalization
```javascript
class DataNormalizer {
  normalizePersonData(rawPerson) {
    return {
      id: this.normalizeId(rawPerson.id),
      name: this.normalizeName(rawPerson.name),
      birthDate: this.normalizeDate(rawPerson.birthDate),
      deathDate: this.normalizeDate(rawPerson.deathDate),
      birthLocation: this.normalizeLocation(rawPerson.birthLocation),
      deathLocation: this.normalizeLocation(rawPerson.deathLocation),
      relationships: this.normalizeRelationships(rawPerson),
      metadata: this.extractMetadata(rawPerson)
    };
  }

  normalizeDate(dateString) {
    if (!dateString || dateString.trim() === '') return null;

    // Handle various date formats
    const patterns = [
      /^(\w+),\s+(\w+)\s+(\d+),\s+(\d{4})$/, // "Sunday, November 12, 1944"
      /^(\w+)\s+(\d+),\s+(\d{4})$/,          // "November 12, 1944"
      /^(\d{4})$/,                           // "1944"
      /^circa\s+(\d{4})$/i                   // "circa 1944"
    ];

    for (const pattern of patterns) {
      const match = dateString.match(pattern);
      if (match) {
        return this.parseMatchedDate(match);
      }
    }

    return { original: dateString, normalized: null, uncertain: true };
  }

  normalizeRelationships(person) {
    const relationships = {
      parents: [],
      spouses: [],
      children: []
    };

    // Extract parent relationships
    if (person.father) {
      relationships.parents.push({
        type: 'father',
        name: person.father,
        personId: this.extractPersonId(person.father)
      });
    }

    if (person.mother) {
      relationships.parents.push({
        type: 'mother',
        name: person.mother,
        personId: this.extractPersonId(person.mother)
      });
    }

    // Extract spouse relationships
    ['spouse', 'spouse2', 'spouse3', 'spouse4'].forEach(spouseField => {
      if (person[spouseField] && person[spouseField].trim()) {
        relationships.spouses.push({
          name: person[spouseField],
          personId: this.extractPersonId(person[spouseField]),
          order: relationships.spouses.length + 1
        });
      }
    });

    return relationships;
  }

  extractPersonId(nameWithLineage) {
    // Extract person ID from format "Name [Lineage]"
    // This requires correlation with existing data
    const match = nameWithLineage.match(/^(.+?)\s*\[(.+?)\]$/);
    if (match) {
      const [, personName, lineageName] = match;
      return this.findPersonByNameAndLineage(personName.trim(), lineageName.trim());
    }
    return null;
  }
}
```

### Caching Patterns
```javascript
class IntelligentCache {
  constructor(options = {}) {
    this.cache = new Map();
    this.maxSize = options.maxSize || 100;
    this.ttl = options.ttl || 300000; // 5 minutes
    this.hitCount = new Map();
  }

  get(key) {
    const entry = this.cache.get(key);

    if (!entry) return null;

    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    // Update hit count for LRU
    this.hitCount.set(key, (this.hitCount.get(key) || 0) + 1);
    entry.lastAccessed = Date.now();

    return entry.data;
  }

  set(key, data) {
    // Evict if cache is full
    if (this.cache.size >= this.maxSize) {
      this.evictLeastUsed();
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      lastAccessed: Date.now()
    });

    this.hitCount.set(key, 0);
  }

  evictLeastUsed() {
    let leastUsedKey = null;
    let minHits = Infinity;
    let oldestAccess = Infinity;

    for (const [key, hits] of this.hitCount) {
      const entry = this.cache.get(key);
      if (hits < minHits || (hits === minHits && entry.lastAccessed < oldestAccess)) {
        minHits = hits;
        oldestAccess = entry.lastAccessed;
        leastUsedKey = key;
      }
    }

    if (leastUsedKey) {
      this.cache.delete(leastUsedKey);
      this.hitCount.delete(leastUsedKey);
    }
  }
}
```

## Error Handling Patterns

### Graceful Degradation Pattern
```javascript
class GracefulDegradationHandler {
  static wrapWithFallback(asyncFunction, fallbackFunction, context = null) {
    return async function(...args) {
      try {
        return await asyncFunction.apply(context, args);
      } catch (error) {
        console.warn('Primary function failed, using fallback:', error);

        if (typeof fallbackFunction === 'function') {
          return fallbackFunction.apply(context, args);
        }

        return fallbackFunction; // Return static fallback value
      }
    };
  }

  static createRobustComponent(ComponentClass, fallbackContent = null) {
    return class RobustWrapper extends ComponentClass {
      async init() {
        try {
          await super.init();
        } catch (error) {
          console.error(`${ComponentClass.name} failed to initialize:`, error);
          this.showFallback(fallbackContent);
        }
      }

      showFallback(content) {
        if (this.element) {
          this.element.innerHTML = content ||
            `<div class="component-fallback">
               <p>Enhanced features unavailable. Basic functionality remains accessible.</p>
             </div>`;
        }
      }
    };
  }
}
```

### Error Recovery Pattern
```javascript
class ErrorRecoverySystem {
  constructor() {
    this.errorCount = new Map();
    this.maxRetries = 3;
    this.recoveryStrategies = new Map();
  }

  registerRecoveryStrategy(errorType, strategy) {
    this.recoveryStrategies.set(errorType, strategy);
  }

  async executeWithRecovery(operation, errorContext) {
    const errorKey = this.getErrorKey(errorContext);
    const currentErrors = this.errorCount.get(errorKey) || 0;

    try {
      const result = await operation();
      // Reset error count on success
      this.errorCount.delete(errorKey);
      return result;
    } catch (error) {
      this.errorCount.set(errorKey, currentErrors + 1);

      if (currentErrors < this.maxRetries) {
        // Try recovery strategy
        const strategy = this.recoveryStrategies.get(error.name);
        if (strategy) {
          try {
            await strategy(error, errorContext);
            // Retry after recovery attempt
            return this.executeWithRecovery(operation, errorContext);
          } catch (recoveryError) {
            console.error('Recovery strategy failed:', recoveryError);
          }
        }
      }

      // All recovery attempts failed
      throw new Error(`Operation failed after ${this.maxRetries} retries: ${error.message}`);
    }
  }

  getErrorKey(context) {
    return `${context.component || 'unknown'}:${context.operation || 'unknown'}`;
  }
}
```

## Security Patterns

### Safe Data Processing
```javascript
class SecureDataProcessor {
  static sanitizeHTMLString(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  static validatePersonId(id) {
    // Ensure person ID is numeric and within expected range
    const numId = parseInt(id, 10);
    return !isNaN(numId) && numId > 0 && numId < 100000;
  }

  static sanitizeSearchQuery(query) {
    // Remove potentially dangerous characters but preserve genealogy-relevant ones
    return query
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/[<>\"']/g, '')
      .substring(0, 100); // Limit length
  }

  static validateURL(url, allowedDomains = []) {
    try {
      const urlObj = new URL(url);

      // Only allow same origin or explicitly allowed domains
      if (urlObj.origin !== window.location.origin &&
          !allowedDomains.includes(urlObj.hostname)) {
        throw new Error('URL not allowed');
      }

      return true;
    } catch {
      return false;
    }
  }
}
```

## Monitoring & Analytics Patterns

### Performance Monitoring
```javascript
class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = [];
  }

  startMeasurement(name, category = 'general') {
    const key = `${category}:${name}`;
    performance.mark(`${key}:start`);

    return {
      end: () => this.endMeasurement(key),
      category,
      name
    };
  }

  endMeasurement(key) {
    performance.mark(`${key}:end`);
    performance.measure(key, `${key}:start`, `${key}:end`);

    const entries = performance.getEntriesByName(key, 'measure');
    if (entries.length > 0) {
      const duration = entries[entries.length - 1].duration;
      this.recordMetric(key, duration);
      return duration;
    }
    return null;
  }

  recordMetric(name, value, metadata = {}) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }

    this.metrics.get(name).push({
      value,
      timestamp: Date.now(),
      metadata
    });

    // Notify observers
    this.notifyObservers(name, value, metadata);
  }

  addObserver(callback) {
    this.observers.push(callback);
  }

  notifyObservers(name, value, metadata) {
    this.observers.forEach(observer => {
      try {
        observer(name, value, metadata);
      } catch (error) {
        console.error('Performance observer error:', error);
      }
    });
  }

  getMetrics(name = null) {
    if (name) {
      return this.metrics.get(name) || [];
    }
    return Object.fromEntries(this.metrics);
  }

  getAverageMetric(name) {
    const values = this.metrics.get(name) || [];
    if (values.length === 0) return 0;

    const sum = values.reduce((total, entry) => total + entry.value, 0);
    return sum / values.length;
  }
}