# PRP: Core Features Implementation (Phase 2)

## Executive Summary
**Project:** AuntieRuth.com Genealogy Site Modernization - Phase 2
**Duration:** 2-4 weeks
**Priority:** High Impact - Transforms site from static pages to interactive research platform
**Confidence Score:** 7/10 for one-pass implementation

This PRP implements the core features that transform AuntieRuth.com from a static genealogy site into an interactive research platform. Building on Phase 1's foundation architecture, this phase delivers enhanced search with advanced filtering, family tree visualization with D3.js, and progressive information disclosure that significantly improves the user experience for genealogy research.

## Critical Context

### Foundation Architecture (Phase 1 - Already Implemented)
- **BaseComponent:** `docs/new/js/core/base-component.js` - Lifecycle management pattern (lines 13-25)
- **DataManager:** `docs/new/js/core/data-manager.js` - Lineage-based data loading (lines 49-63)
- **Data Structure:** Chunked into 10 lineages (`docs/new/js/data/lineages/L0.json` - `L9.json`)
- **Metadata System:** `docs/new/js/data/metadata.json` - Person-to-lineage mapping (2,985+ people)
- **Mobile-First CSS:** `docs/new/css/foundation.css` - Responsive variables and utilities (lines 11-43)

### Current Search Implementation
- **Basic Search:** `docs/new/js/search.js` - Pattern for component structure (lines 7-48)
- **Search Indices:** `docs/new/js/data/indices/` - Location suggestions already exist
- **Build Script:** `scripts/build-search-indices.js` - Needs enhancement for Lunr.js integration

### External Documentation & Libraries
- **D3.js Tree Layout:** https://d3js.org/d3-hierarchy/tree - Core API for family tree visualization
- **D3.js Hierarchy:** https://d3js.org/d3-hierarchy - Data structure transformation
- **Lunr.js:** https://lunrjs.com/guides/getting_started.html - Client-side search indexing
- **Family Chart Examples:** https://github.com/donatso/family-chart - Reference implementation

### File Naming Conventions (CRITICAL - Must Preserve URLs)
- `XF###.htm` - Person/family detail pages (Phase 2 transforms with disclosure)
- `THF###.htm` - Person thumbnail galleries
- `L#` directory pattern - Lineage organization (0-9)

## Implementation Blueprint

### Task List (In Order)

1. **Enhance Search Indices with Lunr.js**
   - Modify existing `scripts/build-search-indices.js` to create Lunr.js indices
   - Build pre-computed search indices for each lineage
   - Create location and name suggestion systems

2. **Create Enhanced Search Component**
   - Build `docs/new/js/components/enhanced-search.js` extending BaseComponent
   - Implement advanced filtering (dates, locations, lineages, relationships)
   - Add real-time search with debouncing and keyboard navigation

3. **Build Family Tree Visualization Component**
   - Create `docs/new/js/components/family-tree.js` with D3.js tree layout
   - Handle complex genealogy relationships (multiple spouses, missing parents)
   - Implement pan/zoom with touch support for mobile

4. **Implement Progressive Information Disclosure**
   - Create `docs/new/js/components/information-disclosure.js`
   - Transform existing table-based person pages to organized sections
   - Add user preference persistence with localStorage

5. **Build Component Integration Layer**
   - Connect search -> tree -> person page workflows
   - Implement cross-component communication
   - Add URL state management for bookmarkable views

6. **Create CSS Styling Systems**
   - Build component-specific CSS following foundation.css patterns
   - Implement mobile-responsive layouts with touch targets
   - Add smooth animations and transitions

## Detailed Implementation

### 1. Enhanced Search Indices (Lunr.js Integration)

#### Modify `scripts/build-search-indices.js`:
```javascript
// Add Lunr.js integration to existing script
const lunr = require('lunr');

class SearchIndexBuilder {
  // Existing methods...

  async buildLineageSearchIndex(lineageId) {
    const lineageData = await this.loadLineageData(lineageId);

    const index = lunr(function () {
      this.ref('id');
      this.field('name', { boost: 10 });
      this.field('birthLocation', { boost: 5 });
      this.field('deathLocation', { boost: 5 });
      this.field('occupation', { boost: 3 });
      this.field('spouse', { boost: 2 });

      lineageData.people.forEach((person) => {
        this.add({
          id: person.id,
          name: person.name || '',
          birthLocation: person.birthLocation || '',
          deathLocation: person.deathLocation || '',
          occupation: person.occupation || '',
          spouse: [person.spouse, person.spouse2, person.spouse3, person.spouse4]
            .filter(Boolean).join(' ')
        });
      });
    });

    // Save serialized index
    await this.saveSearchIndex(lineageId, index.toJSON());
  }
}
```

