/**
 * Search Component for AuntieRuth.com Modernization
 * Client-side search with Lunr.js integration
 * Provides autocomplete and fast search across genealogy data
 */

class SearchComponent {
    constructor() {
        this.searchIndex = null;
        this.searchData = null;
        this.searchInput = null;
        this.searchResults = null;
        this.searchFilters = null;
        this.isLoading = false;
        this.currentResults = [];
        this.selectedIndex = -1;

        // Debounce search input
        this.searchDebounce = null;
        this.debounceDelay = 150;

        // Search settings
        this.maxResults = 50;
        this.minQueryLength = 2;

        // Bind methods
        this.handleSearchInput = this.handleSearchInput.bind(this);
        this.handleKeydown = this.handleKeydown.bind(this);
        this.handleFilterChange = this.handleFilterChange.bind(this);
        this.handleResultClick = this.handleResultClick.bind(this);
        this.handleDocumentClick = this.handleDocumentClick.bind(this);

        this.init();
    }

    async init() {
        this.createSearchInterface();
        this.setupEventListeners();

        try {
            await this.loadSearchData();
            this.buildSearchIndex();
            this.enableSearch();
        } catch (error) {
            console.error('Failed to initialize search:', error);
            this.showError('Search functionality unavailable');
        }
    }

    createSearchInterface() {
        // Find existing search container or create one
        let searchContainer = document.querySelector('.search-container');

        if (!searchContainer) {
            // Create and insert search interface
            const searchHTML = this.getSearchHTML();

            // Insert after navigation or at the beginning of main content
            const mainContent = document.querySelector('.main-content, main, body');
            if (mainContent) {
                mainContent.insertAdjacentHTML('afterbegin', searchHTML);
            }
        }

        // Get references to search elements
        this.searchInput = document.getElementById('people-search');
        this.searchResults = document.getElementById('search-results');
        this.searchFilters = document.querySelectorAll('.search-filters input[type="checkbox"]');

        if (!this.searchInput) {
            console.warn('Search input not found - search functionality disabled');
            return;
        }
    }

