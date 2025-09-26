import BaseComponent from '../core/base-component.js';
import DataManager from '../core/data-manager.js';

/**
 * Relationship Navigator Component
 * Intelligent family relationship exploration with path finding
 * Builds comprehensive relationship graph and provides BFS-based relationship discovery
 */
class RelationshipNavigatorComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.relationshipGraph = null;
    this.currentPerson = null;
    this.relationshipHistory = [];
    this.sidebarVisible = window.innerWidth > 768;
    this.isBuilding = false;
  }

  async loadDependencies() {
    // Load relationship graph data
    await this.buildRelationshipGraph();
  }

  async buildRelationshipGraph() {
    if (this.isBuilding || this.relationshipGraph) return;

    console.log('Building relationship graph...');
    this.isBuilding = true;

    try {
      this.relationshipGraph = {
        nodes: new Map(),
        edges: new Map(),
        paths: new Map(), // Pre-computed relationship paths
        nameIndex: new Map() // For name-based lookups
      };

      // Load metadata to get total count
      const metadata = await this.dataManager.getMetadata();
      console.log(`Building graph for ${metadata?.totalPeople || 'unknown'} people...`);

      // Load all lineage data to build complete graph
      for (let lineageId = 0; lineageId <= 9; lineageId++) {
        const lineageData = await this.dataManager.getLineageData(lineageId.toString());
        if (!lineageData) continue;

        console.log(`Processing lineage ${lineageId}: ${lineageData.people.length} people`);

        lineageData.people.forEach(person => {
          this.addPersonToGraph(person);
        });
      }

      // Build reverse relationships and pre-compute common paths
      await this.finalizeGraph();

      console.log(`Relationship graph built: ${this.relationshipGraph.nodes.size} people`);
    } catch (error) {
      console.error('Error building relationship graph:', error);
      throw error;
    } finally {
      this.isBuilding = false;
    }
  }

  addPersonToGraph(person) {
    // Add person node
    const node = {
      person: person,
      relationships: {
        parents: [],
        children: [],
        spouses: [],
        siblings: []
      }
    };

    this.relationshipGraph.nodes.set(person.id, node);

    // Add to name index for lookup
    if (person.name) {
      const normalizedName = person.name.toLowerCase().trim();
      if (!this.relationshipGraph.nameIndex.has(normalizedName)) {
        this.relationshipGraph.nameIndex.set(normalizedName, []);
      }
      this.relationshipGraph.nameIndex.get(normalizedName).push(person.id);
    }

    // Parse and store relationships (will be processed in finalizeGraph)
    const relationships = this.parseRelationships(person);
    node.pendingRelationships = relationships;
  }

  parseRelationships(person) {
    const relationships = {
      parents: [],
      spouses: [],
      children: person.children || []
    };

    // Parse father/mother format: "Name [Lineage]"
    [person.father, person.mother].forEach(parent => {
      if (parent && parent.trim()) {
        const personRef = this.parseRelationshipString(parent);
        if (personRef) relationships.parents.push(personRef);
      }
    });

    // Parse spouse relationships
    [person.spouse, person.spouse2, person.spouse3, person.spouse4].forEach(spouse => {
      if (spouse && spouse.trim()) {
        const personRef = this.parseRelationshipString(spouse);
        if (personRef) relationships.spouses.push(personRef);
      }
    });

    return relationships;
  }

  parseRelationshipString(relationshipString) {
    // Parse "Walter Arnold Hagborg [Hagborg-Hansson]" format
    const match = relationshipString.match(/^(.+?)\s*\[(.+?)\]$/);
    if (!match) {
      // Handle cases without lineage brackets
      return { name: relationshipString.trim(), lineage: null };
    }

    const [, name, lineageName] = match;
    return {
      name: name.trim(),
      lineage: lineageName.trim()
    };
  }

  async finalizeGraph() {
    console.log('Finalizing relationship graph...');

    // Resolve all pending relationships
    for (const [personId, node] of this.relationshipGraph.nodes) {
      if (!node.pendingRelationships) continue;

      const relationships = node.pendingRelationships;

      // Resolve parent relationships
      relationships.parents.forEach(parentRef => {
        const parentId = this.findPersonByNameAndLineage(parentRef.name, parentRef.lineage);
        if (parentId) {
          node.relationships.parents.push(parentId);
          this.addReverseRelationship(parentId, personId, 'children');
        }
      });

      // Resolve spouse relationships
      relationships.spouses.forEach(spouseRef => {
        const spouseId = this.findPersonByNameAndLineage(spouseRef.name, spouseRef.lineage);
        if (spouseId) {
          node.relationships.spouses.push(spouseId);
          this.addReverseRelationship(spouseId, personId, 'spouses');
        }
      });

      // Add children relationships
      relationships.children.forEach(childId => {
        if (this.relationshipGraph.nodes.has(childId)) {
          node.relationships.children.push(childId);
          this.addReverseRelationship(childId, personId, 'parents');
        }
      });

      // Clean up
      delete node.pendingRelationships;
    }

    // Build sibling relationships
    this.buildSiblingRelationships();

    // Pre-compute relationship paths for performance
    await this.precomputeRelationshipPaths();

    console.log('Graph finalization complete');
  }

  findPersonByNameAndLineage(name, lineageName) {
    // Try exact match first
    const normalizedName = name.toLowerCase().trim();
    const candidates = this.relationshipGraph.nameIndex.get(normalizedName) || [];

    if (candidates.length === 0) return null;

    // If only one match, return it
    if (candidates.length === 1) return candidates[0];

    // Multiple matches - try to filter by lineage
    if (lineageName) {
      for (const candidateId of candidates) {
        const node = this.relationshipGraph.nodes.get(candidateId);
        if (node?.person?.lineageName === lineageName) {
          return candidateId;
        }
      }
    }

    // Return first match as fallback
    return candidates[0];
  }

  addReverseRelationship(targetId, sourceId, relationshipType) {
    const targetNode = this.relationshipGraph.nodes.get(targetId);
    if (targetNode && !targetNode.relationships[relationshipType].includes(sourceId)) {
      targetNode.relationships[relationshipType].push(sourceId);
    }
  }

  buildSiblingRelationships() {
    // Build sibling relationships based on shared parents
    for (const [personId, node] of this.relationshipGraph.nodes) {
      const parents = node.relationships.parents;

      if (parents.length > 0) {
        // Find all people who share any parent
        const siblings = new Set();

        parents.forEach(parentId => {
          const parentNode = this.relationshipGraph.nodes.get(parentId);
          if (parentNode) {
            parentNode.relationships.children.forEach(siblingId => {
              if (siblingId !== personId) {
                siblings.add(siblingId);
              }
            });
          }
        });

        node.relationships.siblings = Array.from(siblings);
      }
    }
  }

  async precomputeRelationshipPaths() {
    console.log('Pre-computing relationship paths...');

    // Pre-compute paths for a subset of people (performance consideration)
    const personIds = Array.from(this.relationshipGraph.nodes.keys());
    const maxPrecompute = Math.min(personIds.length, 500); // Limit for performance

    for (let i = 0; i < maxPrecompute; i++) {
      const sourceId = personIds[i];
      const paths = this.findRelationshipPaths(sourceId, 4); // Max 4 degrees
      this.relationshipGraph.paths.set(sourceId, paths);

      if (i % 100 === 0) {
        console.log(`Pre-computed paths for ${i}/${maxPrecompute} people`);
      }
    }

    console.log('Path pre-computation complete');
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
          relationship: this.describeRelationship(path),
          reversePath: this.reverseRelationshipPath(path)
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

    // Single step relationships
    if (path.length === 1) {
      const step = path[0];
      switch (step.type) {
        case 'parents': return 'parent';
        case 'children': return 'child';
        case 'spouses': return 'spouse';
        case 'siblings': return 'sibling';
        default: return 'connected';
      }
    }

    // Two-step relationships
    if (path.length === 2) {
      const [step1, step2] = path;

      // Grandparent/grandchild relationships
      if (step1.type === 'parents' && step2.type === 'parents') return 'grandparent';
      if (step1.type === 'children' && step2.type === 'children') return 'grandchild';

      // Aunt/uncle and niece/nephew relationships
      if (step1.type === 'parents' && step2.type === 'siblings') return 'aunt/uncle';
      if (step1.type === 'siblings' && step2.type === 'children') return 'niece/nephew';

      // Sibling through different parent paths
      if (step1.type === 'parents' && step2.type === 'children') return 'sibling';
      if (step1.type === 'children' && step2.type === 'parents') return 'sibling';

      // In-law relationships
      if (step1.type === 'spouses' && step2.type === 'parents') return 'parent-in-law';
      if (step1.type === 'parents' && step2.type === 'spouses') return 'child-in-law';
      if (step1.type === 'spouses' && step2.type === 'siblings') return 'sibling-in-law';
      if (step1.type === 'siblings' && step2.type === 'spouses') return 'sibling-in-law';

      // Step relationships
      if (step1.type === 'spouses' && step2.type === 'children') return 'step-child';
      if (step1.type === 'children' && step2.type === 'spouses') return 'step-parent';
    }

    // Three-step relationships
    if (path.length === 3) {
      const [step1, step2, step3] = path;

      // Great-grandparent/great-grandchild
      if (step1.type === 'parents' && step2.type === 'parents' && step3.type === 'parents') {
        return 'great-grandparent';
      }
      if (step1.type === 'children' && step2.type === 'children' && step3.type === 'children') {
        return 'great-grandchild';
      }

      // Great-aunt/uncle relationships
      if (step1.type === 'parents' && step2.type === 'parents' && step3.type === 'siblings') {
        return 'great-aunt/uncle';
      }
      if (step1.type === 'siblings' && step2.type === 'children' && step3.type === 'children') {
        return 'grand-niece/nephew';
      }

      // First cousin relationships
      if (step1.type === 'parents' && step2.type === 'siblings' && step3.type === 'children') {
        return 'first cousin';
      }
      if (step1.type === 'children' && step2.type === 'siblings' && step3.type === 'parents') {
        return 'first cousin';
      }

      // Parent's cousin relationships
      if (step1.type === 'parents' && step2.type === 'parents' && step3.type === 'siblings') {
        return 'parent\'s cousin';
      }
    }

    // Four-step relationships
    if (path.length === 4) {
      const [step1, step2, step3, step4] = path;

      // Great-great relationships
      if (step1.type === 'parents' && step2.type === 'parents' &&
          step3.type === 'parents' && step4.type === 'parents') {
        return 'great-great-grandparent';
      }

      // Second cousin
      if (step1.type === 'parents' && step2.type === 'parents' &&
          step3.type === 'siblings' && step4.type === 'children') {
        return 'second cousin';
      }

      // First cousin once removed
      if (step1.type === 'parents' && step2.type === 'siblings' &&
          step3.type === 'children' && step4.type === 'children') {
        return 'first cousin once removed';
      }
    }

    // Five-step relationships
    if (path.length === 5) {
      // Third cousin patterns
      if (this.isCousinPattern(path, 3)) {
        return 'third cousin';
      }

      // First cousin twice removed
      if (this.isCousinRemovedPattern(path, 1, 2)) {
        return 'first cousin twice removed';
      }
    }

    // Six-step relationships
    if (path.length === 6) {
      // Fourth cousin
      if (this.isCousinPattern(path, 4)) {
        return 'fourth cousin';
      }
    }

    // Default for complex or unrecognized relationships
    return `${path.length} degrees of separation`;
  }

  // Helper method to identify cousin patterns
  isCousinPattern(path, cousinLevel) {
    if (path.length !== (cousinLevel + 2)) return false;

    // Pattern: up N generations, across siblings, down N generations
    let upCount = 0;
    let acrossFound = false;
    let downCount = 0;

    for (const step of path) {
      if (!acrossFound && step.type === 'parents') {
        upCount++;
      } else if (step.type === 'siblings') {
        acrossFound = true;
      } else if (acrossFound && step.type === 'children') {
        downCount++;
      }
    }

    return upCount === cousinLevel && downCount === cousinLevel && acrossFound;
  }

  // Helper method to identify cousin once/twice removed patterns
  isCousinRemovedPattern(path, cousinLevel, removedCount) {
    // More complex pattern matching for removed cousin relationships
    // This is a simplified implementation
    return false;
  }

  reverseRelationshipPath(path) {
    // Create reverse description
    const reversed = [...path].reverse();
    const reverseMap = {
      'parents': 'children',
      'children': 'parents',
      'spouses': 'spouses',
      'siblings': 'siblings'
    };

    return reversed.map(step => ({
      from: step.to,
      to: step.from,
      type: reverseMap[step.type]
    }));
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

  generateCurrentPersonCard() {
    if (!this.currentPerson) {
      return `
        <div class="current-person-card empty">
          <p>No person selected</p>
          <p class="hint">Select someone from search or family tree to explore relationships</p>
        </div>
      `;
    }

    const person = this.currentPerson;
    return `
      <div class="current-person-card">
        <div class="person-name">${person.name || 'Unknown'}</div>
        <div class="person-details">
          ${person.birthDate ? `<span>Born: ${person.birthDate}</span>` : ''}
          ${person.lineageName ? `<span>Lineage: ${person.lineageName}</span>` : ''}
        </div>
        <button class="view-person-details" data-person-id="${person.id}">
          View Full Details
        </button>
      </div>
    `;
  }

  generateImmediateFamilySection() {
    if (!this.currentPerson || !this.relationshipGraph) {
      return '<div class="family-section empty">Loading family data...</div>';
    }

    const node = this.relationshipGraph.nodes.get(this.currentPerson.id);
    if (!node) return '<div class="family-section empty">No family data available</div>';

    return `
      <div class="family-section">
        <h4>Immediate Family</h4>

        ${this.generateFamilyGroup('Parents', node.relationships.parents)}
        ${this.generateFamilyGroup('Spouses', node.relationships.spouses)}
        ${this.generateFamilyGroup('Children', node.relationships.children)}
        ${this.generateFamilyGroup('Siblings', node.relationships.siblings)}
      </div>
    `;
  }

  generateFamilyGroup(title, personIds) {
    if (!personIds || personIds.length === 0) return '';

    const people = personIds
      .map(id => this.relationshipGraph.nodes.get(id)?.person)
      .filter(person => person);

    if (people.length === 0) return '';

    return `
      <div class="family-group">
        <h5>${title}</h5>
        <ul class="family-list">
          ${people.map(person => `
            <li class="family-member" data-person-id="${person.id}">
              <span class="member-name">${person.name || 'Unknown'}</span>
              ${person.birthDate ? `<span class="member-year">(${this.extractYear(person.birthDate)})</span>` : ''}
            </li>
          `).join('')}
        </ul>
      </div>
    `;
  }

  generateRelationshipTools() {
    return `
      <div class="relationship-tools">
        <h4>Explore Relationships</h4>
        <button class="tool-btn find-connection" disabled>
          Find Connection to...
        </button>
        <button class="tool-btn show-ancestors" disabled>
          Show All Ancestors
        </button>
        <button class="tool-btn show-descendants" disabled>
          Show All Descendants
        </button>
      </div>
    `;
  }

  generateRecentExploration() {
    if (this.relationshipHistory.length === 0) {
      return `
        <div class="recent-exploration">
          <h4>Recent Exploration</h4>
          <p class="empty">No recent relationship searches</p>
        </div>
      `;
    }

    return `
      <div class="recent-exploration">
        <h4>Recent Exploration</h4>
        <ul class="exploration-list">
          ${this.relationshipHistory.slice(0, 5).map(item => `
            <li class="exploration-item">
              <span class="relationship">${item.relationship}</span>
              <span class="people">${item.person1} → ${item.person2}</span>
            </li>
          `).join('')}
        </ul>
      </div>
    `;
  }

  attachEventListeners() {
    if (!this.element) return;

    // Sidebar toggle
    const toggleBtn = this.element.querySelector('.sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        this.toggleSidebar();
      });
    }

    // Relationship finder button
    const finderBtn = this.element.querySelector('.relationship-finder-btn');
    if (finderBtn) {
      finderBtn.addEventListener('click', () => {
        this.showRelationshipFinder();
      });
    }

    // Family member clicks
    const familyMembers = this.element.querySelectorAll('.family-member');
    familyMembers.forEach(member => {
      member.addEventListener('click', () => {
        const personId = member.dataset.personId;
        this.selectPerson(personId);
      });
    });

    // Listen for person selections from other components
    document.addEventListener('person-selected', (event) => {
      if (event.detail && event.detail.personId) {
        this.selectPerson(event.detail.personId);
      }
    });
  }

  toggleSidebar() {
    this.sidebarVisible = !this.sidebarVisible;
    this.element.classList.toggle('visible', this.sidebarVisible);
    this.element.classList.toggle('hidden', !this.sidebarVisible);

    const toggleBtn = this.element.querySelector('.sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-expanded', this.sidebarVisible.toString());
      const icon = toggleBtn.querySelector('.toggle-icon');
      if (icon) {
        icon.textContent = this.sidebarVisible ? '◀' : '▶';
      }
    }
  }

  async selectPerson(personId) {
    if (!this.relationshipGraph) {
      console.warn('Relationship graph not ready');
      return;
    }

    const node = this.relationshipGraph.nodes.get(personId);
    if (!node) {
      console.warn('Person not found in relationship graph:', personId);
      return;
    }

    this.currentPerson = node.person;
    await this.updateFamilyContext();

    // Dispatch event for other components
    document.dispatchEvent(new CustomEvent('relationship-navigator-person-selected', {
      detail: { personId, person: this.currentPerson }
    }));
  }

  async updateFamilyContext() {
    if (!this.element || !this.currentPerson) return;

    // Update current person card
    const personCard = this.element.querySelector('.current-person-section');
    if (personCard) {
      personCard.innerHTML = this.generateCurrentPersonCard();
    }

    // Update immediate family
    const familySection = this.element.querySelector('.immediate-family-section');
    if (familySection) {
      familySection.innerHTML = this.generateImmediateFamilySection();
    }

    // Re-attach event listeners for new elements
    this.attachFamilyMemberListeners();

    // Enable tools
    this.enableRelationshipTools();
  }

  attachFamilyMemberListeners() {
    const familyMembers = this.element.querySelectorAll('.family-member');
    familyMembers.forEach(member => {
      member.addEventListener('click', () => {
        const personId = member.dataset.personId;
        this.selectPerson(personId);
      });
    });
  }

  enableRelationshipTools() {
    const toolBtns = this.element.querySelectorAll('.tool-btn');
    toolBtns.forEach(btn => {
      btn.disabled = false;
    });
  }

  showRelationshipFinder() {
    // Create and show modal for finding relationships between two people
    const modal = document.createElement('div');
    modal.className = 'relationship-finder-modal';
    modal.innerHTML = `
      <div class="modal-backdrop">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Find Relationship</h3>
            <button class="modal-close">&times;</button>
          </div>
          <div class="modal-body">
            <div class="person-selector">
              <label>First Person:</label>
              <input type="text" class="person-search" id="person1-search" placeholder="Search by name...">
              <div class="search-results" id="person1-results"></div>
            </div>
            <div class="person-selector">
              <label>Second Person:</label>
              <input type="text" class="person-search" id="person2-search" placeholder="Search by name...">
              <div class="search-results" id="person2-results"></div>
            </div>
            <div class="relationship-result" hidden>
              <h4>Relationship:</h4>
              <div class="relationship-details"></div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary modal-cancel">Cancel</button>
            <button class="btn-primary find-relationship" disabled>Find Relationship</button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    this.setupRelationshipFinderModal(modal);
  }

  setupRelationshipFinderModal(modal) {
    // Setup event listeners for the modal
    const closeBtn = modal.querySelector('.modal-close');
    const cancelBtn = modal.querySelector('.modal-cancel');
    const findBtn = modal.querySelector('.find-relationship');

    [closeBtn, cancelBtn].forEach(btn => {
      btn.addEventListener('click', () => {
        document.body.removeChild(modal);
      });
    });

    // Setup person search functionality
    // (Implementation would involve search autocomplete and relationship finding)
    // This is a placeholder for the complete implementation
  }

  extractYear(dateString) {
    if (!dateString) return '';
    const match = dateString.match(/\b(1[89]\d{2}|20[0-2]\d)\b/);
    return match ? match[0] : '';
  }

  // Public API methods
  async findRelationship(personId1, personId2) {
    if (!this.relationshipGraph) return null;

    // Check if we have pre-computed path
    const precomputedPaths = this.relationshipGraph.paths.get(personId1);
    if (precomputedPaths && precomputedPaths.has(personId2)) {
      return precomputedPaths.get(personId2);
    }

    // Compute path on demand
    const paths = this.findRelationshipPaths(personId1, 6);
    return paths.get(personId2) || null;
  }

  getPersonNode(personId) {
    return this.relationshipGraph?.nodes.get(personId);
  }

  isGraphReady() {
    return this.relationshipGraph !== null && !this.isBuilding;
  }
}

export default RelationshipNavigatorComponent;