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
        this.toggleSidebar = this.toggleSidebar.bind(this);
        this.closeSidebar = this.closeSidebar.bind(this);
        this.handleOverlayClick = this.handleOverlayClick.bind(this);
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

        this.injectNavigation();
        this.highlightCurrentSection();
        this.setupEventListeners();
        this.setupMobileMenu();
        this.populateLineageNavigation();
        this.populateQuickLinks();
        this.updateRecentPages();
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
                '0': 'Base',
                '1': 'Hagborg-Hansson',
                '2': 'Nelson',
                '3': 'Lineage 3',
                '4': 'Lineage 4',
                '5': 'Lineage 5',
                '6': 'Lineage 6',
                '7': 'Lineage 7',
                '8': 'Lineage 8',
                '9': 'Lineage 9'
            };

            return {
                number: lineageNumber,
                name: lineageNames[lineageNumber] || `Lineage ${lineageNumber}`,
                path: `/auntruth/new/htm/L${lineageNumber}/`
            };
        }

        return null;
    }

    injectNavigation() {
        // Create and inject the top navigation
        const topNav = this.createTopNavigation();
        const sidebar = this.createSidebar();
        const overlay = this.createSidebarOverlay();

        // Insert at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', topNav);
        document.body.insertAdjacentHTML('afterbegin', sidebar);
        document.body.insertAdjacentHTML('afterbegin', overlay);

        // Wrap main content if not already wrapped
        const existingContent = document.body.innerHTML;
        if (!document.querySelector('.main-content')) {
            // Find the main content (everything after navigation)
            const navEnd = existingContent.indexOf('</nav>') + 6;
            const sidebarEnd = existingContent.lastIndexOf('</aside>') + 8;
            const overlayEnd = existingContent.lastIndexOf('sidebar-overlay') + 20;

            let contentStart = Math.max(navEnd, sidebarEnd, overlayEnd);
            const beforeContent = existingContent.substring(0, contentStart);
            const mainContent = existingContent.substring(contentStart);

            document.body.innerHTML = beforeContent +
                '<main class="main-content" role="main">' +
                mainContent +
                '</main>';
        }

        this.isNavigationInjected = true;
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
                        <li><a href="#" id="browse-trigger" aria-haspopup="true">Browse Lineages</a></li>
                        <li><a href="#" id="search-trigger" aria-haspopup="true">Search People</a></li>
                        <li><a href="${basePath}timeline.html">Timeline</a></li>
                        <li><a href="${basePath}about.html">About</a></li>
                        <li><a href="/auntruth/htm/">Original Site</a></li>
                    </ul>
                    <button class="mobile-menu-toggle" aria-label="Toggle navigation menu" aria-expanded="false">
                        ☰
                    </button>
                </div>
            </nav>
        `;
    }

    createSidebar() {
        return `
            <aside class="sidebar" role="complementary" aria-label="Secondary navigation">
                <div class="sidebar-header">
                    <h3>Navigation</h3>
                    <button class="sidebar-close" aria-label="Close sidebar">×</button>
                </div>
                <div class="sidebar-content">
                    <section class="lineage-tree">
                        <h4>Current Lineage</h4>
                        <nav id="lineage-nav" aria-label="Lineage navigation">
                            <!-- Dynamically populated -->
                        </nav>
                    </section>
                    <section class="quick-links">
                        <h4>Quick Links</h4>
                        <ul id="related-people" aria-label="Related people">
                            <!-- Dynamically populated -->
                        </ul>
                    </section>
                    <section class="recent-history">
                        <h4>Recently Viewed</h4>
                        <ul id="recent-pages" aria-label="Recently viewed pages">
                            <!-- Local storage based -->
                        </ul>
                    </section>
                </div>
            </aside>
        `;
    }

    createSidebarOverlay() {
        return `<div class="sidebar-overlay" aria-hidden="true"></div>`;
    }

    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', this.handleResize);

        // Mobile menu toggle
        const menuToggle = document.querySelector('.mobile-menu-toggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', this.toggleSidebar);
        }

        // Sidebar close button
        const sidebarClose = document.querySelector('.sidebar-close');
        if (sidebarClose) {
            sidebarClose.addEventListener('click', this.closeSidebar);
        }

        // Overlay click to close sidebar
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) {
            overlay.addEventListener('click', this.handleOverlayClick);
        }

        // Keyboard navigation
        document.addEventListener('keydown', this.handleKeydown);

        // Browse trigger (opens sidebar with lineage focus)
        const browseTriger = document.getElementById('browse-trigger');
        if (browseTriger) {
            browseTriger.addEventListener('click', (e) => {
                e.preventDefault();
                this.openSidebar();
                // Focus on lineage navigation
                const lineageNav = document.getElementById('lineage-nav');
                if (lineageNav) {
                    const firstLink = lineageNav.querySelector('a');
                    if (firstLink) firstLink.focus();
                }
            });
        }

        // Search trigger (focus search if visible, or show search)
        const searchTrigger = document.getElementById('search-trigger');
        if (searchTrigger) {
            searchTrigger.addEventListener('click', (e) => {
                e.preventDefault();
                const searchInput = document.getElementById('people-search');
                if (searchInput) {
                    searchInput.focus();
                } else {
                    // TODO: Show search interface
                    console.log('Search interface not yet implemented');
                }
            });
        }
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
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');

        if (!this.isMobile) {
            // Desktop mode - close sidebar and remove mobile classes
            if (sidebar) sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('active');
        }
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const menuToggle = document.querySelector('.mobile-menu-toggle');

        if (sidebar && overlay) {
            const isOpen = sidebar.classList.contains('open');

            if (isOpen) {
                this.closeSidebar();
            } else {
                this.openSidebar();
            }
        }
    }

    openSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const menuToggle = document.querySelector('.mobile-menu-toggle');

        if (sidebar && overlay) {
            sidebar.classList.add('open');
            overlay.classList.add('active');
            if (menuToggle) menuToggle.setAttribute('aria-expanded', 'true');

            // Trap focus in sidebar
            this.trapFocus(sidebar);
        }
    }

    closeSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const menuToggle = document.querySelector('.mobile-menu-toggle');

        if (sidebar && overlay) {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            if (menuToggle) {
                menuToggle.setAttribute('aria-expanded', 'false');
                menuToggle.focus(); // Return focus to toggle button
            }
        }
    }

    handleOverlayClick() {
        this.closeSidebar();
    }

    handleKeydown(e) {
        // Escape key closes sidebar
        if (e.key === 'Escape') {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && sidebar.classList.contains('open')) {
                this.closeSidebar();
            }
        }
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

    populateLineageNavigation() {
        const lineageNav = document.getElementById('lineage-nav');
        if (!lineageNav) return;

        const lineages = [
            { number: '0', name: 'Base', path: '/auntruth/new/htm/L0/' },
            { number: '1', name: 'Hagborg-Hansson', path: '/auntruth/new/htm/L1/' },
            { number: '2', name: 'Nelson', path: '/auntruth/new/htm/L2/' },
            { number: '3', name: 'Lineage 3', path: '/auntruth/new/htm/L3/' },
            { number: '4', name: 'Lineage 4', path: '/auntruth/new/htm/L4/' },
            { number: '5', name: 'Lineage 5', path: '/auntruth/new/htm/L5/' },
            { number: '6', name: 'Lineage 6', path: '/auntruth/new/htm/L6/' },
            { number: '7', name: 'Lineage 7', path: '/auntruth/new/htm/L7/' },
            { number: '8', name: 'Lineage 8', path: '/auntruth/new/htm/L8/' },
            { number: '9', name: 'Lineage 9', path: '/auntruth/new/htm/L9/' }
        ];

        const currentLineageNumber = this.currentLineage?.number;

        const html = `
            <ul>
                ${lineages.map(lineage => `
                    <li>
                        <a href="${lineage.path}"
                           ${lineage.number === currentLineageNumber ? 'class="current"' : ''}
                           aria-current="${lineage.number === currentLineageNumber ? 'page' : 'false'}">
                            L${lineage.number}: ${lineage.name}
                        </a>
                    </li>
                `).join('')}
            </ul>
        `;

        lineageNav.innerHTML = html;
    }

    populateQuickLinks() {
        const quickLinks = document.getElementById('related-people');
        if (!quickLinks) return;

        // TODO: This would be populated based on the current person's relationships
        // For now, provide some sample quick navigation
        const sampleLinks = [
            { name: 'Family Index', url: '/auntruth/new/htm/' },
            { name: 'Photo Timeline', url: '/auntruth/new/htm/timeline.html' },
            { name: 'Location Index', url: '/auntruth/new/htm/locations.html' }
        ];

        const html = sampleLinks.map(link => `
            <li><a href="${link.url}">${link.name}</a></li>
        `).join('');

        quickLinks.innerHTML = html;
    }

    updateRecentPages() {
        const recentContainer = document.getElementById('recent-pages');
        if (!recentContainer) return;

        const recentPages = this.loadRecentPages();

        if (recentPages.length === 0) {
            recentContainer.innerHTML = '<li><em>No recent pages</em></li>';
            return;
        }

        const html = recentPages.slice(0, 5).map(page => `
            <li>
                <a href="${page.url}" title="${page.title}">
                    ${page.title || page.filename}
                </a>
            </li>
        `).join('');

        recentContainer.innerHTML = html;
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