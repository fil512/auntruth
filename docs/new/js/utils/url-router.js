import DataManager from '../core/data-manager.js';

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
    this.patternRedirects = [];
    this.history = [];
    this.initialized = false;
    this.dataManager = new DataManager();

    // Route handler context
    this.components = {};
    this.pageCallbacks = new Map();
  }

  init() {
    if (this.initialized) return;

    this.setupRoutes();
    this.setupLegacyRedirects();
    this.handleInitialRoute();
    this.setupEventListeners();

    this.initialized = true;
    console.log('URL Router initialized');
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

    // Pattern: genealogy index pages
    this.addPatternRedirect(
      /^\/auntruth\/new\/htm\/index\.htm$/,
      () => '/'
    );

    // Pattern: search pages with legacy parameters
    this.addPatternRedirect(
      /^\/auntruth\/new\/htm\/.*search.*$/,
      () => '/search'
    );
  }

  addRoute(pattern, handler) {
    const regex = this.patternToRegex(pattern);
    this.routes.set(pattern, { regex, handler, pattern });
  }

  addPatternRedirect(pattern, handler) {
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
    console.log('Handling initial route:', currentPath);

    // Check for legacy URL that needs redirect
    const modernURL = await this.resolveLegacyURL(currentPath);
    if (modernURL && modernURL !== currentPath) {
      console.log('Redirecting legacy URL:', currentPath, '→', modernURL);
      this.navigate(modernURL, true); // Replace history entry
      return;
    }

    // Handle modern URL
    await this.handleRoute(currentPath);
  }

  async resolveLegacyURL(legacyPath) {
    // Direct mapping first
    if (this.legacyRedirects.has(legacyPath)) {
      return this.legacyRedirects.get(legacyPath);
    }

    // Pattern-based redirects
    for (const redirect of this.patternRedirects) {
      const matches = legacyPath.match(redirect.pattern);
      if (matches) {
        try {
          const result = await redirect.handler(matches);
          if (result) {
            // Cache this redirect for future use
            this.legacyRedirects.set(legacyPath, result);
            return result;
          }
        } catch (error) {
          console.error('Error in pattern redirect:', error);
        }
      }
    }

    return null;
  }

  async generatePersonSlugURL(personId, lineageId) {
    try {
      const person = await this.dataManager.getPersonData(personId);

      if (person) {
        const slug = this.generatePersonSlug(person.name, personId);
        return `/person/${slug}`;
      }
    } catch (error) {
      console.error('Error generating person slug URL:', error);
    }

    // Fallback to numeric ID
    return `/person/${personId}`;
  }

  generatePersonSlug(personName, personId) {
    if (!personName) return personId;

    const slug = personName
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
      .replace(/\s+/g, '-')         // Replace spaces with hyphens
      .replace(/-+/g, '-')          // Collapse multiple hyphens
      .replace(/^-|-$/g, '');       // Remove leading/trailing hyphens

    return slug ? `${slug}-${personId}` : personId;
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

  async handleRoute(path) {
    console.log('Handling route:', path);

    // Find matching route
    for (const [pattern, route] of this.routes) {
      const matches = path.match(route.regex);
      if (matches) {
        const params = this.extractParams(pattern, matches);
        this.currentRoute = { pattern, path, params };

        try {
          await route.handler(params, path);
          this.addToHistory(path, params);
          return true;
        } catch (error) {
          console.error('Route handler error:', error);
          await this.handleNotFound(path);
          return false;
        }
      }
    }

    await this.handleNotFound(path);
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
             !href.includes('.htm') && // Skip legacy .htm files
             !href.includes('.html') &&
             !href.includes('mailto:') &&
             !href.includes('tel:');
    } catch {
      return false;
    }
  }

  addToHistory(path, params) {
    this.history.unshift({ path, params, timestamp: Date.now() });

    // Keep history size reasonable
    if (this.history.length > 50) {
      this.history = this.history.slice(0, 50);
    }
  }

  // Route Handlers
  async handleHomePage(params, path) {
    console.log('Loading home page');

    document.title = 'AuntieRuth.com - Family Genealogy';
    this.updateMetaTags({
      title: 'AuntieRuth.com - Family Genealogy',
      description: 'Explore the rich family history and genealogy of the Hagborg, Nelson, Pringle-Hambley and related families.',
      type: 'website',
      url: window.location.href
    });

    this.updateBreadcrumbs([
      { name: 'Home', path: '/' }
    ]);

    await this.loadPageComponents(['search', 'navigation']);
  }

  async handlePersonPage(params, path) {
    const { slug } = params;
    const personId = this.extractPersonIdFromSlug(slug);

    console.log('Loading person page for:', slug, personId);

    try {
      const person = await this.dataManager.getPersonData(personId);

      if (person) {
        document.title = `${person.name} - AuntieRuth.com`;

        this.updateMetaTags({
          title: `${person.name} - AuntieRuth.com`,
          description: `Family information for ${person.name}${person.birthDate ? `, born ${person.birthDate}` : ''}${person.lineageName ? ` of the ${person.lineageName} lineage` : ''}.`,
          type: 'profile',
          url: window.location.href
        });

        this.updateBreadcrumbs([
          { name: 'Home', path: '/' },
          { name: person.lineageName, path: this.generateLineageURL(person.lineage) },
          { name: person.name, path: path }
        ]);

        await this.loadPageComponents(['relationship-navigator', 'timeline']);

        // Notify components about selected person
        document.dispatchEvent(new CustomEvent('router-person-selected', {
          detail: { personId, person }
        }));

      } else {
        await this.handleNotFound(path);
      }
    } catch (error) {
      console.error('Error loading person page:', error);
      await this.handleNotFound(path);
    }
  }

  async handlePersonSection(params, path) {
    const { slug, section } = params;
    const personId = this.extractPersonIdFromSlug(slug);

    console.log('Loading person section:', slug, section);

    try {
      const person = await this.dataManager.getPersonData(personId);

      if (person) {
        document.title = `${person.name} - ${section.charAt(0).toUpperCase() + section.slice(1)} - AuntieRuth.com`;

        await this.handlePersonPage({ slug }, path.replace(`/${section}`, ''));

        // Load section-specific components
        if (section === 'photos') {
          await this.loadPageComponents(['photo-gallery']);
        } else if (section === 'timeline') {
          await this.loadPageComponents(['timeline']);
        }

      } else {
        await this.handleNotFound(path);
      }
    } catch (error) {
      console.error('Error loading person section:', error);
      await this.handleNotFound(path);
    }
  }

  async handleSearchPage(params, path) {
    console.log('Loading search page');

    document.title = 'Search - AuntieRuth.com';
    this.updateMetaTags({
      title: 'Search - AuntieRuth.com',
      description: 'Search the family genealogy database for people, places, and events.',
      type: 'website',
      url: window.location.href
    });

    this.updateBreadcrumbs([
      { name: 'Home', path: '/' },
      { name: 'Search', path: '/search' }
    ]);

    await this.loadPageComponents(['enhanced-search']);
  }

  async handleSearchWithQuery(params, path) {
    const { query } = params;
    console.log('Loading search with query:', query);

    await this.handleSearchPage(params, path);

    // Trigger search with query
    document.dispatchEvent(new CustomEvent('router-search-requested', {
      detail: { query: decodeURIComponent(query) }
    }));
  }

  async handleFamilyTreePage(params, path) {
    console.log('Loading family tree page');

    document.title = 'Family Tree - AuntieRuth.com';
    this.updateMetaTags({
      title: 'Family Tree - AuntieRuth.com',
      description: 'Interactive family tree visualization showing family relationships across generations.',
      type: 'website',
      url: window.location.href
    });

    this.updateBreadcrumbs([
      { name: 'Home', path: '/' },
      { name: 'Family Tree', path: '/family-tree' }
    ]);

    await this.loadPageComponents(['family-tree', 'relationship-navigator']);
  }

  async handleFamilyTreePerson(params, path) {
    const { person } = params;
    const personId = this.extractPersonIdFromSlug(person);

    console.log('Loading family tree focused on:', person, personId);

    await this.handleFamilyTreePage(params, path);

    // Focus tree on person
    document.dispatchEvent(new CustomEvent('router-tree-focus-requested', {
      detail: { personId }
    }));
  }

  async handleTimelinePage(params, path) {
    console.log('Loading timeline page');

    document.title = 'Timeline - AuntieRuth.com';
    this.updateMetaTags({
      title: 'Timeline - AuntieRuth.com',
      description: 'Chronological timeline of family events and historical context.',
      type: 'website',
      url: window.location.href
    });

    this.updateBreadcrumbs([
      { name: 'Home', path: '/' },
      { name: 'Timeline', path: '/timeline' }
    ]);

    await this.loadPageComponents(['timeline', 'relationship-navigator']);
  }

  async handleTimelinePeriod(params, path) {
    const { period } = params;
    console.log('Loading timeline for period:', period);

    await this.handleTimelinePage(params, path);

    // Focus timeline on period
    document.dispatchEvent(new CustomEvent('router-timeline-period-requested', {
      detail: { period }
    }));
  }

  async handleLineagePage(params, path) {
    const { lineageName } = params;
    console.log('Loading lineage page:', lineageName);

    document.title = `${lineageName} Lineage - AuntieRuth.com`;
    this.updateMetaTags({
      title: `${lineageName} Lineage - AuntieRuth.com`,
      description: `Genealogy information for the ${lineageName} family lineage.`,
      type: 'website',
      url: window.location.href
    });

    this.updateBreadcrumbs([
      { name: 'Home', path: '/' },
      { name: `${lineageName} Lineage`, path: path }
    ]);

    await this.loadPageComponents(['enhanced-search', 'family-tree']);
  }

  async handleRelationshipPage(params, path) {
    const { person1, person2 } = params;
    console.log('Loading relationship page:', person1, '→', person2);

    document.title = `Relationship Explorer - AuntieRuth.com`;
    await this.loadPageComponents(['relationship-navigator']);
  }

  async handleNotFound(path) {
    console.log('404 - Page not found:', path);

    document.title = 'Page Not Found - AuntieRuth.com';
    this.updateMetaTags({
      title: 'Page Not Found - AuntieRuth.com',
      description: 'The requested page could not be found.',
      type: 'website',
      url: window.location.href
    });

    // Try to suggest alternatives
    const suggestions = await this.generateSuggestions(path);

    // Show 404 page with suggestions
    this.show404Page(path, suggestions);
  }

  async generateSuggestions(path) {
    // Simple suggestion algorithm
    const suggestions = [];

    // Check if it looks like a person page
    if (path.includes('XF') || path.includes('THF')) {
      suggestions.push({
        text: 'Try using the search to find people',
        url: '/search'
      });
    }

    // Add general navigation suggestions
    suggestions.push(
      { text: 'Go to Home Page', url: '/' },
      { text: 'Browse Family Tree', url: '/family-tree' },
      { text: 'View Timeline', url: '/timeline' },
      { text: 'Search the Database', url: '/search' }
    );

    return suggestions;
  }

  show404Page(path, suggestions) {
    const content = `
      <div class="not-found-page">
        <h1>Page Not Found</h1>
        <p>The page <code>${path}</code> could not be found.</p>

        ${suggestions.length > 0 ? `
          <h3>Suggestions:</h3>
          <ul>
            ${suggestions.map(s => `<li><a href="${s.url}">${s.text}</a></li>`).join('')}
          </ul>
        ` : ''}
      </div>
    `;

    const main = document.querySelector('main, .main-content, body');
    if (main) {
      main.innerHTML = content;
    }
  }

  extractPersonIdFromSlug(slug) {
    // Extract person ID from slug (format: name-123 or just 123)
    const match = slug.match(/-(\d+)$/) || slug.match(/^(\d+)$/);
    return match ? match[1] : slug;
  }

  updateMetaTags(meta) {
    // Update page title
    if (meta.title) {
      document.title = meta.title;
    }

    // Update meta description
    this.updateMetaTag('description', meta.description);

    // Open Graph tags
    this.updateMetaProperty('og:title', meta.title);
    this.updateMetaProperty('og:description', meta.description);
    this.updateMetaProperty('og:type', meta.type || 'website');
    this.updateMetaProperty('og:url', meta.url);

    // Twitter Card tags
    this.updateMetaName('twitter:card', 'summary');
    this.updateMetaName('twitter:title', meta.title);
    this.updateMetaName('twitter:description', meta.description);
  }

  updateMetaTag(name, content) {
    if (!content) return;

    let tag = document.querySelector(`meta[name="${name}"]`);
    if (!tag) {
      tag = document.createElement('meta');
      tag.name = name;
      document.head.appendChild(tag);
    }
    tag.content = content;
  }

  updateMetaProperty(property, content) {
    if (!content) return;

    let tag = document.querySelector(`meta[property="${property}"]`);
    if (!tag) {
      tag = document.createElement('meta');
      tag.setAttribute('property', property);
      document.head.appendChild(tag);
    }
    tag.content = content;
  }

  updateMetaName(name, content) {
    if (!content) return;

    let tag = document.querySelector(`meta[name="${name}"]`);
    if (!tag) {
      tag = document.createElement('meta');
      tag.name = name;
      document.head.appendChild(tag);
    }
    tag.content = content;
  }

  updateBreadcrumbs(breadcrumbs) {
    // Create or update breadcrumb navigation
    let breadcrumbNav = document.querySelector('.breadcrumb-nav');
    if (!breadcrumbNav) {
      breadcrumbNav = document.createElement('nav');
      breadcrumbNav.className = 'breadcrumb-nav';
      breadcrumbNav.setAttribute('aria-label', 'Breadcrumb');

      const main = document.querySelector('main, .main-content, body');
      if (main) {
        main.insertAdjacentElement('afterbegin', breadcrumbNav);
      }
    }

    const breadcrumbHTML = `
      <ol class="breadcrumb-list">
        ${breadcrumbs.map((crumb, index) => `
          <li class="breadcrumb-item">
            ${index === breadcrumbs.length - 1
              ? `<span aria-current="page">${crumb.name}</span>`
              : `<a href="${crumb.path}">${crumb.name}</a>`
            }
          </li>
        `).join('')}
      </ol>
    `;

    breadcrumbNav.innerHTML = breadcrumbHTML;
  }

  async loadPageComponents(componentNames) {
    // Placeholder for loading page-specific components
    console.log('Loading page components:', componentNames);

    // Dispatch event for integration layer
    document.dispatchEvent(new CustomEvent('router-components-requested', {
      detail: { components: componentNames, route: this.currentRoute }
    }));
  }

  // Public API methods
  getCurrentRoute() {
    return this.currentRoute;
  }

  getHistory() {
    return this.history;
  }

  generatePersonURL(person) {
    const slug = this.generatePersonSlug(person.name, person.id);
    return `/person/${slug}`;
  }

  generateSearchURL(query) {
    return `/search/${encodeURIComponent(query)}`;
  }
}

// Global router instance
const router = new URLRouter();

// Initialize when DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => router.init());
} else {
  router.init();
}

// Make available globally
window.URLRouter = router;

export default router;