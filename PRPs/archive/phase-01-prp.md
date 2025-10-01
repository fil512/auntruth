# PRP: Foundation Architecture Implementation

## Executive Summary
**Project:** AuntieRuth.com Genealogy Site Modernization - Phase 1
**Duration:** 1-2 weeks
**Priority:** Critical - Foundation for all subsequent UX improvements
**Confidence Score:** 8/10 for one-pass implementation

This PRP implements the core architectural foundation for the AuntieRuth.com genealogy site modernization. It establishes a component-based JavaScript architecture, optimizes data structure for GitHub Pages deployment, implements enhanced navigation to fix critical usability issues, and provides mobile-responsive improvements.

## Critical Context

### Codebase Understanding
- **Scale:** 11,120+ HTML files across 10 lineage directories (L0-L9)
- **Current Location:** `/Volumes/bork/pers/auntruth/`
- **Deployment:** GitHub Pages static hosting (no server-side processing)
- **Data:** 2,985+ people currently in single `docs/new/js/data.json` file
- **Progressive Enhancement:** Site must function without JavaScript

### File Naming Conventions (from `docs/README.md`)
- `XF###.htm` - Person/family detail pages
- `THF###.htm` - Person thumbnail galleries
- `XI###.htm` - Individual image detail pages
- `TH####.htm` - Year-based thumbnail pages
- **Critical:** All existing URLs must continue working

### Existing Patterns to Follow
1. **Navigation Component:** `docs/new/js/navigation.js` - Current implementation pattern
2. **CSS Structure:** `docs/new/css/navigation.css` - Mobile-first responsive approach
3. **Python Scripts:** `PRPs/scripts/` - Mass file operation patterns
4. **No Build System:** Currently static files served directly by GitHub Pages

## Implementation Blueprint

### Task List (In Order)

1. **Setup Node.js Project Structure**
   - Create package.json with build scripts
   - Setup directory structure for new components
   - Configure GitHub Actions workflow

2. **Create Component Architecture**
   - Implement BaseComponent class
   - Create DataManager service
   - Build component loader system

3. **Implement Data Chunking**
   - Split data.json into lineage-based chunks
   - Create metadata index
   - Build data migration script

4. **Enhance Navigation Component**
   - Fix stranded user problem on person pages
   - Add breadcrumb navigation
   - Implement family navigation links
   - Mobile menu improvements

5. **Mobile-First CSS Framework**
   - Create foundation.css with responsive utilities
   - Convert tables to mobile-friendly cards
   - Implement touch-friendly targets (44px minimum)

6. **Build Pipeline**
   - Create optimization scripts
   - Setup GitHub Actions workflow
   - Configure deployment process

## Detailed Implementation

### 1. Setup Node.js Project Structure

#### Create `package.json` in project root:
```json
{
  "name": "auntruth-modernization",
  "version": "2.0.0",
  "description": "AuntieRuth.com genealogy site modernization",
  "scripts": {
    "build:data-chunks": "node scripts/build-data-chunks.js",
    "build:search-indices": "node scripts/build-search-indices.js",
    "build:optimize": "node scripts/optimize-assets.js",
    "build:all": "npm run build:data-chunks && npm run build:search-indices && npm run build:optimize",
    "dev": "python3 -m http.server 8000 --directory docs",
    "test": "node scripts/test-navigation.js",
    "validate": "node scripts/validate-data.js"
  },
  "devDependencies": {
    "terser": "^5.19.0",
    "clean-css": "^5.3.2",
    "html-minifier-terser": "^7.2.0"
  }
}
```

#### Create directory structure:
```
docs/new/js/
├── core/
│   ├── app.js              # Main application controller
│   ├── base-component.js   # Base class for all components
│   └── data-manager.js     # Centralized data access
├── components/
│   └── navigation-enhanced.js # Enhanced navigation component
├── utils/
│   ├── performance.js      # Performance utilities
│   └── mobile-detection.js # Mobile detection
└── data/
    ├── metadata.json       # Site-wide metadata
    └── lineages/          # Lineage-specific data chunks
```

### 2. Component Architecture Implementation

#### `docs/new/js/core/base-component.js`:
```javascript
/**
 * Base Component Class
 * Foundation for all UI components with lifecycle management
 */
class BaseComponent {
  constructor(options = {}) {
    this.options = options;
    this.element = null;
    this.initialized = false;
    this.mobile = this.detectMobile();
  }

  async init() {
    if (this.initialized) return;

    try {
      await this.loadDependencies();
      await this.render();
      this.attachEventListeners();
      this.initialized = true;
    } catch (error) {
      console.error(`Failed to initialize ${this.constructor.name}:`, error);
      throw error;
    }
  }

  async loadDependencies() {
    // Override in subclasses for async dependency loading
  }

  async render() {
    // Override in subclasses for rendering logic
  }

  attachEventListeners() {
    // Override in subclasses for event handling
  }

  destroy() {
    if (this.element) {
      // Remove all event listeners
      const clone = this.element.cloneNode(true);
      this.element.parentNode.replaceChild(clone, this.element);
      this.element = null;
    }
    this.initialized = false;
  }

  detectMobile() {
    return window.innerWidth <= 768 ||
           'ontouchstart' in window ||
           navigator.maxTouchPoints > 0;
  }

  // Utility method for safe DOM queries
  $(selector, context = document) {
    return context.querySelector(selector);
  }

  $$(selector, context = document) {
    return Array.from(context.querySelectorAll(selector));
  }
}

// Export for ES6 modules and global
export default BaseComponent;
window.BaseComponent = BaseComponent;
```

