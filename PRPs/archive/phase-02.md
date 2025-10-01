# PRP-Phase-02: Core Features Implementation

## Executive Summary

**Phase:** Core Features (2 of 3)
**Duration:** 2-4 weeks
**Priority:** High Impact - Implements essential genealogy research tools
**Impact:** High - Transforms site from static pages to interactive research platform

This phase implements the core features that transform AuntieRuth.com from a static genealogy site into an interactive research platform. Building on Phase 1's foundation architecture, this phase delivers enhanced search with advanced filtering, basic family tree visualization, and progressive information disclosure that significantly improves the user experience for genealogy research.

## Background & Context

### Prerequisites - Required Reading
Before starting this PRP, read:
- `../docs/README.md` - Complete understanding of genealogy file naming conventions and directory structure
- `docs/new/CLAUDE.md` - Architecture and development guidelines for the modernization project
- `PRPs/phase-01.md` - Foundation architecture that must be completed before this phase
- `PRPs/priority-03.md` - Enhanced search requirements implemented in this phase
- `PRPs/priority-02.md` - Family tree visualization requirements implemented in this phase
- `PRPs/priority-07.md` - Progressive information disclosure requirements implemented in this phase

### Foundation Architecture Dependencies
This phase builds on Phase 1's completed architecture:
- **Component System:** BaseComponent class and modular architecture
- **Data Manager:** Lineage-based data chunking and caching system
- **Enhanced Navigation:** NavigationComponent with family context
- **Mobile-Responsive Framework:** Mobile-first CSS foundation
- **Build Pipeline:** GitHub Actions workflow and asset optimization

### Current Site Capabilities After Phase 1
- Navigation crisis resolved - users can move between family members
- Mobile-responsive layout that works on touch devices
- Optimized data loading with lineage-based chunks
- Component architecture ready for feature enhancement
- 2,985+ people accessible through efficient data structure

## Phase 2 Objectives

### Core Feature Implementation
1. **Enhanced Search System:** Advanced filtering by dates, locations, lineages, and relationships
2. **Family Tree Visualization:** Interactive tree showing multi-generation family relationships
3. **Progressive Information Disclosure:** Organized information presentation reducing cognitive load
4. **Integration Layer:** Seamless integration between search, tree, and navigation components

### Technical Deliverables
1. SearchComponent with pre-built indices and advanced filtering
2. FamilyTreeComponent with D3.js visualization and touch interactions
3. InformationDisclosure system for person pages
4. Cross-component integration enabling comprehensive research workflows

## Implementation Details

### 1. Enhanced Search System Implementation

#### Search Architecture with Pre-built Indices
Building on Phase 1's data chunking, implement efficient client-side search with pre-computed indices.