### 2. Enhanced Search Component

#### Create `docs/new/js/components/enhanced-search.js`:
```javascript
import BaseComponent from '../core/base-component.js';

class EnhancedSearchComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.searchIndices = new Map();
    this.activeFilters = {
      query: '',
      lineages: [],
      birthYearRange: [1800, 2025],
      locations: [],
      hasPhotos: null
    };
  }

  async init() {
    await super.init();
    await this.loadSearchIndices();
    this.setupAdvancedFilters();
  }

  async loadSearchIndices() {
    // Load pre-built Lunr.js indices from build process
    for (let lineageId = 0; lineageId <= 9; lineageId++) {
      try {
        const response = await fetch(`/auntruth/new/js/data/indices/search-L${lineageId}.json`);
        if (response.ok) {
          const indexData = await response.json();
          this.searchIndices.set(lineageId.toString(), lunr.Index.load(indexData));
        }
      } catch (error) {
        console.warn(`Failed to load search index for lineage ${lineageId}`);
      }
    }
  }

  // Follow pattern from existing search.js lines 278-313
  async performSearch(query, filters = {}) {
    // Implementation follows existing search patterns but with Lunr.js
  }
}
```

### 3. Family Tree Component with D3.js

#### Create `docs/new/js/components/family-tree.js`:
```javascript
import BaseComponent from '../core/base-component.js';

class FamilyTreeComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.focusPersonId = options.focusPersonId;
    this.generations = options.generations || 3;
  }

  async render() {
    // Create SVG container following D3.js tree layout pattern
    const svg = d3.select(this.container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', 600);

    // Load family data and build tree structure
    const treeData = await this.buildFamilyHierarchy(this.focusPersonId);

    // Use D3.js tree layout - https://d3js.org/d3-hierarchy/tree
    const tree = d3.tree().size([580, 400]);
    const root = d3.hierarchy(treeData);
    const nodes = tree(root);

    // Render nodes and links with mobile touch support
    this.renderTreeNodes(svg, nodes);
    this.setupPanZoom(svg); // Mobile touch interactions
  }

  async buildFamilyHierarchy(personId) {
    // Handle complex genealogy relationships
    // Account for multiple spouses, missing parents
    // Use DataManager pattern from lines 49-63
  }
}
```

### 4. Progressive Information Disclosure

#### Create `docs/new/js/components/information-disclosure.js`:
```javascript
import BaseComponent from '../core/base-component.js';

class InformationDisclosureComponent extends BaseComponent {
  async render() {
    // Find existing table structure (preserves URLs)
    const contentTable = document.querySelector('table#List');
    if (!contentTable) return;

    // Parse table data and categorize information
    const tableData = this.parseTableData(contentTable);

    // Transform to disclosure-based layout
    const disclosureHtml = this.generateDisclosureHTML(tableData);
    contentTable.outerHTML = disclosureHtml;

    // Apply user preferences from localStorage
    this.applyUserPreferences();
  }

  parseTableData(table) {
    // Categorize information into sections:
    // - Essential (always visible): birth/death dates and locations
    // - Family: parents, spouses, children
    // - Biographical: occupation, address, notes
    // - Photos: thumbnail links
    // - Research: sources, genetics, etc.
  }
}
```

## Validation Gates (Executable)

### Package.json Scripts (Add to existing):
```json
{
  "scripts": {
    "build:enhanced-search": "node scripts/build-lunr-indices.js",
    "test:search": "node scripts/test-search-functionality.js",
    "test:tree": "node scripts/test-tree-rendering.js",
    "test:mobile": "node scripts/test-mobile-responsiveness.js",
    "build:phase2": "npm run build:enhanced-search && npm run build:all",
    "test:phase2": "npm run test:search && npm run test:tree && npm run test:mobile"
  }
}
```