### 3. Data Manager Implementation

#### `docs/new/js/core/data-manager.js`:
```javascript
/**
 * DataManager Service
 * Handles efficient data loading with lineage-based chunking
 */
class DataManager {
  constructor() {
    this.cache = new Map();
    this.metadata = null;
    this.maxCacheSize = this.isMobile() ? 3 : 6;
    this.basePath = '/auntruth/new/js/data/';
  }

  async getMetadata() {
    if (this.metadata) return this.metadata;

    try {
      const response = await fetch(`${this.basePath}metadata.json`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      this.metadata = await response.json();
      return this.metadata;
    } catch (error) {
      console.error('Failed to load metadata:', error);
      // Fallback to original data.json if new structure doesn't exist
      return this.loadLegacyData();
    }
  }

  async getLineageData(lineageId) {
    const cacheKey = `lineage-${lineageId}`;

    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    try {
      const response = await fetch(`${this.basePath}lineages/L${lineageId}.json`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      this.cache.set(cacheKey, data);
      this.maintainCacheSize();
      return data;
    } catch (error) {
      console.error(`Failed to load lineage ${lineageId}:`, error);
      return null;
    }
  }

  async getPersonData(personId) {
    const metadata = await this.getMetadata();
    if (!metadata || !metadata.personToLineage) return null;

    const lineageId = metadata.personToLineage[personId];
    if (!lineageId) return null;

    const lineageData = await this.getLineageData(lineageId);
    if (!lineageData) return null;

    return lineageData.people.find(person => person.id === personId);
  }

  async searchPeople(query, options = {}) {
    const metadata = await this.getMetadata();
    if (!metadata) return [];

    const searchTerm = query.toLowerCase();
    const results = [];

    // Search through cached lineages first
    for (const [key, lineageData] of this.cache) {
      if (lineageData && lineageData.people) {
        const matches = lineageData.people.filter(person =>
          person.name.toLowerCase().includes(searchTerm)
        );
        results.push(...matches);
      }
    }

    return results;
  }

  maintainCacheSize() {
    if (this.cache.size > this.maxCacheSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
  }

  async loadLegacyData() {
    // Fallback to original data.json
    try {
      const response = await fetch('/auntruth/new/js/data.json');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Failed to load legacy data:', error);
      return null;
    }
  }

  isMobile() {
    return window.innerWidth <= 768;
  }
}

// Export for ES6 modules and global
export default DataManager;
window.DataManager = DataManager;
```

### 4. Enhanced Navigation Component