```javascript
// components/enhanced-search.js
import BaseComponent from '../core/base-component.js';

class EnhancedSearchComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.searchIndices = new Map();
    this.currentResults = [];
    this.activeFilters = {
      query: '',
      lineages: [],
      birthYearRange: [1800, 2025],
      deathYearRange: [1800, 2025],
      locations: [],
      hasPhotos: null,
      isAlive: null
    };
  }

  async init() {
    await super.init();
    await this.loadSearchIndices();
    this.setupAdvancedFilters();
  }

  async render() {
    const searchHtml = this.generateSearchInterface();
    const targetElement = document.getElementById('search-container') || document.body;

    if (document.querySelector('.enhanced-search')) {
      document.querySelector('.enhanced-search').outerHTML = searchHtml;
    } else {
      targetElement.insertAdjacentHTML('afterbegin', searchHtml);
    }

    await this.initializeFilters();
  }

  generateSearchInterface() {
    return `
      <div class="enhanced-search" role="search">
        <div class="search-header">
          <h2>Family Search</h2>
          <button class="filters-toggle" aria-expanded="false" aria-controls="advanced-filters">
            <span>Advanced Filters</span>
            <span class="toggle-icon">▼</span>
          </button>
        </div>

        <div class="search-main">
          <div class="search-input-group">
            <input
              type="search"
              id="main-search-input"
              placeholder="Search by name, location, or occupation..."
              aria-label="Search genealogy database"
              class="search-input"
            >
            <button type="button" class="search-button" aria-label="Execute search">
              <span class="search-icon">🔍</span>
            </button>
          </div>

          <div class="quick-filters">
            ${this.generateQuickFilters()}
          </div>
        </div>

        <div class="advanced-filters" id="advanced-filters" hidden>
          ${this.generateAdvancedFilters()}
        </div>

        <div class="search-results" id="search-results" aria-live="polite">
          ${this.generateInitialResults()}
        </div>
      </div>
    `;
  }

  generateQuickFilters() {
    const lineages = [
      { id: '1', name: 'Hagborg-Hansson' },
      { id: '2', name: 'Nelson' },
      { id: '3', name: 'Pringle-Hambley' },
      { id: '4', name: 'Lathrop-Lothropp' },
      { id: '5', name: 'Ward' },
      { id: '6', name: 'Selch-Weiss' },
      { id: '7', name: 'Stebbe' },
      { id: '8', name: 'Lentz' },
      { id: '9', name: 'Phoenix-Rogerson' }
    ];

    return `
      <div class="quick-filter-group">
        <span class="filter-label">Lineages:</span>
        ${lineages.map(lineage => `
          <button class="quick-filter-btn lineage-filter" data-lineage="${lineage.id}">
            ${lineage.name}
          </button>
        `).join('')}
      </div>

      <div class="quick-filter-group">
        <span class="filter-label">Quick Searches:</span>
        <button class="quick-filter-btn" data-preset="recent">Recent (1950-2025)</button>
        <button class="quick-filter-btn" data-preset="historical">Historical (1800-1950)</button>
        <button class="quick-filter-btn" data-preset="with-photos">Has Photos</button>
      </div>
    `;
  }

  generateAdvancedFilters() {
    return `
      <div class="filter-grid">
        <div class="filter-section">
          <h3>Birth Year Range</h3>
          <div class="range-inputs">
            <input type="number" id="birth-year-min" min="1800" max="2025" value="1800" placeholder="From">
            <span>to</span>
            <input type="number" id="birth-year-max" min="1800" max="2025" value="2025" placeholder="To">
          </div>
          <div class="range-slider">
            <input type="range" id="birth-range" min="1800" max="2025" value="1800,2025" class="dual-range">
          </div>
        </div>

        <div class="filter-section">
          <h3>Death Year Range</h3>
          <div class="range-inputs">
            <input type="number" id="death-year-min" min="1800" max="2025" value="1800" placeholder="From">
            <span>to</span>
            <input type="number" id="death-year-max" min="1800" max="2025" value="2025" placeholder="To">
          </div>
        </div>

        <div class="filter-section">
          <h3>Locations</h3>
          <input type="text" id="location-filter" placeholder="City, Province, Country...">
          <div class="location-suggestions" id="location-suggestions"></div>
        </div>

        <div class="filter-section">
          <h3>Additional Filters</h3>
          <label class="checkbox-label">
            <input type="checkbox" id="has-photos-filter">
            <span>Has Photos</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" id="living-filter">
            <span>Still Living</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" id="deceased-filter">
            <span>Deceased</span>
          </label>
        </div>

        <div class="filter-actions">
          <button type="button" class="btn-secondary" id="clear-filters">Clear All</button>
          <button type="button" class="btn-primary" id="apply-filters">Apply Filters</button>
        </div>
      </div>
    `;
  }

  async loadSearchIndices() {
    try {
      // Load pre-built search indices created during build process
      const metadata = await this.dataManager.getMetadata();

      for (let lineageId = 0; lineageId <= 9; lineageId++) {
        try {
          const indexResponse = await fetch(`/auntruth/new/js/data/indices/search-L${lineageId}.json`);
          if (indexResponse.ok) {
            const indexData = await indexResponse.json();
            // Initialize Lunr index from serialized data
            this.searchIndices.set(lineageId.toString(), lunr.Index.load(indexData));
          }
        } catch (error) {
          console.warn(`Failed to load search index for lineage ${lineageId}:`, error);
        }
      }

      // Load location suggestions
      this.locationSuggestions = await this.loadLocationSuggestions();

    } catch (error) {
      console.error('Failed to load search indices:', error);
      this.fallbackToBasicSearch();
    }
  }

  async performSearch(query, filters = {}) {
    const mergedFilters = { ...this.activeFilters, ...filters };

    if (!query && Object.values(mergedFilters).every(filter =>
      Array.isArray(filter) ? filter.length === 0 : !filter)) {
      return this.getRecentlyViewed();
    }

    let allResults = [];

    // Search across specified lineages or all if none specified
    const searchLineages = mergedFilters.lineages.length > 0
      ? mergedFilters.lineages
      : ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    for (const lineageId of searchLineages) {
      const index = this.searchIndices.get(lineageId);
      if (!index) continue;

      try {
        // Perform Lunr search
        const searchResults = query ? index.search(query) : [];

        // Get full person data for results
        const lineageData = await this.dataManager.getLineageData(lineageId);

        const enrichedResults = searchResults.map(result => {
          const person = lineageData.people.find(p => p.id === result.ref);
          return person ? { ...person, searchScore: result.score } : null;
        }).filter(Boolean);

        // Apply additional filters
        const filteredResults = this.applyAdditionalFilters(enrichedResults, mergedFilters);
        allResults.push(...filteredResults);

      } catch (error) {
        console.error(`Search error for lineage ${lineageId}:`, error);
      }
    }

    // Sort by relevance score and limit results
    allResults.sort((a, b) => (b.searchScore || 0) - (a.searchScore || 0));
    return allResults.slice(0, 100);
  }

  applyAdditionalFilters(results, filters) {
    return results.filter(person => {
      // Birth year filter
      if (filters.birthYearRange) {
        const birthYear = this.extractYear(person.birthDate);
        if (birthYear && (birthYear < filters.birthYearRange[0] || birthYear > filters.birthYearRange[1])) {
          return false;
        }
      }

      // Death year filter
      if (filters.deathYearRange) {
        const deathYear = this.extractYear(person.deathDate);
        if (deathYear && (deathYear < filters.deathYearRange[0] || deathYear > filters.deathYearRange[1])) {
          return false;
        }
      }

      // Location filter
      if (filters.locations && filters.locations.length > 0) {
        const personLocations = [person.birthLocation, person.deathLocation, person.address].join(' ').toLowerCase();
        const hasMatchingLocation = filters.locations.some(location =>
          personLocations.includes(location.toLowerCase()));
        if (!hasMatchingLocation) return false;
      }

      // Has photos filter
      if (filters.hasPhotos === true) {
        // Check if person has thumbnail page (THF file exists)
        // This would need to be pre-computed during build
        if (!person.hasPhotos) return false;
      }

      // Living/deceased filter
      if (filters.isAlive === true && person.deathDate && person.deathDate.trim()) {
        return false;
      }
      if (filters.isAlive === false && (!person.deathDate || !person.deathDate.trim())) {
        return false;
      }

      return true;
    });
  }

  generateSearchResults(results) {
    if (results.length === 0) {
      return `
        <div class="no-results">
          <h3>No results found</h3>
          <p>Try adjusting your search terms or filters.</p>
        </div>
      `;
    }

    return `
      <div class="search-results-header">
        <h3>Found ${results.length} ${results.length === 1 ? 'person' : 'people'}</h3>
      </div>
      <div class="results-grid">
        ${results.map(person => this.generatePersonCard(person)).join('')}
      </div>
    `;
  }

  generatePersonCard(person) {
    const birthYear = this.extractYear(person.birthDate) || '';
    const deathYear = this.extractYear(person.deathDate) || '';
    const lifespan = birthYear && deathYear ? `${birthYear}-${deathYear}` :
                    birthYear ? `b. ${birthYear}` :
                    deathYear ? `d. ${deathYear}` : '';

    return `
      <div class="person-card" data-person-id="${person.id}">
        <div class="person-info">
          <h4 class="person-name">
            <a href="${person.url}" class="person-link">${person.name}</a>
          </h4>
          <p class="person-details">
            ${lifespan ? `<span class="lifespan">${lifespan}</span>` : ''}
            ${person.birthLocation ? `<span class="location">📍 ${person.birthLocation}</span>` : ''}
            ${person.occupation ? `<span class="occupation">💼 ${person.occupation}</span>` : ''}
          </p>
          <p class="person-lineage">
            <span class="lineage-badge lineage-${person.lineage}">${person.lineageName}</span>
          </p>
        </div>
        <div class="person-actions">
          <button class="btn-sm view-tree" data-person-id="${person.id}" title="View family tree">🌳</button>
          <button class="btn-sm view-photos" data-person-id="${person.id}" title="View photos">📸</button>
        </div>
      </div>
    `;
  }

  attachEventListeners() {
    // Search input handling
    const searchInput = document.getElementById('main-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', this.debounce(async (e) => {
        await this.handleSearch(e.target.value);
      }, 300));

      searchInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          await this.handleSearch(e.target.value);
        }
      });
    }

    // Advanced filters toggle
    const filtersToggle = document.querySelector('.filters-toggle');
    const advancedFilters = document.getElementById('advanced-filters');

    if (filtersToggle && advancedFilters) {
      filtersToggle.addEventListener('click', () => {
        const isExpanded = filtersToggle.getAttribute('aria-expanded') === 'true';
        filtersToggle.setAttribute('aria-expanded', !isExpanded);
        advancedFilters.hidden = isExpanded;
        filtersToggle.querySelector('.toggle-icon').textContent = isExpanded ? '▼' : '▲';
      });
    }

    // Quick filters
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.handleQuickFilter(e.target);
      });
    });

    // Advanced filter controls
    document.getElementById('apply-filters')?.addEventListener('click', () => {
      this.applyAdvancedFilters();
    });

    document.getElementById('clear-filters')?.addEventListener('click', () => {
      this.clearAllFilters();
    });

    // Person card actions
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('view-tree')) {
        this.handleViewTree(e.target.dataset.personId);
      } else if (e.target.classList.contains('view-photos')) {
        this.handleViewPhotos(e.target.dataset.personId);
      }
    });
  }

  async handleSearch(query) {
    this.activeFilters.query = query;
    const results = await this.performSearch(query, this.activeFilters);
    this.displayResults(results);
  }

  handleQuickFilter(button) {
    // Toggle active state
    button.classList.toggle('active');

    if (button.hasAttribute('data-lineage')) {
      const lineageId = button.dataset.lineage;
      if (button.classList.contains('active')) {
        if (!this.activeFilters.lineages.includes(lineageId)) {
          this.activeFilters.lineages.push(lineageId);
        }
      } else {
        this.activeFilters.lineages = this.activeFilters.lineages.filter(id => id !== lineageId);
      }
    } else if (button.hasAttribute('data-preset')) {
      this.applyPresetFilter(button.dataset.preset);
    }

    // Re-run search with new filters
    this.handleSearch(this.activeFilters.query);
  }

  applyPresetFilter(preset) {
    switch (preset) {
      case 'recent':
        this.activeFilters.birthYearRange = [1950, 2025];
        break;
      case 'historical':
        this.activeFilters.birthYearRange = [1800, 1950];
        break;
      case 'with-photos':
        this.activeFilters.hasPhotos = true;
        break;
    }
  }

  extractYear(dateString) {
    if (!dateString) return null;
    const match = dateString.match(/\b(19|20)\d{2}\b/);
    return match ? parseInt(match[0]) : null;
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  async handleViewTree(personId) {
    // Integration point with family tree component
    const treeComponent = this.getComponent('family-tree');
    if (treeComponent) {
      await treeComponent.focusOnPerson(personId);
    } else {
      // Navigate to tree page
      window.location.href = `/auntruth/new/family-tree/?person=${personId}`;
    }
  }

  handleViewPhotos(personId) {
    // Navigate to person's photo gallery
    const person = this.currentResults.find(p => p.id === personId);
    if (person) {
      window.location.href = `/auntruth/new/htm/L${person.lineage}/THF${personId}.htm`;
    }
  }
}

export default EnhancedSearchComponent;
```

