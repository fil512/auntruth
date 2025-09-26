# PRP-Phase-01: Foundation Architecture Implementation

## Executive Summary

**Phase:** Foundation (1 of 3)
**Duration:** 1-2 weeks
**Priority:** Critical - Establishes architectural foundation for all subsequent UX improvements
**Impact:** High - Enables all 8 priority improvements while maintaining backward compatibility

This phase implements the core architectural foundation required for the AuntieRuth.com UX modernization. It establishes component architecture, optimizes data structure for GitHub Pages deployment, implements enhanced navigation, and provides mobile-responsive improvements that serve as the foundation for all subsequent feature development.

## Background & Context

### Prerequisites - Required Reading
Before starting this PRP, read:
- `../docs/README.md` - Complete understanding of genealogy file naming conventions and directory structure
- `docs/new/CLAUDE.md` - Architecture and development guidelines for the modernization project
- `PRPs/priority-01.md` - Navigation improvements (core component of this phase)
- `PRPs/priority-05.md` - Mobile responsive requirements (foundational for this phase)

### Current Site Architecture
- **11,120+ HTML files** across 10 lineage directories (L0-L9: Hagborg-Hansson, Nelson, Pringle-Hambley, etc.)
- **2,985+ people** in single large `js/data.json` file (~2MB+)
- **Legacy compatibility** requirement - all existing URLs must continue working
- **GitHub Pages hosting** - static site with no server-side processing
- **Progressive enhancement** approach - site must function without JavaScript

### Critical Problems This Phase Solves
1. **Navigation Crisis:** Legacy person pages only show "Home |" link, stranding users
2. **Performance Issues:** Single large data file impacts mobile performance
3. **Architecture Debt:** No component system for future feature development
4. **Mobile Usability:** Poor mobile experience across all genealogy pages
5. **Data Structure:** Inefficient data loading for GitHub Pages constraints

## Phase 1 Objectives

### Core Architectural Foundation
1. **Component Architecture:** Establish modular JavaScript component system
2. **Data Optimization:** Split large data file into efficient, cacheable chunks
3. **Enhanced Navigation:** Fix critical navigation problems across all pages
4. **Mobile Foundation:** Implement mobile-first responsive improvements
5. **Build Pipeline:** Create GitHub Pages compatible build and deployment process

### Technical Deliverables
1. Modular component architecture supporting progressive enhancement
2. Optimized data structure with lineage-based chunking
3. Enhanced NavigationComponent fixing critical usability issues
4. Mobile-first responsive CSS framework
5. Automated build pipeline for GitHub Pages deployment

## Implementation Details

### 1. Component Architecture Implementation

#### Component System Structure
```
/docs/new/js/
├── core/
│   ├── app.js              # Main application controller
│   ├── component-loader.js # Progressive component loading
│   └── data-manager.js     # Centralized data access layer
├── components/
│   ├── navigation.js       # Enhanced NavigationComponent
│   └── base-component.js   # Base class for all components
├── utils/
│   ├── performance.js      # Performance optimization utilities
│   └── mobile-detection.js # Mobile device and capability detection
└── data/
    ├── metadata.json       # Site-wide metadata
    └── lineages/           # Lineage-specific data chunks
```

#### Base Component Architecture
```javascript
// base-component.js
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

#### Application Controller
```javascript
// app.js
class AuntieRuthApp {
  constructor() {
    this.components = new Map();
    this.dataManager = new DataManager();
    this.currentLineage = this.detectCurrentLineage();
    this.currentPage = this.detectCurrentPage();
  }

  async init() {
    // Initialize critical components first
    await this.initNavigation();

    // Progressive enhancement - load additional components based on page type
    if (this.currentPage.type === 'person') {
      await this.initPersonPageEnhancements();
    }

    // Initialize mobile optimizations
    if (this.isMobile()) {
      await this.initMobileEnhancements();
    }
  }

