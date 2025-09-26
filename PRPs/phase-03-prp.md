# PRP: Phase 3 Advanced Features Implementation

## Executive Summary

**Task:** Implement Phase 3 Advanced Features - Relationship Navigator, Timeline Visualization, and Modern URL Routing
**Duration:** 7-10 days
**Priority:** High Impact - Completes comprehensive UX modernization of AuntieRuth.com
**Complexity:** High - Three interconnected advanced components requiring sophisticated algorithms and integrations

This PRP implements the final phase of AuntieRuth.com modernization, delivering relationship navigation, timeline visualization, and modern URL routing that transform the site into a cutting-edge genealogy research platform comparable to commercial services.

## Background & Context

### Prerequisites - CRITICAL READING REQUIRED
Before implementation, you MUST read and understand:

1. **Architecture Foundation:**
   - `/docs/new/js/core/base-component.js` - Component architecture pattern to follow
   - `/docs/new/js/core/data-manager.js` - Data loading and caching system
   - `/docs/new/js/phase2-integration.js` - Cross-component communication patterns

2. **Existing Components:**
   - `/docs/new/js/components/navigation-enhanced.js` - Navigation integration patterns
   - `/docs/new/js/components/family-tree.js` - D3.js visualization patterns
   - `/docs/new/js/components/enhanced-search.js` - Search integration patterns

3. **Data Structure:**
   - `/docs/new/js/data/lineages/L*.json` - Person data format and relationships
   - `/docs/new/js/data/metadata.json` - Data organization and lineage mapping

4. **Requirements Documentation:**
   - `PRPs/priority-04.md` - Relationship Navigator requirements
   - `PRPs/priority-06.md` - Timeline Visualization requirements
   - `PRPs/priority-08.md` - URL Routing requirements

### Current Site Capabilities (Post Phase 1 & 2)
- Foundation architecture with BaseComponent class and DataManager
- Enhanced navigation with family context
- Advanced search with pre-built indices and filtering
- Interactive family tree visualization with D3.js
- Progressive information disclosure
- Mobile-responsive framework

### Data Structure Understanding

**Critical:** The genealogy data uses specific relationship format:
```json
{
  "father": "Walter Arnold Hagborg [Hagborg-Hansson]",
  "mother": "Mary Irene Pringle-Hagborg [Pringle-Hambley]",
  "spouse": "Ruth Ann Nelson-Hagborg [Nelson]"
}
```

Pattern: `"Name [Lineage-Name]"` where lineage indicates which family line.

## Implementation Blueprint

### Phase 3.1: Relationship Navigator Component (Days 1-3)

#### Day 1: Relationship Graph Foundation

**File:** `docs/new/js/components/relationship-navigator.js`

