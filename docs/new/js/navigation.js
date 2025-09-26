/**
 * Navigation Component for AuntieRuth.com Modernization
 * Progressive Enhancement Implementation
 * Provides sticky navigation, sidebar, and contextual navigation
 */

class NavigationComponent {
    constructor() {
        this.currentPage = this.detectCurrentPage();
        this.currentLineage = this.detectCurrentLineage();
        this.recentPages = this.loadRecentPages();
        this.isNavigationInjected = false;
        this.isMobile = window.innerWidth <= 768;

        // Bind methods to maintain context
        this.handleResize = this.handleResize.bind(this);
        this.handleKeydown = this.handleKeydown.bind(this);

        this.init();
    }

    init() {
        // Check if navigation is already present to avoid duplicate injection
        if (document.querySelector('.top-nav')) {
            this.isNavigationInjected = true;
            this.setupEventListeners();
            return;
        }

        // Check if we have a proper main content structure (from our fixed HTML)
        const mainContent = document.querySelector('main#main-content');
        if (mainContent) {
            // We have proper structure, inject navigation properly
            this.injectNavigationClean();
        } else {
            // Fallback to original injection method
            this.injectNavigation();
        }

        this.highlightCurrentSection();
        this.setupEventListeners();
        this.setupMobileMenu();
        this.saveCurrentPage();
    }

    detectCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';

        // Extract page type and ID
        let pageType = 'unknown';
        let pageId = null;
        let title = document.title || '';

        if (filename.startsWith('XF')) {
            pageType = 'person';
            pageId = filename.replace('.htm', '').replace('XF', '');
        } else if (filename.startsWith('THF')) {
            pageType = 'thumbnail';
            pageId = filename.replace('.htm', '').replace('THF', '');
        } else if (filename.startsWith('CX')) {
            pageType = 'context';
            pageId = filename.replace('.htm', '').replace('CX', '');
        } else if (filename === 'index.htm' || filename === 'index.html') {
            pageType = 'index';
        }