#### Build Script for Search Indices
```javascript
// scripts/build-search-indices.js
const fs = require('fs').promises;
const path = require('path');
const lunr = require('lunr');

class SearchIndexBuilder {
  async buildAllIndices() {
    console.log('Building search indices...');

    // Load metadata to get lineage information
    const metadata = JSON.parse(
      await fs.readFile('./docs/new/js/data/metadata.json', 'utf8')
    );

    // Build search index for each lineage
    for (let lineageId = 0; lineageId <= 9; lineageId++) {
      await this.buildLineageIndex(lineageId.toString());
    }

    // Build location suggestions
    await this.buildLocationSuggestions();

    console.log('Search indices built successfully!');
  }

  async buildLineageIndex(lineageId) {
    try {
      const lineageData = JSON.parse(
        await fs.readFile(`./docs/new/js/data/lineages/L${lineageId}.json`, 'utf8')
      );

      const searchIndex = lunr(function() {
        this.ref('id');
        this.field('name', { boost: 10 });
        this.field('birthLocation', { boost: 5 });
        this.field('deathLocation', { boost: 5 });
        this.field('occupation', { boost: 3 });
        this.field('address', { boost: 2 });
        this.field('father');
        this.field('mother');
        this.field('spouse');

        lineageData.people.forEach(person => {
          // Create searchable text combining all relevant fields
          const searchDoc = {
            id: person.id,
            name: person.name || '',
            birthLocation: person.birthLocation || '',
            deathLocation: person.deathLocation || '',
            occupation: person.occupation || '',
            address: person.address || '',
            father: person.father || '',
            mother: person.mother || '',
            spouse: [person.spouse, person.spouse2, person.spouse3, person.spouse4]
              .filter(s => s && s.trim()).join(' ')
          };

          this.add(searchDoc);
        });
      });

      // Save serialized index
      const indexPath = `./docs/new/js/data/indices/search-L${lineageId}.json`;
      await fs.writeFile(indexPath, JSON.stringify(searchIndex.toJSON()));

      console.log(`Built search index for lineage ${lineageId}: ${lineageData.people.length} people`);

    } catch (error) {
      console.warn(`Failed to build index for lineage ${lineageId}:`, error);
    }
  }

  async buildLocationSuggestions() {
    const allLocations = new Set();

    // Collect all unique locations from all lineages
    for (let lineageId = 0; lineageId <= 9; lineageId++) {
      try {
        const lineageData = JSON.parse(
          await fs.readFile(`./docs/new/js/data/lineages/L${lineageId}.json`, 'utf8')
        );

        lineageData.people.forEach(person => {
          [person.birthLocation, person.deathLocation, person.address].forEach(location => {
            if (location && location.trim()) {
              // Extract city, province, country components
              const parts = location.split(/\s+/).filter(part => part.length > 2);
              parts.forEach(part => {
                // Remove common abbreviations and clean up
                const cleaned = part.replace(/[,\s]+$/, '').trim();
                if (cleaned.length > 2) {
                  allLocations.add(cleaned);
                }
              });
            }
          });
        });
      } catch (error) {
        console.warn(`Failed to process lineage ${lineageId} for locations:`, error);
      }
    }

    // Convert to sorted array
    const locationSuggestions = Array.from(allLocations).sort();

    await fs.writeFile(
      './docs/new/js/data/indices/locations.json',
      JSON.stringify(locationSuggestions, null, 2)
    );

    console.log(`Built location suggestions: ${locationSuggestions.length} unique locations`);
  }
}

if (require.main === module) {
  const builder = new SearchIndexBuilder();
  builder.buildAllIndices().catch(console.error);
}

module.exports = SearchIndexBuilder;
```