#### `docs/new/js/components/navigation-enhanced.js`:
```javascript
/**
 * Enhanced Navigation Component
 * Fixes critical navigation issues and adds family context
 */
import BaseComponent from '../core/base-component.js';
import DataManager from '../core/data-manager.js';

class NavigationEnhanced extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.currentPage = this.detectCurrentPage();
    this.currentLineage = this.detectCurrentLineage();
    this.recentPages = this.loadRecentPages();
  }

  async render() {
    // Check if navigation already exists
    if (document.querySelector('.enhanced-nav')) {
      console.log('Enhanced navigation already present');
      return;
    }

    const navHtml = await this.generateNavigationHTML();
    this.injectNavigation(navHtml);

    // Save reference to element
    this.element = document.querySelector('.enhanced-nav');

    // Add family context for person pages
    if (this.currentPage.type === 'person') {
      await this.enhanceWithFamilyContext();
    }
  }

  async generateNavigationHTML() {
    const breadcrumbs = await this.generateBreadcrumbs();
    const familyNav = await this.generateFamilyNavigation();
    const basePath = '/auntruth/new/';

    return `
      <nav class="enhanced-nav" role="navigation" aria-label="Main navigation">
        <!-- Primary Navigation Bar -->
        <div class="primary-nav">
          <div class="nav-container">
            <div class="nav-brand">
              <a href="${basePath}">AuntieRuth.com</a>
            </div>

            <div class="nav-controls ${this.mobile ? 'mobile' : 'desktop'}">
              ${this.mobile ? this.generateMobileMenu() : this.generateDesktopMenu()}
            </div>
          </div>
        </div>

        <!-- Breadcrumb Navigation -->
        ${breadcrumbs ? `<div class="breadcrumb-nav">${breadcrumbs}</div>` : ''}

        <!-- Family Navigation (person pages only) -->
        ${familyNav ? `<div class="family-nav">${familyNav}</div>` : ''}
      </nav>
    `;
  }

  async generateBreadcrumbs() {
    if (this.currentPage.type === 'index') return null;

    const basePath = '/auntruth/new/';
    let breadcrumbs = '<nav class="breadcrumbs" aria-label="Breadcrumb">';
    breadcrumbs += `<a href="${basePath}">Home</a>`;

    if (this.currentLineage) {
      breadcrumbs += ' › ';
      const lineagePath = `${basePath}htm/L${this.currentLineage.number}/`;
      breadcrumbs += `<a href="${lineagePath}">${this.currentLineage.name}</a>`;
    }

    if (this.currentPage.type === 'person' && this.currentPage.title) {
      breadcrumbs += ' › ';
      breadcrumbs += `<span class="current">${this.currentPage.title}</span>`;
    }

    breadcrumbs += '</nav>';
    return breadcrumbs;
  }

  async generateFamilyNavigation() {
    if (this.currentPage.type !== 'person') return null;

    try {
      // Extract person ID from filename (e.g., XF191.htm -> 191)
      const personId = this.currentPage.pageId;
      if (!personId) return null;

      const personData = await this.dataManager.getPersonData(personId);
      if (!personData) {
        console.log(`No person data found for ID: ${personId}`);
        return null;
      }

      let familyNav = '<div class="family-navigation">';

      // Parents section
      if (personData.father || personData.mother) {
        familyNav += '<div class="family-group">';
        familyNav += '<span class="family-label">Parents:</span>';
        familyNav += '<div class="family-links">';

        if (personData.father) {
          const fatherId = this.extractPersonId(personData.father);
          if (fatherId) {
            familyNav += `<a href="XF${fatherId}.htm" class="family-link">Father: ${personData.fatherName || personData.father}</a>`;
          }
        }

        if (personData.mother) {
          const motherId = this.extractPersonId(personData.mother);
          if (motherId) {
            familyNav += `<a href="XF${motherId}.htm" class="family-link">Mother: ${personData.motherName || personData.mother}</a>`;
          }
        }

        familyNav += '</div></div>';
      }

      // Spouse(s) section
      const spouses = ['spouse', 'spouse2', 'spouse3', 'spouse4']
        .map(key => personData[key])
        .filter(Boolean);

      if (spouses.length > 0) {
        familyNav += '<div class="family-group">';
        familyNav += '<span class="family-label">Spouse(s):</span>';
        familyNav += '<div class="family-links">';

        spouses.forEach((spouse, index) => {
          const spouseId = this.extractPersonId(spouse);
          if (spouseId) {
            const spouseName = personData[`spouse${index ? index + 1 : ''}Name`] || spouse;
            familyNav += `<a href="XF${spouseId}.htm" class="family-link">${spouseName}</a>`;
          }
        });

        familyNav += '</div></div>';
      }

      // Children section (if available)
      if (personData.children && personData.children.length > 0) {
        familyNav += '<div class="family-group">';
        familyNav += '<span class="family-label">Children:</span>';
        familyNav += '<div class="family-links">';

        personData.children.forEach(child => {
          const childId = this.extractPersonId(child);
          if (childId) {
            familyNav += `<a href="XF${childId}.htm" class="family-link">${child}</a>`;
          }
        });

        familyNav += '</div></div>';
      }

      // Photos link
      familyNav += '<div class="family-group">';
      familyNav += `<a href="THF${personId}.htm" class="family-link photos-link">📷 View Photos</a>`;
      familyNav += '</div>';

      familyNav += '</div>';
      return familyNav;

    } catch (error) {
      console.error('Failed to generate family navigation:', error);
      return null;
    }
  }

  generateMobileMenu() {
    const basePath = '/auntruth/new/';

    return `
      <button class="mobile-menu-toggle" aria-expanded="false" aria-controls="mobile-menu">
        <span class="sr-only">Toggle navigation</span>
        <span class="menu-icon"></span>
      </button>
      <div class="mobile-menu" id="mobile-menu" hidden>
        <a href="${basePath}" class="menu-item">Home</a>
        <a href="${basePath}search/" class="menu-item">Search</a>
        <button class="menu-item lineage-toggle" aria-expanded="false">
          Lineages <span class="arrow">▼</span>
        </button>
        <div class="lineage-submenu" hidden>
          ${this.generateLineageLinks()}
        </div>
        <a href="/auntruth/htm/" class="menu-item">Original Site</a>
      </div>
    `;
  }

  generateDesktopMenu() {
    const basePath = '/auntruth/new/';

    return `
      <ul class="desktop-menu">
        <li><a href="${basePath}" class="menu-item">Home</a></li>
        <li><a href="${basePath}search/" class="menu-item">Search</a></li>
        <li class="dropdown">
          <button class="menu-item dropdown-toggle" aria-expanded="false">
            Lineages <span class="arrow">▼</span>
          </button>
          <ul class="dropdown-menu" hidden>
            ${this.generateLineageLinks('li')}
          </ul>
        </li>
        <li><a href="/auntruth/htm/" class="menu-item">Original Site</a></li>
      </ul>
    `;
  }

  generateLineageLinks(wrapper = 'div') {
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

    const basePath = '/auntruth/new/htm/';
    const links = lineages.map(lineage => {
      const isCurrent = this.currentLineage?.number === lineage.id;
      const link = `<a href="${basePath}L${lineage.id}/" class="lineage-link ${isCurrent ? 'current' : ''}">${lineage.name}</a>`;
      return wrapper === 'li' ? `<li>${link}</li>` : link;
    }).join('');

    return links;
  }

  injectNavigation(navHtml) {
    // Remove any existing navigation
    const existing = document.querySelector('nav');
    if (existing) {
      existing.remove();
    }

    // Insert new navigation at beginning of body
    document.body.insertAdjacentHTML('afterbegin', navHtml);

    // Add padding to body to account for fixed navigation
    document.body.style.paddingTop = this.mobile ? '120px' : '80px';
  }

  attachEventListeners() {
    // Mobile menu toggle
    const mobileToggle = this.$('.mobile-menu-toggle');
    const mobileMenu = this.$('.mobile-menu');

    if (mobileToggle && mobileMenu) {
      mobileToggle.addEventListener('click', () => {
        const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
        mobileToggle.setAttribute('aria-expanded', !expanded);
        mobileMenu.hidden = expanded;
      });
    }

    // Desktop dropdown
    const dropdownToggle = this.$('.dropdown-toggle');
    const dropdownMenu = this.$('.dropdown-menu');

    if (dropdownToggle && dropdownMenu) {
      dropdownToggle.addEventListener('click', (e) => {
        e.preventDefault();
        const expanded = dropdownToggle.getAttribute('aria-expanded') === 'true';
        dropdownToggle.setAttribute('aria-expanded', !expanded);
        dropdownMenu.hidden = expanded;
      });

      // Close on outside click
      document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
          dropdownToggle.setAttribute('aria-expanded', 'false');
          dropdownMenu.hidden = true;
        }
      });
    }

    // Lineage submenu in mobile
    const lineageToggle = this.$('.lineage-toggle');
    const lineageSubmenu = this.$('.lineage-submenu');

    if (lineageToggle && lineageSubmenu) {
      lineageToggle.addEventListener('click', () => {
        const expanded = lineageToggle.getAttribute('aria-expanded') === 'true';
        lineageToggle.setAttribute('aria-expanded', !expanded);
        lineageSubmenu.hidden = expanded;
      });
    }
  }

  detectCurrentPage() {
    const path = window.location.pathname;
    const filename = path.split('/').pop() || 'index.html';

    let type = 'unknown';
    let pageId = null;
    let title = document.title || '';

    if (filename.startsWith('XF')) {
      type = 'person';
      pageId = filename.replace('.htm', '').replace('.html', '').replace('XF', '');
    } else if (filename.startsWith('THF')) {
      type = 'thumbnail';
      pageId = filename.replace('.htm', '').replace('.html', '').replace('THF', '');
    } else if (filename === 'index.htm' || filename === 'index.html') {
      type = 'index';
    }

    // Clean up title
    title = title.replace('<br>AuntieRuth.com', '')
                 .replace('AuntieRuth.com', '')
                 .trim();

    return {
      path,
      filename,
      type,
      pageId,
      title,
      url: window.location.href
    };
  }

  detectCurrentLineage() {
    const path = window.location.pathname;
    const match = path.match(/\/L(\d+)\//);

    if (!match) return null;

    const number = match[1];
    const lineageNames = {
      '0': 'All',
      '1': 'Hagborg-Hansson',
      '2': 'Nelson',
      '3': 'Pringle-Hambley',
      '4': 'Lathrop-Lothropp',
      '5': 'Ward',
      '6': 'Selch-Weiss',
      '7': 'Stebbe',
      '8': 'Lentz',
      '9': 'Phoenix-Rogerson'
    };

    return {
      number,
      name: lineageNames[number] || `Lineage ${number}`,
      path: `/auntruth/new/htm/L${number}/`
    };
  }

  extractPersonId(text) {
    // Extract person ID from various formats
    // Could be: "123", "[123]", "John Doe [123]", etc.
    if (!text) return null;

    const match = text.match(/\[?(\d+)\]?/);
    return match ? match[1] : null;
  }

  loadRecentPages() {
    try {
      return JSON.parse(localStorage.getItem('recentPages') || '[]');
    } catch {
      return [];
    }
  }

  saveCurrentPage() {
    if (this.currentPage.type === 'person') {
      const recent = this.loadRecentPages();
      const pageData = {
        title: this.currentPage.title,
        url: this.currentPage.url,
        timestamp: Date.now()
      };

      // Remove duplicates and add to beginning
      const filtered = recent.filter(page => page.url !== pageData.url);
      filtered.unshift(pageData);

      // Keep only last 10
      const limited = filtered.slice(0, 10);

      try {
        localStorage.setItem('recentPages', JSON.stringify(limited));
      } catch {
        // Ignore storage errors
      }
    }
  }

  async enhanceWithFamilyContext() {
    // Additional enhancements for person pages
    this.saveCurrentPage();
  }
}

// Export for ES6 modules and global
export default NavigationEnhanced;
window.NavigationEnhanced = NavigationEnhanced;
```

