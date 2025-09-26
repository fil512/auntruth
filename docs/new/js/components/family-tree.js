import BaseComponent from '../core/base-component.js';
import DataManager from '../core/data-manager.js';

/**
 * Family Tree Component
 * Interactive family tree visualization using D3.js
 * Handles complex genealogy relationships with touch support
 */
class FamilyTreeComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.focusPersonId = options.focusPersonId;
    this.generations = options.generations || 3;
    this.container = options.container || '#family-tree';

    // D3.js components
    this.svg = null;
    this.g = null;
    this.tree = null;
    this.zoom = null;

    // Tree data
    this.treeData = null;
    this.allPeople = new Map();

    // Dimensions
    this.width = 0;
    this.height = 0;
    this.nodeWidth = 150;
    this.nodeHeight = 80;

    // Colors
    this.colors = {
      male: '#4A90E2',
      female: '#E24A90',
      unknown: '#9B9B9B',
      deceased: '#666666'
    };
  }

  async loadDependencies() {
    // Load D3.js if not already available
    if (!window.d3) {
      await this.loadD3Js();
    }
  }

  async render() {
    try {
      // Get or create container
      let containerElement = typeof this.container === 'string'
        ? this.$(this.container)
        : this.container;

      if (!containerElement) {
        // Create family tree container
        containerElement = this.createTreeContainer();
      }

      this.element = containerElement;

      // Set up dimensions
      this.updateDimensions();

      // Create SVG
      this.createSVG();

      // Load and render tree data
      if (this.focusPersonId) {
        await this.loadFamilyData(this.focusPersonId);
        this.renderTree();
      }

    } catch (error) {
      console.error('Failed to render family tree:', error);
      this.showError('Failed to load family tree');
    }
  }

  attachEventListeners() {
    // Handle window resize
    window.addEventListener('resize', this.handleResize.bind(this));

    // Handle person selection from other components
    document.addEventListener('person-selected', (event) => {
      if (event.detail && event.detail.personId) {
        this.focusOnPerson(event.detail.personId);
      }
    });
  }

  createTreeContainer() {
    const containerHTML = `
      <div id="family-tree" class="family-tree-container">
        <div class="tree-header">
          <div class="tree-controls">
            <button class="btn-secondary tree-control" data-action="zoom-in" title="Zoom In">+</button>
            <button class="btn-secondary tree-control" data-action="zoom-out" title="Zoom Out">-</button>
            <button class="btn-secondary tree-control" data-action="center" title="Center View">⌂</button>
            <button class="btn-secondary tree-control" data-action="expand" title="Expand All">⊞</button>
          </div>
          <div class="tree-info">
            <span class="generations-display">Showing ${this.generations} generations</span>
          </div>
        </div>
        <div class="tree-loading" hidden>
          <div class="loading-spinner"></div>
          <p>Loading family tree...</p>
        </div>
        <div class="tree-error" hidden>
          <p>Unable to load family tree</p>
        </div>
        <div class="tree-canvas">
          <!-- SVG will be inserted here -->
        </div>
      </div>
    `;

    // Insert into page
    const mainContent = this.$('.main-content, main, body');
    if (mainContent) {
      mainContent.insertAdjacentHTML('beforeend', containerHTML);
      return this.$('#family-tree');
    }

    return null;
  }

  updateDimensions() {
    if (!this.element) return;

    const rect = this.element.getBoundingClientRect();
    this.width = rect.width || 800;
    this.height = Math.max(rect.height, 600);
  }

  createSVG() {
    const canvas = this.$('.tree-canvas');
    if (!canvas) return;

    // Remove existing SVG
    const existingSvg = canvas.querySelector('svg');
    if (existingSvg) {
      existingSvg.remove();
    }

    // Create new SVG
    this.svg = d3.select(canvas)
      .append('svg')
      .attr('width', this.width)
      .attr('height', this.height);

    // Create main group for pan/zoom
    this.g = this.svg.append('g');

    // Setup zoom behavior
    this.zoom = d3.zoom()
      .scaleExtent([0.1, 3])
      .on('zoom', (event) => {
        this.g.attr('transform', event.transform);
      });

    this.svg.call(this.zoom);

    // Setup tree layout
    this.tree = d3.tree()
      .size([this.height - 100, this.width - 200])
      .separation((a, b) => a.parent === b.parent ? 1 : 1.2);

    this.setupControlHandlers();
  }

  setupControlHandlers() {
    const controls = this.$$('.tree-control');
    controls.forEach(control => {
      control.addEventListener('click', (event) => {
        const action = event.target.dataset.action;
        this.handleControlAction(action);
      });
    });
  }

  handleControlAction(action) {
    if (!this.svg || !this.zoom) return;

    const transition = this.svg.transition().duration(350);

    switch (action) {
      case 'zoom-in':
        this.svg.call(this.zoom.scaleBy, 1.5);
        break;
      case 'zoom-out':
        this.svg.call(this.zoom.scaleBy, 1 / 1.5);
        break;
      case 'center':
        this.centerView();
        break;
      case 'expand':
        this.expandAll();
        break;
    }
  }

  async loadFamilyData(personId) {
    this.showLoading();

    try {
      // Get focus person data
      const focusPerson = await this.dataManager.getPersonData(personId);
      if (!focusPerson) {
        throw new Error(`Person ${personId} not found`);
      }

      // Build family hierarchy
      this.treeData = await this.buildFamilyHierarchy(focusPerson);

    } catch (error) {
      console.error('Failed to load family data:', error);
      throw error;
    } finally {
      this.hideLoading();
    }
  }

  async buildFamilyHierarchy(focusPerson) {
    // Start with focus person as root
    const root = {
      id: focusPerson.id,
      name: focusPerson.name || 'Unknown',
      person: focusPerson,
      children: [],
      parents: [],
      spouses: [],
      generation: 0
    };

    this.allPeople.set(focusPerson.id, root);

    // Build upward (ancestors) and downward (descendants)
    await this.buildAncestors(root, 1);
    await this.buildDescendants(root, 1);

    return root;
  }

  async buildAncestors(node, generation) {
    if (generation > this.generations || !node.person) return;

    const person = node.person;
    const parents = [];

    // Add father
    if (person.father) {
      const fatherData = await this.dataManager.getPersonData(person.father);
      if (fatherData) {
        const father = {
          id: fatherData.id,
          name: fatherData.name || 'Unknown',
          person: fatherData,
          children: [node],
          parents: [],
          spouses: [],
          generation: generation
        };
        parents.push(father);
        this.allPeople.set(fatherData.id, father);
      }
    }

    // Add mother
    if (person.mother) {
      const motherData = await this.dataManager.getPersonData(person.mother);
      if (motherData) {
        const mother = {
          id: motherData.id,
          name: motherData.name || 'Unknown',
          person: motherData,
          children: [node],
          parents: [],
          spouses: [],
          generation: generation
        };
        parents.push(mother);
        this.allPeople.set(motherData.id, mother);
      }
    }

    node.parents = parents;

    // Continue building ancestors
    for (const parent of parents) {
      await this.buildAncestors(parent, generation + 1);
    }
  }

  async buildDescendants(node, generation) {
    if (generation > this.generations || !node.person) return;

    const person = node.person;
    const children = [];

    // Get children
    if (person.children && Array.isArray(person.children)) {
      for (const childId of person.children) {
        const childData = await this.dataManager.getPersonData(childId);
        if (childData) {
          const child = {
            id: childData.id,
            name: childData.name || 'Unknown',
            person: childData,
            children: [],
            parents: [node],
            spouses: [],
            generation: -generation
          };
          children.push(child);
          this.allPeople.set(childData.id, child);
        }
      }
    }

    node.children = children;

    // Continue building descendants
    for (const child of children) {
      await this.buildDescendants(child, generation + 1);
    }
  }

  renderTree() {
    if (!this.treeData || !this.g) return;

    // Create D3 hierarchy
    const root = d3.hierarchy(this.treeData, d => {
      // Combine parents and children for tree structure
      const descendants = [...(d.children || [])];
      const ancestors = [...(d.parents || [])];

      // For visualization, we'll show ancestors above and descendants below
      return generation > 0 ? ancestors : descendants;
    });

    // Generate tree layout
    const treeLayout = this.tree(root);

    // Clear previous content
    this.g.selectAll('*').remove();

    // Add links
    this.renderLinks(treeLayout);

    // Add nodes
    this.renderNodes(treeLayout);

    // Center the view
    this.centerView();
  }

  renderLinks(root) {
    const links = root.links();

    const link = this.g.selectAll('.tree-link')
      .data(links)
      .enter().append('path')
      .attr('class', 'tree-link')
      .attr('d', d3.linkHorizontal()
        .x(d => d.y)
        .y(d => d.x)
      );
  }

  renderNodes(root) {
    const nodes = root.descendants();

    const node = this.g.selectAll('.tree-node')
      .data(nodes)
      .enter().append('g')
      .attr('class', d => `tree-node ${d.data.id === this.focusPersonId ? 'focus-node' : ''}`)
      .attr('transform', d => `translate(${d.y},${d.x})`)
      .on('click', (event, d) => this.handleNodeClick(event, d))
      .on('contextmenu', (event, d) => this.handleNodeRightClick(event, d));

    // Add node rectangles
    node.append('rect')
      .attr('class', 'node-rect')
      .attr('x', -this.nodeWidth / 2)
      .attr('y', -this.nodeHeight / 2)
      .attr('width', this.nodeWidth)
      .attr('height', this.nodeHeight)
      .attr('rx', 5)
      .style('fill', d => this.getNodeColor(d.data.person))
      .style('stroke', d => d.data.id === this.focusPersonId ? '#FFD700' : '#ccc')
      .style('stroke-width', d => d.data.id === this.focusPersonId ? 3 : 1);

    // Add person names
    node.append('text')
      .attr('class', 'node-name')
      .attr('dy', -5)
      .attr('text-anchor', 'middle')
      .style('font-weight', 'bold')
      .style('font-size', '12px')
      .style('fill', 'white')
      .text(d => this.truncateName(d.data.name, 20));

    // Add birth/death dates
    node.append('text')
      .attr('class', 'node-dates')
      .attr('dy', 10)
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .style('fill', 'white')
      .text(d => this.formatDates(d.data.person));

    // Add spouse information
    node.append('text')
      .attr('class', 'node-spouse')
      .attr('dy', 25)
      .attr('text-anchor', 'middle')
      .style('font-size', '9px')
      .style('fill', 'rgba(255,255,255,0.8)')
      .text(d => d.data.person.spouse ? `m. ${this.truncateName(d.data.person.spouse, 15)}` : '');

    // Add hover effects
    if (!this.mobile) {
      node.on('mouseenter', (event, d) => this.showNodeTooltip(event, d))
           .on('mouseleave', () => this.hideNodeTooltip());
    }
  }

  getNodeColor(person) {
    if (!person) return this.colors.unknown;

    // Check if deceased
    if (person.deathDate || person.died) {
      return this.colors.deceased;
    }

    // Gender-based coloring
    if (person.gender) {
      const gender = person.gender.toLowerCase();
      if (gender === 'male' || gender === 'm') return this.colors.male;
      if (gender === 'female' || gender === 'f') return this.colors.female;
    }

    // Try to guess from name patterns (fallback)
    const name = (person.name || '').toLowerCase();
    if (name.includes('mrs.') || name.includes('miss ') ||
        name.endsWith(' née ') || name.includes('(née')) {
      return this.colors.female;
    }

    return this.colors.unknown;
  }

  truncateName(name, maxLength) {
    if (!name || name.length <= maxLength) return name;
    return name.substring(0, maxLength - 3) + '...';
  }

  formatDates(person) {
    if (!person) return '';

    const birth = this.formatYear(person.birthDate);
    const death = this.formatYear(person.deathDate);

    if (birth && death) return `${birth} - ${death}`;
    if (birth) return `b. ${birth}`;
    if (death) return `d. ${death}`;

    return '';
  }

  formatYear(dateStr) {
    if (!dateStr) return '';

    // Try to extract 4-digit year
    const match = dateStr.match(/\b(1[789]\d{2}|20[0-2]\d)\b/);
    return match ? match[0] : '';
  }

  handleNodeClick(event, node) {
    if (event.defaultPrevented) return;

    // Focus on clicked person
    this.focusOnPerson(node.data.id);

    // Dispatch event for other components
    document.dispatchEvent(new CustomEvent('tree-person-selected', {
      detail: { personId: node.data.id, person: node.data.person }
    }));
  }

  handleNodeRightClick(event, node) {
    event.preventDefault();

    // Show context menu
    this.showContextMenu(event, node);
  }

  showContextMenu(event, node) {
    // Create context menu
    const menu = document.createElement('div');
    menu.className = 'tree-context-menu';
    menu.innerHTML = `
      <button data-action="view-details">View Details</button>
      <button data-action="center-on">Center Tree Here</button>
      <button data-action="expand-family">Show More Family</button>
    `;

    // Position menu
    menu.style.position = 'absolute';
    menu.style.left = event.pageX + 'px';
    menu.style.top = event.pageY + 'px';
    menu.style.zIndex = '1000';

    document.body.appendChild(menu);

    // Handle menu actions
    menu.addEventListener('click', (e) => {
      const action = e.target.dataset.action;
      if (action) {
        this.handleContextAction(action, node);
      }
      document.body.removeChild(menu);
    });

    // Close on outside click
    setTimeout(() => {
      document.addEventListener('click', () => {
        if (menu.parentNode) {
          document.body.removeChild(menu);
        }
      }, { once: true });
    }, 0);
  }

  handleContextAction(action, node) {
    switch (action) {
      case 'view-details':
        const url = `/auntruth/new/htm/L${node.data.person.lineage || '0'}/${node.data.person.filename || node.data.id}.htm`;
        window.open(url, '_blank');
        break;
      case 'center-on':
        this.focusOnPerson(node.data.id);
        break;
      case 'expand-family':
        this.generations = Math.min(this.generations + 1, 5);
        this.loadFamilyData(node.data.id).then(() => this.renderTree());
        break;
    }
  }

  async focusOnPerson(personId) {
    if (this.focusPersonId === personId) return;

    this.focusPersonId = personId;
    await this.loadFamilyData(personId);
    this.renderTree();

    // Update URL if possible (for bookmarking)
    if (window.history && window.history.pushState) {
      const url = new URL(window.location);
      url.searchParams.set('focus', personId);
      window.history.pushState({}, '', url);
    }
  }

  centerView() {
    if (!this.svg || !this.treeData) return;

    const bounds = this.g.node().getBBox();
    const centerX = this.width / 2;
    const centerY = this.height / 2;

    const scale = 0.8 / Math.max(
      bounds.width / this.width,
      bounds.height / this.height
    );

    const translateX = centerX - bounds.x - bounds.width / 2;
    const translateY = centerY - bounds.y - bounds.height / 2;

    this.svg.transition()
      .duration(750)
      .call(this.zoom.transform,
        d3.zoomIdentity
          .translate(translateX, translateY)
          .scale(Math.min(scale, 1))
      );
  }

  expandAll() {
    // Expand to show more generations
    this.generations = Math.min(this.generations + 1, 5);
    if (this.focusPersonId) {
      this.loadFamilyData(this.focusPersonId).then(() => this.renderTree());
    }
  }

  showNodeTooltip(event, node) {
    const person = node.data.person;
    if (!person) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'tree-tooltip';
    tooltip.innerHTML = `
      <div class="tooltip-name">${person.name || 'Unknown'}</div>
      ${person.birthDate ? `<div>Born: ${person.birthDate}</div>` : ''}
      ${person.birthLocation ? `<div>In: ${person.birthLocation}</div>` : ''}
      ${person.deathDate ? `<div>Died: ${person.deathDate}</div>` : ''}
      ${person.spouse ? `<div>Spouse: ${person.spouse}</div>` : ''}
      ${person.occupation ? `<div>Occupation: ${person.occupation}</div>` : ''}
    `;

    tooltip.style.position = 'absolute';
    tooltip.style.left = (event.pageX + 10) + 'px';
    tooltip.style.top = (event.pageY - 10) + 'px';
    tooltip.style.zIndex = '1000';

    document.body.appendChild(tooltip);
    this.currentTooltip = tooltip;
  }

  hideNodeTooltip() {
    if (this.currentTooltip) {
      document.body.removeChild(this.currentTooltip);
      this.currentTooltip = null;
    }
  }

  handleResize() {
    this.updateDimensions();
    if (this.svg) {
      this.svg.attr('width', this.width).attr('height', this.height);
      this.tree.size([this.height - 100, this.width - 200]);
      this.renderTree();
    }
  }

  showLoading() {
    const loading = this.$('.tree-loading');
    if (loading) loading.hidden = false;
  }

  hideLoading() {
    const loading = this.$('.tree-loading');
    if (loading) loading.hidden = true;
  }

  showError(message) {
    const error = this.$('.tree-error');
    if (error) {
      error.querySelector('p').textContent = message;
      error.hidden = false;
    }
  }

  async loadD3Js() {
    return new Promise((resolve, reject) => {
      if (window.d3) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://unpkg.com/d3@7/dist/d3.min.js';
      script.onload = resolve;
      script.onerror = () => {
        console.error('Failed to load D3.js');
        reject(new Error('Failed to load D3.js'));
      };

      document.head.appendChild(script);
    });
  }

  destroy() {
    // Clean up event listeners
    window.removeEventListener('resize', this.handleResize);

    // Remove tooltip
    this.hideNodeTooltip();

    // Remove context menus
    const menus = document.querySelectorAll('.tree-context-menu');
    menus.forEach(menu => menu.remove());

    super.destroy();
  }
}

export default FamilyTreeComponent;