### 2. Family Tree Visualization Implementation

#### Interactive Family Tree Component
```javascript
// components/family-tree.js
import BaseComponent from '../core/base-component.js';

class FamilyTreeComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.focusPersonId = options.focusPersonId || null;
    this.generations = options.generations || 3;
    this.layout = options.layout || 'horizontal'; // horizontal, vertical, radial
    this.zoom = { scale: 1, x: 0, y: 0 };
    this.nodes = [];
    this.links = [];
  }

  async init() {
    await super.init();
    if (this.focusPersonId) {
      await this.loadFamilyTree(this.focusPersonId);
    }
  }

  async render() {
    const treeHtml = this.generateTreeInterface();
    const targetElement = document.getElementById('family-tree-container') || document.body;

    if (document.querySelector('.family-tree')) {
      document.querySelector('.family-tree').outerHTML = treeHtml;
    } else {
      targetElement.insertAdjacentHTML('afterbegin', treeHtml);
    }

    if (this.focusPersonId) {
      await this.renderTree();
    }
  }

  generateTreeInterface() {
    return `
      <div class="family-tree">
        <div class="tree-controls">
          <div class="tree-toolbar">
            <button class="btn-sm" id="zoom-in" title="Zoom In">🔍+</button>
            <button class="btn-sm" id="zoom-out" title="Zoom Out">🔍-</button>
            <button class="btn-sm" id="center-tree" title="Center">🎯</button>
            <button class="btn-sm" id="fit-tree" title="Fit to Screen">⚏</button>

            <div class="layout-controls">
              <select id="tree-layout" aria-label="Tree Layout">
                <option value="horizontal">Horizontal</option>
                <option value="vertical">Vertical</option>
                <option value="compact">Compact</option>
              </select>
            </div>

            <div class="generation-controls">
              <label for="generations">Generations:</label>
              <input type="range" id="generations" min="2" max="5" value="3" step="1">
              <span id="generations-value">3</span>
            </div>
          </div>
        </div>

        <div class="tree-container">
          <svg class="tree-svg" width="100%" height="600">
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" stroke-width="1"/>
              </pattern>
              <filter id="drop-shadow">
                <feDropShadow dx="2" dy="2" stdDeviation="2" flood-opacity="0.2"/>
              </filter>
            </defs>

            <rect width="100%" height="100%" fill="url(#grid)" />
            <g class="tree-content" transform="translate(0,0) scale(1)">
              <g class="links"></g>
              <g class="nodes"></g>
            </g>
          </svg>

          <div class="tree-overlay">
            <div class="person-tooltip" id="person-tooltip" style="display: none;">
              <div class="tooltip-content"></div>
            </div>
          </div>
        </div>

        ${this.generateTreeLegend()}
      </div>
    `;
  }

  generateTreeLegend() {
    return `
      <div class="tree-legend">
        <h4>Family Tree Guide</h4>
        <div class="legend-items">
          <div class="legend-item">
            <div class="legend-symbol male-node"></div>
            <span>Male</span>
          </div>
          <div class="legend-item">
            <div class="legend-symbol female-node"></div>
            <span>Female</span>
          </div>
          <div class="legend-item">
            <div class="legend-symbol unknown-node"></div>
            <span>Unknown</span>
          </div>
          <div class="legend-item">
            <div class="legend-line parent-link"></div>
            <span>Parent-Child</span>
          </div>
          <div class="legend-item">
            <div class="legend-line spouse-link"></div>
            <span>Marriage</span>
          </div>
        </div>
      </div>
    `;
  }

  async loadFamilyTree(personId) {
    try {
      const rootPerson = await this.dataManager.getPersonData(personId);
      if (!rootPerson) {
        throw new Error(`Person ${personId} not found`);
      }

      this.nodes = [];
      this.links = [];

      // Build family tree data structure
      await this.buildFamilyGraph(rootPerson, 0, this.generations);

      // Calculate positions based on layout
      this.calculateNodePositions();

    } catch (error) {
      console.error('Failed to load family tree:', error);
      this.showError('Failed to load family tree. Please try again.');
    }
  }

  async buildFamilyGraph(person, currentGeneration, maxGenerations) {
    if (currentGeneration > maxGenerations || !person) return;

    // Add person node if not already added
    if (!this.nodes.find(n => n.id === person.id)) {
      this.nodes.push({
        id: person.id,
        name: person.name,
        gender: this.inferGender(person),
        birthYear: this.extractYear(person.birthDate),
        deathYear: this.extractYear(person.deathDate),
        generation: currentGeneration,
        lineage: person.lineage,
        url: person.url,
        data: person
      });
    }

    // Process parents (previous generation)
    if (currentGeneration > 0) {
      await this.processParents(person, currentGeneration - 1, maxGenerations);
    }

    // Process children (next generation)
    if (currentGeneration < maxGenerations) {
      await this.processChildren(person, currentGeneration + 1, maxGenerations);
    }

    // Process spouse relationships
    await this.processSpouses(person, currentGeneration);
  }

  async processParents(person, generation, maxGenerations) {
    // Process father
    if (person.father) {
      const fatherId = this.extractPersonId(person.father);
      if (fatherId) {
        const father = await this.dataManager.getPersonData(fatherId);
        if (father) {
          await this.buildFamilyGraph(father, generation, maxGenerations);
          this.addLink(father.id, person.id, 'parent-child');
        }
      }
    }

    // Process mother
    if (person.mother) {
      const motherId = this.extractPersonId(person.mother);
      if (motherId) {
        const mother = await this.dataManager.getPersonData(motherId);
        if (mother) {
          await this.buildFamilyGraph(mother, generation, maxGenerations);
          this.addLink(mother.id, person.id, 'parent-child');
        }
      }
    }
  }

  async processSpouses(person, generation) {
    const spouses = [person.spouse, person.spouse2, person.spouse3, person.spouse4]
      .filter(spouse => spouse && spouse.trim());

    for (const spouseInfo of spouses) {
      const spouseId = this.extractPersonId(spouseInfo);
      if (spouseId) {
        const spouse = await this.dataManager.getPersonData(spouseId);
        if (spouse) {
          if (!this.nodes.find(n => n.id === spouse.id)) {
            this.nodes.push({
              id: spouse.id,
              name: spouse.name,
              gender: this.inferGender(spouse),
              birthYear: this.extractYear(spouse.birthDate),
              deathYear: this.extractYear(spouse.deathDate),
              generation: generation,
              lineage: spouse.lineage,
              url: spouse.url,
              data: spouse
            });
          }
          this.addLink(person.id, spouse.id, 'marriage');
        }
      }
    }
  }

  addLink(sourceId, targetId, type) {
    const existingLink = this.links.find(link =>
      (link.source === sourceId && link.target === targetId) ||
      (link.source === targetId && link.target === sourceId && type === 'marriage')
    );

    if (!existingLink) {
      this.links.push({
        source: sourceId,
        target: targetId,
        type: type
      });
    }
  }

  calculateNodePositions() {
    switch (this.layout) {
      case 'horizontal':
        this.calculateHorizontalLayout();
        break;
      case 'vertical':
        this.calculateVerticalLayout();
        break;
      case 'compact':
        this.calculateCompactLayout();
        break;
    }
  }

  calculateHorizontalLayout() {
    const generationWidth = 200;
    const nodeHeight = 80;

    // Group nodes by generation
    const generations = {};
    this.nodes.forEach(node => {
      if (!generations[node.generation]) {
        generations[node.generation] = [];
      }
      generations[node.generation].push(node);
    });

    // Position nodes
    Object.keys(generations).forEach(gen => {
      const genNodes = generations[gen];
      const genY = parseInt(gen) * generationWidth;

      genNodes.forEach((node, index) => {
        node.x = genY;
        node.y = (index - (genNodes.length - 1) / 2) * nodeHeight;
      });
    });
  }

  async renderTree() {
    if (!this.nodes.length) return;

    const svg = document.querySelector('.tree-svg');
    const nodesGroup = svg.querySelector('.nodes');
    const linksGroup = svg.querySelector('.links');

    // Clear existing content
    nodesGroup.innerHTML = '';
    linksGroup.innerHTML = '';

    // Render links first (so they appear behind nodes)
    this.links.forEach(link => {
      const sourceNode = this.nodes.find(n => n.id === link.source);
      const targetNode = this.nodes.find(n => n.id === link.target);

      if (sourceNode && targetNode) {
        const linkElement = this.createLinkElement(sourceNode, targetNode, link.type);
        linksGroup.appendChild(linkElement);
      }
    });

    // Render nodes
    this.nodes.forEach(node => {
      const nodeElement = this.createNodeElement(node);
      nodesGroup.appendChild(nodeElement);
    });

    // Center the tree
    this.centerTree();
  }

  createNodeElement(node) {
    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.classList.add('person-node', `lineage-${node.lineage}`);
    group.setAttribute('transform', `translate(${node.x}, ${node.y})`);
    group.setAttribute('data-person-id', node.id);

    // Node background
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', -40);
    rect.setAttribute('y', -25);
    rect.setAttribute('width', 80);
    rect.setAttribute('height', 50);
    rect.setAttribute('rx', 5);
    rect.classList.add('node-bg', `${node.gender}-node`);

    // Person name
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('dy', '0.35em');
    text.textContent = this.truncateName(node.name, 10);
    text.classList.add('node-text');

    // Life years
    if (node.birthYear || node.deathYear) {
      const years = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      years.setAttribute('text-anchor', 'middle');
      years.setAttribute('dy', '1.2em');
      years.setAttribute('font-size', '10px');
      years.textContent = `${node.birthYear || '?'}-${node.deathYear || '?'}`;
      years.classList.add('node-years');
      group.appendChild(years);
    }

    group.appendChild(rect);
    group.appendChild(text);

    // Add interaction handlers
    group.addEventListener('click', (e) => {
      e.stopPropagation();
      this.handleNodeClick(node);
    });

    group.addEventListener('mouseenter', (e) => {
      this.showPersonTooltip(node, e);
    });

    group.addEventListener('mouseleave', () => {
      this.hidePersonTooltip();
    });

    return group;
  }

  createLinkElement(sourceNode, targetNode, type) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', sourceNode.x);
    line.setAttribute('y1', sourceNode.y);
    line.setAttribute('x2', targetNode.x);
    line.setAttribute('y2', targetNode.y);
    line.classList.add('family-link', `${type}-link`);

    return line;
  }

  showPersonTooltip(node, event) {
    const tooltip = document.getElementById('person-tooltip');
    const content = tooltip.querySelector('.tooltip-content');

    content.innerHTML = `
      <strong>${node.name}</strong><br>
      ${node.birthYear ? `Born: ${node.birthYear}` : ''}<br>
      ${node.deathYear ? `Died: ${node.deathYear}` : ''}<br>
      <em>Lineage: ${node.data.lineageName}</em>
    `;

    tooltip.style.display = 'block';
    tooltip.style.left = event.pageX + 10 + 'px';
    tooltip.style.top = event.pageY + 10 + 'px';
  }

  hidePersonTooltip() {
    document.getElementById('person-tooltip').style.display = 'none';
  }

  handleNodeClick(node) {
    // Navigate to person's detail page
    window.location.href = node.url;
  }

  attachEventListeners() {
    // Tree controls
    document.getElementById('zoom-in')?.addEventListener('click', () => this.zoomIn());
    document.getElementById('zoom-out')?.addEventListener('click', () => this.zoomOut());
    document.getElementById('center-tree')?.addEventListener('click', () => this.centerTree());
    document.getElementById('fit-tree')?.addEventListener('click', () => this.fitTree());

    // Layout controls
    document.getElementById('tree-layout')?.addEventListener('change', (e) => {
      this.layout = e.target.value;
      this.calculateNodePositions();
      this.renderTree();
    });

    // Generation controls
    const generationsSlider = document.getElementById('generations');
    const generationsValue = document.getElementById('generations-value');

    if (generationsSlider && generationsValue) {
      generationsSlider.addEventListener('input', (e) => {
        generationsValue.textContent = e.target.value;
      });

      generationsSlider.addEventListener('change', async (e) => {
        this.generations = parseInt(e.target.value);
        if (this.focusPersonId) {
          await this.loadFamilyTree(this.focusPersonId);
          await this.renderTree();
        }
      });
    }

    // SVG pan and zoom
    this.setupPanZoom();
  }

  setupPanZoom() {
    const svg = document.querySelector('.tree-svg');
    const content = svg.querySelector('.tree-content');

    let isPointing = false;
    let pointStart = { x: 0, y: 0 };
    let transform = { x: 0, y: 0, scale: 1 };

    svg.addEventListener('mousedown', (e) => {
      isPointing = true;
      pointStart = { x: e.clientX, y: e.clientY };
      svg.style.cursor = 'grabbing';
    });

    svg.addEventListener('mousemove', (e) => {
      if (!isPointing) return;

      const dx = e.clientX - pointStart.x;
      const dy = e.clientY - pointStart.y;

      transform.x += dx;
      transform.y += dy;

      this.updateTransform(content, transform);

      pointStart = { x: e.clientX, y: e.clientY };
    });

    svg.addEventListener('mouseup', () => {
      isPointing = false;
      svg.style.cursor = 'default';
    });

    // Touch support
    if ('ontouchstart' in window) {
      this.setupTouchControls(svg, content, transform);
    }
  }

  setupTouchControls(svg, content, transform) {
    let touches = [];

    svg.addEventListener('touchstart', (e) => {
      e.preventDefault();
      touches = Array.from(e.touches);
    });

    svg.addEventListener('touchmove', (e) => {
      e.preventDefault();

      if (touches.length === 1 && e.touches.length === 1) {
        // Single touch - pan
        const touch = e.touches[0];
        const lastTouch = touches[0];

        const dx = touch.clientX - lastTouch.clientX;
        const dy = touch.clientY - lastTouch.clientY;

        transform.x += dx;
        transform.y += dy;

        this.updateTransform(content, transform);
      } else if (touches.length === 2 && e.touches.length === 2) {
        // Two touches - pinch zoom
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const lastTouch1 = touches[0];
        const lastTouch2 = touches[1];

        const currentDistance = Math.sqrt(
          Math.pow(touch2.clientX - touch1.clientX, 2) +
          Math.pow(touch2.clientY - touch1.clientY, 2)
        );

        const lastDistance = Math.sqrt(
          Math.pow(lastTouch2.clientX - lastTouch1.clientX, 2) +
          Math.pow(lastTouch2.clientY - lastTouch1.clientY, 2)
        );

        const scale = currentDistance / lastDistance;
        transform.scale *= scale;
        transform.scale = Math.max(0.1, Math.min(3, transform.scale));

        this.updateTransform(content, transform);
      }

      touches = Array.from(e.touches);
    });
  }

  updateTransform(element, transform) {
    element.setAttribute('transform',
      `translate(${transform.x}, ${transform.y}) scale(${transform.scale})`
    );
  }

  // Utility methods
  inferGender(person) {
    // Simple heuristics - could be improved with more data
    const name = person.name.toLowerCase();
    const maleIndicators = ['jr.', 'sr.', 'son of'];
    const femaleIndicators = ['daughter of', 'wife of'];

    if (maleIndicators.some(indicator => name.includes(indicator))) return 'male';
    if (femaleIndicators.some(indicator => name.includes(indicator))) return 'female';

    return 'unknown';
  }

  extractYear(dateString) {
    if (!dateString) return null;
    const match = dateString.match(/\b(19|20)\d{2}\b/);
    return match ? parseInt(match[0]) : null;
  }

  extractPersonId(familyMember) {
    // Extract person ID from family member string
    // This would need to be implemented based on data format
    return null; // Placeholder
  }

  truncateName(name, maxLength) {
    if (name.length <= maxLength) return name;
    return name.substring(0, maxLength - 3) + '...';
  }

  centerTree() {
    const svg = document.querySelector('.tree-svg');
    const content = svg.querySelector('.tree-content');
    const svgRect = svg.getBoundingClientRect();

    // Reset transform to center
    const transform = {
      x: svgRect.width / 2,
      y: svgRect.height / 2,
      scale: 1
    };

    this.updateTransform(content, transform);
  }
}

export default FamilyTreeComponent;
```

