# PRP-Phase-03: Advanced Features Implementation

## Executive Summary

**Phase:** Advanced Features (3 of 3)
**Duration:** 1-2 months
**Priority:** High Impact - Completes comprehensive UX modernization
**Impact:** High - Delivers advanced genealogy research capabilities and modern web experience

This phase implements the advanced features that complete the comprehensive UX modernization of AuntieRuth.com. Building on the foundation architecture (Phase 1) and core features (Phase 2), this phase delivers relationship navigation, timeline visualization, and modern URL routing that transform the site into a cutting-edge genealogy research platform.

## Background & Context

### Prerequisites - Required Reading
Before starting this PRP, read:
- `../docs/README.md` - Complete understanding of genealogy file naming conventions and directory structure
- `docs/new/CLAUDE.md` - Architecture and development guidelines for the modernization project
- `PRPs/phase-01.md` - Foundation architecture that provides the component system and data structure
- `PRPs/phase-02.md` - Core features providing search, family tree, and information disclosure
- `PRPs/priority-04.md` - Relationship navigator requirements implemented in this phase
- `PRPs/priority-06.md` - Timeline view requirements implemented in this phase
- `PRPs/priority-08.md` - URL routing requirements implemented in this phase

### Foundation Dependencies
This phase builds on completed Phase 1 and Phase 2 capabilities:
- **Component Architecture:** Modular system with BaseComponent class
- **Data Management:** Lineage-based chunking with DataManager
- **Enhanced Navigation:** NavigationComponent with family context
- **Advanced Search:** SearchComponent with pre-built indices and filtering
- **Family Tree:** FamilyTreeComponent with D3.js visualization
- **Information Disclosure:** Progressive information presentation system
- **Mobile-Responsive Framework:** Touch-optimized interface

### Current Site Capabilities After Phase 2
- Enhanced navigation resolving critical usability issues
- Advanced search with filtering by dates, locations, and lineages
- Interactive family tree visualization with touch support
- Progressive information disclosure reducing cognitive load
- Mobile-first responsive design across all components
- Optimized data loading with efficient caching

## Phase 3 Objectives

### Advanced Feature Implementation
1. **Relationship Navigator:** Intelligent relationship path finding and family context
2. **Timeline Visualization:** Chronological family event visualization with historical context
3. **Modern URL Routing:** Clean URLs with deep linking and state management
4. **Advanced Integration:** Seamless interaction between all components

### Technical Deliverables
1. RelationshipNavigator with pre-computed relationship graphs
2. TimelineComponent with D3.js chronological visualization
3. URLRouter with History API and legacy URL compatibility
4. Complete component ecosystem with advanced research workflows

## Implementation Details

### 1. Relationship Navigator Implementation

#### Relationship Graph Pre-computation
Building on Phase 1's data chunking, implement relationship graph with pre-computed paths for performance.

```javascript
// scripts/build-relationship-graph.js
const fs = require('fs').promises;
const path = require('path');

class RelationshipGraphBuilder {
  constructor() {
    this.relationshipGraph = new Map();
    this.personIndex = new Map();
  }

  async buildRelationshipGraph() {
    console.log('Building relationship graph...');

    // Load all lineage data
    const allPeople = await this.loadAllPeople();

    // Build person index for fast lookups
    this.buildPersonIndex(allPeople);

    // Build relationship graph
    this.buildGraph(allPeople);

    // Pre-compute common relationship paths
    await this.preComputeRelationshipPaths();

    // Save optimized graph structure
    await this.saveRelationshipGraph();

    console.log(`Relationship graph built: ${allPeople.length} people, ${this.relationshipGraph.size} relationships`);
  }

  async loadAllPeople() {
    const allPeople = [];

    for (let lineageId = 0; lineageId <= 9; lineageId++) {
      try {
        const lineageData = JSON.parse(
          await fs.readFile(`./docs/new/js/data/lineages/L${lineageId}.json`, 'utf8')
        );
        allPeople.push(...lineageData.people);
      } catch (error) {
        console.warn(`Failed to load lineage ${lineageId}:`, error);
      }
    }

    return allPeople;
  }

  buildPersonIndex(people) {
    people.forEach(person => {
      this.personIndex.set(person.id, person);
      // Also index by name for relationship string matching
      if (person.name) {
        this.personIndex.set(person.name.toLowerCase(), person);
      }
    });
  }

  buildGraph(people) {
    people.forEach(person => {
      const personId = person.id;

      if (!this.relationshipGraph.has(personId)) {
        this.relationshipGraph.set(personId, {
          person: person,
          relationships: {
            parents: [],
            children: [],
            spouses: [],
            siblings: []
          },
          paths: new Map() // Pre-computed paths to other people
        });
      }

      const node = this.relationshipGraph.get(personId);

      // Process parent relationships
      [person.father, person.mother].forEach(parent => {
        if (parent) {
          const parentId = this.extractPersonId(parent);
          if (parentId && this.personIndex.has(parentId)) {
            node.relationships.parents.push(parentId);
            this.addReverseRelationship(parentId, personId, 'children');
          }
        }
      });

      // Process spouse relationships
      [person.spouse, person.spouse2, person.spouse3, person.spouse4].forEach(spouse => {
        if (spouse && spouse.trim()) {
          const spouseId = this.extractPersonId(spouse);
          if (spouseId && this.personIndex.has(spouseId)) {
            node.relationships.spouses.push(spouseId);
            this.addReverseRelationship(spouseId, personId, 'spouses');
          }
        }
      });
    });

    // Compute siblings (people with same parents)
    this.computeSiblings();
  }

  addReverseRelationship(targetPersonId, sourcePersonId, relationshipType) {
    if (!this.relationshipGraph.has(targetPersonId)) {
      const targetPerson = this.personIndex.get(targetPersonId);
      if (targetPerson) {
        this.relationshipGraph.set(targetPersonId, {
          person: targetPerson,
          relationships: {
            parents: [],
            children: [],
            spouses: [],
            siblings: []
          },
          paths: new Map()
        });
      }
    }

    const targetNode = this.relationshipGraph.get(targetPersonId);
    if (targetNode && !targetNode.relationships[relationshipType].includes(sourcePersonId)) {
      targetNode.relationships[relationshipType].push(sourcePersonId);
    }
  }

  computeSiblings() {
    // Group people by parents to find siblings
    const parentGroups = new Map();

    this.relationshipGraph.forEach((node, personId) => {
      if (node.relationships.parents.length > 0) {
        const parentKey = node.relationships.parents.sort().join(',');
        if (!parentGroups.has(parentKey)) {
          parentGroups.set(parentKey, []);
        }
        parentGroups.get(parentKey).push(personId);
      }
    });

    // Add sibling relationships
    parentGroups.forEach(siblings => {
      if (siblings.length > 1) {
        siblings.forEach(personId => {
          const node = this.relationshipGraph.get(personId);
          if (node) {
            node.relationships.siblings = siblings.filter(id => id !== personId);
          }
        });
      }
    });
  }

  async preComputeRelationshipPaths() {
    const personIds = Array.from(this.relationshipGraph.keys());

    // Pre-compute paths for close relationships (up to 4 degrees of separation)
    for (let i = 0; i < personIds.length; i++) {
      const sourceId = personIds[i];

      // Use breadth-first search to find paths
      const visited = new Set();
      const queue = [{ personId: sourceId, path: [], degree: 0 }];

      while (queue.length > 0) {
        const { personId, path, degree } = queue.shift();

        if (visited.has(personId) || degree > 4) continue;
        visited.add(personId);

        if (personId !== sourceId) {
          // Store the path
          const sourceNode = this.relationshipGraph.get(sourceId);
          if (sourceNode) {
            sourceNode.paths.set(personId, {
              path: [...path],
              degree: degree,
              relationship: this.calculateRelationshipType(path)
            });
          }
        }

        // Add connected people to queue
        const node = this.relationshipGraph.get(personId);
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

      // Progress indicator
      if (i % 100 === 0) {
        console.log(`Processed ${i}/${personIds.length} people for relationship paths`);
      }
    }
  }

  calculateRelationshipType(path) {
    if (path.length === 0) return 'self';
    if (path.length === 1) {
      const rel = path[0];
      switch (rel.type) {
        case 'parents': return 'parent';
        case 'children': return 'child';
        case 'spouses': return 'spouse';
        case 'siblings': return 'sibling';
      }
    }

    // More complex relationships
    if (path.length === 2) {
      const [rel1, rel2] = path;
      if (rel1.type === 'parents' && rel2.type === 'children') return 'grandparent';
      if (rel1.type === 'children' && rel2.type === 'parents') return 'grandchild';
      if (rel1.type === 'siblings' && rel2.type === 'children') return 'aunt/uncle';
      if (rel1.type === 'parents' && rel2.type === 'siblings') return 'aunt/uncle';
      // Add more relationship types as needed
    }

    return `${path.length} degrees of separation`;
  }

  extractPersonId(familyMemberString) {
    // Implementation depends on data format
    // This is a simplified version - would need actual parsing logic
    const match = familyMemberString.match(/\[(.+?)\]/);
    if (match) {
      // Try to find person by name in the lineage mentioned
      const lineageName = match[1];
      // Would need more sophisticated matching
    }
    return null; // Placeholder
  }

  async saveRelationshipGraph() {
    // Convert Map to serializable format
    const graphData = {
      metadata: {
        generated: new Date().toISOString(),
        totalPeople: this.relationshipGraph.size,
        version: '1.0'
      },
      relationships: {}
    };

    this.relationshipGraph.forEach((node, personId) => {
      graphData.relationships[personId] = {
        relationships: node.relationships,
        paths: Object.fromEntries(node.paths)
      };
    });

    await fs.writeFile(
      './docs/new/js/data/relationship-graph.json',
      JSON.stringify(graphData, null, 2)
    );
  }
}

if (require.main === module) {
  const builder = new RelationshipGraphBuilder();
  builder.buildRelationshipGraph().catch(console.error);
}
```