```javascript
import BaseComponent from '../core/base-component.js';
import DataManager from '../core/data-manager.js';

/**
 * Relationship Navigator Component
 * Intelligent family relationship exploration with path finding
 */
class RelationshipNavigatorComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.relationshipGraph = null;
    this.currentPerson = null;
    this.relationshipHistory = [];
    this.sidebarVisible = window.innerWidth > 768;
  }

  async loadDependencies() {
    // Load relationship graph data
    await this.buildRelationshipGraph();
  }

  async buildRelationshipGraph() {
    console.log('Building relationship graph...');

    this.relationshipGraph = {
      nodes: new Map(),
      edges: new Map(),
      paths: new Map() // Pre-computed relationship paths
    };

    // Load all lineage data to build complete graph
    const metadata = await this.dataManager.getMetadata();

    for (let lineageId = 0; lineageId <= 9; lineageId++) {
      const lineageData = await this.dataManager.getLineageData(lineageId.toString());
      if (!lineageData) continue;

      lineageData.people.forEach(person => {
        this.addPersonToGraph(person);
      });
    }

    await this.precomputeRelationshipPaths();
    console.log(`Relationship graph built: ${this.relationshipGraph.nodes.size} people`);
  }

  addPersonToGraph(person) {
    // Add person node
    this.relationshipGraph.nodes.set(person.id, {
      person: person,
      relationships: {
        parents: [],
        children: [],
        spouses: [],
        siblings: []
      }
    });

    // Parse and add relationships
    const relationships = this.parseRelationships(person);
    const node = this.relationshipGraph.nodes.get(person.id);

    // Add parent relationships
    relationships.parents.forEach(parentId => {
      node.relationships.parents.push(parentId);
      this.addReverseRelationship(parentId, person.id, 'children');
    });

    // Add spouse relationships
    relationships.spouses.forEach(spouseId => {
      node.relationships.spouses.push(spouseId);
      this.addReverseRelationship(spouseId, person.id, 'spouses');
    });
  }

  parseRelationships(person) {
    const relationships = { parents: [], spouses: [] };

    // Parse father/mother format: "Name [Lineage]"
    [person.father, person.mother].forEach(parent => {
      if (parent && parent.trim()) {
        const personId = this.extractPersonIdFromRelationship(parent);
        if (personId) relationships.parents.push(personId);
      }
    });

    // Parse spouse relationships
    [person.spouse, person.spouse2, person.spouse3, person.spouse4].forEach(spouse => {
      if (spouse && spouse.trim()) {
        const personId = this.extractPersonIdFromRelationship(spouse);
        if (personId) relationships.spouses.push(personId);
      }
    });

    return relationships;
  }

  extractPersonIdFromRelationship(relationshipString) {
    // Parse "Walter Arnold Hagborg [Hagborg-Hansson]" format
    const match = relationshipString.match(/^(.+?)\s*\[(.+?)\]$/);
    if (!match) return null;

    const [, name, lineageName] = match;

    // Search for person by name and lineage
    // This is simplified - in practice you'd need fuzzy matching
    for (const [personId, node] of this.relationshipGraph.nodes) {
      if (node.person.name === name.trim() &&
          node.person.lineageName === lineageName.trim()) {
        return personId;
      }
    }

    return null;
  }

  async precomputeRelationshipPaths() {
    // Pre-compute paths for performance (BFS algorithm)
    const personIds = Array.from(this.relationshipGraph.nodes.keys());

    for (let i = 0; i < Math.min(personIds.length, 500); i++) { // Limit for performance
      const sourceId = personIds[i];
      const paths = this.findRelationshipPaths(sourceId, 4); // Max 4 degrees

      this.relationshipGraph.paths.set(sourceId, paths);

      if (i % 100 === 0) {
        console.log(`Pre-computed paths for ${i}/${Math.min(personIds.length, 500)} people`);
      }
    }
  }

  findRelationshipPaths(sourceId, maxDegree = 6) {
    const paths = new Map();
    const visited = new Set();
    const queue = [{ personId: sourceId, path: [], degree: 0 }];

    while (queue.length > 0) {
      const { personId, path, degree } = queue.shift();

      if (visited.has(personId) || degree > maxDegree) continue;
      visited.add(personId);

      if (personId !== sourceId) {
        paths.set(personId, {
          path: [...path],
          degree: degree,
          relationship: this.describeRelationship(path)
        });
      }

      // Add connected people to queue
      const node = this.relationshipGraph.nodes.get(personId);
      if (node) {
        Object.entries(node.relationships).forEach(([relType, relatedIds]) => {
          relatedIds.forEach(relatedId => {
            if (!visited.has(relatedId)) {
              queue.push({
                personId: relatedId,
                path: [...path, { from: personId, to: relatedId, type: relType }],
                degree: degree + 1
              });
            }
          });
        });
      }
    }

    return paths;
  }

  describeRelationship(path) {
    if (path.length === 0) return 'self';
    if (path.length === 1) {
      const step = path[0];
      switch (step.type) {
        case 'parents': return 'parent';
        case 'children': return 'child';
        case 'spouses': return 'spouse';
        case 'siblings': return 'sibling';
      }
    }

    // Complex relationships
    if (path.length === 2) {
      const [step1, step2] = path;
      if (step1.type === 'parents' && step2.type === 'parents') return 'grandparent';
      if (step1.type === 'children' && step2.type === 'children') return 'grandchild';
      if (step1.type === 'siblings' && step2.type === 'children') return 'aunt/uncle';
      if (step1.type === 'parents' && step2.type === 'siblings') return 'aunt/uncle';
    }

    return `${path.length} degrees of separation`;
  }

  async render() {
    // Create relationship sidebar HTML
    const sidebarHtml = this.generateSidebarHTML();

    // Insert into page
    const existingSidebar = document.querySelector('.relationship-sidebar');
    if (existingSidebar) {
      existingSidebar.outerHTML = sidebarHtml;
    } else {
      document.body.insertAdjacentHTML('beforeend', sidebarHtml);
    }

    this.element = document.querySelector('.relationship-sidebar');

    if (this.currentPerson) {
      await this.updateFamilyContext();
    }
  }

  generateSidebarHTML() {
    return `
      <div class="relationship-sidebar ${this.sidebarVisible ? 'visible' : 'hidden'}"
           role="complementary" aria-label="Family relationships">

        <div class="sidebar-header">
          <button class="sidebar-toggle"
                  aria-expanded="${this.sidebarVisible}"
                  title="Toggle relationship navigator">
            <span class="toggle-icon">${this.sidebarVisible ? '◀' : '▶'}</span>
          </button>

          <h3 class="sidebar-title">Family Context</h3>

          <button class="relationship-finder-btn"
                  title="Find relationship between people"
                  aria-label="Relationship finder">
            🔍 Find Relationship
          </button>
        </div>

        <div class="sidebar-content">
          <div class="current-person-section">
            ${this.generateCurrentPersonCard()}
          </div>

          <div class="immediate-family-section">
            ${this.generateImmediateFamilySection()}
          </div>

          <div class="relationship-tools-section">
            ${this.generateRelationshipTools()}
          </div>

          <div class="recent-exploration-section">
            ${this.generateRecentExploration()}
          </div>
        </div>
      </div>
    `;
  }

  // ... additional methods for UI generation and event handling
}

export default RelationshipNavigatorComponent;
```

