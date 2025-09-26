import BaseComponent from '../core/base-component.js';

/**
 * Information Disclosure Component
 * Transforms table-based person pages to organized disclosure sections
 * Preserves URLs and provides fallback to original table structure
 */
class InformationDisclosureComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.userPreferences = this.loadUserPreferences();
    this.originalTable = null;
    this.disclosureContainer = null;

    // Section configuration
    this.sectionConfig = {
      essential: {
        title: 'Essential Information',
        icon: '👤',
        defaultOpen: true,
        fields: ['name', 'birthDate', 'birthLocation', 'deathDate', 'deathLocation', 'age']
      },
      family: {
        title: 'Family Relationships',
        icon: '👨‍👩‍👧‍👦',
        defaultOpen: true,
        fields: ['father', 'mother', 'spouse', 'spouse2', 'spouse3', 'spouse4', 'children', 'siblings']
      },
      biographical: {
        title: 'Biographical Details',
        icon: '📝',
        defaultOpen: false,
        fields: ['occupation', 'address', 'residence', 'education', 'military', 'religion', 'notes', 'biography']
      },
      photos: {
        title: 'Photos & Media',
        icon: '📸',
        defaultOpen: false,
        fields: ['photo', 'photos', 'thumbnail', 'image', 'media']
      },
      research: {
        title: 'Research & Sources',
        icon: '🔍',
        defaultOpen: false,
        fields: ['sources', 'census', 'burial', 'cemetery', 'research', 'dna', 'genetics', 'notes']
      }
    };
  }

  async render() {
    try {
      // Find existing table structure
      this.originalTable = this.$('table#List') || this.$('table[id*="List"]') || this.$('table');

      if (!this.originalTable) {
        console.log('No table found for information disclosure transformation');
        return;
      }

      // Parse table data
      const tableData = this.parseTableData(this.originalTable);
      if (!tableData || Object.keys(tableData).length === 0) {
        console.log('No data found in table for transformation');
        return;
      }

      // Create disclosure layout
      this.createDisclosureLayout(tableData);

      // Apply user preferences
      this.applyUserPreferences();

      // Hide original table (but keep for fallback)
      this.originalTable.style.display = 'none';
      this.originalTable.setAttribute('data-disclosure-fallback', 'true');

    } catch (error) {
      console.error('Failed to create information disclosure layout:', error);
      this.showFallback();
    }
  }

  attachEventListeners() {
    // Section toggle handlers
    const toggleButtons = this.$$('.disclosure-section-toggle');
    toggleButtons.forEach(button => {
      button.addEventListener('click', this.handleSectionToggle.bind(this));
    });

    // Show/hide original table toggle
    const fallbackToggle = this.$('.disclosure-fallback-toggle');
    if (fallbackToggle) {
      fallbackToggle.addEventListener('click', this.toggleFallbackView.bind(this));
    }

    // Preference save on section toggle
    document.addEventListener('disclosure-section-toggled', (event) => {
      this.saveUserPreferences();
    });
  }

  parseTableData(table) {
    const data = {};
    const rows = Array.from(table.querySelectorAll('tr'));

    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 2) {
        const key = this.normalizeKey(cells[0].textContent.trim());
        const value = this.extractCellValue(cells[1]);

        if (key && value) {
          data[key] = value;
        }
      }
    });

    return data;
  }

  normalizeKey(text) {
    if (!text) return '';

    // Remove colons and normalize
    return text
      .toLowerCase()
      .replace(/[:\s]+/g, '_')
      .replace(/[^a-z0-9_]/g, '')
      .replace(/_+/g, '_')
      .replace(/^_|_$/g, '');
  }

  extractCellValue(cell) {
    if (!cell) return null;

    // Check for links
    const links = Array.from(cell.querySelectorAll('a'));
    if (links.length > 0) {
      return {
        type: 'links',
        content: cell.innerHTML.trim(),
        links: links.map(link => ({
          text: link.textContent.trim(),
          href: link.href,
          title: link.title || link.textContent.trim()
        }))
      };
    }

    // Check for images
    const images = Array.from(cell.querySelectorAll('img'));
    if (images.length > 0) {
      return {
        type: 'images',
        content: cell.innerHTML.trim(),
        images: images.map(img => ({
          src: img.src,
          alt: img.alt || '',
          title: img.title || img.alt || ''
        }))
      };
    }

    // Regular text content
    const textContent = cell.textContent.trim();
    if (textContent) {
      return {
        type: 'text',
        content: cell.innerHTML.trim(),
        text: textContent
      };
    }

    return null;
  }

  createDisclosureLayout(tableData) {
    // Create disclosure container
    const disclosureHTML = this.generateDisclosureHTML(tableData);

    // Insert after original table
    this.originalTable.insertAdjacentHTML('afterend', disclosureHTML);
    this.disclosureContainer = this.$('.information-disclosure');

    // Add fallback toggle
    this.addFallbackToggle();
  }

  generateDisclosureHTML(tableData) {
    const sections = this.categorizeData(tableData);

    const sectionsHTML = Object.entries(this.sectionConfig)
      .map(([sectionKey, config]) => {
        const sectionData = sections[sectionKey];
        if (!sectionData || sectionData.length === 0) {
          return ''; // Skip empty sections
        }

        const isOpen = this.userPreferences[sectionKey] !== undefined
          ? this.userPreferences[sectionKey]
          : config.defaultOpen;

        return `
          <div class="disclosure-section" data-section="${sectionKey}">
            <button class="disclosure-section-toggle"
                    aria-expanded="${isOpen}"
                    aria-controls="section-${sectionKey}">
              <span class="section-icon">${config.icon}</span>
              <span class="section-title">${config.title}</span>
              <span class="section-count">(${sectionData.length})</span>
              <span class="toggle-arrow ${isOpen ? 'open' : ''}">${isOpen ? '▼' : '▶'}</span>
            </button>

            <div class="disclosure-section-content"
                 id="section-${sectionKey}"
                 ${isOpen ? '' : 'hidden'}>
              <div class="section-items">
                ${sectionData.map(item => this.renderDataItem(item)).join('')}
              </div>
            </div>
          </div>
        `;
      })
      .filter(Boolean)
      .join('');

    return `
      <div class="information-disclosure">
        <div class="disclosure-header">
          <h3>Person Information</h3>
          <div class="disclosure-controls">
            <button class="btn-secondary expand-all">Expand All</button>
            <button class="btn-secondary collapse-all">Collapse All</button>
            <button class="btn-secondary disclosure-fallback-toggle" title="Show Original Table">
              📋 Original View
            </button>
          </div>
        </div>

        <div class="disclosure-sections">
          ${sectionsHTML}
        </div>

        ${this.renderSummarySection(tableData)}
      </div>
    `;
  }

  categorizeData(tableData) {
    const sections = {
      essential: [],
      family: [],
      biographical: [],
      photos: [],
      research: []
    };

    Object.entries(tableData).forEach(([key, value]) => {
      const section = this.findSectionForField(key);
      if (section && value) {
        sections[section].push({ key, value, displayName: this.getDisplayName(key) });
      }
    });

    return sections;
  }

  findSectionForField(fieldKey) {
    for (const [sectionKey, config] of Object.entries(this.sectionConfig)) {
      if (config.fields.some(field =>
        fieldKey.includes(field) || field.includes(fieldKey)
      )) {
        return sectionKey;
      }
    }

    // Default categorization based on common patterns
    if (fieldKey.includes('photo') || fieldKey.includes('image') || fieldKey.includes('picture')) {
      return 'photos';
    }
    if (fieldKey.includes('source') || fieldKey.includes('research') || fieldKey.includes('census')) {
      return 'research';
    }
    if (fieldKey.includes('spouse') || fieldKey.includes('parent') || fieldKey.includes('child') || fieldKey.includes('family')) {
      return 'family';
    }
    if (fieldKey.includes('birth') || fieldKey.includes('death') || fieldKey.includes('name')) {
      return 'essential';
    }

    return 'biographical'; // Default section
  }

  getDisplayName(key) {
    const displayNames = {
      'birth_date': 'Birth Date',
      'birth_location': 'Birth Location',
      'death_date': 'Death Date',
      'death_location': 'Death Location',
      'father': 'Father',
      'mother': 'Mother',
      'spouse': 'Spouse',
      'spouse_2': 'Second Spouse',
      'occupation': 'Occupation',
      'residence': 'Residence',
      'cemetery': 'Cemetery',
      'burial': 'Burial',
      'sources': 'Sources'
    };

    return displayNames[key] || key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }

  renderDataItem(item) {
    const { key, value, displayName } = item;

    let contentHTML = '';

    switch (value.type) {
      case 'links':
        contentHTML = `
          <div class="item-links">
            ${value.links.map(link =>
              `<a href="${link.href}" title="${this.escapeHtml(link.title)}">${this.escapeHtml(link.text)}</a>`
            ).join(' • ')}
          </div>
        `;
        break;

      case 'images':
        contentHTML = `
          <div class="item-images">
            ${value.images.map(img =>
              `<img src="${img.src}" alt="${this.escapeHtml(img.alt)}" title="${this.escapeHtml(img.title)}" loading="lazy">`
            ).join('')}
          </div>
        `;
        break;

      default:
        contentHTML = `<div class="item-text">${value.content}</div>`;
    }

    return `
      <div class="disclosure-item" data-field="${key}">
        <div class="item-label">${this.escapeHtml(displayName)}</div>
        <div class="item-content">${contentHTML}</div>
      </div>
    `;
  }

  renderSummarySection(tableData) {
    // Create a quick summary for mobile/overview
    const essentialFields = ['name', 'birth_date', 'birth_location', 'death_date', 'death_location'];
    const summary = essentialFields
      .map(field => tableData[field])
      .filter(Boolean)
      .slice(0, 3);

    if (summary.length === 0) return '';

    return `
      <div class="disclosure-summary">
        <div class="summary-items">
          ${summary.map(item => `<span class="summary-item">${item.text || item.content}</span>`).join(' • ')}
        </div>
      </div>
    `;
  }

  addFallbackToggle() {
    // Add event listeners for expand/collapse all
    const expandAll = this.$('.expand-all');
    const collapseAll = this.$('.collapse-all');

    if (expandAll) {
      expandAll.addEventListener('click', () => this.toggleAllSections(true));
    }

    if (collapseAll) {
      collapseAll.addEventListener('click', () => this.toggleAllSections(false));
    }
  }

  handleSectionToggle(event) {
    const button = event.currentTarget;
    const section = button.closest('.disclosure-section');
    const content = section.querySelector('.disclosure-section-content');
    const arrow = button.querySelector('.toggle-arrow');

    const isOpen = content.hidden;

    // Toggle visibility
    content.hidden = !isOpen;
    button.setAttribute('aria-expanded', isOpen.toString());
    arrow.textContent = isOpen ? '▼' : '▶';
    arrow.classList.toggle('open', isOpen);

    // Save preference
    const sectionKey = section.dataset.section;
    this.userPreferences[sectionKey] = isOpen;
    this.saveUserPreferences();

    // Dispatch event
    document.dispatchEvent(new CustomEvent('disclosure-section-toggled', {
      detail: { section: sectionKey, isOpen }
    }));
  }

  toggleAllSections(open) {
    const sections = this.$$('.disclosure-section');
    sections.forEach(section => {
      const button = section.querySelector('.disclosure-section-toggle');
      const content = section.querySelector('.disclosure-section-content');
      const arrow = section.querySelector('.toggle-arrow');

      if (content) {
        content.hidden = !open;
        button.setAttribute('aria-expanded', open.toString());
        arrow.textContent = open ? '▼' : '▶';
        arrow.classList.toggle('open', open);

        // Save preference
        const sectionKey = section.dataset.section;
        this.userPreferences[sectionKey] = open;
      }
    });

    this.saveUserPreferences();
  }

  toggleFallbackView() {
    if (!this.originalTable || !this.disclosureContainer) return;

    const showingOriginal = this.originalTable.style.display !== 'none';

    if (showingOriginal) {
      // Show disclosure view
      this.originalTable.style.display = 'none';
      this.disclosureContainer.style.display = 'block';
      this.$('.disclosure-fallback-toggle').textContent = '📋 Original View';
    } else {
      // Show original table
      this.originalTable.style.display = 'table';
      this.disclosureContainer.style.display = 'none';
      this.$('.disclosure-fallback-toggle').textContent = '📱 Enhanced View';
    }
  }

  showFallback() {
    // Show original table in case of errors
    if (this.originalTable) {
      this.originalTable.style.display = 'table';
    }

    if (this.disclosureContainer) {
      this.disclosureContainer.style.display = 'none';
    }
  }

  loadUserPreferences() {
    try {
      const saved = localStorage.getItem('disclosure-preferences');
      return saved ? JSON.parse(saved) : {};
    } catch (error) {
      console.warn('Failed to load disclosure preferences:', error);
      return {};
    }
  }

  saveUserPreferences() {
    try {
      localStorage.setItem('disclosure-preferences', JSON.stringify(this.userPreferences));
    } catch (error) {
      console.warn('Failed to save disclosure preferences:', error);
    }
  }

  applyUserPreferences() {
    // Preferences are already applied during HTML generation
    // This method can be used for any additional preference-based setup
  }

  escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  destroy() {
    // Restore original table if it was hidden
    if (this.originalTable) {
      this.originalTable.style.display = 'table';
    }

    // Remove disclosure container
    if (this.disclosureContainer) {
      this.disclosureContainer.remove();
    }

    super.destroy();
  }
}

export default InformationDisclosureComponent;