import BaseComponent from '../core/base-component.js';
import DataManager from '../core/data-manager.js';

/**
 * Enhanced Search Component
 * Advanced search with Lunr.js integration and filtering capabilities
 */
class EnhancedSearchComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.searchIndices = new Map();
    this.activeFilters = {
      query: '',
      lineages: [],
      birthYearRange: [1800, 2025],
      deathYearRange: [1800, 2025],
      locations: [],
      hasPhotos: null,
      hasSpouse: null
    };

    // Search settings
    this.maxResults = 50;
    this.minQueryLength = 2;
    this.debounceDelay = 150;
    this.searchDebounce = null;
    this.currentResults = [];
    this.selectedIndex = -1;

    // UI elements
    this.searchContainer = null;
    this.searchInput = null;
    this.searchResults = null;
    this.filtersContainer = null;
  }

  async loadDependencies() {
    // Load Lunr.js if not already available
    if (!window.lunr) {
      await this.loadLunrJs();
    }
  }

  async render() {
    // Find or create search container
    this.searchContainer = this.$('.search-container');
    if (!this.searchContainer) {
      this.createSearchInterface();
    }

    await this.loadSearchIndices();
    this.setupAdvancedFilters();
    this.enableSearch();
  }

  attachEventListeners() {
    if (this.searchInput) {
      this.searchInput.addEventListener('input', this.handleSearchInput.bind(this));
      this.searchInput.addEventListener('keydown', this.handleKeydown.bind(this));
      this.searchInput.addEventListener('focus', () => {
        if (this.currentResults.length > 0) {
          this.showResults();
        }
      });
    }

    // Filter change handlers
    const filterInputs = this.$$('.search-filter input');
    filterInputs.forEach(input => {
      input.addEventListener('change', this.handleFilterChange.bind(this));
    });

    // Range slider handlers
    const rangeInputs = this.$$('.year-range input[type="range"]');
    rangeInputs.forEach(input => {
      input.addEventListener('input', this.handleRangeChange.bind(this));
    });

    // Close results when clicking outside
    document.addEventListener('click', this.handleDocumentClick.bind(this));

    // Close button
    const closeBtn = this.$('.search-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        this.searchContainer.classList.remove('active');
      });
    }
  }

  createSearchInterface() {
    const searchHTML = this.getSearchHTML();

    // Insert search interface
    const mainContent = this.$('.main-content, main, body');
    if (mainContent) {
      mainContent.insertAdjacentHTML('afterbegin', searchHTML);
      this.searchContainer = this.$('.search-container');
    }

    // Get references to elements
    this.searchInput = this.$('#enhanced-people-search');
    this.searchResults = this.$('#enhanced-search-results');
    this.filtersContainer = this.$('.enhanced-search-filters');
  }

  getSearchHTML() {
    return `
      <div class="search-container enhanced-search">
        <div class="search-header">
          <h3>Enhanced Family Search</h3>
          <button class="search-close" aria-label="Close search">&times;</button>
        </div>
        <div class="search-wrapper">
          <div class="search-input-wrapper">
            <input type="search"
                   id="enhanced-people-search"
                   placeholder="Search people, places, dates..."
                   autocomplete="off"
                   aria-label="Enhanced search genealogy database"
                   disabled>
            <div class="search-loading" hidden>
              <div class="loading-spinner"></div>
            </div>
          </div>

          <div class="enhanced-search-filters">
            <div class="filters-header">
              <h4>Advanced Filters</h4>
              <button class="filters-toggle" aria-label="Toggle filters">
                <span class="filter-icon"></span>
              </button>
            </div>

            <div class="filters-content" hidden>
              <div class="filter-group">
                <label class="filter-label">Search In:</label>
                <div class="checkbox-group">
                  <label><input type="checkbox" class="search-filter" data-field="name" checked> Names</label>
                  <label><input type="checkbox" class="search-filter" data-field="location" checked> Locations</label>
                  <label><input type="checkbox" class="search-filter" data-field="occupation"> Occupations</label>
                  <label><input type="checkbox" class="search-filter" data-field="notes"> Notes</label>
                </div>
              </div>

              <div class="filter-group">
                <label class="filter-label">Lineages:</label>
                <div class="checkbox-group lineage-filters">
                  <!-- Dynamically populated -->
                </div>
              </div>

              <div class="filter-group">
                <label class="filter-label">Birth Year Range:</label>
                <div class="range-group">
                  <input type="range" class="year-range" data-range="birth"
                         min="1800" max="2025" value="1800" data-type="min">
                  <input type="range" class="year-range" data-range="birth"
                         min="1800" max="2025" value="2025" data-type="max">
                  <div class="range-display">
                    <span class="range-min">1800</span> - <span class="range-max">2025</span>
                  </div>
                </div>
              </div>

              <div class="filter-group">
                <label class="filter-label">Additional Filters:</label>
                <div class="checkbox-group">
                  <label><input type="checkbox" class="search-filter" data-field="hasPhotos"> Has Photos</label>
                  <label><input type="checkbox" class="search-filter" data-field="hasSpouse"> Has Spouse Info</label>
                </div>
              </div>

              <div class="filter-actions">
                <button class="btn-secondary clear-filters">Clear All</button>
                <button class="btn-primary apply-filters">Apply Filters</button>
              </div>
            </div>
          </div>
        </div>

        <div class="search-results enhanced-results" id="enhanced-search-results"
             hidden aria-live="polite" role="listbox">
          <!-- Enhanced search results populated here -->
        </div>
      </div>
    `;
  }

  async loadSearchIndices() {
    console.log('Loading enhanced search indices...');

    for (let lineageId = 0; lineageId <= 9; lineageId++) {
      try {
        const response = await fetch(`/auntruth/new/js/data/indices/search-L${lineageId}.json`);
        if (response.ok) {
          const indexData = await response.json();
          this.searchIndices.set(lineageId.toString(), window.lunr.Index.load(indexData));
          console.log(`Loaded search index for lineage ${lineageId}`);
        }
      } catch (error) {
        console.warn(`Failed to load search index for lineage ${lineageId}:`, error);
      }
    }

    console.log(`Loaded ${this.searchIndices.size} search indices`);
  }

  setupAdvancedFilters() {
    // Setup lineage filters based on available indices
    const lineageContainer = this.$('.lineage-filters');
    if (lineageContainer) {
      const lineageOptions = [];
      for (let i = 0; i <= 9; i++) {
        if (this.searchIndices.has(i.toString())) {
          lineageOptions.push(`
            <label><input type="checkbox" class="search-filter" data-lineage="${i}" checked> Lineage ${i}</label>
          `);
        }
      }
      lineageContainer.innerHTML = lineageOptions.join('');
    }

    // Setup filters toggle
    const filtersToggle = this.$('.filters-toggle');
    const filtersContent = this.$('.filters-content');
    if (filtersToggle && filtersContent) {
      filtersToggle.addEventListener('click', () => {
        filtersContent.hidden = !filtersContent.hidden;
        filtersToggle.setAttribute('aria-expanded', (!filtersContent.hidden).toString());
      });
    }

    // Setup clear and apply buttons
    const clearBtn = this.$('.clear-filters');
    const applyBtn = this.$('.apply-filters');

    if (clearBtn) {
      clearBtn.addEventListener('click', this.clearFilters.bind(this));
    }

    if (applyBtn) {
      applyBtn.addEventListener('click', this.applyCurrentFilters.bind(this));
    }
  }

  enableSearch() {
    if (this.searchInput) {
      this.searchInput.disabled = false;
      this.searchInput.placeholder = 'Search people, places, dates...';
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
    this.updateActiveFilters();
    const query = this.searchInput ? this.searchInput.value.trim() : '';
    if (query.length >= this.minQueryLength) {
      this.performSearch(query);
    }
  }

  handleRangeChange(event) {
    const range = event.target.dataset.range;
    const type = event.target.dataset.type;
    const value = parseInt(event.target.value);

    if (range === 'birth') {
      if (type === 'min') {
        this.activeFilters.birthYearRange[0] = value;
        this.$('.range-min').textContent = value;
      } else {
        this.activeFilters.birthYearRange[1] = value;
        this.$('.range-max').textContent = value;
      }
    }

    this.handleFilterChange();
  }

  handleDocumentClick(event) {
    if (this.searchContainer && !this.searchContainer.contains(event.target)) {
      this.hideResults();
    }
  }

  async performSearch(query) {
    if (query.length < this.minQueryLength) {
      this.hideResults();
      return;
    }

    this.showLoading();

    try {
      const results = await this.searchWithLunr(query);
      const filteredResults = this.applyFilters(results);
      const limitedResults = filteredResults.slice(0, this.maxResults);

      this.currentResults = limitedResults;
      this.displayResults(limitedResults, query);
    } catch (error) {
      console.error('Enhanced search error:', error);
      this.showError('Search failed');
    } finally {
      this.hideLoading();
    }
  }

  async searchWithLunr(query) {
    const allResults = [];

    // Get active lineages from filters
    const activeLineages = this.getActiveLineages();

    for (const lineageId of activeLineages) {
      const index = this.searchIndices.get(lineageId);
      if (!index) continue;

      try {
        // Try multiple search strategies
        const searchStrategies = [
          query + '*',           // Prefix search
          query,                 // Exact search
          query.split(' ').join('* ') + '*'  // Multi-word prefix
        ];

        for (const searchQuery of searchStrategies) {
          const searchResults = index.search(searchQuery);

          for (const result of searchResults) {
            // Get full person data from DataManager
            const person = await this.dataManager.getPersonData(result.ref);
            if (person) {
              allResults.push({
                ...person,
                score: result.score,
                lineageId: lineageId,
                matches: result.matchData
              });
            }
          }

          if (searchResults.length > 0) break; // Use first strategy that returns results
        }
      } catch (error) {
        console.warn(`Search failed for lineage ${lineageId}:`, error);
      }
    }

    // Remove duplicates and sort by score
    const uniqueResults = allResults.filter((result, index, self) =>
      index === self.findIndex(r => r.id === result.id)
    );

    return uniqueResults.sort((a, b) => b.score - a.score);
  }

  applyFilters(results) {
    return results.filter(person => {
      // Year range filters
      if (person.birthDate) {
        const birthYear = this.extractYear(person.birthDate);
        if (birthYear && (
          birthYear < this.activeFilters.birthYearRange[0] ||
          birthYear > this.activeFilters.birthYearRange[1]
        )) {
          return false;
        }
      }

      // Has photos filter
      if (this.activeFilters.hasPhotos && !person.photoUrl) {
        return false;
      }

      // Has spouse filter
      if (this.activeFilters.hasSpouse && !person.spouse) {
        return false;
      }

      return true;
    });
  }

  getActiveLineages() {
    const checkboxes = this.$$('.search-filter[data-lineage]');
    return Array.from(checkboxes)
      .filter(cb => cb.checked)
      .map(cb => cb.dataset.lineage);
  }

  updateActiveFilters() {
    // Update from UI state
    this.activeFilters.hasPhotos = this.$('.search-filter[data-field="hasPhotos"]')?.checked || null;
    this.activeFilters.hasSpouse = this.$('.search-filter[data-field="hasSpouse"]')?.checked || null;
  }

  extractYear(dateString) {
    if (!dateString) return null;
    const match = dateString.match(/\b(1[89]\d{2}|20[0-2]\d)\b/);
    return match ? parseInt(match[0]) : null;
  }

  displayResults(results, query) {
    if (!this.searchResults) return;

    this.selectedIndex = -1;

    if (results.length === 0) {
      this.searchResults.innerHTML = `
        <div class="search-no-results">
          <p>No results found for "${this.escapeHtml(query)}"</p>
          <p>Try adjusting your filters or search terms.</p>
        </div>
      `;
    } else {
      const resultsHTML = results.map((person, index) =>
        this.renderEnhancedResult(person, index, query)
      ).join('');

      this.searchResults.innerHTML = resultsHTML;
      this.searchResults.addEventListener('click', this.handleResultClick.bind(this));
    }

    this.showResults();
    this.announceResults(results.length, query);
  }

  renderEnhancedResult(person, index, query) {
    const url = person.url || `/auntruth/new/htm/L${person.lineage || '0'}/${person.filename || person.id}.htm`;

    // Highlight matching terms
    const highlightedName = this.highlightMatches(person.name || 'Unknown', query);

    return `
      <div class="search-result-item enhanced-result"
           data-url="${this.escapeHtml(url)}"
           data-index="${index}"
           role="option"
           aria-selected="false">
        <div class="result-header">
          <div class="result-name">${highlightedName}</div>
          <div class="result-score">${Math.round((person.score || 0) * 100)}% match</div>
        </div>
        <div class="result-details">
          ${person.birthDate ? `<span class="detail-item">Born: ${this.escapeHtml(person.birthDate)}</span>` : ''}
          ${person.birthLocation ? `<span class="detail-item">in ${this.escapeHtml(person.birthLocation)}</span>` : ''}
          ${person.deathDate ? `<span class="detail-item">Died: ${this.escapeHtml(person.deathDate)}</span>` : ''}
        </div>
        <div class="result-secondary">
          ${person.spouse ? `<span class="detail-item">Spouse: ${this.escapeHtml(person.spouse)}</span>` : ''}
          ${person.occupation ? `<span class="detail-item">Occupation: ${this.escapeHtml(person.occupation)}</span>` : ''}
        </div>
        <div class="result-lineage">Lineage ${person.lineage || 'Unknown'}</div>
      </div>
    `;
  }

  highlightMatches(text, query) {
    if (!query || !text) return this.escapeHtml(text);

    const escaped = this.escapeHtml(text);
    const queryTerms = query.toLowerCase().split(/\s+/).filter(term => term.length > 1);

    let highlighted = escaped;
    queryTerms.forEach(term => {
      const regex = new RegExp(`(${this.escapeRegex(term)})`, 'gi');
      highlighted = highlighted.replace(regex, '<mark>$1</mark>');
    });

    return highlighted;
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
      const resultItem = this.searchResults.children[this.selectedIndex];
      const url = resultItem.getAttribute('data-url');
      if (url) window.location.href = url;
    }
  }

  updateSelection() {
    const resultItems = this.$$('.search-result-item');
    resultItems.forEach((item, index) => {
      const isSelected = index === this.selectedIndex;
      item.setAttribute('aria-selected', isSelected.toString());

      if (isSelected) {
        item.classList.add('selected');
        item.scrollIntoView({ block: 'nearest' });
      } else {
        item.classList.remove('selected');
      }
    });
  }

  handleResultClick(event) {
    const resultItem = event.target.closest('.search-result-item');
    if (resultItem) {
      const url = resultItem.getAttribute('data-url');
      if (url) window.location.href = url;
    }
  }

  clearFilters() {
    // Reset all checkboxes
    const checkboxes = this.$$('.search-filter');
    checkboxes.forEach(cb => {
      cb.checked = cb.dataset.field === 'name' || cb.dataset.field === 'location' || cb.hasAttribute('data-lineage');
    });

    // Reset ranges
    const rangeInputs = this.$$('.year-range');
    rangeInputs.forEach(input => {
      if (input.dataset.type === 'min') {
        input.value = input.min;
      } else {
        input.value = input.max;
      }
    });

    // Reset active filters
    this.activeFilters = {
      query: '',
      lineages: [],
      birthYearRange: [1800, 2025],
      deathYearRange: [1800, 2025],
      locations: [],
      hasPhotos: null,
      hasSpouse: null
    };

    // Re-run search if there's a query
    this.handleFilterChange();
  }

  applyCurrentFilters() {
    this.handleFilterChange();

    // Close filters panel
    const filtersContent = this.$('.filters-content');
    if (filtersContent) {
      filtersContent.hidden = true;
    }
  }

  showResults() {
    if (this.searchResults) {
      this.searchResults.hidden = false;
    }
  }

  hideResults() {
    if (this.searchResults) {
      this.searchResults.hidden = true;
    }
    this.selectedIndex = -1;
  }

  showLoading() {
    const spinner = this.$('.search-loading');
    if (spinner) spinner.hidden = false;
  }

  hideLoading() {
    const spinner = this.$('.search-loading');
    if (spinner) spinner.hidden = true;
  }

  showError(message) {
    if (this.searchResults) {
      this.searchResults.innerHTML = `
        <div class="search-error">
          <p>⚠️ ${this.escapeHtml(message)}</p>
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
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);
    setTimeout(() => document.body.removeChild(announcement), 1000);
  }

  async loadLunrJs() {
    return new Promise((resolve, reject) => {
      if (window.lunr) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://unpkg.com/lunr@2.3.9/lunr.min.js';
      script.onload = resolve;
      script.onerror = () => {
        console.error('Failed to load Lunr.js');
        reject(new Error('Failed to load Lunr.js'));
      };

      document.head.appendChild(script);
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  escapeRegex(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}

export default EnhancedSearchComponent;