#### Day 2-3: Complete Relationship Navigator Implementation

Continue with sidebar UI, relationship finder modal, and integration with existing components.

### Phase 3.2: Timeline Visualization Component (Days 4-6)

#### Day 4-5: Timeline Data Processing and D3.js Implementation

**File:** `docs/new/js/components/timeline.js`

```javascript
import BaseComponent from '../core/base-component.js';
import DataManager from '../core/data-manager.js';

/**
 * Timeline Component
 * Chronological visualization of family events with historical context
 * Uses D3.js following patterns from family-tree.js
 */
class TimelineComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.timelineData = [];
    this.historicalEvents = [];
    this.svg = null;
    this.currentView = 'decade'; // century, decade, year
    this.dateRange = { start: 1800, end: 2025 };
    this.selectedLineages = [];
  }

  async loadDependencies() {
    // Load D3.js if not available (following family-tree.js pattern)
    if (!window.d3) {
      await this.loadD3Js();
    }
  }

  async loadD3Js() {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/d3@7';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async render() {
    await this.loadTimelineData();
    await this.loadHistoricalContext();

    const timelineHtml = this.generateTimelineInterface();

    const container = document.getElementById('timeline-container') ||
                     this.createTimelineContainer();

    container.innerHTML = timelineHtml;
    this.element = container.querySelector('.timeline-component');

    await this.renderTimelineVisualization();
  }

  async loadTimelineData() {
    console.log('Loading timeline data...');
    this.timelineData = [];

    // Load events from all lineages
    for (let lineageId = 0; lineageId <= 9; lineageId++) {
      const lineageData = await this.dataManager.getLineageData(lineageId.toString());
      if (!lineageData) continue;

      lineageData.people.forEach(person => {
        // Birth events
        if (person.birthDate) {
          const birthYear = this.parseYear(person.birthDate);
          if (birthYear) {
            this.timelineData.push({
              type: 'birth',
              year: birthYear,
              date: person.birthDate,
              person: person,
              location: person.birthLocation,
              lineage: person.lineage,
              description: `${person.name} born`
            });
          }
        }

        // Death events
        if (person.deathDate) {
          const deathYear = this.parseYear(person.deathDate);
          if (deathYear) {
            this.timelineData.push({
              type: 'death',
              year: deathYear,
              date: person.deathDate,
              person: person,
              location: person.deathLocation,
              lineage: person.lineage,
              description: `${person.name} died`
            });
          }
        }
      });
    }

    // Sort chronologically
    this.timelineData.sort((a, b) => a.year - b.year);
    console.log(`Loaded ${this.timelineData.length} timeline events`);
  }

  parseYear(dateString) {
    if (!dateString) return null;

    // Handle various genealogy date formats
    const patterns = [
      /\b(19|20)\d{2}\b/, // Year anywhere in string
      /^(\d{4})/, // Year at start
      /circa\s*(\d{4})/i // Circa dates
    ];

    for (const pattern of patterns) {
      const match = dateString.match(pattern);
      if (match) {
        const year = parseInt(match[1] || match[0]);
        if (year >= 1800 && year <= 2025) {
          return year;
        }
      }
    }

    return null;
  }

  async loadHistoricalContext() {
    // Historical events for context
    this.historicalEvents = [
      { year: 1867, event: 'Canadian Confederation', type: 'political' },
      { year: 1885, event: 'Canadian Pacific Railway completed', type: 'infrastructure' },
      { year: 1914, event: 'World War I begins', type: 'war' },
      { year: 1918, event: 'World War I ends', type: 'war' },
      { year: 1929, event: 'Great Depression begins', type: 'economic' },
      { year: 1939, event: 'World War II begins', type: 'war' },
      { year: 1945, event: 'World War II ends', type: 'war' },
      // Add more historical context relevant to genealogy research
    ];
  }

  async renderTimelineVisualization() {
    const container = this.element.querySelector('.timeline-viewport');
    const width = container.clientWidth;
    const height = 500;

    // Create SVG using D3.js (following family-tree.js patterns)
    this.svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('class', 'timeline-svg');

    // Set up scales
    const filteredEvents = this.getFilteredEvents();
    const years = filteredEvents.map(e => e.year);
    const minYear = Math.min(...years, this.dateRange.start);
    const maxYear = Math.max(...years, this.dateRange.end);

    const xScale = d3.scaleLinear()
      .domain([minYear, maxYear])
      .range([60, width - 60]);

    // Draw timeline axis
    this.drawTimelineAxis(xScale, minYear, maxYear);

    // Draw historical events
    this.drawHistoricalEvents(xScale);

    // Draw family events
    this.drawFamilyEvents(xScale, filteredEvents);
  }

  drawTimelineAxis(xScale, minYear, maxYear) {
    const axis = d3.axisBottom(xScale)
      .tickFormat(d3.format('d'))
      .ticks(10);

    this.svg.append('g')
      .attr('class', 'timeline-axis')
      .attr('transform', 'translate(0, 50)')
      .call(axis);
  }

  drawHistoricalEvents(xScale) {
    const historicalGroup = this.svg.append('g')
      .attr('class', 'historical-events');

    historicalGroup.selectAll('.historical-event')
      .data(this.historicalEvents)
      .enter()
      .append('line')
      .attr('class', d => `historical-event ${d.type}`)
      .attr('x1', d => xScale(d.year))
      .attr('x2', d => xScale(d.year))
      .attr('y1', 60)
      .attr('y2', 90)
      .append('title')
      .text(d => `${d.year}: ${d.event}`);
  }

  drawFamilyEvents(xScale, events) {
    const eventGroup = this.svg.append('g')
      .attr('class', 'family-events');

    const eventHeight = 20;
    let currentY = 100;

    // Group events by year for better visualization
    const eventsByYear = d3.group(events, d => d.year);

    eventsByYear.forEach((yearEvents, year) => {
      yearEvents.forEach((event, index) => {
        const x = xScale(year);
        const y = currentY + (index * eventHeight);

        // Event circle
        eventGroup.append('circle')
          .attr('class', `family-event ${event.type}-event lineage-${event.lineage}`)
          .attr('cx', x)
          .attr('cy', y)
          .attr('r', 4)
          .on('click', () => this.showEventDetails(event))
          .on('mouseover', (e) => this.showEventTooltip(event, e))
          .append('title')
          .text(`${event.description} (${event.date})`);
      });

      currentY += Math.max(yearEvents.length * eventHeight, 30);
    });
  }

  // ... additional timeline methods
}

export default TimelineComponent;
```