  async initNavigation() {
    const NavigationComponent = await import('./components/navigation.js');
    const nav = new NavigationComponent.default({
      currentLineage: this.currentLineage,
      currentPage: this.currentPage
    });
    await nav.init();
    this.components.set('navigation', nav);
  }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new AuntieRuthApp();
  app.init();
});
```

### 2. Data Architecture Optimization

#### Current Problem
- Single `js/data.json` file (~2MB+) with 2,985 people
- Poor performance on mobile devices
- Inefficient for GitHub Pages CDN caching
- All data loaded regardless of user needs

#### Solution: Lineage-Based Data Chunking
```javascript
// data-manager.js
class DataManager {
  constructor() {
    this.cache = new Map();
    this.metadata = null;
    this.maxCacheSize = this.isMobile() ? 3 : 6; // Lineages to keep in memory
  }

  async getMetadata() {
    if (this.metadata) return this.metadata;
    this.metadata = await this.fetchJSON('/auntruth/new/js/data/metadata.json');
    return this.metadata;
  }

  async getLineageData(lineageId) {
    const cacheKey = `lineage-${lineageId}`;

    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const data = await this.fetchJSON(`/auntruth/new/js/data/lineages/L${lineageId}.json`);
    this.cache.set(cacheKey, data);
    this.maintainCacheSize();
    return data;
  }

  async getPersonData(personId) {
    // First check metadata to determine which lineage contains this person
    const metadata = await this.getMetadata();
    const lineageId = metadata.personToLineage[personId];

    if (!lineageId) return null;

    const lineageData = await this.getLineageData(lineageId);
    return lineageData.people.find(person => person.id === personId);
  }