#### Relationship Navigator Component
```javascript
// components/relationship-navigator.js
import BaseComponent from '../core/base-component.js';

class RelationshipNavigatorComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.relationshipGraph = null;
    this.currentPerson = null;
    this.relationshipHistory = [];
    this.sidebarVisible = true;
  }

  async init() {
    await super.init();
    await this.loadRelationshipGraph();

    if (this.currentPage.type === 'person') {
      await this.initializeForPerson(this.currentPage.pageId);
    }
  }

  async render() {
    const navigatorHtml = this.generateNavigatorInterface();

    // Add as sidebar to existing page layout
    const existingSidebar = document.querySelector('.relationship-sidebar');
    if (existingSidebar) {
      existingSidebar.outerHTML = navigatorHtml;
    } else {
      document.body.insertAdjacentHTML('beforeend', navigatorHtml);
    }

    if (this.currentPerson) {
      await this.updateRelationshipContext();
    }
  }

  generateNavigatorInterface() {
    return `
      <div class="relationship-sidebar ${this.sidebarVisible ? 'visible' : 'hidden'}"
           aria-label="Relationship Navigator">

        <div class="sidebar-header">
          <button class="sidebar-toggle"
                  aria-expanded="${this.sidebarVisible}"
                  aria-controls="relationship-content"
                  title="Toggle relationship navigator">
            <span class="toggle-icon">${this.sidebarVisible ? '◀' : '▶'}</span>
          </button>

          <h3 class="sidebar-title">Family Context</h3>

          <button class="relationship-finder-btn"
                  title="Find relationship between two people"
                  aria-label="Relationship finder">
            🔍
          </button>
        </div>

        <div class="sidebar-content" id="relationship-content">
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

        <div class="relationship-finder-modal" id="relationship-finder" hidden>
          ${this.generateRelationshipFinderModal()}
        </div>
      </div>
    `;
  }

  generateCurrentPersonCard() {
    if (!this.currentPerson) {
      return '<div class="no-person">No person selected</div>';
    }

    const birthYear = this.extractYear(this.currentPerson.birthDate) || '';
    const deathYear = this.extractYear(this.currentPerson.deathDate) || '';
    const lifespan = birthYear && deathYear ? `${birthYear}-${deathYear}` :
                    birthYear ? `b. ${birthYear}` :
                    deathYear ? `d. ${deathYear}` : '';

    return `
      <div class="current-person-card">
        <h4 class="person-name">${this.currentPerson.name}</h4>
        <div class="person-details">
          ${lifespan ? `<div class="lifespan">📅 ${lifespan}</div>` : ''}
          ${this.currentPerson.birthLocation ?
            `<div class="location">📍 ${this.currentPerson.birthLocation}</div>` : ''}
          <div class="lineage">🌳 ${this.currentPerson.lineageName}</div>
        </div>
      </div>
    `;
  }

  generateImmediateFamilySection() {
    if (!this.currentPerson || !this.relationshipGraph) {
      return '<div class="loading">Loading family context...</div>';
    }

    const personNode = this.relationshipGraph.relationships[this.currentPerson.id];
    if (!personNode) {
      return '<div class="no-family">No family relationships found</div>';
    }

    const { relationships } = personNode;

    return `
      <div class="immediate-family">
        <h5>Immediate Family</h5>

        ${relationships.parents.length > 0 ? `
          <div class="family-group">
            <span class="group-label">Parents</span>
            <div class="family-members">
              ${relationships.parents.map(parentId =>
                this.generateFamilyMemberLink(parentId, 'parent')).join('')}
            </div>
          </div>
        ` : ''}

        ${relationships.spouses.length > 0 ? `
          <div class="family-group">
            <span class="group-label">Spouse${relationships.spouses.length > 1 ? 's' : ''}</span>
            <div class="family-members">
              ${relationships.spouses.map(spouseId =>
                this.generateFamilyMemberLink(spouseId, 'spouse')).join('')}
            </div>
          </div>
        ` : ''}

        ${relationships.children.length > 0 ? `
          <div class="family-group">
            <span class="group-label">Children</span>
            <div class="family-members">
              ${relationships.children.map(childId =>
                this.generateFamilyMemberLink(childId, 'child')).join('')}
            </div>
          </div>
        ` : ''}

        ${relationships.siblings.length > 0 ? `
          <div class="family-group">
            <span class="group-label">Siblings</span>
            <div class="family-members">
              ${relationships.siblings.map(siblingId =>
                this.generateFamilyMemberLink(siblingId, 'sibling')).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }

  generateFamilyMemberLink(personId, relationshipType) {
    const person = this.getPersonById(personId);
    if (!person) return '';

    const birthYear = this.extractYear(person.birthDate);
    const deathYear = this.extractYear(person.deathDate);
    const yearInfo = birthYear || deathYear ?
      `(${birthYear || '?'}-${deathYear || '?'})` : '';

    return `
      <button class="family-member-btn"
              data-person-id="${personId}"
              data-relationship="${relationshipType}"
              title="View ${person.name}'s details">
        <span class="member-name">${person.name}</span>
        ${yearInfo ? `<span class="member-years">${yearInfo}</span>` : ''}
      </button>
    `;
  }

  generateRelationshipTools() {
    return `
      <div class="relationship-tools">
        <h5>Relationship Tools</h5>

        <button class="tool-btn" id="find-common-ancestors" title="Find common ancestors">
          🌳 Common Ancestors
        </button>

        <button class="tool-btn" id="explore-descendants" title="Explore all descendants">
          👨‍👩‍👧‍👦 All Descendants
        </button>

        <button class="tool-btn" id="find-cousins" title="Find cousins">
          👥 Find Cousins
        </button>

        <button class="tool-btn" id="migration-path" title="Track family migration">
          🗺️ Migration Path
        </button>
      </div>
    `;
  }

  generateRecentExploration() {
    if (this.relationshipHistory.length === 0) {
      return '<div class="no-history">No recent exploration</div>';
    }

    return `
      <div class="recent-exploration">
        <h5>Recent Exploration</h5>
        <div class="exploration-history">
          ${this.relationshipHistory.slice(0, 5).map(entry => `
            <button class="history-item" data-person-id="${entry.personId}">
              <span class="history-name">${entry.name}</span>
              <span class="history-relationship">${entry.relationship}</span>
            </button>
          `).join('')}
        </div>
      </div>
    `;
  }

  generateRelationshipFinderModal() {
    return `
      <div class="modal-content">
        <div class="modal-header">
          <h4>How Are They Related?</h4>
          <button class="modal-close" aria-label="Close">&times;</button>
        </div>

        <div class="modal-body">
          <div class="person-selector">
            <label for="person1-search">First Person:</label>
            <input type="text"
                   id="person1-search"
                   placeholder="Search by name..."
                   class="person-search-input">
            <div class="search-suggestions" id="person1-suggestions"></div>
          </div>

          <div class="person-selector">
            <label for="person2-search">Second Person:</label>
            <input type="text"
                   id="person2-search"
                   placeholder="Search by name..."
                   class="person-search-input">
            <div class="search-suggestions" id="person2-suggestions"></div>
          </div>

          <button class="btn-primary" id="find-relationship" disabled>
            Find Relationship
          </button>

          <div class="relationship-result" id="relationship-result"></div>
        </div>
      </div>
    `;
  }

  async loadRelationshipGraph() {
    try {
      const response = await fetch('/auntruth/new/js/data/relationship-graph.json');
      if (response.ok) {
        this.relationshipGraph = await response.json();
        console.log('Relationship graph loaded successfully');
      } else {
        throw new Error('Failed to load relationship graph');
      }
    } catch (error) {
      console.error('Failed to load relationship graph:', error);
      // Fallback to basic functionality without pre-computed relationships
    }
  }

  async initializeForPerson(personId) {
    try {
      this.currentPerson = await this.dataManager.getPersonData(personId);
      if (this.currentPerson) {
        this.addToRelationshipHistory(this.currentPerson, 'current');
      }
    } catch (error) {
      console.error('Failed to initialize relationship navigator:', error);
    }
  }

  attachEventListeners() {
    // Sidebar toggle
    document.querySelector('.sidebar-toggle')?.addEventListener('click', () => {
      this.toggleSidebar();
    });

    // Family member navigation
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('family-member-btn') ||
          e.target.closest('.family-member-btn')) {

        const btn = e.target.closest('.family-member-btn');
        const personId = btn.dataset.personId;
        const relationship = btn.dataset.relationship;

        this.navigateToFamilyMember(personId, relationship);
      }
    });

    // Relationship tools
    document.getElementById('find-common-ancestors')?.addEventListener('click', () => {
      this.findCommonAncestors();
    });

    document.getElementById('explore-descendants')?.addEventListener('click', () => {
      this.exploreDescendants();
    });

    document.getElementById('find-cousins')?.addEventListener('click', () => {
      this.findCousins();
    });

    // Relationship finder modal
    document.querySelector('.relationship-finder-btn')?.addEventListener('click', () => {
      this.openRelationshipFinder();
    });

    document.querySelector('.modal-close')?.addEventListener('click', () => {
      this.closeRelationshipFinder();
    });

    document.getElementById('find-relationship')?.addEventListener('click', () => {
      this.executeRelationshipSearch();
    });

    // Person search in modal
    this.setupPersonSearchAutocomplete();
  }

  async navigateToFamilyMember(personId, relationship) {
    try {
      const person = await this.dataManager.getPersonData(personId);
      if (person) {
        // Add to relationship history
        this.addToRelationshipHistory(person, relationship);

        // Navigate to person's page
        window.location.href = person.url;
      }
    } catch (error) {
      console.error('Failed to navigate to family member:', error);
    }
  }

  async findRelationshipPath(person1Id, person2Id) {
    if (!this.relationshipGraph || !this.relationshipGraph.relationships) {
      return this.findRelationshipPathBFS(person1Id, person2Id);
    }

    // Check pre-computed paths first
    const person1Node = this.relationshipGraph.relationships[person1Id];
    if (person1Node && person1Node.paths && person1Node.paths[person2Id]) {
      return person1Node.paths[person2Id];
    }

    // Fallback to BFS if not pre-computed
    return this.findRelationshipPathBFS(person1Id, person2Id);
  }

  findRelationshipPathBFS(startId, targetId) {
    if (startId === targetId) {
      return { relationship: 'self', degree: 0, path: [] };
    }

    const visited = new Set();
    const queue = [{ personId: startId, path: [], degree: 0 }];

    while (queue.length > 0) {
      const { personId, path, degree } = queue.shift();

      if (visited.has(personId) || degree > 6) continue; // Limit search depth
      visited.add(personId);

      if (personId === targetId) {
        return {
          relationship: this.describeRelationshipPath(path),
          degree: degree,
          path: path
        };
      }

      // Add connected people to queue
      const relationships = this.getPersonRelationships(personId);
      if (relationships) {
        Object.entries(relationships).forEach(([relType, relatedIds]) => {
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

    return null; // No relationship found
  }

  describeRelationshipPath(path) {
    if (path.length === 0) return 'self';
    if (path.length === 1) {
      const step = path[0];
      switch (step.type) {
        case 'parents': return 'parent';
        case 'children': return 'child';
        case 'spouses': return 'spouse';
        case 'siblings': return 'sibling';
        default: return 'related';
      }
    }

    // Complex relationships
    if (path.length === 2) {
      const [step1, step2] = path;
      if (step1.type === 'parents' && step2.type === 'parents') return 'grandparent';
      if (step1.type === 'children' && step2.type === 'children') return 'grandchild';
      if (step1.type === 'siblings' && step2.type === 'children') return 'nephew/niece';
      if (step1.type === 'parents' && step2.type === 'siblings') return 'aunt/uncle';
      // Add more specific relationships
    }

    return `${path.length} degrees of separation`;
  }

  addToRelationshipHistory(person, relationship) {
    const historyEntry = {
      personId: person.id,
      name: person.name,
      relationship: relationship,
      timestamp: Date.now()
    };

    // Remove if already exists
    this.relationshipHistory = this.relationshipHistory.filter(
      entry => entry.personId !== person.id
    );

    // Add to beginning
    this.relationshipHistory.unshift(historyEntry);

    // Keep only last 20
    this.relationshipHistory = this.relationshipHistory.slice(0, 20);
  }

  getPersonById(personId) {
    // This would use the DataManager to get person data
    // For now, placeholder implementation
    return null;
  }

  getPersonRelationships(personId) {
    if (!this.relationshipGraph || !this.relationshipGraph.relationships) return null;
    const node = this.relationshipGraph.relationships[personId];
    return node ? node.relationships : null;
  }

  extractYear(dateString) {
    if (!dateString) return null;
    const match = dateString.match(/\b(19|20)\d{2}\b/);
    return match ? parseInt(match[0]) : null;
  }
}

export default RelationshipNavigatorComponent;
```

### 2. Timeline Visualization Implementation

#### Timeline Component with Historical Context
```javascript
// components/timeline.js
import BaseComponent from '../core/base-component.js';

class TimelineComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.timelineData = [];
    this.historicalEvents = [];
    this.currentView = 'century'; // century, decade, year
    this.dateRange = { start: 1800, end: 2025 };
    this.selectedLineages = [];
    this.eventTypes = {
      birth: true,
      death: true,
      marriage: true,
      migration: false
    };
  }

  async init() {
    await super.init();
    await this.loadTimelineData();
    await this.loadHistoricalContext();
  }

  async render() {
    const timelineHtml = this.generateTimelineInterface();
    const targetElement = document.getElementById('timeline-container') || document.body;

    if (document.querySelector('.timeline-component')) {
      document.querySelector('.timeline-component').outerHTML = timelineHtml;
    } else {
      targetElement.insertAdjacentHTML('afterbegin', timelineHtml);
    }

    await this.renderTimeline();
  }

  generateTimelineInterface() {
    return `
      <div class="timeline-component">
        <div class="timeline-controls">
          <div class="timeline-toolbar">
            <div class="view-controls">
              <label>Timeline View:</label>
              <select id="timeline-view" aria-label="Timeline view level">
                <option value="century">Century View</option>
                <option value="decade" selected>Decade View</option>
                <option value="year">Year View</option>
              </select>
            </div>

            <div class="date-range-controls">
              <label for="start-year">From:</label>
              <input type="number" id="start-year" min="1800" max="2025" value="1800" step="10">
              <label for="end-year">To:</label>
              <input type="number" id="end-year" min="1800" max="2025" value="2025" step="10">
            </div>

            <div class="lineage-filters">
              <label>Show Lineages:</label>
              <div class="lineage-checkboxes">
                ${this.generateLineageCheckboxes()}
              </div>
            </div>

            <div class="event-filters">
              <label>Event Types:</label>
              <div class="event-checkboxes">
                <label><input type="checkbox" id="show-births" checked> Births</label>
                <label><input type="checkbox" id="show-deaths" checked> Deaths</label>
                <label><input type="checkbox" id="show-marriages"> Marriages</label>
                <label><input type="checkbox" id="show-migrations"> Migrations</label>
              </div>
            </div>

            <div class="timeline-actions">
              <button class="btn-sm" id="zoom-to-events" title="Zoom to events">🎯</button>
              <button class="btn-sm" id="export-timeline" title="Export timeline">📄</button>
              <button class="btn-sm" id="timeline-help" title="Help">❓</button>
            </div>
          </div>
        </div>

        <div class="timeline-container">
          <div class="timeline-legends">
            <div class="event-legend">
              <span class="legend-item birth-event">● Birth</span>
              <span class="legend-item death-event">● Death</span>
              <span class="legend-item marriage-event">● Marriage</span>
              <span class="legend-item historical-event">● Historical</span>
            </div>
          </div>

          <div class="timeline-viewport">
            <svg class="timeline-svg" width="100%" height="500">
              <defs>
                <pattern id="timeline-grid" width="50" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 50 0 L 0 0 0 20" fill="none" stroke="#f5f5f5" stroke-width="1"/>
                </pattern>
                <filter id="event-glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>

              <rect width="100%" height="100%" fill="url(#timeline-grid)"/>

              <g class="timeline-content" transform="translate(60, 40)">
                <g class="time-axis"></g>
                <g class="historical-events"></g>
                <g class="family-events"></g>
                <g class="event-labels"></g>
              </g>
            </svg>
          </div>

          <div class="timeline-details" id="timeline-details">
            <div class="details-header">
              <h4>Timeline Details</h4>
              <button class="details-close" aria-label="Close details">&times;</button>
            </div>
            <div class="details-content" id="details-content">
              Select an event to view details
            </div>
          </div>
        </div>

        <div class="timeline-summary">
          <div class="event-summary" id="event-summary">
            <span class="summary-text">Loading timeline data...</span>
          </div>
        </div>
      </div>
    `;
  }

  generateLineageCheckboxes() {
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

    return lineages.map(lineage => `
      <label class="lineage-checkbox">
        <input type="checkbox" value="${lineage.id}" checked>
        <span class="lineage-name">${lineage.name}</span>
      </label>
    `).join('');
  }

  async loadTimelineData() {
    try {
      const metadata = await this.dataManager.getMetadata();
      this.timelineData = [];

      // Load timeline events from all lineages
      for (let lineageId = 0; lineageId <= 9; lineageId++) {
        try {
          const lineageData = await this.dataManager.getLineageData(lineageId.toString());

          lineageData.people.forEach(person => {
            // Birth events
            if (person.birthDate) {
              const birthYear = this.extractYear(person.birthDate);
              if (birthYear) {
                this.timelineData.push({
                  type: 'birth',
                  year: birthYear,
                  date: person.birthDate,
                  person: person,
                  location: person.birthLocation,
                  lineage: person.lineage,
                  lineageName: person.lineageName,
                  description: `${person.name} born`,
                  id: `birth-${person.id}`
                });
              }
            }

            // Death events
            if (person.deathDate) {
              const deathYear = this.extractYear(person.deathDate);
              if (deathYear) {
                this.timelineData.push({
                  type: 'death',
                  year: deathYear,
                  date: person.deathDate,
                  person: person,
                  location: person.deathLocation,
                  lineage: person.lineage,
                  lineageName: person.lineageName,
                  description: `${person.name} died`,
                  id: `death-${person.id}`
                });
              }
            }

            // Marriage events (simplified - would need more sophisticated parsing)
            if (person.spouse && person.birthDate) {
              const birthYear = this.extractYear(person.birthDate);
              if (birthYear) {
                // Estimate marriage year (birth + 25 years as rough estimate)
                const estimatedMarriageYear = birthYear + 25;
                if (estimatedMarriageYear <= 2025) {
                  this.timelineData.push({
                    type: 'marriage',
                    year: estimatedMarriageYear,
                    date: `circa ${estimatedMarriageYear}`,
                    person: person,
                    spouse: person.spouse,
                    lineage: person.lineage,
                    lineageName: person.lineageName,
                    description: `${person.name} married`,
                    id: `marriage-${person.id}`,
                    estimated: true
                  });
                }
              }
            }
          });
        } catch (error) {
          console.warn(`Failed to load timeline data for lineage ${lineageId}:`, error);
        }
      }

      // Sort events chronologically
      this.timelineData.sort((a, b) => a.year - b.year);

      console.log(`Loaded ${this.timelineData.length} timeline events`);

    } catch (error) {
      console.error('Failed to load timeline data:', error);
    }
  }

  async loadHistoricalContext() {
    // Load historical events for context
    // This would ideally come from a historical events database
    this.historicalEvents = [
      { year: 1867, event: 'Canadian Confederation', type: 'political' },
      { year: 1869, event: 'Red River Rebellion', type: 'political' },
      { year: 1885, event: 'Canadian Pacific Railway completed', type: 'infrastructure' },
      { year: 1914, event: 'World War I begins', type: 'war' },
      { year: 1918, event: 'World War I ends', type: 'war' },
      { year: 1929, event: 'Great Depression begins', type: 'economic' },
      { year: 1939, event: 'World War II begins', type: 'war' },
      { year: 1945, event: 'World War II ends', type: 'war' },
      { year: 1967, event: 'Canadian Centennial', type: 'celebration' },
      { year: 1982, event: 'Charter of Rights and Freedoms', type: 'political' }
    ];
  }

  async renderTimeline() {
    const svg = document.querySelector('.timeline-svg');
    const timelineContent = svg.querySelector('.timeline-content');
    const timeAxis = timelineContent.querySelector('.time-axis');
    const historicalEventsGroup = timelineContent.querySelector('.historical-events');
    const familyEventsGroup = timelineContent.querySelector('.family-events');

    // Clear existing content
    timeAxis.innerHTML = '';
    historicalEventsGroup.innerHTML = '';
    familyEventsGroup.innerHTML = '';

    // Calculate dimensions and scales
    const containerRect = svg.getBoundingClientRect();
    const timelineWidth = containerRect.width - 120; // Account for margins
    const timelineHeight = containerRect.height - 80;

    // Filter events based on current settings
    const filteredEvents = this.getFilteredEvents();

    // Determine time scale based on view
    const { startYear, endYear, tickInterval } = this.getTimeScale();

    // Create time axis
    this.renderTimeAxis(timeAxis, startYear, endYear, tickInterval, timelineWidth);

    // Render historical context
    this.renderHistoricalEvents(historicalEventsGroup, startYear, endYear, timelineWidth, timelineHeight);

    // Render family events
    this.renderFamilyEvents(familyEventsGroup, filteredEvents, startYear, endYear, timelineWidth, timelineHeight);

    // Update summary
    this.updateTimelineSummary(filteredEvents);
  }

  getTimeScale() {
    let startYear = this.dateRange.start;
    let endYear = this.dateRange.end;
    let tickInterval = 10;

    switch (this.currentView) {
      case 'century':
        tickInterval = 25;
        break;
      case 'decade':
        tickInterval = 10;
        break;
      case 'year':
        tickInterval = 5;
        // Narrow the range for year view
        const filteredEvents = this.getFilteredEvents();
        if (filteredEvents.length > 0) {
          const eventYears = filteredEvents.map(e => e.year);
          startYear = Math.max(this.dateRange.start, Math.min(...eventYears) - 5);
          endYear = Math.min(this.dateRange.end, Math.max(...eventYears) + 5);
        }
        break;
    }

    return { startYear, endYear, tickInterval };
  }

  getFilteredEvents() {
    return this.timelineData.filter(event => {
      // Date range filter
      if (event.year < this.dateRange.start || event.year > this.dateRange.end) {
        return false;
      }

      // Lineage filter
      if (this.selectedLineages.length > 0 && !this.selectedLineages.includes(event.lineage)) {
        return false;
      }

      // Event type filter
      if (!this.eventTypes[event.type]) {
        return false;
      }

      return true;
    });
  }

  renderTimeAxis(timeAxis, startYear, endYear, tickInterval, timelineWidth) {
    const yearRange = endYear - startYear;

    // Main timeline
    const mainLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    mainLine.setAttribute('x1', 0);
    mainLine.setAttribute('y1', 20);
    mainLine.setAttribute('x2', timelineWidth);
    mainLine.setAttribute('y2', 20);
    mainLine.classList.add('timeline-axis');
    timeAxis.appendChild(mainLine);

    // Year ticks and labels
    for (let year = startYear; year <= endYear; year += tickInterval) {
      const x = ((year - startYear) / yearRange) * timelineWidth;

      // Tick mark
      const tick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      tick.setAttribute('x1', x);
      tick.setAttribute('y1', 15);
      tick.setAttribute('x2', x);
      tick.setAttribute('y2', 25);
      tick.classList.add('timeline-tick');
      timeAxis.appendChild(tick);

      // Year label
      const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      label.setAttribute('x', x);
      label.setAttribute('y', 10);
      label.setAttribute('text-anchor', 'middle');
      label.classList.add('timeline-label');
      label.textContent = year.toString();
      timeAxis.appendChild(label);
    }
  }

  renderHistoricalEvents(historicalEventsGroup, startYear, endYear, timelineWidth, timelineHeight) {
    const yearRange = endYear - startYear;

    this.historicalEvents.forEach(historicalEvent => {
      if (historicalEvent.year >= startYear && historicalEvent.year <= endYear) {
        const x = ((historicalEvent.year - startYear) / yearRange) * timelineWidth;

        // Historical event marker
        const eventLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        eventLine.setAttribute('x1', x);
        eventLine.setAttribute('y1', 30);
        eventLine.setAttribute('x2', x);
        eventLine.setAttribute('y2', 50);
        eventLine.classList.add('historical-event-line', historicalEvent.type);
        historicalEventsGroup.appendChild(eventLine);

        // Event label (rotated for space)
        const eventLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        eventLabel.setAttribute('x', x);
        eventLabel.setAttribute('y', 45);
        eventLabel.setAttribute('text-anchor', 'start');
        eventLabel.setAttribute('transform', `rotate(-45, ${x}, 45)`);
        eventLabel.classList.add('historical-event-label');
        eventLabel.textContent = historicalEvent.event;
        historicalEventsGroup.appendChild(eventLabel);
      }
    });
  }

  renderFamilyEvents(familyEventsGroup, events, startYear, endYear, timelineWidth, timelineHeight) {
    const yearRange = endYear - startYear;
    const eventHeight = Math.max(20, (timelineHeight - 100) / Math.max(events.length, 1));

    // Group events by year for better visualization
    const eventsByYear = new Map();
    events.forEach(event => {
      if (!eventsByYear.has(event.year)) {
        eventsByYear.set(event.year, []);
      }
      eventsByYear.get(event.year).push(event);
    });

    let yOffset = 60;

    eventsByYear.forEach((yearEvents, year) => {
      const x = ((year - startYear) / yearRange) * timelineWidth;

      yearEvents.forEach((event, index) => {
        const y = yOffset + (index * 25);

        // Event circle
        const eventCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        eventCircle.setAttribute('cx', x);
        eventCircle.setAttribute('cy', y);
        eventCircle.setAttribute('r', 4);
        eventCircle.classList.add('family-event', `${event.type}-event`, `lineage-${event.lineage}`);
        eventCircle.setAttribute('data-event-id', event.id);
        familyEventsGroup.appendChild(eventCircle);

        // Event label (on hover or for important events)
        if (this.currentView === 'year' || yearEvents.length <= 3) {
          const eventLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          eventLabel.setAttribute('x', x + 8);
          eventLabel.setAttribute('y', y + 4);
          eventLabel.classList.add('family-event-label');
          eventLabel.textContent = `${event.person.name} (${event.type})`;
          familyEventsGroup.appendChild(eventLabel);
        }

        // Add interaction
        eventCircle.addEventListener('click', (e) => {
          e.stopPropagation();
          this.showEventDetails(event);
        });

        eventCircle.addEventListener('mouseenter', (e) => {
          this.showEventTooltip(event, e);
        });
      });

      yOffset += Math.max(50, yearEvents.length * 25 + 10);
    });
  }

  showEventDetails(event) {
    const detailsPanel = document.getElementById('timeline-details');
    const detailsContent = document.getElementById('details-content');

    const birthYear = this.extractYear(event.person.birthDate) || '';
    const deathYear = this.extractYear(event.person.deathDate) || '';
    const lifespan = birthYear && deathYear ? `${birthYear}-${deathYear}` :
                    birthYear ? `b. ${birthYear}` :
                    deathYear ? `d. ${deathYear}` : '';

    detailsContent.innerHTML = `
      <div class="event-detail-card">
        <h5>${event.description}</h5>
        <div class="event-meta">
          <div class="meta-item">
            <strong>Date:</strong> ${event.date}
            ${event.estimated ? ' <em>(estimated)</em>' : ''}
          </div>
          ${event.location ? `
            <div class="meta-item">
              <strong>Location:</strong> ${event.location}
            </div>
          ` : ''}
          <div class="meta-item">
            <strong>Lineage:</strong> ${event.lineageName}
          </div>
          ${lifespan ? `
            <div class="meta-item">
              <strong>Life Span:</strong> ${lifespan}
            </div>
          ` : ''}
        </div>

        <div class="event-actions">
          <a href="${event.person.url}" class="btn-sm btn-primary">View Person</a>
          <button class="btn-sm" onclick="this.closest('.timeline-component').querySelector('.timeline-component').showInFamilyTree('${event.person.id}')">
            View in Family Tree
          </button>
        </div>

        ${event.spouse ? `
          <div class="spouse-info">
            <strong>Spouse:</strong> ${event.spouse}
          </div>
        ` : ''}
      </div>
    `;

    detailsPanel.style.display = 'block';
  }

  showEventTooltip(event, mouseEvent) {
    // Create or update tooltip
    let tooltip = document.getElementById('timeline-tooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'timeline-tooltip';
      tooltip.className = 'timeline-tooltip';
      document.body.appendChild(tooltip);
    }

    tooltip.innerHTML = `
      <strong>${event.person.name}</strong><br>
      ${event.description}<br>
      <em>${event.date}</em>
    `;

    tooltip.style.left = mouseEvent.pageX + 10 + 'px';
    tooltip.style.top = mouseEvent.pageY - 10 + 'px';
    tooltip.style.display = 'block';

    // Hide tooltip after delay
    setTimeout(() => {
      tooltip.style.display = 'none';
    }, 3000);
  }

  updateTimelineSummary(events) {
    const summary = document.getElementById('event-summary');
    if (!summary) return;

    const eventCounts = events.reduce((counts, event) => {
      counts[event.type] = (counts[event.type] || 0) + 1;
      return counts;
    }, {});

    const summaryText = Object.entries(eventCounts)
      .map(([type, count]) => `${count} ${type}${count > 1 ? 's' : ''}`)
      .join(', ');

    summary.innerHTML = `
      <span class="summary-text">
        Showing ${events.length} events: ${summaryText}
        (${this.dateRange.start}-${this.dateRange.end})
      </span>
    `;
  }

  attachEventListeners() {
    // Timeline view controls
    document.getElementById('timeline-view')?.addEventListener('change', (e) => {
      this.currentView = e.target.value;
      this.renderTimeline();
    });

    // Date range controls
    document.getElementById('start-year')?.addEventListener('change', (e) => {
      this.dateRange.start = parseInt(e.target.value);
      this.renderTimeline();
    });

    document.getElementById('end-year')?.addEventListener('change', (e) => {
      this.dateRange.end = parseInt(e.target.value);
      this.renderTimeline();
    });

    // Lineage filters
    document.querySelectorAll('.lineage-checkbox input').forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        this.selectedLineages = Array.from(
          document.querySelectorAll('.lineage-checkbox input:checked')
        ).map(cb => cb.value);
        this.renderTimeline();
      });
    });

    // Event type filters
    ['births', 'deaths', 'marriages', 'migrations'].forEach(eventType => {
      document.getElementById(`show-${eventType}`)?.addEventListener('change', (e) => {
        this.eventTypes[eventType.slice(0, -1)] = e.target.checked; // Remove 's'
        this.renderTimeline();
      });
    });

    // Timeline actions
    document.getElementById('zoom-to-events')?.addEventListener('click', () => {
      this.zoomToEvents();
    });

    document.getElementById('export-timeline')?.addEventListener('click', () => {
      this.exportTimeline();
    });

    // Details panel close
    document.querySelector('.details-close')?.addEventListener('click', () => {
      document.getElementById('timeline-details').style.display = 'none';
    });

    // SVG pan and zoom (simplified)
    this.setupTimelinePanZoom();
  }

  zoomToEvents() {
    const filteredEvents = this.getFilteredEvents();
    if (filteredEvents.length === 0) return;

    const eventYears = filteredEvents.map(e => e.year);
    const minYear = Math.min(...eventYears);
    const maxYear = Math.max(...eventYears);

    // Add some padding
    this.dateRange.start = Math.max(1800, minYear - 10);
    this.dateRange.end = Math.min(2025, maxYear + 10);

    // Update controls
    document.getElementById('start-year').value = this.dateRange.start;
    document.getElementById('end-year').value = this.dateRange.end;

    this.renderTimeline();
  }

  exportTimeline() {
    const filteredEvents = this.getFilteredEvents();

    const csvContent = [
      'Year,Event Type,Person Name,Description,Location,Lineage',
      ...filteredEvents.map(event =>
        `${event.year},"${event.type}","${event.person.name}","${event.description}","${event.location || ''}","${event.lineageName}"`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `family-timeline-${this.dateRange.start}-${this.dateRange.end}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    window.URL.revokeObjectURL(url);
  }

  extractYear(dateString) {
    if (!dateString) return null;
    const match = dateString.match(/\b(19|20)\d{2}\b/);
    return match ? parseInt(match[0]) : null;
  }
}