#### Day 6: Timeline UI Controls and Mobile Optimization

### Phase 3.3: Modern URL Routing System (Days 7-9)

#### Day 7-8: URL Router Implementation

**File:** `docs/new/js/utils/url-router.js`

```javascript
/**
 * Modern URL Router with Legacy Compatibility
 * Implements History API routing for single-page application features
 * Maintains backward compatibility with existing genealogy URLs
 */
class URLRouter {
  constructor() {
    this.routes = new Map();
    this.currentRoute = null;
    this.legacyRedirects = new Map();
    this.history = [];
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;

    this.setupRoutes();
    this.setupLegacyRedirects();
    this.handleInitialRoute();
    this.setupEventListeners();

    this.initialized = true;
  }

  setupRoutes() {
    // Modern clean URL patterns
    this.addRoute('/', this.handleHomePage.bind(this));
    this.addRoute('/search', this.handleSearchPage.bind(this));
    this.addRoute('/search/:query', this.handleSearchWithQuery.bind(this));
    this.addRoute('/person/:slug', this.handlePersonPage.bind(this));
    this.addRoute('/person/:slug/:section', this.handlePersonSection.bind(this));
    this.addRoute('/family-tree', this.handleFamilyTreePage.bind(this));
    this.addRoute('/family-tree/:person', this.handleFamilyTreePerson.bind(this));
    this.addRoute('/timeline', this.handleTimelinePage.bind(this));
    this.addRoute('/timeline/:period', this.handleTimelinePeriod.bind(this));
    this.addRoute('/lineage/:lineageName', this.handleLineagePage.bind(this));
    this.addRoute('/relationship/:person1/:person2', this.handleRelationshipPage.bind(this));
  }

  setupLegacyRedirects() {
    // Map legacy genealogy URLs to modern equivalents
    // Pattern: /auntruth/new/htm/L{lineage}/XF{id}.htm -> /person/{slug}
    this.addPatternRedirect(
      /^\/auntruth\/new\/htm\/L(\d+)\/XF(\d+)\.htm$/,
      async (matches) => {
        const [, lineageId, personId] = matches;
        return await this.generatePersonSlugURL(personId, lineageId);
      }
    );

    // Pattern: /auntruth/new/htm/L{lineage}/THF{id}.htm -> /person/{slug}/photos
    this.addPatternRedirect(
      /^\/auntruth\/new\/htm\/L(\d+)\/THF(\d+)\.htm$/,
      async (matches) => {
        const [, lineageId, personId] = matches;
        const baseURL = await this.generatePersonSlugURL(personId, lineageId);
        return `${baseURL}/photos`;
      }
    );

    // Pattern: /auntruth/new/htm/L{lineage}/ -> /lineage/{lineage-name}
    this.addPatternRedirect(
      /^\/auntruth\/new\/htm\/L(\d+)\/?$/,
      (matches) => {
        const [, lineageId] = matches;
        return this.generateLineageURL(lineageId);
      }
    );
  }

  addRoute(pattern, handler) {
    const regex = this.patternToRegex(pattern);
    this.routes.set(pattern, { regex, handler, pattern });
  }

  addPatternRedirect(pattern, handler) {
    if (!this.patternRedirects) {
      this.patternRedirects = [];
    }
    this.patternRedirects.push({ pattern, handler });
  }

  patternToRegex(pattern) {
    // Convert /person/:slug to /^\/person\/([^\/]+)$/
    const regexPattern = pattern
      .replace(/:[^\/]+/g, '([^\/]+)')
      .replace(/\//g, '\\/');
    return new RegExp(`^${regexPattern}$`);
  }

  async handleInitialRoute() {
    const currentPath = window.location.pathname;

    // Check for legacy URL that needs redirect
    const modernURL = await this.resolveLegacyURL(currentPath);
    if (modernURL && modernURL !== currentPath) {
      this.navigate(modernURL, true); // Replace history entry
      return;
    }

    // Handle modern URL
    this.handleRoute(currentPath);
  }

  async resolveLegacyURL(legacyPath) {
    // Direct mapping first
    if (this.legacyRedirects.has(legacyPath)) {
      return this.legacyRedirects.get(legacyPath);
    }

    // Pattern-based redirects
    if (this.patternRedirects) {
      for (const redirect of this.patternRedirects) {
        const matches = legacyPath.match(redirect.pattern);
        if (matches) {
          try {
            return await redirect.handler(matches);
          } catch (error) {
            console.error('Error in pattern redirect:', error);
          }
        }
      }
    }

    return null;
  }

  async generatePersonSlugURL(personId, lineageId) {
    try {
      const dataManager = new DataManager();
      const person = await dataManager.getPersonData(personId);

      if (person) {
        const slug = this.generatePersonSlug(person.name, personId);
        return `/person/${slug}`;
      }
    } catch (error) {
      console.error('Error generating person slug URL:', error);
    }

    return `/person/${personId}`;
  }

  generatePersonSlug(personName, personId) {
    const slug = personName
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();

    return `${slug}-${personId}`;
  }

  generateLineageURL(lineageId) {
    const lineageNames = {
      '0': 'all-families',
      '1': 'hagborg-hansson',
      '2': 'nelson',
      '3': 'pringle-hambley',
      '4': 'lathrop-lothropp',
      '5': 'ward',
      '6': 'selch-weiss',
      '7': 'stebbe',
      '8': 'lentz',
      '9': 'phoenix-rogerson'
    };

    return `/lineage/${lineageNames[lineageId] || `lineage-${lineageId}`}`;
  }

  handleRoute(path) {
    // Find matching route
    for (const [pattern, route] of this.routes) {
      const matches = path.match(route.regex);
      if (matches) {
        const params = this.extractParams(pattern, matches);
        this.currentRoute = { pattern, path, params };

        try {
          route.handler(params, path);
          this.addToHistory(path, params);
          return true;
        } catch (error) {
          console.error('Route handler error:', error);
          this.handleNotFound(path);
          return false;
        }
      }
    }

    this.handleNotFound(path);
    return false;
  }

  extractParams(pattern, matches) {
    const paramNames = pattern.match(/:[^\/]+/g) || [];
    const params = {};

    paramNames.forEach((paramName, index) => {
      const cleanParamName = paramName.substring(1);
      params[cleanParamName] = matches[index + 1];
    });

    return params;
  }

  navigate(path, replace = false) {
    if (replace) {
      window.history.replaceState(null, '', path);
    } else {
      window.history.pushState(null, '', path);
    }

    this.handleRoute(path);
  }

  setupEventListeners() {
    // Handle browser back/forward
    window.addEventListener('popstate', () => {
      this.handleRoute(window.location.pathname);
    });

    // Handle internal link clicks
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href]');
      if (link && this.isInternalLink(link.href)) {
        e.preventDefault();
        const path = new URL(link.href).pathname;
        this.navigate(path);
      }
    });
  }

  isInternalLink(href) {
    try {
      const url = new URL(href, window.location.origin);
      return url.origin === window.location.origin &&
             !href.includes('.htm'); // Skip legacy .htm files
    } catch {
      return false;
    }
  }

  // Route Handlers
  async handlePersonPage(params, path) {
    const { slug } = params;
    const personId = this.extractPersonIdFromSlug(slug);

    try {
      const dataManager = new DataManager();
      const person = await dataManager.getPersonData(personId);

      if (person) {
        document.title = `${person.name} - AuntieRuth.com`;
        this.updateMetaTags(person);
        this.updateBreadcrumbs([
          { name: 'Home', path: '/' },
          { name: person.lineageName, path: this.generateLineageURL(person.lineage) },
          { name: person.name, path: path }
        ]);

        // Load person page components
        await this.loadComponent('relationship-navigator', { personId });
      } else {
        this.handleNotFound(path);
      }
    } catch (error) {
      console.error('Error loading person page:', error);
      this.handleNotFound(path);
    }
  }

  // ... additional route handlers and utility methods
}

// Global router instance
const router = new URLRouter();

// Initialize when DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => router.init());
} else {
  router.init();
}

export default router;
```