### Validation Commands:
```bash
# Build enhanced search indices with Lunr.js
npm run build:enhanced-search

# Test search functionality across all lineages
npm run test:search

# Validate family tree rendering with D3.js
npm run test:tree

# Test mobile responsiveness and touch interactions
npm run test:mobile

# Build all Phase 2 components
npm run build:phase2

# Run comprehensive Phase 2 tests
npm run test:phase2

# Validate existing URLs still work
npm run validate
```

## Success Criteria

### Core Functionality Delivered
1. **Enhanced Search:** Sub-200ms advanced searches with filtering by dates, locations, lineages
2. **Family Tree Visualization:** Interactive multi-generation trees with touch support
3. **Information Disclosure:** Organized information presentation reducing cognitive overload
4. **Component Integration:** Seamless search->tree->person workflows

### Performance Metrics
- Search index loading < 500ms on mobile
- Family tree rendering < 1s for 3 generations
- Progressive disclosure smooth on mid-range devices
- Memory efficient during extended browsing

### User Experience Validation
- 50% faster genealogy research task completion
- Regular use of advanced search filters
- Intuitive family tree navigation
- Less overwhelming information presentation

## Testing Strategy

### Component Integration Testing
```bash
# Test search-to-tree navigation workflow
npm run test:search-tree-integration

# Verify tree-to-person page navigation
npm run test:tree-person-integration

# Test information disclosure on various person page types
npm run test:disclosure-integration
```

### Mobile Testing
```bash
# Test touch interactions on actual mobile devices
npm run test:mobile-touch

# Validate responsive layouts across screen sizes
npm run test:responsive

# Test performance on mid-range mobile devices
npm run test:mobile-performance
```

## Implementation Gotchas & Solutions

### Search Implementation Challenges
- **Challenge:** 2,985+ people across 10 lineages performance
- **Solution:** Pre-built Lunr.js indices during build, lineage-based chunking
- **Reference:** Existing DataManager caching pattern (lines 28-42)

### Family Tree Visualization Challenges
- **Challenge:** Genealogy has complex relationships (multiple parents/spouses)
- **Solution:** Use D3.js tree layout with custom relationship handling
- **Reference:** D3.js hierarchy documentation - https://d3js.org/d3-hierarchy/tree

### Information Disclosure Challenges
- **Challenge:** Transform existing HTML without breaking URLs
- **Solution:** Progressive enhancement, preserve table structure for fallback
- **Reference:** Existing navigation enhancement pattern

### Mobile Performance Challenges
- **Challenge:** SVG rendering and touch interactions on mobile
- **Solution:** Touch-optimized pan/zoom, performance monitoring
- **Reference:** Foundation CSS touch targets (line 42)

## File Structure (New Components)

```
docs/new/js/components/
├── enhanced-search.js          # Advanced search with Lunr.js
├── family-tree.js              # D3.js tree visualization
└── information-disclosure.js   # Progressive information layout

docs/new/css/
├── enhanced-search.css         # Search UI styling
├── family-tree.css            # Tree visualization styles
└── information-disclosure.css  # Progressive disclosure styles

docs/new/js/data/indices/
├── search-L0.json             # Lunr.js search index lineage 0
├── search-L1.json             # Lunr.js search index lineage 1
└── ...                        # (through L9.json)

scripts/
└── build-lunr-indices.js     # Enhanced search index builder
```

## Dependencies to Add

### Package.json additions:
```json
{
  "dependencies": {
    "lunr": "^2.3.9"
  },
  "devDependencies": {
    "d3": "^7.8.5",
    "d3-hierarchy": "^3.1.2"
  }
}
```

### CDN Fallbacks (for GitHub Pages):
- Lunr.js: `https://unpkg.com/lunr@2.3.9/lunr.min.js`
- D3.js: `https://unpkg.com/d3@7/dist/d3.min.js`

---

**Confidence Score: 7/10** - High confidence due to solid foundation architecture, comprehensive external documentation, and clear existing code patterns to follow. Main risks are family tree complexity and mobile performance optimization, but mitigation strategies are included.