### 3. Progressive Information Disclosure Implementation

#### Information Disclosure System
```javascript
// components/information-disclosure.js
import BaseComponent from '../core/base-component.js';

class InformationDisclosureComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.disclosureState = {
      essential: true,
      family: false,
      biographical: false,
      photos: false,
      research: false
    };
    this.userPreferences = this.loadUserPreferences();
  }

  async render() {
    if (this.currentPage.type !== 'person') return;

    // Find the main content table
    const contentTable = document.querySelector('table#List');
    if (!contentTable) return;

    // Transform table into disclosure-based layout
    await this.transformToDisclosureLayout(contentTable);
  }

  async transformToDisclosureLayout(table) {
    const tableData = this.parseTableData(table);
    const disclosureHtml = this.generateDisclosureHTML(tableData);

    // Replace table with disclosure layout
    table.outerHTML = disclosureHtml;

    // Apply user preferences
    this.applyUserPreferences();
  }

  parseTableData(table) {
    const rows = Array.from(table.querySelectorAll('tr'));
    const data = {
      essential: {},
      family: {},
      biographical: {},
      photos: [],
      research: {}
    };

    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 2) {
        const label = cells[0].textContent.trim();
        const value = cells[1].innerHTML.trim();

        this.categorizeInformation(label, value, data);
      }
    });

    return data;
  }

  categorizeInformation(label, value, data) {
    const lowerLabel = label.toLowerCase();

    // Essential information (always visible)
    if (['birthdate', 'birth location', 'deathdate', 'death location'].includes(lowerLabel)) {
      data.essential[label] = value;
    }

    // Family relationships
    else if (['father', 'mother', 'spouse', 'children'].includes(lowerLabel)) {
      data.family[label] = value;
    }

    // Biographical details
    else if (['occupation', 'address', 'notes', 'education'].includes(lowerLabel)) {
      data.biographical[label] = value;
    }

    // Photos and media
    else if (lowerLabel.includes('photo') || lowerLabel.includes('image')) {
      data.photos.push({ label, value });
    }

    // Research information
    else {
      data.research[label] = value;
    }
  }

  generateDisclosureHTML(data) {
    return `
      <div class="information-disclosure">
        ${this.generateEssentialSection(data.essential)}
        ${this.generateDisclosureSection('family', 'Family Relationships', data.family)}
        ${this.generateDisclosureSection('biographical', 'Biographical Details', data.biographical)}
        ${this.generatePhotosSection(data.photos)}
        ${this.generateDisclosureSection('research', 'Research Information', data.research)}
      </div>
    `;
  }

  generateEssentialSection(essentialData) {
    if (Object.keys(essentialData).length === 0) return '';

    return `
      <div class="disclosure-section essential-info" data-section="essential">
        <div class="section-content">
          ${Object.entries(essentialData).map(([label, value]) => `
            <div class="info-item essential-item">
              <span class="info-label">${label}:</span>
              <span class="info-value">${value}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  generateDisclosureSection(sectionId, sectionTitle, sectionData) {
    if (Object.keys(sectionData).length === 0) return '';

    return `
      <div class="disclosure-section" data-section="${sectionId}">
        <button class="disclosure-toggle"
                aria-expanded="${this.disclosureState[sectionId]}"
                aria-controls="${sectionId}-content">
          <span class="toggle-icon">${this.disclosureState[sectionId] ? '▼' : '▶'}</span>
          <span class="section-title">${sectionTitle}</span>
          <span class="item-count">(${Object.keys(sectionData).length})</span>
        </button>

        <div class="section-content"
             id="${sectionId}-content"
             ${!this.disclosureState[sectionId] ? 'hidden' : ''}>
          ${Object.entries(sectionData).map(([label, value]) => `
            <div class="info-item">
              <span class="info-label">${label}:</span>
              <span class="info-value">${value}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  generatePhotosSection(photos) {
    if (photos.length === 0) return '';

    return `
      <div class="disclosure-section" data-section="photos">
        <button class="disclosure-toggle"
                aria-expanded="${this.disclosureState.photos}"
                aria-controls="photos-content">
          <span class="toggle-icon">${this.disclosureState.photos ? '▼' : '▶'}</span>
          <span class="section-title">Photos & Media</span>
          <span class="item-count">(${photos.length})</span>
        </button>

        <div class="section-content photo-gallery"
             id="photos-content"
             ${!this.disclosureState.photos ? 'hidden' : ''}>
          ${photos.map(photo => `
            <div class="photo-item">
              <span class="photo-label">${photo.label}:</span>
              <div class="photo-value">${photo.value}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  attachEventListeners() {
    // Disclosure toggle buttons
    document.querySelectorAll('.disclosure-toggle').forEach(button => {
      button.addEventListener('click', (e) => {
        this.handleDisclosureToggle(e.target.closest('.disclosure-toggle'));
      });
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab' && e.target.classList.contains('disclosure-toggle')) {
        // Ensure keyboard accessibility
        e.target.addEventListener('keydown', (keyEvent) => {
          if (keyEvent.key === 'Enter' || keyEvent.key === ' ') {
            keyEvent.preventDefault();
            this.handleDisclosureToggle(e.target);
          }
        });
      }
    });
  }

  handleDisclosureToggle(button) {
    const section = button.closest('.disclosure-section');
    const sectionId = section.dataset.section;
    const content = section.querySelector('.section-content');
    const icon = button.querySelector('.toggle-icon');

    const isExpanded = button.getAttribute('aria-expanded') === 'true';
    const newState = !isExpanded;

    // Update UI
    button.setAttribute('aria-expanded', newState);
    content.hidden = !newState;
    icon.textContent = newState ? '▼' : '▶';

    // Update state
    this.disclosureState[sectionId] = newState;

    // Save user preference
    this.saveUserPreferences();

    // Add smooth transition
    if (newState) {
      content.style.animation = 'slideDown 0.3s ease-out';
    } else {
      content.style.animation = 'slideUp 0.3s ease-out';
    }
  }

  loadUserPreferences() {
    try {
      const saved = localStorage.getItem('disclosure-preferences');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  }

  saveUserPreferences() {
    try {
      localStorage.setItem('disclosure-preferences', JSON.stringify(this.disclosureState));
    } catch {
      // Ignore storage errors
    }
  }

  applyUserPreferences() {
    if (Object.keys(this.userPreferences).length === 0) return;

    // Apply saved preferences
    Object.entries(this.userPreferences).forEach(([sectionId, isOpen]) => {
      if (sectionId !== 'essential') {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (section) {
          const button = section.querySelector('.disclosure-toggle');
          const content = section.querySelector('.section-content');

          if (button && content) {
            button.setAttribute('aria-expanded', isOpen);
            content.hidden = !isOpen;
            button.querySelector('.toggle-icon').textContent = isOpen ? '▼' : '▶';
            this.disclosureState[sectionId] = isOpen;
          }
        }
      }
    });
  }
}

export default InformationDisclosureComponent;
```

#### Progressive Disclosure CSS
```css
/* css/information-disclosure.css */

.information-disclosure {
  max-width: 800px;
  margin: var(--space-lg) auto;
  padding: 0 var(--space-md);
}

.disclosure-section {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: var(--space-md);
  background: var(--color-surface);
  overflow: hidden;
}

.disclosure-section.essential-info {
  border-color: var(--color-primary);
  background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
}

.disclosure-toggle {
  width: 100%;
  padding: var(--space-md);
  background: none;
  border: none;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  font-size: var(--font-size-base);
  min-height: var(--touch-target-min);
}

.disclosure-toggle:hover,
.disclosure-toggle:focus {
  background: rgba(0,0,0,0.05);
}

.disclosure-toggle:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.toggle-icon {
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
  transition: transform 0.2s ease;
}

.section-title {
  font-weight: bold;
  color: var(--color-text);
  flex: 1;
  text-align: left;
}

.item-count {
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
  background: #f0f0f0;
  padding: var(--space-xs) var(--space-sm);
  border-radius: 12px;
}

.section-content {
  padding: 0 var(--space-md) var(--space-md);
}

.essential-info .section-content {
  padding: var(--space-md);
}

.info-item {
  display: flex;
  flex-direction: column;
  margin-bottom: var(--space-md);
  padding: var(--space-sm);
  border-radius: 4px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.essential-item {
  background: rgba(255,255,255,0.8);
  border: 1px solid #e3f2fd;
}

.info-label {
  font-weight: bold;
  color: var(--color-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-xs);
}

.info-value {
  color: var(--color-text);
  line-height: 1.4;
}

.info-value a {
  color: var(--color-link);
  text-decoration: none;
}

.info-value a:hover,
.info-value a:focus {
  text-decoration: underline;
}

/* Photo gallery specific styles */
.photo-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-md);
}

.photo-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: var(--space-sm);
  background: #fafafa;
}

.photo-label {
  display: block;
  font-weight: bold;
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
  margin-bottom: var(--space-xs);
}

.photo-value img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

/* Smooth animations */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .info-item {
    flex-direction: column;
  }

  .info-label {
    margin-bottom: var(--space-xs);
  }

  .photo-gallery {
    grid-template-columns: 1fr;
  }

  .disclosure-toggle {
    padding: var(--space-sm);
  }

  .section-content {
    padding: 0 var(--space-sm) var(--space-sm);
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .disclosure-section {
    border-width: 2px;
  }

  .disclosure-toggle:focus {
    outline-width: 3px;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .toggle-icon,
  .section-content {
    transition: none;
  }

  @keyframes slideDown,
  @keyframes slideUp {
    from, to {
      opacity: 1;
      transform: none;
    }
  }
}
```

## Success Criteria

### Core Functionality Delivered
1. **Enhanced Search:** Advanced filtering by dates, locations, lineages with pre-built indices
2. **Family Tree Visualization:** Interactive multi-generation family tree with touch support
3. **Information Disclosure:** Organized information presentation reducing cognitive overload
4. **Component Integration:** Seamless interaction between search, tree, and navigation

### Performance Metrics
1. **Search Performance:** Advanced searches complete within 200ms
2. **Tree Rendering:** Family tree loads within 500ms for 3 generations
3. **Mobile Performance:** Smooth interactions on mid-range mobile devices
4. **Memory Efficiency:** Optimized caching prevents memory issues during extended use

### User Experience Validation
1. **Research Efficiency:** Users complete genealogy research tasks 50% faster
2. **Feature Adoption:** Regular use of advanced search filters and family tree
3. **Information Digestibility:** Users report less overwhelming experience with progressive disclosure
4. **Cross-Component Flow:** Seamless navigation between search results, family tree, and person pages

## Testing Plan

### Component Integration Testing
1. Test search-to-tree navigation workflow
2. Verify tree-to-person page navigation
3. Test information disclosure on various person page types
4. Confirm mobile touch interactions across all components

### Performance Testing
1. Measure search index loading and query performance
2. Test family tree rendering with various family sizes
3. Validate mobile performance on actual devices
4. Monitor memory usage during extended browsing sessions

### User Experience Testing
1. Test complete genealogy research workflows
2. Verify accessibility compliance across all components
3. Test cross-browser compatibility
4. Validate progressive enhancement functionality

## Deployment Instructions

### Prerequisites
- Phase 1 foundation architecture completed and deployed
- Node.js build environment setup
- Search indices and optimized data structure in place

### Deployment Steps
1. **Build Enhanced Components:**
   ```bash
   npm run build:search-indices
   npm run build:tree-data
   npm run build:disclosure-data
   ```

2. **Deploy Components:**
   ```bash
   git add docs/new/js/components/
   git add docs/new/css/
   git commit -m "Phase 2: Core features implementation"
   git push origin main
   ```

3. **Verify Functionality:**
   - Test enhanced search functionality
   - Verify family tree rendering
   - Check information disclosure on person pages
   - Confirm mobile responsiveness

## Phase 2 Completion Checklist

- [ ] Enhanced search with advanced filtering implemented
- [ ] Pre-built search indices created and optimized
- [ ] Family tree component with D3.js visualization working
- [ ] Touch interactions and mobile optimization functional
- [ ] Progressive information disclosure system deployed
- [ ] User preference persistence working
- [ ] Cross-component integration tested
- [ ] Performance metrics met across all features
- [ ] Mobile experience significantly improved
- [ ] Accessibility compliance verified
- [ ] Cross-browser compatibility tested
- [ ] Documentation updated for new components

---

**Phase 2 Completion Note:** This phase transforms AuntieRuth.com from a static genealogy site into an interactive research platform. The enhanced search, family tree visualization, and progressive information disclosure provide the core functionality needed for efficient genealogy research, setting the stage for Phase 3's advanced features.