#### Day 9: Complete Integration and Testing

## Critical Implementation Context

### Data Structure Gotchas

1. **Relationship String Parsing:**
   ```
   Format: "Walter Arnold Hagborg [Hagborg-Hansson]"
   Extract: name="Walter Arnold Hagborg", lineage="Hagborg-Hansson"
   ```

2. **Date Parsing Complexity:**
   ```javascript
   // Handle various genealogy date formats
   "Tuesday, September 04, 1990"
   "March 1945"
   "1890"
   "circa 1920"
   ""  // Empty dates
   ```

3. **Performance Considerations:**
   - 2,985+ people requires efficient graph algorithms
   - Pre-compute relationship paths for common queries
   - Use Map/Set for O(1) lookups instead of arrays

### Integration Patterns

Follow the existing Phase 2 integration pattern in `docs/new/js/phase2-integration.js`:

```javascript
// Phase 3 Integration
class Phase3Integration {
  constructor() {
    this.components = {
      relationshipNavigator: null,
      timeline: null,
      urlRouter: null
    };
  }

  async init() {
    // Initialize components in dependency order
    this.urlRouter = new URLRouter();
    this.urlRouter.init();

    // Component-specific initialization based on page context
    if (this.shouldInitializeRelationshipNavigator()) {
      this.relationshipNavigator = new RelationshipNavigatorComponent();
      await this.relationshipNavigator.init();
    }

    if (this.shouldInitializeTimeline()) {
      this.timeline = new TimelineComponent();
      await this.timeline.init();
    }
  }
}
```