  maintainCacheSize() {
    if (this.cache.size > this.maxCacheSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
  }

  async fetchJSON(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch ${url}:`, error);
      throw error;
    }
  }

  isMobile() {
    return window.innerWidth <= 768;
  }
}
```

#### Data Structure Migration
```javascript
// Build script: scripts/build-data-chunks.js
const fs = require('fs').promises;
const path = require('path');

class DataChunker {
  async processOriginalData() {
    const originalData = JSON.parse(
      await fs.readFile('./js/data.json', 'utf8')
    );

    // Create metadata file
    const metadata = {
      generated: new Date().toISOString(),
      totalPeople: originalData.people.length,
      totalLineages: originalData.metadata.totalLineages,
      version: '2.0',
      personToLineage: {}
    };

    // Group people by lineage
    const lineageGroups = new Map();

    originalData.people.forEach(person => {
      const lineageId = person.lineage;
      if (!lineageGroups.has(lineageId)) {
        lineageGroups.set(lineageId, {
          lineageId,
          lineageName: person.lineageName,
          people: []
        });
      }

      lineageGroups.get(lineageId).people.push(person);
      metadata.personToLineage[person.id] = lineageId;
    });

    // Write metadata file
    await fs.writeFile(
      './js/data/metadata.json',
      JSON.stringify(metadata, null, 2)
    );

    // Write lineage-specific files
    for (const [lineageId, lineageData] of lineageGroups) {
      await fs.writeFile(
        `./js/data/lineages/L${lineageId}.json`,
        JSON.stringify(lineageData, null, 2)
      );

      console.log(`Created L${lineageId}.json with ${lineageData.people.length} people`);
    }
  }
}

// Run if called directly
if (require.main === module) {
  const chunker = new DataChunker();
  chunker.processOriginalData().catch(console.error);
}
```

### 3. Enhanced Navigation Component

#### Critical Navigation Problems Fixed
- **Stranded Users:** Legacy pages only show "Home |" - users can't navigate to family
- **No Context:** Users don't know which lineage they're exploring
- **Missing Features:** No search access, breadcrumbs, or family navigation from person pages

#### Enhanced NavigationComponent Implementation
```javascript
// components/navigation.js
import BaseComponent from '../core/base-component.js';

class NavigationComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.currentPage = options.currentPage || this.detectCurrentPage();
    this.currentLineage = options.currentLineage || this.detectCurrentLineage();
    this.dataManager = options.dataManager || new DataManager();
    this.recentPages = this.loadRecentPages();
  }

  async render() {
    // Check if navigation already exists to avoid duplicate injection
    if (document.querySelector('.enhanced-nav')) {
      return;
    }

    const navHtml = await this.generateNavigationHTML();
    this.injectNavigation(navHtml);
    await this.enhanceWithFamilyContext();
  }

  async generateNavigationHTML() {
    const breadcrumbs = await this.generateBreadcrumbs();
    const familyNav = await this.generateFamilyNavigation();

    return `
      <nav class="enhanced-nav" role="navigation" aria-label="Main navigation">
        <!-- Primary Navigation -->
        <div class="primary-nav">
          <div class="nav-brand">
            <a href="/auntruth/new/" class="brand-link">AuntieRuth.com</a>
          </div>

          <div class="nav-controls ${this.mobile ? 'mobile' : 'desktop'}">
            ${this.mobile ? this.generateMobileMenu() : this.generateDesktopMenu()}
          </div>
        </div>

        <!-- Breadcrumb Navigation -->
        ${breadcrumbs ? `<div class="breadcrumb-nav">${breadcrumbs}</div>` : ''}

        <!-- Family-specific Navigation (for person pages) -->
        ${familyNav ? `<div class="family-nav">${familyNav}</div>` : ''}
      </nav>
    `;
  }

  async generateBreadcrumbs() {
    if (this.currentPage.type === 'index') return null;

    let breadcrumbs = '<nav class="breadcrumbs" aria-label="Breadcrumb">';
    breadcrumbs += '<a href="/auntruth/new/">Home</a>';

    if (this.currentLineage) {
      breadcrumbs += ' > ';
      breadcrumbs += `<a href="/auntruth/new/htm/L${this.currentLineage.number}/">${this.currentLineage.name}</a>`;
    }

    if (this.currentPage.type === 'person' && this.currentPage.title) {
      breadcrumbs += ' > ';
      breadcrumbs += `<span class="current-page">${this.currentPage.title}</span>`;
    }

    breadcrumbs += '</nav>';
    return breadcrumbs;
  }

  async generateFamilyNavigation() {
    if (this.currentPage.type !== 'person') return null;

    try {
      const personData = await this.dataManager.getPersonData(this.currentPage.pageId);
      if (!personData) return null;

      let familyNav = '<div class="family-navigation">';

      // Parents
      if (personData.father || personData.mother) {
        familyNav += '<div class="family-group">';
        familyNav += '<span class="family-label">Parents:</span>';
        if (personData.father) {
          const fatherLink = this.extractPersonLink(personData.father);
          if (fatherLink) {
            familyNav += `<a href="${fatherLink.url}" class="family-link">${fatherLink.name}</a>`;
          }
        }
        if (personData.mother) {
          const motherLink = this.extractPersonLink(personData.mother);
          if (motherLink) {
            familyNav += `<a href="${motherLink.url}" class="family-link">${motherLink.name}</a>`;
          }
        }
        familyNav += '</div>';
      }

      // Spouse(s)
      if (personData.spouse || personData.spouse2 || personData.spouse3 || personData.spouse4) {
        familyNav += '<div class="family-group">';
        familyNav += '<span class="family-label">Spouse(s):</span>';

        [personData.spouse, personData.spouse2, personData.spouse3, personData.spouse4]
          .filter(spouse => spouse && spouse.trim())
          .forEach(spouse => {
            const spouseLink = this.extractPersonLink(spouse);
            if (spouseLink) {
              familyNav += `<a href="${spouseLink.url}" class="family-link">${spouseLink.name}</a>`;
            }
          });
        familyNav += '</div>';
      }

      // Photos link
      const photoLink = `/auntruth/new/htm/L${this.currentLineage.number}/THF${this.currentPage.pageId}.htm`;
      familyNav += `<div class="family-group">`;
      familyNav += `<a href="${photoLink}" class="family-link photos-link">View Photos</a>`;
      familyNav += '</div>';

      familyNav += '</div>';
      return familyNav;

    } catch (error) {
      console.error('Failed to generate family navigation:', error);
      return null;
    }
  }

  extractPersonLink(familyMember) {
    if (!familyMember || !familyMember.includes('[')) return null;

    // Parse format: "Name [Lineage]" to extract lineage and construct URL
    const match = familyMember.match(/^(.+?)\s*\[(.+?)\]$/);
    if (!match) return null;

    const [, name, lineageInfo] = match;
    // This is simplified - in practice, you'd need to look up the person ID
    // For now, return the name for display
    return { name: name.trim(), url: '#' }; // TODO: Implement proper person ID lookup
  }

  generateMobileMenu() {
    return `
      <button class="mobile-menu-toggle" aria-expanded="false" aria-controls="mobile-menu">
        <span class="sr-only">Toggle navigation</span>
        <span class="menu-icon"></span>
      </button>
      <div class="mobile-menu" id="mobile-menu" hidden>
        <a href="/auntruth/new/" class="menu-item">Home</a>
        <a href="/auntruth/new/search/" class="menu-item">Search</a>
        <div class="lineage-menu">
          <span class="menu-label">Lineages:</span>
          ${this.generateLineageLinks()}
        </div>
      </div>
    `;
  }

  generateDesktopMenu() {
    return `
      <div class="desktop-menu">
        <a href="/auntruth/new/" class="menu-item">Home</a>
        <a href="/auntruth/new/search/" class="menu-item">Search</a>
        <div class="lineage-dropdown">
          <button class="dropdown-toggle" aria-expanded="false">
            Lineages <span class="dropdown-arrow">▼</span>
          </button>
          <div class="dropdown-menu" hidden>
            ${this.generateLineageLinks()}
          </div>
        </div>
      </div>
    `;
  }

  generateLineageLinks() {
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

    return lineages.map(lineage =>
      `<a href="/auntruth/new/htm/L${lineage.id}/" class="lineage-link ${this.currentLineage?.number === lineage.id ? 'current' : ''}">${lineage.name}</a>`
    ).join('');
  }

  injectNavigation(navHtml) {
    // Find the best insertion point
    const body = document.body;
    const existingNav = body.querySelector('nav');

    if (existingNav) {
      existingNav.outerHTML = navHtml;
    } else {
      body.insertAdjacentHTML('afterbegin', navHtml);
    }

    // Ensure body has proper padding for fixed navigation
    document.body.style.paddingTop = this.mobile ? '120px' : '80px';
  }

  attachEventListeners() {
    // Mobile menu toggle
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (mobileToggle && mobileMenu) {
      mobileToggle.addEventListener('click', () => {
        const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
        mobileToggle.setAttribute('aria-expanded', !expanded);
        mobileMenu.hidden = expanded;
      });
    }

    // Desktop dropdown
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownToggle && dropdownMenu) {
      dropdownToggle.addEventListener('click', () => {
        const expanded = dropdownToggle.getAttribute('aria-expanded') === 'true';
        dropdownToggle.setAttribute('aria-expanded', !expanded);
        dropdownMenu.hidden = expanded;
      });

      // Close on outside click
      document.addEventListener('click', (e) => {
        if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
          dropdownToggle.setAttribute('aria-expanded', 'false');
          dropdownMenu.hidden = true;
        }
      });
    }
  }

  detectCurrentPage() {
    const path = window.location.pathname;
    const filename = path.split('/').pop() || 'index.html';

    let pageType = 'unknown';
    let pageId = null;
    let title = document.title || '';

    if (filename.startsWith('XF')) {
      pageType = 'person';
      pageId = filename.replace('.htm', '').replace('XF', '');
    } else if (filename.startsWith('XI')) {
      pageType = 'image';
      pageId = filename.replace('.htm', '').replace('XI', '');
    } else if (filename.startsWith('THF')) {
      pageType = 'thumbnail';
      pageId = filename.replace('.htm', '').replace('THF', '');
    } else if (filename === 'index.htm' || filename === 'index.html') {
      pageType = 'index';
    }

    return {
      path,
      filename,
      type: pageType,
      pageId,
      title: title.replace('<br>AuntieRuth.com', '').replace('AuntieRuth.com', '').trim(),
      url: window.location.href
    };
  }

  detectCurrentLineage() {
    const path = window.location.pathname;
    const lineageMatch = path.match(/\/L(\d+)\//);

    if (lineageMatch) {
      const lineageNumber = lineageMatch[1];
      const lineageNames = {
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
        number: lineageNumber,
        name: lineageNames[lineageNumber] || `Lineage ${lineageNumber}`,
        path: `/auntruth/new/htm/L${lineageNumber}/`
      };
    }

    return null;
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
}

export default NavigationComponent;
```

### 4. Mobile-First Responsive CSS Framework

#### Enhanced Mobile-First CSS Architecture
```css
/* css/foundation.css - Mobile-first responsive framework */

/* Reset and base styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Mobile-first typography */
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

  /* Colors */
  --color-primary: #0066cc;
  --color-secondary: #666;
  --color-background: #C1CFBA;
  --color-surface: #fff;
  --color-text: #333;
  --color-link: #0000FF;

  /* Touch targets */
  --touch-target-min: 44px;
}

body {
  font-family: Verdana, Arial, sans-serif;
  font-size: var(--font-size-base);
  line-height: 1.5;
  color: var(--color-text);
  background-color: var(--color-background);

  /* Account for fixed navigation */
  padding-top: var(--nav-height-mobile);
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) var(--space-md);
  min-height: 60px;
}

.nav-brand .brand-link {
  font-size: var(--font-size-xl);
  font-weight: bold;
  color: var(--color-primary);
  text-decoration: none;
}

/* Mobile menu styles */
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
  border-top: 1px solid #eee;
  padding: var(--space-md);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.mobile-menu .menu-item {
  display: block;
  padding: var(--space-md) var(--space-sm);
  color: var(--color-link);
  text-decoration: none;
  min-height: var(--touch-target-min);
  border-bottom: 1px solid #eee;
}

.mobile-menu .menu-item:hover,
.mobile-menu .menu-item:focus {
  background: #f5f5f5;
  text-decoration: underline;
}

/* Desktop menu - hidden on mobile */
.desktop-menu {
  display: none;
}

/* Breadcrumb Navigation */
.breadcrumb-nav {
  background: #f8f9fa;
  padding: var(--space-sm) var(--space-md);
  border-top: 1px solid #eee;
  font-size: var(--font-size-sm);
}

.breadcrumbs a {
  color: var(--color-link);
  text-decoration: none;
}

.breadcrumbs a:hover {
  text-decoration: underline;
}

.current-page {
  color: var(--color-text);
  font-weight: bold;
}

/* Family Navigation */
.family-nav {
  background: #f0f8ff;
  padding: var(--space-sm) var(--space-md);
  border-top: 1px solid #ddd;
}

.family-navigation {
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

.family-link {
  color: var(--color-link);
  text-decoration: none;
  padding: var(--space-xs) var(--space-sm);
  background: var(--color-surface);
  border: 1px solid #ddd;
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

/* Responsive table improvements */
table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-md) 0;
}

/* Convert tables to cards on mobile */
table, tbody, th, td, tr {
  display: block;
}

table {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

tr {
  border-bottom: 1px solid #eee;
  padding: var(--space-md);
  background: var(--color-surface);
}

tr:last-child {
  border-bottom: none;
}

td {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  padding: var(--space-xs) 0;
  min-height: var(--touch-target-min);
}

/* Make the first cell (label) stand out */
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

/* Links within tables */
td a {
  color: var(--color-link);
  text-decoration: none;
  word-break: break-word;
}

td a:hover,
td a:focus {
  text-decoration: underline;
}

/* Image responsiveness */
img {
  max-width: 100%;
  height: auto;
  border: 0;
}

/* Center elements properly on mobile */
center {
  display: block;
  text-align: center;
  margin: var(--space-md) 0;
}

/* Utility classes */
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

/* Responsive breakpoints */
@media (min-width: 768px) {
  body {
    padding-top: var(--nav-height-desktop);
  }

  .primary-nav {
    padding: var(--space-md) var(--space-lg);
  }

  /* Hide mobile menu, show desktop menu */
  .mobile-menu-toggle,
  .mobile-menu {
    display: none;
  }

  .desktop-menu {
    display: flex;
    align-items: center;
    gap: var(--space-lg);
  }

  .desktop-menu .menu-item {
    color: var(--color-link);
    text-decoration: none;
    padding: var(--space-sm) var(--space-md);
    min-height: var(--touch-target-min);
    display: flex;
    align-items: center;
  }

  .desktop-menu .menu-item:hover,
  .desktop-menu .menu-item:focus {
    text-decoration: underline;
  }

  /* Dropdown menu */
  .lineage-dropdown {
    position: relative;
  }

  .dropdown-toggle {
    background: none;
    border: 1px solid var(--color-secondary);
    color: var(--color-link);
    padding: var(--space-sm) var(--space-md);
    border-radius: 4px;
    cursor: pointer;
    min-height: var(--touch-target-min);
    display: flex;
    align-items: center;
    gap: var(--space-xs);
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--color-surface);
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    min-width: 200px;
    z-index: 1001;
  }

  .lineage-link {
    display: block;
    padding: var(--space-sm) var(--space-md);
    color: var(--color-link);
    text-decoration: none;
    border-bottom: 1px solid #eee;
  }

  .lineage-link:last-child {
    border-bottom: none;
  }

  .lineage-link:hover,
  .lineage-link:focus {
    background: #f5f5f5;
    text-decoration: underline;
  }

  .lineage-link.current {
    background: #e3f2fd;
    font-weight: bold;
  }

  /* Family navigation horizontal on desktop */
  .family-navigation {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .family-group {
    flex-direction: row;
  }

  /* Restore table layout on desktop */
  table, tbody, th, td, tr {
    display: table;
  }

  table { display: table; }
  tbody { display: table-row-group; }
  tr { display: table-row; }
  td { display: table-cell; }

  td {
    padding: var(--space-sm) var(--space-md);
    border-bottom: 1px solid #eee;
    vertical-align: top;
  }

  td:nth-child(1) {
    background: #f8f9fa;
    font-weight: bold;
    width: 150px;
    min-width: auto;
  }

  td:nth-child(1)::after {
    content: none;
  }
}

@media (min-width: 1024px) {
  .primary-nav {
    max-width: var(--content-max-width);
    margin: 0 auto;
  }

  .breadcrumb-nav,
  .family-nav {
    padding-left: calc((100vw - var(--content-max-width)) / 2 + var(--space-md));
    padding-right: calc((100vw - var(--content-max-width)) / 2 + var(--space-md));
  }
}

/* High contrast and accessibility improvements */
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
```

### 5. Build Pipeline for GitHub Pages

#### GitHub Actions Workflow
```yaml
# .github/workflows/build-and-deploy.yml
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

#### Build Scripts Package.json
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
    "dev": "node scripts/dev-server.js",
    "test": "node scripts/test-runner.js",
    "validate": "node scripts/validate-data.js"
  },
  "devDependencies": {
    "terser": "^5.19.0",
    "clean-css": "^5.3.2",
    "html-minifier-terser": "^7.2.0"
  }
}
```

#### Asset Optimization Script
```javascript
// scripts/optimize-assets.js
const fs = require('fs').promises;
const path = require('path');
const { minify } = require('terser');
const CleanCSS = require('clean-css');

class AssetOptimizer {
  constructor() {
    this.baseDir = './docs/new';
  }

  async optimizeAll() {
    console.log('Starting asset optimization...');

    await this.optimizeJavaScript();
    await this.optimizeCSS();
    await this.generateResourceHints();

    console.log('Asset optimization complete!');
  }

  async optimizeJavaScript() {
    const jsDir = path.join(this.baseDir, 'js');
    const files = await this.getAllJSFiles(jsDir);

    for (const file of files) {
      if (file.endsWith('.min.js')) continue; // Skip already minified

      const content = await fs.readFile(file, 'utf8');
      const result = await minify(content, {
        compress: {
          drop_console: true,
          dead_code: true
        },
        mangle: true
      });

      if (result.code) {
        const minPath = file.replace('.js', '.min.js');
        await fs.writeFile(minPath, result.code);
        console.log(`Minified: ${file} -> ${minPath}`);
      }
    }
  }

  async optimizeCSS() {
    const cssDir = path.join(this.baseDir, 'css');
    const files = await this.getAllCSSFiles(cssDir);

    const cleanCSS = new CleanCSS({
      level: 2,
      returnPromise: true
    });

    for (const file of files) {
      if (file.endsWith('.min.css')) continue;

      const content = await fs.readFile(file, 'utf8');
      const result = await cleanCSS.minify(content);

      if (result.styles) {
        const minPath = file.replace('.css', '.min.css');
        await fs.writeFile(minPath, result.styles);
        console.log(`Minified: ${file} -> ${minPath}`);
      }
    }
  }

  async generateResourceHints() {
    const hints = `
<!-- Resource hints for better performance -->
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="dns-prefetch" href="https://hagborg.github.io">
<link rel="preload" href="/auntruth/new/css/foundation.min.css" as="style">
<link rel="preload" href="/auntruth/new/js/core/app.min.js" as="script">
<link rel="preload" href="/auntruth/new/js/data/metadata.json" as="fetch" crossorigin>
`;

    await fs.writeFile(
      path.join(this.baseDir, 'includes/resource-hints.html'),
      hints.trim()
    );
  }

  async getAllJSFiles(dir) {
    const files = [];
    const items = await fs.readdir(dir, { withFileTypes: true });

    for (const item of items) {
      const fullPath = path.join(dir, item.name);
      if (item.isDirectory()) {
        files.push(...await this.getAllJSFiles(fullPath));
      } else if (item.name.endsWith('.js') && !item.name.endsWith('.min.js')) {
        files.push(fullPath);
      }
    }

    return files;
  }

  async getAllCSSFiles(dir) {
    const files = [];
    const items = await fs.readdir(dir, { withFileTypes: true });

    for (const item of items) {
      const fullPath = path.join(dir, item.name);
      if (item.isDirectory()) {
        files.push(...await this.getAllCSSFiles(fullPath));
      } else if (item.name.endsWith('.css') && !item.name.endsWith('.min.css')) {
        files.push(fullPath);
      }
    }

    return files;
  }
}

if (require.main === module) {
  const optimizer = new AssetOptimizer();
  optimizer.optimizeAll().catch(console.error);
}
```

## Success Criteria

### Functional Requirements
1. **Navigation Fixed:** All person pages have functional navigation to family members and lineages
2. **Data Optimized:** Site loads efficiently with chunked data instead of single large file
3. **Mobile Responsive:** All genealogy pages work properly on mobile devices
4. **Component Architecture:** Foundation established for all future feature development
5. **Build Pipeline:** Automated optimization and deployment for GitHub Pages

### Performance Metrics
1. **Mobile Page Load:** < 2 seconds on 3G connection
2. **Data Loading:** Initial site metadata loads within 500ms
3. **Navigation Response:** Enhanced navigation responds within 100ms
4. **Memory Usage:** Efficient caching prevents memory bloat on mobile
5. **Touch Targets:** All interactive elements meet 44px minimum

### User Experience Validation
1. **Navigation Success:** Users can navigate between family members without getting lost
2. **Mobile Usability:** Genealogy research possible on mobile devices
3. **Progressive Enhancement:** Site works without JavaScript, enhanced with it
4. **Backward Compatibility:** All existing URLs continue working
5. **Accessibility:** Navigation meets WCAG guidelines

## Testing Plan

### Navigation Testing
1. Test navigation injection on sample pages from each lineage (L0-L9)
2. Verify breadcrumb generation for different page types
3. Test family navigation with various relationship patterns
4. Confirm mobile menu functionality across devices

### Performance Testing
1. Measure page load times with chunked vs original data structure
2. Test memory usage during extended browsing sessions
3. Validate mobile performance on actual devices
4. Confirm CDN caching effectiveness

### Cross-Browser Testing
1. Test component functionality across Chrome, Firefox, Safari, Edge
2. Verify mobile experience on iOS Safari and Chrome Mobile
3. Test progressive enhancement with JavaScript disabled
4. Validate accessibility with screen readers

### Data Integrity Testing
1. Verify all 2,985 people accessible after data chunking
2. Test lineage data loading and caching
3. Confirm family relationships preserved across chunks
4. Validate metadata accuracy and completeness

## Deployment Instructions

### Prerequisites
1. Node.js 18+ installed
2. GitHub repository with Pages enabled
3. Access to repository Actions settings

### Deployment Steps
1. **Setup Build Environment:**
   ```bash
   npm install
   mkdir -p docs/new/js/data/lineages
   mkdir -p docs/new/js/data/indices
   ```

2. **Build Optimized Data Structure:**
   ```bash
   npm run build:data-chunks
   npm run build:search-indices
   ```

3. **Optimize Assets:**
   ```bash
   npm run build:optimize
   ```

4. **Test Locally:**
   ```bash
   npm run dev
   # Verify navigation works on localhost:8000/auntruth/new/
   ```

5. **Deploy to GitHub Pages:**
   ```bash
   git add docs/
   git commit -m "Phase 1: Foundation architecture implementation"
   git push origin main
   # GitHub Actions will automatically deploy
   ```

6. **Verify Deployment:**
   - Check https://hagborg.github.io/auntruth/new/
   - Test navigation on person pages
   - Verify mobile responsiveness
   - Confirm data loading works correctly

### Rollback Plan
If issues arise:
1. Revert to previous commit: `git revert HEAD`
2. Original data.json remains as fallback
3. GitHub Pages will deploy previous working version
4. All legacy URLs continue working unchanged

## Phase 1 Completion Checklist

- [ ] Component architecture implemented with BaseComponent class
- [ ] DataManager class created with lineage-based chunking
- [ ] Enhanced NavigationComponent fixes navigation crisis
- [ ] Mobile-first responsive CSS framework implemented
- [ ] Build pipeline created and GitHub Actions configured
- [ ] All 2,985 people accessible through new data structure
- [ ] Navigation works on sample pages from each lineage
- [ ] Mobile experience significantly improved
- [ ] Performance metrics meet requirements
- [ ] Backward compatibility maintained - all existing URLs work
- [ ] Progressive enhancement verified - works without JavaScript
- [ ] Cross-browser testing completed
- [ ] Documentation updated with new architecture

---

**Phase 1 Completion Note:** This phase establishes the architectural foundation that enables all subsequent UX improvements. The component system, optimized data structure, enhanced navigation, and mobile responsiveness provide the essential infrastructure for Phase 2 and Phase 3 feature development.