### 5. Mobile-First CSS Framework

#### `docs/new/css/foundation.css`:
```css
/* Foundation CSS - Mobile-First Responsive Framework */

/* Reset and Base Styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Mobile-First Typography */
:root {
  /* Fluid typography scale */
  --font-size-sm: clamp(0.8rem, 2vw, 0.875rem);
  --font-size-base: clamp(0.875rem, 2.5vw, 1rem);
  --font-size-lg: clamp(1rem, 3vw, 1.125rem);
  --font-size-xl: clamp(1.125rem, 4vw, 1.25rem);
  --font-size-2xl: clamp(1.25rem, 5vw, 1.5rem);

  /* Spacing scale */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;

  /* Layout */
  --nav-height-mobile: 120px;
  --nav-height-desktop: 80px;
  --content-max-width: 1200px;

  /* Colors - AuntieRuth.com brand */
  --color-primary: #0066cc;
  --color-secondary: #666;
  --color-background: #C1CFBA;
  --color-surface: #fff;
  --color-text: #333;
  --color-link: #0000FF;
  --color-border: #ddd;

  /* Touch targets */
  --touch-target-min: 44px;
}

/* Base body styles */
body {
  font-family: Verdana, Arial, sans-serif;
  font-size: var(--font-size-base);
  line-height: 1.5;
  color: var(--color-text);
  background-color: var(--color-background);
  padding-top: var(--nav-height-mobile);
  -webkit-text-size-adjust: 100%;
}

/* Enhanced Navigation Styles */
.enhanced-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: var(--color-surface);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1000;
}

.primary-nav {
  border-bottom: 1px solid var(--color-border);
}

.nav-container {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-sm) var(--space-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 60px;
}

.nav-brand a {
  font-size: var(--font-size-xl);
  font-weight: bold;
  color: var(--color-primary);
  text-decoration: none;
}

/* Mobile Menu Styles */
.mobile-menu-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--touch-target-min);
  height: var(--touch-target-min);
  background: none;
  border: 1px solid var(--color-secondary);
  border-radius: 4px;
  cursor: pointer;
  padding: 0;
}

.menu-icon {
  width: 20px;
  height: 2px;
  background: var(--color-text);
  position: relative;
}

.menu-icon::before,
.menu-icon::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 2px;
  background: var(--color-text);
  left: 0;
}

.menu-icon::before { top: -6px; }
.menu-icon::after { top: 6px; }

.mobile-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: var(--space-md);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.mobile-menu .menu-item {
  display: block;
  padding: var(--space-md) var(--space-sm);
  color: var(--color-link);
  text-decoration: none;
  min-height: var(--touch-target-min);
  border-bottom: 1px solid var(--color-border);
}

/* Desktop menu - hidden on mobile */
.desktop-menu {
  display: none;
}

/* Breadcrumb Navigation */
.breadcrumb-nav {
  background: #f8f9fa;
  padding: var(--space-sm) var(--space-md);
  border-top: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
}

.breadcrumbs {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.breadcrumbs a {
  color: var(--color-link);
  text-decoration: none;
}

.breadcrumbs a:hover {
  text-decoration: underline;
}

.breadcrumbs .current {
  color: var(--color-text);
  font-weight: bold;
}

/* Family Navigation */
.family-nav {
  background: #f0f8ff;
  padding: var(--space-sm) var(--space-md);
  border-top: 1px solid var(--color-border);
}

.family-navigation {
  max-width: var(--content-max-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.family-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-sm);
}

.family-label {
  font-weight: bold;
  color: var(--color-secondary);
  font-size: var(--font-size-sm);
  min-width: 60px;
}

.family-links {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.family-link {
  color: var(--color-link);
  text-decoration: none;
  padding: var(--space-xs) var(--space-sm);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  min-height: var(--touch-target-min);
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm);
}

.family-link:hover,
.family-link:focus {
  text-decoration: underline;
  background: #f5f5f5;
}

/* Responsive Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-md) 0;
}

/* Mobile: Convert tables to cards */
@media (max-width: 767px) {
  table, tbody, th, td, tr {
    display: block;
  }

  tr {
    border: 1px solid var(--color-border);
    border-radius: 8px;
    margin-bottom: var(--space-md);
    padding: var(--space-md);
    background: var(--color-surface);
  }

  td {
    display: flex;
    gap: var(--space-sm);
    padding: var(--space-xs) 0;
    min-height: var(--touch-target-min);
    align-items: flex-start;
  }

  td:nth-child(1) {
    font-weight: bold;
    color: var(--color-secondary);
    font-size: var(--font-size-sm);
    min-width: 120px;
    flex-shrink: 0;
  }

  td:nth-child(1)::after {
    content: ':';
  }
}

/* Image Responsiveness */
img {
  max-width: 100%;
  height: auto;
  border: 0;
}

/* Main Content Area */
main {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-md);
}

/* Utility Classes */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Tablet Breakpoint */
@media (min-width: 768px) {
  body {
    padding-top: var(--nav-height-desktop);
  }

  .mobile-menu-toggle,
  .mobile-menu {
    display: none;
  }

  .desktop-menu {
    display: flex;
    list-style: none;
    gap: var(--space-lg);
    align-items: center;
  }

  .desktop-menu .menu-item {
    color: var(--color-link);
    text-decoration: none;
    padding: var(--space-sm) var(--space-md);
    min-height: var(--touch-target-min);
    display: flex;
    align-items: center;
  }

  .dropdown {
    position: relative;
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    min-width: 200px;
    list-style: none;
    padding: var(--space-xs) 0;
  }

  /* Tables: restore normal layout */
  table { display: table; }
  tbody { display: table-row-group; }
  tr {
    display: table-row;
    border: none;
    margin: 0;
    padding: 0;
  }
  td {
    display: table-cell;
    padding: var(--space-sm) var(--space-md);
    border-bottom: 1px solid var(--color-border);
    vertical-align: top;
  }

  td:nth-child(1) {
    background: #f8f9fa;
    font-weight: bold;
    width: 150px;
  }

  td:nth-child(1)::after {
    content: none;
  }
}

/* Desktop Breakpoint */
@media (min-width: 1024px) {
  .family-navigation {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .family-group {
    flex-direction: row;
  }
}

/* Accessibility Improvements */
@media (prefers-contrast: high) {
  :root {
    --color-background: #fff;
    --color-text: #000;
    --color-secondary: #000;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Print Styles */
@media print {
  .enhanced-nav,
  .mobile-menu-toggle {
    display: none;
  }

  body {
    padding-top: 0;
  }
}
```