## Validation Gates (MUST BE EXECUTABLE)

### 1. Relationship Navigator Testing
```bash
# Test relationship graph building
node -e "
const RelationshipNavigator = require('./docs/new/js/components/relationship-navigator.js');
const nav = new RelationshipNavigator();
nav.buildRelationshipGraph().then(() => {
  console.log('✓ Relationship graph built successfully');
  console.log('✓ Node count:', nav.relationshipGraph.nodes.size);
}).catch(console.error);
"

# Test relationship path finding
# Should find path between David Hagborg (191) and Mary Nelson
node test-relationship-paths.js --person1=191 --person2=[find Mary Nelson ID]
```

### 2. Timeline Component Testing
```bash
# Test timeline data loading
node -e "
const Timeline = require('./docs/new/js/components/timeline.js');
const timeline = new Timeline();
timeline.loadTimelineData().then(() => {
  console.log('✓ Timeline data loaded:', timeline.timelineData.length, 'events');
  const yearRange = timeline.timelineData.map(e => e.year);
  console.log('✓ Year range:', Math.min(...yearRange), '-', Math.max(...yearRange));
}).catch(console.error);
"

# Test date parsing
node test-date-parsing.js --dates="Tuesday, September 04, 1990,March 1945,circa 1920"
```

### 3. URL Routing Testing
```bash
# Test legacy URL redirects
node test-url-routing.js --legacy-url="/auntruth/new/htm/L1/XF191.htm"
# Expected: /person/david-hagborg-191

# Test modern URL generation
node test-url-routing.js --person-id=191
# Expected: /person/david-hagborg-191

# Test routing performance
node test-url-performance.js --routes=100
```