        return {
            path,
            filename,
            pageType,
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
                number: lineageNumber,
                name: lineageNames[lineageNumber] || `Lineage ${lineageNumber}`,
                path: `/auntruth/new/htm/L${lineageNumber}/`
            };
        }

        return null;
    }

    /**
     * Parse family relationships from legacy HTML table structure
     * Extracts Father, Mother, Spouse(s), Children from XF page tables
     */
    parseFamilyRelationships() {
        const listTable = document.querySelector('table#List');
        if (!listTable) return null;

        const relationships = {
            father: null,
            mother: null,
            spouses: [],
            children: [],
            thumbnails: null
        };

        const rows = listTable.querySelectorAll('tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 2) return;

            const label = cells[0].textContent.trim();
            const valueCell = cells[1];
            const link = valueCell.querySelector('a');

            if (link) {
                const linkData = {
                    name: link.textContent.replace(/\[.*?\]/g, '').trim(),
                    url: link.href,
                    lineage: this.extractLineageFromText(link.textContent)
                };

                switch (label.toLowerCase()) {
                    case 'father':
                        relationships.father = linkData;
                        break;
                    case 'mother':
                        relationships.mother = linkData;
                        break;
                    case 'spouse(1)':
                    case 'spouse(2)':
                    case 'spouse(3)':
                    case 'spouse(4)':
                        if (linkData.name) relationships.spouses.push(linkData);
                        break;
                    default:
                        if (label.startsWith('Child')) {
                            relationships.children.push(linkData);
                        }
                }
            }
        });

        // Find thumbnail link
        const thumbLink = document.querySelector('a[href*="THF"]');
        if (thumbLink) {
            relationships.thumbnails = {
                name: 'Photos',
                url: thumbLink.href
            };
        }

        return relationships;
    }

    /**
     * Extract lineage information from relationship text
     */
    extractLineageFromText(text) {
        const match = text.match(/\[(.*?)\]/);
        return match ? match[1] : null;
    }

    /**
     * Generate breadcrumb navigation based on current page context
     */
    generateBreadcrumbs() {
        const currentPage = this.currentPage;
        const currentLineage = this.currentLineage;

        const isNew = currentPage.path.includes('/new/');
        const breadcrumbs = [
            {
                name: 'Home',
                url: isNew ? '/auntruth/new/' : '/auntruth/htm/',
                active: false
            }
        ];

        // Add lineage breadcrumb
        if (currentLineage) {
            breadcrumbs.push({
                name: currentLineage.name,
                url: currentLineage.path,
                active: false
            });
        }

        // Add current page breadcrumb
        if (currentPage.pageType === 'person' && currentPage.title) {
            breadcrumbs.push({
                name: currentPage.title,
                url: currentPage.url,
                active: true
            });
        }

        return breadcrumbs;
    }

    /**
     * Create breadcrumb HTML structure
     */
    createBreadcrumbHTML(breadcrumbs) {
        if (!breadcrumbs || breadcrumbs.length <= 1) return '';

        const breadcrumbItems = breadcrumbs.map(crumb => {
            if (crumb.active) {
                return `<span class="breadcrumb-current">${crumb.name}</span>`;
            } else {
                return `<a href="${crumb.url}" class="breadcrumb-link">${crumb.name}</a>`;
            }
        }).join('<span class="breadcrumb-separator"> &gt; </span>');

        return `
            <nav class="breadcrumb-nav" aria-label="Breadcrumb navigation">
                <div class="breadcrumb-container">
                    ${breadcrumbItems}
                </div>
            </nav>
        `;
    }

    /**
     * Create family navigation bar with immediate relationships
     */
    createFamilyNavigation() {
        if (this.currentPage.pageType !== 'person') return '';

        const relationships = this.parseFamilyRelationships();
        if (!relationships) return '';

        const navItems = [];

        // Parents navigation
        const parents = [];
        if (relationships.father) parents.push(relationships.father);
        if (relationships.mother) parents.push(relationships.mother);

        if (parents.length > 0) {
            if (parents.length === 1) {
                navItems.push(`<a href="${parents[0].url}" class="family-nav-item">
                    <span class="family-nav-label">Parent:</span>
                    <span class="family-nav-name">${parents[0].name}</span>
                </a>`);
            } else {
                navItems.push(`<div class="family-nav-dropdown">
                    <span class="family-nav-label">Parents:</span>
                    <div class="family-nav-dropdown-content">
                        ${parents.map(parent =>
                            `<a href="${parent.url}" class="family-nav-dropdown-item">${parent.name}</a>`
                        ).join('')}
                    </div>
                </div>`);
            }
        }

        // Spouse navigation
        if (relationships.spouses.length > 0) {
            if (relationships.spouses.length === 1) {
                navItems.push(`<a href="${relationships.spouses[0].url}" class="family-nav-item">
                    <span class="family-nav-label">Spouse:</span>
                    <span class="family-nav-name">${relationships.spouses[0].name}</span>
                </a>`);
            } else {
                navItems.push(`<div class="family-nav-dropdown">
                    <span class="family-nav-label">Spouses:</span>
                    <div class="family-nav-dropdown-content">
                        ${relationships.spouses.map(spouse =>
                            `<a href="${spouse.url}" class="family-nav-dropdown-item">${spouse.name}</a>`
                        ).join('')}
                    </div>
                </div>`);
            }
        }

        // Children navigation
        if (relationships.children.length > 0) {
            if (relationships.children.length <= 3) {
                relationships.children.forEach(child => {
                    navItems.push(`<a href="${child.url}" class="family-nav-item">
                        <span class="family-nav-label">Child:</span>
                        <span class="family-nav-name">${child.name}</span>
                    </a>`);
                });
            } else {
                navItems.push(`<div class="family-nav-dropdown">
                    <span class="family-nav-label">Children (${relationships.children.length}):</span>
                    <div class="family-nav-dropdown-content">
                        ${relationships.children.map(child =>
                            `<a href="${child.url}" class="family-nav-dropdown-item">${child.name}</a>`
                        ).join('')}
                    </div>
                </div>`);
            }
        }

        // Photos link
        if (relationships.thumbnails) {
            navItems.push(`<a href="${relationships.thumbnails.url}" class="family-nav-item family-nav-photos">
                <span class="family-nav-label">Photos</span>
            </a>`);
        }

        if (navItems.length === 0) return '';

        return `
            <nav class="family-navigation" role="navigation" aria-label="Family navigation">
                <div class="family-nav-container">
                    ${navItems.join('')}
                </div>
            </nav>
        `;
    }

    injectNavigation() {
        // Enhanced injection for legacy pages
        const topNav = this.createTopNavigation();
        const breadcrumbs = this.createBreadcrumbHTML(this.generateBreadcrumbs());
        const familyNav = this.createFamilyNavigation();

        // Build complete navigation HTML
        const navigationHTML = topNav + breadcrumbs + familyNav;

        // Insert at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', navigationHTML);

        // Wrap main content if not already wrapped
        const existingContent = document.body.innerHTML;
        if (!document.querySelector('.main-content')) {
            // Find the main content (everything after navigation)
            const navEnd = existingContent.indexOf('</nav>');
            let contentStart = navEnd;

            // Find the last closing nav tag to account for multiple nav elements
            const allNavTags = existingContent.match(/<\/nav>/g);
            if (allNavTags && allNavTags.length > 1) {
                contentStart = existingContent.lastIndexOf('</nav>') + 6;
            } else if (navEnd !== -1) {
                contentStart = navEnd + 6;
            }

            const beforeContent = existingContent.substring(0, contentStart);
            const mainContent = existingContent.substring(contentStart);

            document.body.innerHTML = beforeContent +
                '<main class="main-content" role="main">' +
                mainContent +
                '</main>';
        }

        this.isNavigationInjected = true;
        this.setupFamilyNavigationHandlers();
    }

    injectNavigationClean() {
        // Clean injection for properly structured HTML
        const topNav = this.createTopNavigation();
        const breadcrumbs = this.createBreadcrumbHTML(this.generateBreadcrumbs());
        const familyNav = this.createFamilyNavigation();

        // Insert navigation components at the beginning of body
        const mainContent = document.querySelector('main#main-content, main.main-content');
        if (mainContent) {
            console.log('Main content found, injecting enhanced navigation...');

            // Build complete navigation HTML
            const navigationHTML = topNav + breadcrumbs + familyNav;
            document.body.insertAdjacentHTML('afterbegin', navigationHTML);

            // Scroll to show header properly positioned below navigation
            const header = mainContent.querySelector('.page-header, h1');
            if (header) {
                header.scrollIntoView({ behavior: 'instant', block: 'start' });
            }
        }

        this.isNavigationInjected = true;
        this.setupFamilyNavigationHandlers();
    }

    createTopNavigation() {
        const currentPath = this.currentPage.path;
        const isNew = currentPath.includes('/new/');
        const basePath = isNew ? '/auntruth/new/' : '/auntruth/htm/';

        return `
            <nav class="top-nav" role="navigation" aria-label="Main navigation">
                <div class="nav-container">
                    <div class="nav-brand">
                        <a href="${basePath}">AuntieRuth.com</a>
                    </div>
                    <ul class="nav-links">
                        <li><a href="${basePath}" ${currentPath === basePath ? 'class="active"' : ''}>Home</a></li>
                        <li class="nav-dropdown">
                            <a href="#" class="dropdown-toggle" aria-haspopup="true" aria-expanded="false">
                                Lineages <span class="dropdown-arrow">▼</span>
                            </a>
                            <ul class="dropdown-menu" role="menu">
                                <li><a href="${basePath}htm/L1/" role="menuitem">Hagborg-Hansson</a></li>
                                <li><a href="${basePath}htm/L2/" role="menuitem">Nelson</a></li>
                                <li><a href="${basePath}htm/L3/" role="menuitem">Pringle-Hambley</a></li>
                                <li><a href="${basePath}htm/L4/" role="menuitem">Lathrop-Lothropp</a></li>
                                <li><a href="${basePath}htm/L5/" role="menuitem">Ward</a></li>
                                <li><a href="${basePath}htm/L6/" role="menuitem">Selch-Weiss</a></li>
                                <li><a href="${basePath}htm/L7/" role="menuitem">Stebbe</a></li>
                                <li><a href="${basePath}htm/L8/" role="menuitem">Lentz</a></li>
                                <li><a href="${basePath}htm/L9/" role="menuitem">Phoenix-Rogerson</a></li>
                                <li><a href="${basePath}htm/L0/" role="menuitem">All</a></li>
                            </ul>
                        </li>
                        <li><a href="#" id="search-trigger" aria-haspopup="true">Search People</a></li>
                        <li><a href="/auntruth/htm/">Original Site</a></li>
                    </ul>
                    <button class="mobile-menu-toggle" aria-label="Toggle navigation menu" aria-expanded="false">
                        ☰
                    </button>
                </div>
            </nav>
        `;
    }


    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', this.handleResize);


        // Keyboard navigation
        document.addEventListener('keydown', this.handleKeydown);

        // Dropdown menu functionality
        this.setupDropdownMenu();


        // Search trigger (toggle search interface)
        const searchTrigger = document.getElementById('search-trigger');
        if (searchTrigger) {
            searchTrigger.addEventListener('click', (e) => {
                e.preventDefault();
                const searchContainer = document.querySelector('.search-container');
                const searchInput = document.getElementById('people-search');

                if (searchContainer) {
                    // Toggle search container visibility
                    searchContainer.classList.toggle('active');

                    // Focus search input if now visible
                    if (searchContainer.classList.contains('active') && searchInput) {
                        setTimeout(() => searchInput.focus(), 100);
                    }
                } else {
                    console.log('Search container not found');
                }
            });
        }
    }

    setupDropdownMenu() {
        const dropdownToggle = document.querySelector('.dropdown-toggle');
        const dropdownMenu = document.querySelector('.dropdown-menu');
        const navDropdown = document.querySelector('.nav-dropdown');

        if (!dropdownToggle || !dropdownMenu || !navDropdown) return;

        // Toggle dropdown on click
        dropdownToggle.addEventListener('click', (e) => {
            e.preventDefault();
            const isOpen = navDropdown.classList.contains('open');

            // Close all other dropdowns first
            document.querySelectorAll('.nav-dropdown.open').forEach(dropdown => {
                dropdown.classList.remove('open');
                const toggle = dropdown.querySelector('.dropdown-toggle');
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
            });

            if (!isOpen) {
                navDropdown.classList.add('open');
                dropdownToggle.setAttribute('aria-expanded', 'true');
                // Focus first menu item
                const firstMenuItem = dropdownMenu.querySelector('a');
                if (firstMenuItem) {
                    setTimeout(() => firstMenuItem.focus(), 100);
                }
            } else {
                navDropdown.classList.remove('open');
                dropdownToggle.setAttribute('aria-expanded', 'false');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!navDropdown.contains(e.target)) {
                navDropdown.classList.remove('open');
                dropdownToggle.setAttribute('aria-expanded', 'false');
            }
        });

        // Keyboard navigation for dropdown
        dropdownMenu.addEventListener('keydown', (e) => {
            const menuItems = dropdownMenu.querySelectorAll('a');
            const currentIndex = Array.from(menuItems).indexOf(document.activeElement);

            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    const nextIndex = (currentIndex + 1) % menuItems.length;
                    menuItems[nextIndex].focus();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    const prevIndex = currentIndex > 0 ? currentIndex - 1 : menuItems.length - 1;
                    menuItems[prevIndex].focus();
                    break;
                case 'Escape':
                    e.preventDefault();
                    navDropdown.classList.remove('open');
                    dropdownToggle.setAttribute('aria-expanded', 'false');
                    dropdownToggle.focus();
                    break;
                case 'Tab':
                    if (e.shiftKey && currentIndex === 0) {
                        // Tab backwards from first item - close dropdown
                        navDropdown.classList.remove('open');
                        dropdownToggle.setAttribute('aria-expanded', 'false');
                    } else if (!e.shiftKey && currentIndex === menuItems.length - 1) {
                        // Tab forwards from last item - close dropdown
                        navDropdown.classList.remove('open');
                        dropdownToggle.setAttribute('aria-expanded', 'false');
                    }
                    break;
            }
        });

        // Close dropdown on escape from toggle
        dropdownToggle.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                navDropdown.classList.remove('open');
                dropdownToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }

    /**
     * Setup event handlers for family navigation interactions
     */
    setupFamilyNavigationHandlers() {
        // Family navigation dropdown handlers
        const dropdowns = document.querySelectorAll('.family-nav-dropdown');
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.family-nav-label');
            const content = dropdown.querySelector('.family-nav-dropdown-content');

            if (toggle && content) {
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();

                    // Close other dropdowns
                    dropdowns.forEach(otherDropdown => {
                        if (otherDropdown !== dropdown) {
                            otherDropdown.classList.remove('active');
                        }
                    });

                    // Toggle current dropdown
                    dropdown.classList.toggle('active');
                });

                // Close on outside click
                document.addEventListener('click', (e) => {
                    if (!dropdown.contains(e.target)) {
                        dropdown.classList.remove('active');
                    }
                });
            }
        });

        // Keyboard navigation for family nav
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        });
    }

    setupMobileMenu() {
        this.updateMobileState();
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;

        if (wasMobile !== this.isMobile) {
            this.updateMobileState();
        }
    }

    updateMobileState() {
        // No sidebar to manage
    }

    handleKeydown(e) {
        // Handle general keyboard navigation
        // (sidebar functionality removed)
    }

    trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        const handleTabKey = (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        };

        element.addEventListener('keydown', handleTabKey);
        firstElement.focus();
    }

    highlightCurrentSection() {
        // Highlight current page in navigation
        const navLinks = document.querySelectorAll('.nav-links a');
        navLinks.forEach(link => {
            if (link.href === window.location.href) {
                link.classList.add('active');
            }
        });
    }


    loadRecentPages() {
        try {
            const stored = localStorage.getItem('auntieruth-recent-pages');
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            console.warn('Failed to load recent pages from localStorage:', e);
            return [];
        }
    }

    saveCurrentPage() {
        try {
            const recentPages = this.loadRecentPages();
            const currentPage = this.currentPage;

            // Remove if already exists
            const existingIndex = recentPages.findIndex(page => page.url === currentPage.url);
            if (existingIndex > -1) {
                recentPages.splice(existingIndex, 1);
            }

            // Add to beginning
            recentPages.unshift({
                url: currentPage.url,
                title: currentPage.title,
                filename: currentPage.filename,
                timestamp: Date.now()
            });

            // Keep only last 10 pages
            const trimmed = recentPages.slice(0, 10);

            localStorage.setItem('auntieruth-recent-pages', JSON.stringify(trimmed));
        } catch (e) {
            console.warn('Failed to save current page to localStorage:', e);
        }
    }
}

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're not in the original site
    if (!window.location.pathname.includes('/htm/') || window.location.pathname.includes('/new/')) {
        new NavigationComponent();
    }
});

// Export for potential use by other scripts
window.NavigationComponent = NavigationComponent;