### 6. Data Chunking Script

#### `scripts/build-data-chunks.js`:
```javascript
#!/usr/bin/env node

/**
 * Build Data Chunks Script
 * Splits large data.json into lineage-based chunks for efficient loading
 */

const fs = require('fs').promises;
const path = require('path');

class DataChunker {
  constructor() {
    this.sourceFile = path.join(__dirname, '../docs/new/js/data.json');
    this.outputDir = path.join(__dirname, '../docs/new/js/data');
    this.lineagesDir = path.join(this.outputDir, 'lineages');
  }

  async run() {
    console.log('Starting data chunking process...');

    try {
      // Create output directories
      await this.createDirectories();

      // Load original data
      const originalData = await this.loadOriginalData();

      // Process and chunk data
      const chunks = await this.processData(originalData);

      // Write chunked files
      await this.writeChunks(chunks);

      console.log('Data chunking complete!');
      console.log(`Created ${chunks.lineages.size} lineage files`);
      console.log(`Total people processed: ${chunks.totalPeople}`);

    } catch (error) {
      console.error('Error during data chunking:', error);
      process.exit(1);
    }
  }

  async createDirectories() {
    await fs.mkdir(this.outputDir, { recursive: true });
    await fs.mkdir(this.lineagesDir, { recursive: true });
  }

  async loadOriginalData() {
    try {
      const content = await fs.readFile(this.sourceFile, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      console.error('Failed to load original data.json:', error);
      throw error;
    }
  }

  async processData(data) {
    const metadata = {
      generated: new Date().toISOString(),
      version: '2.0',
      totalPeople: 0,
      totalLineages: 0,
      personToLineage: {},
      lineageNames: {}
    };

    const lineages = new Map();

    // Process people array
    if (data.people && Array.isArray(data.people)) {
      for (const person of data.people) {
        // Determine lineage ID (may need adjustment based on actual data structure)
        const lineageId = person.lineage || this.extractLineageFromPath(person);

        if (!lineages.has(lineageId)) {
          lineages.set(lineageId, {
            lineageId,
            lineageName: this.getLineageName(lineageId),
            people: []
          });
        }

        lineages.get(lineageId).people.push(person);
        metadata.personToLineage[person.id] = lineageId;
        metadata.totalPeople++;
      }
    }

    metadata.totalLineages = lineages.size;

    // Add lineage names to metadata
    for (const [id, data] of lineages) {
      metadata.lineageNames[id] = data.lineageName;
    }

    return { metadata, lineages, totalPeople: metadata.totalPeople };
  }

  extractLineageFromPath(person) {
    // Extract lineage from file path if available
    if (person.path) {
      const match = person.path.match(/L(\d+)/);
      return match ? match[1] : '0';
    }
    return '0'; // Default lineage
  }

  getLineageName(lineageId) {
    const names = {
      '0': 'All',
      '1': 'Hagborg-Hansson',
      '2': 'Nelson',
      '3': 'Pringle-Hambley',
      '4': 'Lathrop-Lothropp',
      '5': 'Ward',
      '6': 'Selch-Weiss',
      '7': 'Stebbe',
      '8': 'Lentz',
      '9': 'Phoenix-Rogerson'
    };
    return names[lineageId] || `Lineage ${lineageId}`;
  }

  async writeChunks(chunks) {
    // Write metadata file
    const metadataPath = path.join(this.outputDir, 'metadata.json');
    await fs.writeFile(
      metadataPath,
      JSON.stringify(chunks.metadata, null, 2)
    );
    console.log(`Created metadata.json`);

    // Write lineage files
    for (const [lineageId, lineageData] of chunks.lineages) {
      const filename = `L${lineageId}.json`;
      const filepath = path.join(this.lineagesDir, filename);

      await fs.writeFile(
        filepath,
        JSON.stringify(lineageData, null, 2)
      );

      console.log(`Created ${filename} with ${lineageData.people.length} people`);
    }
  }
}

// Run if called directly
if (require.main === module) {
  const chunker = new DataChunker();
  chunker.run();
}

module.exports = DataChunker;
```