export default TimelineComponent;
```

### 3. Modern URL Routing Implementation

#### URL Router with Legacy Compatibility
```javascript
// utils/url-router.js
class URLRouter {
  constructor() {
    this.routes = new Map();
    this.currentRoute = null;
    this.history = [];
    this.legacyRedirects = new Map();
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
    // Modern route patterns
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
    this.addRoute('/lineage/:lineageName/:person', this.handleLineagePerson.bind(this));
  }

  setupLegacyRedirects() {
    // Map legacy URLs to modern equivalents
    // This would be populated from the existing genealogy structure

    // Example mappings - these would be generated during build
    this.legacyRedirects.set('/auntruth/new/htm/L1/XF191.htm', '/person/david-hagborg-191');
    this.legacyRedirects.set('/auntruth/new/htm/L1/THF191.htm', '/person/david-hagborg-191/photos');
    this.legacyRedirects.set('/auntruth/new/htm/L1/', '/lineage/hagborg-hansson');

    // Pattern-based redirects for dynamic mapping
    this.addPatternRedirect(/^\/auntruth\/new\/htm\/L(\d+)\/XF(\d+)\.htm$/, (matches) => {
      const lineageId = matches[1];
      const personId = matches[2];
      return this.generatePersonSlugURL(personId, lineageId);
    });

    this.addPatternRedirect(/^\/auntruth\/new\/htm\/L(\d+)\/THF(\d+)\.htm$/, (matches) => {
      const lineageId = matches[1];
      const personId = matches[2];
      return this.generatePersonSlugURL(personId, lineageId) + '/photos';
    });

    this.addPatternRedirect(/^\/auntruth\/new\/htm\/L(\d+)\/$/, (matches) => {
      const lineageId = matches[1];
      return this.generateLineageURL(lineageId);
    });
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
    // Convert route pattern to regex
    // /person/:slug becomes /^\/person\/([^\/]+)$/
    const regexPattern = pattern
      .replace(/:[^\/]+/g, '([^\/]+)')
      .replace(/\//g, '\\/');

    return new RegExp(`^${regexPattern}$`);
  }

  handleInitialRoute() {
    const currentPath = window.location.pathname;

    // Check for legacy URL first
    const modernURL = this.resolveLegacyURL(currentPath);
    if (modernURL && modernURL !== currentPath) {
      this.navigate(modernURL, true); // Replace history entry
      return;
    }

    // Handle modern URL
    this.handleRoute(currentPath);
  }

  resolveLegacyURL(legacyPath) {
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
            return redirect.handler(matches);
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
      // This would use DataManager to get person data and generate slug
      const dataManager = new DataManager();
      const person = await dataManager.getPersonData(personId);

      if (person) {
        const slug = this.generatePersonSlug(person.name, personId);
        return `/person/${slug}`;
      }
    } catch (error) {
      console.error('Error generating person slug URL:', error);
    }

    // Fallback to ID-based URL
    return `/person/${personId}`;
  }

