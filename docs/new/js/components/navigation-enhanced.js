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
            familyNav += `<a href="XF${fatherId}.htm" class="family-link">Father: ${this.extractPersonName(personData.father)}</a>`;
          }
        }

        if (personData.mother) {
          const motherId = this.extractPersonId(personData.mother);
          if (motherId) {
            familyNav += `<a href="XF${motherId}.htm" class="family-link">Mother: ${this.extractPersonName(personData.mother)}</a>`;
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

        spouses.forEach(spouse => {
          const spouseId = this.extractPersonId(spouse);
          if (spouseId) {
            const spouseName = this.extractPersonName(spouse);
            familyNav += `<a href="XF${spouseId}.htm" class="family-link">${spouseName}</a>`;
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

    const match = text.match(/\[(\d+)\]/);
    return match ? match[1] : null;
  }

  extractPersonName(text) {
    // Extract person name, removing ID brackets
    if (!text) return text;
    return text.replace(/\s*\[\d+\]\s*$/, '').trim();
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