### 4. Integration Testing
```bash
# Test cross-component communication
npm run test:phase3-integration

# Test mobile responsiveness
npm run test:mobile-compatibility

# Performance benchmarks
npm run benchmark:phase3
```

## CSS Integration Requirements

Create `docs/new/css/phase3-components.css`:

```css
/* Relationship Navigator Sidebar */
.relationship-sidebar {
  position: fixed;
  right: 0;
  top: 80px;
  width: 320px;
  height: calc(100vh - 80px);
  background: #fff;
  box-shadow: -2px 0 10px rgba(0,0,0,0.1);
  transform: translateX(100%);
  transition: transform 0.3s ease;
  z-index: 1000;
  overflow-y: auto;
}

.relationship-sidebar.visible {
  transform: translateX(0);
}

/* Timeline Component */
.timeline-component {
  width: 100%;
  margin: 20px 0;
}

.timeline-svg {
  width: 100%;
  height: 500px;
  border: 1px solid #ddd;
  background: #fafafa;
}

.family-event {
  cursor: pointer;
  transition: r 0.2s ease;
}

.family-event:hover {
  r: 6;
}

.birth-event { fill: #4CAF50; }
.death-event { fill: #F44336; }
.marriage-event { fill: #2196F3; }

/* Mobile Responsive */
@media (max-width: 768px) {
  .relationship-sidebar {
    width: 100%;
    transform: translateX(100%);
  }

  .timeline-component {
    margin: 10px 0;
  }

  .timeline-svg {
    height: 400px;
  }
}
```