  generatePersonSlug(personName, personId) {
    // Generate URL-friendly slug from person name
    const slug = personName
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single
      .trim();

    // Append ID to ensure uniqueness
    return `${slug}-${personId}`;
  }

  generateLineageURL(lineageId) {
    const lineageNames = {
      '0': 'all',
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

    const lineageName = lineageNames[lineageId] || `lineage-${lineageId}`;
    return `/lineage/${lineageName}`;
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
      const cleanParamName = paramName.substring(1); // Remove ':'
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
    // Handle browser back/forward buttons
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
             !href.includes('.htm') && // Skip legacy .htm files
             !href.includes('#'); // Skip anchors for now
    } catch {
      return false;
    }
  }

  // Route Handlers

  async handleHomePage(params, path) {
    document.title = 'AuntieRuth.com - Family Genealogy';
    this.updateBreadcrumbs([{ name: 'Home', path: '/' }]);

    // Initialize home page components if needed
    await this.loadComponent('enhanced-search');
    await this.loadComponent('recent-activity');
  }

  async handleSearchPage(params, path) {
    const query = new URLSearchParams(window.location.search).get('q') || '';

    document.title = query ? `Search: ${query} - AuntieRuth.com` : 'Search - AuntieRuth.com';
    this.updateBreadcrumbs([
      { name: 'Home', path: '/' },
      { name: 'Search', path: '/search' }
    ]);

    const searchComponent = await this.loadComponent('enhanced-search');
    if (query && searchComponent) {
      searchComponent.performSearch(query);
    }
  }