### 7. Application Controller

#### `docs/new/js/core/app.js`:
```javascript
/**
 * Main Application Controller
 * Initializes and manages all components
 */

class AuntieRuthApp {
  constructor() {
    this.components = new Map();
    this.dataManager = null;
    this.initialized = false;
  }

  async init() {
    if (this.initialized) return;

    console.log('Initializing AuntieRuth.com modernization...');

    try {
      // Initialize data manager
      this.dataManager = new DataManager();

      // Initialize navigation (critical path)
      await this.initNavigation();

      // Progressive enhancement based on page type
      const pageType = this.detectPageType();

      if (pageType === 'person') {
        await this.initPersonPageEnhancements();
      }

      // Initialize mobile optimizations if needed
      if (this.isMobile()) {
        await this.initMobileEnhancements();
      }

      this.initialized = true;
      console.log('Application initialized successfully');

    } catch (error) {
      console.error('Failed to initialize application:', error);
      // Site should still work without JavaScript enhancements
    }
  }

  async initNavigation() {
    try {
      // Dynamic import for code splitting
      const NavigationModule = await this.loadComponent('navigation-enhanced');

      if (NavigationModule) {
        const nav = new NavigationModule.default({
          dataManager: this.dataManager
        });

        await nav.init();
        this.components.set('navigation', nav);
      }
    } catch (error) {
      console.error('Failed to initialize navigation:', error);
      // Fall back to basic navigation if enhanced fails
      this.initFallbackNavigation();
    }
  }

  async initPersonPageEnhancements() {
    // Additional enhancements for person pages
    console.log('Enhancing person page experience...');
  }

  async initMobileEnhancements() {
    // Mobile-specific optimizations
    console.log('Applying mobile optimizations...');

    // Add mobile class to body for CSS hooks
    document.body.classList.add('mobile-device');
  }

  async loadComponent(name) {
    try {
      // Dynamic import for progressive loading
      const module = await import(`./components/${name}.js`);
      return module;
    } catch (error) {
      console.warn(`Component ${name} not found, using fallback`);
      return null;
    }
  }

  initFallbackNavigation() {
    // Basic navigation without JavaScript enhancements
    console.log('Using fallback navigation');
  }

  detectPageType() {
    const filename = window.location.pathname.split('/').pop() || '';

    if (filename.startsWith('XF')) return 'person';
    if (filename.startsWith('THF')) return 'thumbnail';
    if (filename.startsWith('XI')) return 'image';
    if (filename.includes('index')) return 'index';

    return 'unknown';
  }

  isMobile() {
    return window.innerWidth <= 768 ||
           'ontouchstart' in window ||
           navigator.maxTouchPoints > 0;
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.auntieRuthApp = new AuntieRuthApp();
    window.auntieRuthApp.init();
  });
} else {
  // DOM already loaded
  window.auntieRuthApp = new AuntieRuthApp();
  window.auntieRuthApp.init();
}
```