    getSearchHTML() {
        return `
            <div class="search-container">
                <div class="search-wrapper">
                    <input type="search"
                           id="people-search"
                           placeholder="Search people, dates, locations..."
                           autocomplete="off"
                           aria-label="Search genealogy database"
                           aria-describedby="search-help"
                           disabled>
                    <div class="search-filters">
                        <label><input type="checkbox" value="name" checked> Names</label>
                        <label><input type="checkbox" value="date"> Dates</label>
                        <label><input type="checkbox" value="location"> Locations</label>
                        <label><input type="checkbox" value="lineage"> Lineage</label>
                    </div>
                    <div id="search-help" class="sr-only">
                        Use this search to find people, dates, and locations in the genealogy database.
                        Results will appear below as you type.
                    </div>
                </div>
                <div class="search-results" id="search-results" hidden aria-live="polite">
                    <!-- Search results populated here -->
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.handleSearchInput);
            this.searchInput.addEventListener('keydown', this.handleKeydown);
            this.searchInput.addEventListener('focus', () => {
                if (this.currentResults.length > 0) {
                    this.showResults();
                }
            });
        }

        if (this.searchFilters) {
            this.searchFilters.forEach(filter => {
                filter.addEventListener('change', this.handleFilterChange);
            });
        }

        // Close results when clicking outside
        document.addEventListener('click', this.handleDocumentClick);
    }

    async loadSearchData() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading();

        try {
            const response = await fetch('/auntruth/new/js/data.json');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.searchData = await response.json();

            if (!this.searchData || !this.searchData.people) {
                throw new Error('Invalid search data format');
            }

            console.log(`Loaded ${this.searchData.people.length} people for search`);

        } catch (error) {
            console.error('Failed to load search data:', error);
            throw error;
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    buildSearchIndex() {
        if (!this.searchData || !window.lunr) {
            console.warn('Lunr.js not available - falling back to simple search');
            return;
        }

        try {
            this.searchIndex = lunr(function() {
                this.field('name', { boost: 10 });
                this.field('birthDate', { boost: 5 });
                this.field('birthLocation', { boost: 3 });
                this.field('lineage', { boost: 7 });
                this.field('spouse', { boost: 2 });
                this.field('children', { boost: 2 });
                this.field('occupation');
                this.field('notes');
                this.ref('id');

                // Add documents to index
                this.searchData.people.forEach(person => {
                    this.add(person);
                }, this);
            });

            console.log('Search index built successfully');

        } catch (error) {
            console.error('Failed to build search index:', error);
            this.searchIndex = null;
        }
    }

    enableSearch() {
        if (this.searchInput) {
            this.searchInput.disabled = false;
            this.searchInput.placeholder = 'Search people, dates, locations...';
        }
    }

    handleSearchInput(event) {
        const query = event.target.value.trim();

        // Clear previous debounce
        if (this.searchDebounce) {
            clearTimeout(this.searchDebounce);
        }

        // Debounce search
        this.searchDebounce = setTimeout(() => {
            this.performSearch(query);
        }, this.debounceDelay);
    }

    handleKeydown(event) {
        if (!this.searchResults || this.currentResults.length === 0) return;

        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.selectNext();
                break;
            case 'ArrowUp':
                event.preventDefault();
                this.selectPrevious();
                break;
            case 'Enter':
                event.preventDefault();
                this.selectCurrent();
                break;
            case 'Escape':
                this.hideResults();
                this.searchInput.blur();
                break;
        }
    }

    handleFilterChange() {
        const query = this.searchInput ? this.searchInput.value.trim() : '';
        if (query.length >= this.minQueryLength) {
            this.performSearch(query);
        }
    }

    handleResultClick(event) {
        const resultItem = event.target.closest('.search-result-item');
        if (resultItem) {
            const url = resultItem.getAttribute('data-url');
            if (url) {
                window.location.href = url;
            }
        }
    }

    handleDocumentClick(event) {
        const searchContainer = document.querySelector('.search-container');
        if (searchContainer && !searchContainer.contains(event.target)) {
            this.hideResults();
        }
    }

    performSearch(query) {
        if (query.length < this.minQueryLength) {
            this.hideResults();
            return;
        }

        if (!this.searchData) {
            this.showError('Search data not available');
            return;
        }

        try {
            let results;

            if (this.searchIndex && window.lunr) {
                // Use Lunr.js for advanced search
                results = this.searchWithLunr(query);
            } else {
                // Fallback to simple search
                results = this.searchSimple(query);
            }

            // Apply filters
            results = this.applyFilters(results);

            // Limit results
            results = results.slice(0, this.maxResults);

            this.currentResults = results;
            this.displayResults(results, query);

        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed');
        }
    }

    searchWithLunr(query) {
        try {
            const searchResults = this.searchIndex.search(query + '*');

            return searchResults.map(result => {
                const person = this.searchData.people.find(p => p.id === result.ref);
                return {
                    ...person,
                    score: result.score,
                    matches: result.matchData
                };
            }).filter(Boolean);

        } catch (error) {
            console.warn('Lunr search failed, falling back to simple search:', error);
            return this.searchSimple(query);
        }
    }

    searchSimple(query) {
        const queryLower = query.toLowerCase();

        return this.searchData.people.filter(person => {
            return (
                (person.name && person.name.toLowerCase().includes(queryLower)) ||
                (person.birthLocation && person.birthLocation.toLowerCase().includes(queryLower)) ||
                (person.lineage && person.lineage.toLowerCase().includes(queryLower)) ||
                (person.spouse && person.spouse.toLowerCase().includes(queryLower)) ||
                (person.birthDate && person.birthDate.includes(queryLower))
            );
        }).map(person => ({
            ...person,
            score: this.calculateSimpleScore(person, queryLower)
        })).sort((a, b) => b.score - a.score);
    }

    calculateSimpleScore(person, query) {
        let score = 0;

        if (person.name && person.name.toLowerCase().includes(query)) {
            score += person.name.toLowerCase().startsWith(query) ? 10 : 5;
        }

        if (person.lineage && person.lineage.toLowerCase().includes(query)) {
            score += 3;
        }

        if (person.birthLocation && person.birthLocation.toLowerCase().includes(query)) {
            score += 2;
        }

        return score;
    }

    applyFilters(results) {
        const enabledFilters = Array.from(this.searchFilters || [])
            .filter(filter => filter.checked)
            .map(filter => filter.value);

        if (enabledFilters.length === 0) {
            return results;
        }

        // For now, return all results since filtering by content type
        // would require more complex data structure
        return results;
    }

    displayResults(results, query) {
        if (!this.searchResults) return;

        this.selectedIndex = -1;

        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="search-no-results">
                    <p>No results found for "${query}"</p>
                    <p>Try:</p>
                    <ul>
                        <li>Checking your spelling</li>
                        <li>Using fewer words</li>
                        <li>Using different search terms</li>
                    </ul>
                </div>
            `;
        } else {
            const resultsHTML = results.map((person, index) =>
                this.renderSearchResult(person, index)
            ).join('');

            this.searchResults.innerHTML = resultsHTML;

            // Add click listeners to results
            this.searchResults.addEventListener('click', this.handleResultClick);
        }