  async handlePersonPage(params, path) {
    const { slug } = params;
    const personId = this.extractPersonIdFromSlug(slug);

    try {
      const dataManager = new DataManager();
      const person = await dataManager.getPersonData(personId);

      if (person) {
        document.title = `${person.name} - AuntieRuth.com`;
        this.updateBreadcrumbs([
          { name: 'Home', path: '/' },
          { name: person.lineageName, path: `/lineage/${this.slugify(person.lineageName)}` },
          { name: person.name, path: path }
        ]);

        // Load person page components
        await this.loadComponent('relationship-navigator', { personId });
        await this.loadComponent('information-disclosure');

        // Update meta tags
        this.updateMetaTags(person);

      } else {
        this.handleNotFound(path);
      }
    } catch (error) {
      console.error('Error loading person page:', error);
      this.handleNotFound(path);
    }
  }

  async handleFamilyTreePage(params, path) {
    const personParam = new URLSearchParams(window.location.search).get('person');

    document.title = 'Family Tree - AuntieRuth.com';
    this.updateBreadcrumbs([
      { name: 'Home', path: '/' },
      { name: 'Family Tree', path: '/family-tree' }
    ]);

    const treeComponent = await this.loadComponent('family-tree', {
      focusPersonId: personParam
    });
  }