### 8. GitHub Actions Workflow

#### `.github/workflows/build-and-deploy.yml`:
```yaml
name: Build and Deploy AuntieRuth.com

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Create data directories
      run: |
        mkdir -p docs/new/js/data/lineages
        mkdir -p docs/new/js/data/indices

    - name: Build data chunks
      run: npm run build:data-chunks

    - name: Build search indices
      run: npm run build:search-indices

    - name: Optimize assets
      run: npm run build:optimize

    - name: Run tests
      run: npm test

    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs
        cname: hagborg.github.io
```

## Validation Gates

Execute these commands to verify each phase:

### 1. Data Structure Validation
```bash
# Verify data chunks created
ls -la docs/new/js/data/lineages/
# Should see L1.json through L9.json

# Verify metadata file
cat docs/new/js/data/metadata.json | head -20
# Should see personToLineage mappings
```

### 2. Component Testing
```bash
# Test navigation injection
node scripts/test-navigation.js

# Manual browser test
python3 -m http.server 8000 --directory docs
# Navigate to http://localhost:8000/new/htm/L1/XF191.htm
# Should see enhanced navigation with breadcrumbs and family links
```

### 3. Mobile Responsiveness
```bash
# Use Chrome DevTools
# 1. Open any person page
# 2. Toggle device toolbar (Ctrl+Shift+M)
# 3. Select iPhone 12 Pro
# 4. Verify:
#    - Navigation collapses to mobile menu
#    - Tables convert to cards
#    - Touch targets are 44px minimum
```