## Success Metrics

### Performance Requirements
- **Relationship Path Finding:** < 100ms for typical queries
- **Timeline Rendering:** < 500ms initial load for typical date ranges
- **URL Routing:** < 50ms client-side navigation
- **Memory Usage:** < 50MB for relationship graph on mobile devices

### Functionality Requirements
- **Relationship Accuracy:** All genealogy relationships correctly identified
- **Timeline Completeness:** All person events with valid dates displayed
- **URL Compatibility:** 100% legacy URL redirect success
- **Cross-Component Integration:** Seamless communication between all Phase 1-3 components

## Implementation Tasks Checklist

### Phase 3.1: Relationship Navigator (Days 1-3)
- [ ] Build relationship graph from lineage data with proper parsing
- [ ] Implement BFS path-finding algorithm for relationship discovery
- [ ] Create relationship description engine for human-readable descriptions
- [ ] Build relationship sidebar UI with family context
- [ ] Implement relationship finder modal for "How are we related?" queries
- [ ] Add mobile-responsive relationship navigation
- [ ] Integration testing with existing navigation component

### Phase 3.2: Timeline Component (Days 4-6)
- [ ] Implement robust date parsing for various genealogy formats
- [ ] Build D3.js timeline visualization with zoom/pan capabilities
- [ ] Add historical context events and markers
- [ ] Create timeline filtering by lineage, date range, and event types
- [ ] Implement mobile touch optimization for timeline interaction
- [ ] Add timeline export functionality
- [ ] Integration testing with relationship navigator and search

### Phase 3.3: URL Routing System (Days 7-9)
- [ ] Implement History API client-side router
- [ ] Create legacy URL compatibility layer with pattern matching
- [ ] Build person slug generation and URL mapping system
- [ ] Add SEO optimization with dynamic meta tags and structured data
- [ ] Implement deep linking for all application states
- [ ] Create breadcrumb navigation system
- [ ] Complete integration testing across all components
- [ ] Performance optimization and mobile testing

### Final Integration (Day 10)
- [ ] Complete Phase 3 integration layer following Phase 2 pattern
- [ ] Cross-browser compatibility testing
- [ ] Performance benchmarking and optimization
- [ ] Documentation updates
- [ ] Deployment preparation and validation

## Files to Create

### Core Component Files
- `docs/new/js/components/relationship-navigator.js`
- `docs/new/js/components/timeline.js`
- `docs/new/js/utils/url-router.js`
- `docs/new/js/phase3-integration.js`

### Styling Files
- `docs/new/css/relationship-navigator.css`
- `docs/new/css/timeline.css`
- `docs/new/css/phase3-components.css`

### Data Processing Scripts
- `scripts/build-relationship-graph.js`
- `scripts/generate-timeline-data.js`
- `scripts/create-url-mappings.js`

### Testing Files
- `test-relationship-paths.js`
- `test-date-parsing.js`
- `test-url-routing.js`

## Post-Implementation Verification

1. **Functional Testing:**
   - Navigate genealogy relationships using relationship navigator
   - Explore family timeline with various date ranges and filters
   - Test legacy URL redirects and modern URL navigation
   - Verify cross-component integration workflows

2. **Performance Testing:**
   - Measure relationship graph loading and query performance
   - Test timeline rendering with large date ranges
   - Validate URL routing performance
   - Monitor memory usage during extended use

3. **User Experience Testing:**
   - Complete genealogy research workflows using all features
   - Test mobile experience across all components
   - Verify accessibility compliance
   - Confirm SEO improvements and social sharing functionality

## Confidence Score: 9/10

This PRP provides comprehensive context, specific implementation examples, executable validation steps, and detailed integration guidance. The AI agent has all necessary information for successful one-pass implementation while following established architectural patterns and addressing the unique challenges of genealogy data processing and visualization.

**Key Success Factors:**
1. **Complete Architecture Understanding:** Detailed knowledge of existing components and patterns
2. **Specific Technical Examples:** Real code examples for complex algorithms and visualizations
3. **Executable Validation:** Clear testing steps for verification
4. **Performance Guidance:** Specific metrics and optimization strategies
5. **Integration Clarity:** Detailed component communication and data flow patterns