  async handleTimelinePage(params, path) {
    const urlParams = new URLSearchParams(window.location.search);
    const years = urlParams.get('years');
    const lineage = urlParams.get('lineage');

    document.title = 'Family Timeline - AuntieRuth.com';
    this.updateBreadcrumbs([
      { name: 'Home', path: '/' },
      { name: 'Timeline', path: '/timeline' }
    ]);

    const timelineComponent = await this.loadComponent('timeline', {
      dateRange: years ? this.parseYearRange(years) : null,
      selectedLineages: lineage ? [lineage] : []
    });
  }

  // Utility Methods

  extractPersonIdFromSlug(slug) {
    // Extract ID from slug like "david-hagborg-191"
    const match = slug.match(/-(\d+)$/);
    return match ? match[1] : null;
  }

  parseYearRange(yearString) {
    // Parse "1940-1950" format
    const match = yearString.match(/^(\d{4})-(\d{4})$/);
    if (match) {
      return {
        start: parseInt(match[1]),
        end: parseInt(match[2])
      };
    }
    return null;
  }

  slugify(text) {
    return text.toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  }

  async loadComponent(componentName, options = {}) {
    try {
      const module = await import(`../components/${componentName}.js`);
      const ComponentClass = module.default;
      const component = new ComponentClass(options);
      await component.init();
      return component;
    } catch (error) {
      console.error(`Failed to load component ${componentName}:`, error);
      return null;
    }
  }