        this.showResults();
        this.announceResults(results.length, query);
    }

    renderSearchResult(person, index) {
        const url = person.url || `/auntruth/new/htm/L${person.lineage || '0'}/${person.filename || person.id}.htm`;

        return `
            <div class="search-result-item"
                 data-url="${url}"
                 data-index="${index}"
                 role="option"
                 aria-selected="false">
                <div class="search-result-name">${this.escapeHtml(person.name || 'Unknown')}</div>
                <div class="search-result-details">
                    ${person.birthDate ? `Born: ${this.escapeHtml(person.birthDate)}` : ''}
                    ${person.birthLocation ? ` in ${this.escapeHtml(person.birthLocation)}` : ''}
                    ${person.spouse ? ` • Spouse: ${this.escapeHtml(person.spouse)}` : ''}
                </div>
                <div class="search-result-lineage">
                    Lineage: ${this.escapeHtml(person.lineageName || person.lineage || 'Unknown')}
                </div>
            </div>
        `;
    }

    selectNext() {
        if (this.currentResults.length === 0) return;

        this.selectedIndex = Math.min(this.selectedIndex + 1, this.currentResults.length - 1);
        this.updateSelection();
    }

    selectPrevious() {
        if (this.currentResults.length === 0) return;

        this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
        this.updateSelection();
    }

    selectCurrent() {
        if (this.selectedIndex >= 0 && this.selectedIndex < this.currentResults.length) {
            const person = this.currentResults[this.selectedIndex];
            const url = person.url || `/auntruth/new/htm/L${person.lineage || '0'}/${person.filename || person.id}.htm`;
            window.location.href = url;
        }
    }

    updateSelection() {
        const resultItems = this.searchResults.querySelectorAll('.search-result-item');

        resultItems.forEach((item, index) => {
            const isSelected = index === this.selectedIndex;
            item.setAttribute('aria-selected', isSelected.toString());

            if (isSelected) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });

                // Update ARIA live region
                const announcement = `${item.querySelector('.search-result-name').textContent} selected`;
                this.announceToScreenReader(announcement);
            } else {
                item.classList.remove('selected');
            }
        });
    }

    showResults() {
        if (this.searchResults) {
            this.searchResults.hidden = false;
            this.searchResults.setAttribute('aria-expanded', 'true');
        }
    }

    hideResults() {
        if (this.searchResults) {
            this.searchResults.hidden = true;
            this.searchResults.setAttribute('aria-expanded', 'false');
        }
        this.selectedIndex = -1;
    }

    showLoading() {
        if (this.searchInput) {
            this.searchInput.placeholder = 'Loading search data...';
        }
    }

    hideLoading() {
        if (this.searchInput) {
            this.searchInput.placeholder = 'Search people, dates, locations...';
        }
    }

    showError(message) {
        if (this.searchResults) {
            this.searchResults.innerHTML = `
                <div class="search-error">
                    <p>⚠️ ${message}</p>
                </div>
            `;
            this.showResults();
        }
    }

    announceResults(count, query) {
        const message = count === 0
            ? `No results found for ${query}`
            : `${count} result${count === 1 ? '' : 's'} found for ${query}`;

        this.announceToScreenReader(message);
    }

    announceToScreenReader(message) {
        // Create temporary element for screen reader announcement
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Load Lunr.js if not already loaded
function loadLunr() {
    return new Promise((resolve, reject) => {
        if (window.lunr) {
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://unpkg.com/lunr@2.3.9/lunr.min.js';
        script.onload = resolve;
        script.onerror = () => {
            console.warn('Failed to load Lunr.js - search will use simple fallback');
            resolve(); // Don't reject, just continue without Lunr
        };

        document.head.appendChild(script);
    });
}

// Initialize search when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    // Only initialize search in the new site
    if (!window.location.pathname.includes('/htm/') || window.location.pathname.includes('/new/')) {
        try {
            await loadLunr();
            new SearchComponent();
        } catch (error) {
            console.error('Failed to initialize search component:', error);
        }
    }
});

// Export for potential use by other scripts
window.SearchComponent = SearchComponent;