### 4. Performance Metrics
```bash
# Test with Lighthouse
# 1. Open Chrome DevTools
# 2. Go to Lighthouse tab
# 3. Run Mobile audit
# Success criteria:
#   - Performance > 70
#   - First Contentful Paint < 2s
#   - Time to Interactive < 3s
```

### 5. Build Pipeline
```bash
# Test GitHub Actions locally
npm run build:all
# Should complete without errors

# Verify optimized files created
ls -la docs/new/js/*.min.js
ls -la docs/new/css/*.min.css
```

## External References

### JavaScript Best Practices
- **MDN Web Components**: https://developer.mozilla.org/en-US/docs/Web/Web_Components
- **Progressive Enhancement**: https://developer.mozilla.org/en-US/docs/Glossary/Progressive_Enhancement
- **ES6 Modules**: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules

### Performance Optimization
- **Web.dev Performance Guide**: https://web.dev/performance/
- **Code Splitting**: https://web.dev/reduce-javascript-payloads-with-code-splitting/
- **Resource Hints**: https://web.dev/preconnect-and-dns-prefetch/

### Mobile Responsive Design
- **Mobile First CSS**: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Responsive/Mobile_first
- **Touch Target Guidelines**: https://web.dev/accessible-tap-targets/
- **Responsive Tables**: https://css-tricks.com/responsive-data-tables/

### GitHub Pages Deployment
- **GitHub Pages Documentation**: https://docs.github.com/en/pages
- **GitHub Actions for Pages**: https://github.com/marketplace/actions/github-pages-action
- **Custom Domains**: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site

## Common Pitfalls to Avoid

1. **Don't break existing URLs** - All XF###.htm files must keep working
2. **Preserve file case** - GitHub Pages is case-sensitive
3. **Test without JavaScript** - Site must work with JS disabled
4. **Mobile touch targets** - Ensure 44px minimum for all interactive elements
5. **Data loading errors** - Always provide fallbacks to original data.json

## Success Criteria Checklist

- [ ] All 11,120+ HTML files remain accessible
- [ ] Navigation works on all person pages (no more stranded users)
- [ ] Data loads efficiently with lineage-based chunking
- [ ] Mobile experience significantly improved
- [ ] Page load < 2 seconds on 3G
- [ ] All existing URLs continue working
- [ ] Progressive enhancement verified
- [ ] GitHub Actions workflow deploys successfully
- [ ] Cross-browser testing passes (Chrome, Firefox, Safari, Edge)

## Rollback Plan

If issues arise after deployment:

1. **Immediate Rollback**:
```bash
git revert HEAD
git push origin main
```

2. **Data Structure Fallback**:
- Original data.json remains in place
- DataManager falls back automatically if chunks don't exist

3. **Component Fallback**:
- Navigation degrades gracefully if enhancement fails
- Basic HTML navigation still works

## Next Steps After Phase 1

Once foundation is complete:
- Phase 2: Search functionality and filtering
- Phase 3: Photo galleries and visualization
- Performance monitoring setup
- Analytics implementation

---

**PRP Confidence Score: 8/10**

This PRP provides comprehensive context and executable implementation details. The score is 8/10 because:
- ✅ Clear task ordering and dependencies
- ✅ Complete code examples with comments
- ✅ Validation gates that can be executed
- ✅ References to existing patterns in codebase
- ✅ External documentation links provided
- ✅ Fallback strategies included
- ⚠️ May need minor adjustments based on actual data.json structure
- ⚠️ Mobile testing requires manual verification

The AI agent has all necessary information to execute this foundation architecture implementation successfully in one pass.