  updateBreadcrumbs(breadcrumbs) {
    const breadcrumbNav = document.querySelector('.breadcrumb-nav');
    if (breadcrumbNav) {
      const breadcrumbHtml = breadcrumbs.map((crumb, index) => {
        if (index === breadcrumbs.length - 1) {
          return `<span class="current-page">${crumb.name}</span>`;
        } else {
          return `<a href="${crumb.path}">${crumb.name}</a>`;
        }
      }).join(' > ');

      breadcrumbNav.innerHTML = `<nav class="breadcrumbs">${breadcrumbHtml}</nav>`;
    }
  }

  updateMetaTags(person) {
    // Update meta description
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      const birthYear = this.extractYear(person.birthDate) || '';
      const deathYear = this.extractYear(person.deathDate) || '';
      const lifespan = birthYear && deathYear ? `${birthYear}-${deathYear}` :
                      birthYear ? `b. ${birthYear}` :
                      deathYear ? `d. ${deathYear}` : '';

      metaDescription.content = `${person.name} ${lifespan} - ${person.lineageName} family genealogy. ${person.birthLocation ? `Born in ${person.birthLocation}.` : ''} Family history and photos on AuntieRuth.com`;
    }

    // Update Open Graph tags
    this.updateOpenGraphTags(person);
  }

  updateOpenGraphTags(person) {
    const ogTitle = document.querySelector('meta[property="og:title"]');
    const ogDescription = document.querySelector('meta[property="og:description"]');
    const ogUrl = document.querySelector('meta[property="og:url"]');

    if (ogTitle) ogTitle.content = `${person.name} - AuntieRuth.com Family Tree`;
    if (ogDescription) ogDescription.content = `Explore ${person.name}'s family history, genealogy, and photos in the ${person.lineageName} family tree.`;
    if (ogUrl) ogUrl.content = window.location.href;
  }

  handleNotFound(path) {
    document.title = 'Page Not Found - AuntieRuth.com';

    // Show 404 message
    const mainContent = document.querySelector('main') || document.body;
    mainContent.innerHTML = `
      <div class="not-found">
        <h1>Page Not Found</h1>
        <p>The page "${path}" could not be found.</p>
        <p><a href="/">Return to Home</a></p>
      </div>
    `;
  }

  addToHistory(path, params) {
    this.history.unshift({ path, params, timestamp: Date.now() });
    this.history = this.history.slice(0, 50); // Keep last 50 entries
  }

  extractYear(dateString) {
    if (!dateString) return null;
    const match = dateString.match(/\b(19|20)\d{2}\b/);
    return match ? parseInt(match[0]) : null;
  }
}

// Global router instance
const router = new URLRouter();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => router.init());
} else {
  router.init();
}

export default router;
```

## Success Criteria

### Advanced Features Delivered
1. **Relationship Navigator:** Intelligent family context with relationship path finding
2. **Timeline Visualization:** Chronological family events with historical context
3. **Modern URL Routing:** Clean URLs with SEO optimization and legacy compatibility
4. **Complete Integration:** Seamless interaction between all components

### Performance Metrics
1. **Relationship Queries:** Path finding completes within 100ms for typical relationships
2. **Timeline Rendering:** Initial timeline loads within 500ms for typical date ranges
3. **URL Routing:** Client-side routing completes within 50ms
4. **Memory Efficiency:** Optimized data structures prevent memory issues during extended use

### User Experience Validation
1. **Research Efficiency:** Users complete complex genealogy research 75% faster than original site
2. **Feature Discovery:** Regular use of relationship navigator and timeline tools
3. **URL Shareability:** Increased social sharing due to meaningful URLs
4. **Cross-Component Workflow:** Seamless navigation between all features

## Testing Plan

### Advanced Features Integration Testing
1. Test relationship path finding accuracy across complex family structures
2. Verify timeline visualization with various date ranges and event types
3. Test URL routing with legacy URL redirects and modern URL patterns
4. Confirm component interaction workflows (search → tree → timeline → relationships)

### Performance Testing
1. Measure relationship graph loading and query performance
2. Test timeline rendering with large datasets and various view modes
3. Validate URL routing performance and state management
4. Monitor memory usage during extended advanced feature usage

### User Experience Testing
1. Test complete genealogy research workflows using all advanced features
2. Verify accessibility compliance across timeline and relationship components
3. Test mobile experience for advanced features
4. Validate SEO improvements and URL shareability

## Deployment Instructions

### Prerequisites
- Phase 1 foundation architecture completed and deployed
- Phase 2 core features completed and deployed
- Enhanced build pipeline ready for advanced components

### Deployment Steps
1. **Build Advanced Data Structures:**
   ```bash
   npm run build:relationship-graph
   npm run build:timeline-data
   npm run build:url-mappings
   ```

2. **Deploy Advanced Components:**
   ```bash
   git add docs/new/js/components/
   git add docs/new/js/utils/
   git add docs/new/js/data/
   git commit -m "Phase 3: Advanced features implementation"
   git push origin main
   ```

3. **Configure URL Redirects:**
   ```bash
   # If using Apache (not applicable for GitHub Pages)
   # cp .htaccess docs/

   # For GitHub Pages, ensure client-side routing handles legacy URLs
   npm run validate:url-redirects
   ```

4. **Verify Advanced Functionality:**
   - Test relationship navigator on person pages
   - Verify timeline visualization functionality
   - Check URL routing and legacy URL redirects
   - Confirm all components work together seamlessly

## Phase 3 Completion Checklist

- [ ] Relationship navigator with pre-computed graph implemented
- [ ] Timeline component with D3.js visualization working
- [ ] Historical context integration functional
- [ ] Modern URL routing with History API deployed
- [ ] Legacy URL compatibility maintained
- [ ] SEO optimization with meta tags implemented
- [ ] Cross-component integration tested and working
- [ ] Performance metrics met for all advanced features
- [ ] Mobile experience optimized for advanced features
- [ ] Accessibility compliance verified across all components
- [ ] Cross-browser compatibility tested
- [ ] Complete user research workflows validated
- [ ] Documentation updated for advanced features

---

**Phase 3 Completion Note:** This phase completes the comprehensive UX modernization of AuntieRuth.com, transforming it from a static genealogy site into a cutting-edge research platform. The relationship navigator, timeline visualization, and modern URL routing provide advanced capabilities that rival commercial genealogy platforms while maintaining the unique character and complete historical data of the original site.

## Final Implementation Summary

Upon completion of all three phases:

### **Phase 1 Foundation (1-2 weeks):**
- Component architecture with progressive enhancement
- Optimized data structure with lineage-based chunking
- Enhanced navigation fixing critical usability issues
- Mobile-first responsive framework
- Build pipeline for GitHub Pages deployment

### **Phase 2 Core Features (2-4 weeks):**
- Advanced search with pre-built indices and filtering
- Interactive family tree visualization with D3.js
- Progressive information disclosure reducing cognitive load
- Cross-component integration enabling research workflows

### **Phase 3 Advanced Features (1-2 months):**
- Relationship navigator with intelligent path finding
- Timeline visualization with historical context
- Modern URL routing with SEO optimization
- Complete genealogy research platform capabilities

**Total Transformation:** AuntieRuth.com evolves from a static HTML genealogy site into a modern, interactive research platform that preserves its comprehensive historical data while providing cutting-edge user experience comparable to commercial genealogy services.