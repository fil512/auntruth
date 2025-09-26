import BaseComponent from '../core/base-component.js';
import DataManager from '../core/data-manager.js';

/**
 * Timeline Component
 * Chronological visualization of family events with historical context
 * Uses D3.js following patterns from family-tree.js
 */
class TimelineComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.dataManager = options.dataManager || new DataManager();
    this.timelineData = [];
    this.historicalEvents = [];
    this.svg = null;
    this.currentView = 'decade'; // century, decade, year
    this.dateRange = { start: 1800, end: 2025 };
    this.selectedLineages = [];
    this.filteredEvents = [];

    // Timeline dimensions
    this.width = 0;
    this.height = 500;
    this.margin = { top: 60, right: 60, bottom: 60, left: 80 };
  }

  async loadDependencies() {
    // Load D3.js if not available (following family-tree.js pattern)
    if (!window.d3) {
      await this.loadD3Js();
    }
  }

  async render() {
    await this.loadTimelineData();
    await this.loadHistoricalContext();

    const timelineHtml = this.generateTimelineInterface();

    const container = document.getElementById('timeline-container') ||
                     this.createTimelineContainer();

    container.innerHTML = timelineHtml;
    this.element = container.querySelector('.timeline-component');

    await this.renderTimelineVisualization();
  }

  createTimelineContainer() {
    const container = document.createElement('div');
    container.id = 'timeline-container';
    container.style.width = '100%';
    container.style.margin = '20px 0';

    // Insert after main content
    const main = document.querySelector('main, .main-content, body');
    if (main) {
      main.appendChild(container);
    }

    return container;
  }

  generateTimelineInterface() {
    return `
      <div class="timeline-component">
        <div class="timeline-header">
          <h3>Family Timeline</h3>
          <div class="timeline-controls">
            <div class="view-controls">
              <button class="view-btn ${this.currentView === 'century' ? 'active' : ''}"
                      data-view="century">Century</button>
              <button class="view-btn ${this.currentView === 'decade' ? 'active' : ''}"
                      data-view="decade">Decade</button>
              <button class="view-btn ${this.currentView === 'year' ? 'active' : ''}"
                      data-view="year">Year</button>
            </div>

            <div class="filter-controls">
              <button class="filter-btn" title="Filter events">
                <span class="filter-icon">🔽</span> Filters
              </button>
            </div>

            <div class="range-controls">
              <label>From:</label>
              <input type="number" class="year-input" id="start-year"
                     value="${this.dateRange.start}" min="1800" max="2025">
              <label>To:</label>
              <input type="number" class="year-input" id="end-year"
                     value="${this.dateRange.end}" min="1800" max="2025">
            </div>
          </div>
        </div>

        <div class="timeline-filters" hidden>
          <div class="filter-section">
            <h4>Event Types</h4>
            <div class="checkbox-group">
              <label><input type="checkbox" class="event-filter" data-type="birth" checked> Births</label>
              <label><input type="checkbox" class="event-filter" data-type="death" checked> Deaths</label>
              <label><input type="checkbox" class="event-filter" data-type="marriage"> Marriages</label>
              <label><input type="checkbox" class="event-filter" data-type="historical"> Historical Events</label>
            </div>
          </div>

          <div class="filter-section">
            <h4>Lineages</h4>
            <div class="checkbox-group lineage-checkboxes">
              <!-- Populated dynamically -->
            </div>
          </div>

          <div class="filter-actions">
            <button class="btn-secondary clear-timeline-filters">Clear All</button>
            <button class="btn-primary apply-timeline-filters">Apply</button>
          </div>
        </div>

        <div class="timeline-loading" hidden>
          <div class="loading-spinner"></div>
          <p>Loading timeline data...</p>
        </div>

        <div class="timeline-viewport">
          <!-- SVG will be inserted here -->
        </div>

        <div class="timeline-info">
          <div class="event-count">
            <span id="total-events">0</span> events
            (<span id="visible-events">0</span> visible)
          </div>
        </div>
      </div>
    `;
  }

  async loadTimelineData() {
    console.log('Loading timeline data...');
    this.showLoading();

    try {
      this.timelineData = [];
      const lineageNames = {};

      // Load events from all lineages
      for (let lineageId = 0; lineageId <= 9; lineageId++) {
        const lineageData = await this.dataManager.getLineageData(lineageId.toString());
        if (!lineageData) continue;

        lineageNames[lineageId] = lineageData.lineageName || `Lineage ${lineageId}`;

        lineageData.people.forEach(person => {
          // Birth events
          if (person.birthDate) {
            const birthYear = this.parseYear(person.birthDate);
            if (birthYear) {
              this.timelineData.push({
                type: 'birth',
                year: birthYear,
                date: person.birthDate,
                person: person,
                location: person.birthLocation,
                lineage: person.lineage,
                lineageName: person.lineageName || lineageNames[lineageId],
                description: `${person.name} born`,
                id: `birth-${person.id}`
              });
            }
          }

          // Death events
          if (person.deathDate) {
            const deathYear = this.parseYear(person.deathDate);
            if (deathYear) {
              this.timelineData.push({
                type: 'death',
                year: deathYear,
                date: person.deathDate,
                person: person,
                location: person.deathLocation,
                lineage: person.lineage,
                lineageName: person.lineageName || lineageNames[lineageId],
                description: `${person.name} died`,
                id: `death-${person.id}`
              });
            }
          }

          // Marriage events (if we can parse spouse dates)
          // Note: This is basic - real implementation would need marriage date parsing
          if (person.spouse && person.birthDate) {
            const marriageYear = this.estimateMarriageYear(person);
            if (marriageYear) {
              this.timelineData.push({
                type: 'marriage',
                year: marriageYear,
                date: `~${marriageYear}`,
                person: person,
                spouse: person.spouse,
                lineage: person.lineage,
                lineageName: person.lineageName || lineageNames[lineageId],
                description: `${person.name} married`,
                id: `marriage-${person.id}`
              });
            }
          }
        });
      }

      // Sort chronologically
      this.timelineData.sort((a, b) => a.year - b.year);

      // Update date range based on data
      if (this.timelineData.length > 0) {
        const years = this.timelineData.map(e => e.year);
        this.dateRange.start = Math.min(...years, this.dateRange.start);
        this.dateRange.end = Math.max(...years, this.dateRange.end);
      }

      this.populateLineageFilters(lineageNames);
      console.log(`Loaded ${this.timelineData.length} timeline events`);

    } catch (error) {
      console.error('Error loading timeline data:', error);
      throw error;
    } finally {
      this.hideLoading();
    }
  }

  parseYear(dateString) {
    if (!dateString || typeof dateString !== 'string') return null;

    const cleanDate = dateString.trim();
    if (!cleanDate) return null;

    // Handle various genealogy date formats
    const patterns = [
      // Full year (4 digits) - most common
      /\b(1[89]\d{2}|20[0-2]\d)\b/,

      // Year with circa/about indicators
      /(?:circa|about|ca\.?|abt\.?|c\.?)\s*(\d{4})/i,

      // Year ranges (take first year)
      /(\d{4})\s*[-–]\s*\d{4}/,

      // Year with question mark (uncertain)
      /(\d{4})\?/,

      // Partial years (18xx, 19xx) - convert to mid-century
      /(18|19)xx/i,

      // Decades (1890s)
      /(\d{3})0s/,
    ];

    for (const pattern of patterns) {
      const match = cleanDate.match(pattern);
      if (match) {
        let year = parseInt(match[1] || match[0]);

        // Handle special cases
        if (match[0].includes('xx')) {
          // 18xx -> 1850, 19xx -> 1950
          year = parseInt(match[1]) * 100 + 50;
        } else if (match[0].includes('0s')) {
          // 1890s -> 1895
          year = parseInt(match[1] + '5');
        }

        // Validate year range
        if (year >= 1700 && year <= 2030) {
          return year;
        }
      }
    }

    // Try to extract any 4-digit number as fallback
    const fallbackMatch = cleanDate.match(/\d{4}/);
    if (fallbackMatch) {
      const year = parseInt(fallbackMatch[0]);
      if (year >= 1700 && year <= 2030) {
        return year;
      }
    }

    return null;
  }

  estimateMarriageYear(person) {
    // Simple estimation: assume marriage around age 20-25
    const birthYear = this.parseYear(person.birthDate);
    if (!birthYear) return null;

    const estimatedMarriageYear = birthYear + 22; // Average marriage age

    // Don't estimate marriages too far in the future
    if (estimatedMarriageYear > new Date().getFullYear()) {
      return null;
    }

    return estimatedMarriageYear;
  }

  async loadHistoricalContext() {
    // Historical events for context - focusing on Canadian/Swedish history
    // relevant to the genealogy data
    this.historicalEvents = [
      // Major wars
      { year: 1861, event: 'American Civil War begins', type: 'war', category: 'american' },
      { year: 1914, event: 'World War I begins', type: 'war', category: 'global' },
      { year: 1918, event: 'World War I ends', type: 'war', category: 'global' },
      { year: 1939, event: 'World War II begins', type: 'war', category: 'global' },
      { year: 1945, event: 'World War II ends', type: 'war', category: 'global' },

      // Canadian history
      { year: 1867, event: 'Canadian Confederation', type: 'political', category: 'canadian' },
      { year: 1885, event: 'Canadian Pacific Railway completed', type: 'infrastructure', category: 'canadian' },
      { year: 1896, event: 'Klondike Gold Rush begins', type: 'economic', category: 'canadian' },
      { year: 1905, event: 'Alberta and Saskatchewan become provinces', type: 'political', category: 'canadian' },

      // Economic events
      { year: 1929, event: 'Great Depression begins', type: 'economic', category: 'global' },
      { year: 1869, event: 'Transcontinental Railroad completed (US)', type: 'infrastructure', category: 'american' },

      // Immigration waves (relevant for genealogy)
      { year: 1880, event: 'Peak Swedish immigration to America', type: 'demographic', category: 'swedish' },
      { year: 1900, event: 'Peak European immigration to North America', type: 'demographic', category: 'global' },

      // Disease/health
      { year: 1918, event: 'Spanish Flu pandemic', type: 'health', category: 'global' },
      { year: 1832, event: 'Cholera pandemic reaches North America', type: 'health', category: 'global' },

      // Swedish history
      { year: 1866, event: 'Swedish Parliament reforms', type: 'political', category: 'swedish' },
      { year: 1905, event: 'Norway gains independence from Sweden', type: 'political', category: 'swedish' },
    ];
  }

  populateLineageFilters(lineageNames) {
    const container = this.element?.querySelector('.lineage-checkboxes');
    if (!container) return;

    const checkboxes = Object.entries(lineageNames).map(([id, name]) => `
      <label>
        <input type="checkbox" class="lineage-filter" data-lineage="${id}" checked>
        ${name}
      </label>
    `).join('');

    container.innerHTML = checkboxes;
  }

  async renderTimelineVisualization() {
    const container = this.element.querySelector('.timeline-viewport');
    if (!container) return;

    // Clear previous content
    container.innerHTML = '';

    // Set up dimensions
    this.width = container.clientWidth || 800;
    const innerWidth = this.width - this.margin.left - this.margin.right;
    const innerHeight = this.height - this.margin.top - this.margin.bottom;

    // Create SVG using D3.js (following family-tree.js patterns)
    this.svg = d3.select(container)
      .append('svg')
      .attr('width', this.width)
      .attr('height', this.height)
      .attr('class', 'timeline-svg');

    const g = this.svg.append('g')
      .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

    // Get filtered events
    this.filteredEvents = this.getFilteredEvents();

    if (this.filteredEvents.length === 0) {
      this.showNoDataMessage(container);
      return;
    }

    const years = this.filteredEvents.map(e => e.year);
    const minYear = Math.max(Math.min(...years), this.dateRange.start);
    const maxYear = Math.min(Math.max(...years), this.dateRange.end);

    // Set up scales
    const xScale = d3.scaleLinear()
      .domain([minYear, maxYear])
      .range([0, innerWidth]);

    // Create timeline axis
    this.drawTimelineAxis(g, xScale, minYear, maxYear, innerHeight);

    // Draw historical events
    this.drawHistoricalEvents(g, xScale, innerHeight);

    // Draw family events
    this.drawFamilyEvents(g, xScale, innerHeight);

    // Update event counts
    this.updateEventCounts();
  }

  drawTimelineAxis(g, xScale, minYear, maxYear, height) {
    const tickCount = this.currentView === 'century' ? 5 :
                     this.currentView === 'decade' ? 10 : 20;

    const axis = d3.axisBottom(xScale)
      .tickFormat(d3.format('d'))
      .ticks(tickCount);

    g.append('g')
      .attr('class', 'timeline-axis')
      .attr('transform', `translate(0, ${height - 20})`)
      .call(axis);

    // Add axis label
    g.append('text')
      .attr('class', 'axis-label')
      .attr('x', xScale.range()[1] / 2)
      .attr('y', height + 40)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Year');
  }

  drawHistoricalEvents(g, xScale, height) {
    const filteredHistorical = this.historicalEvents.filter(event =>
      event.year >= xScale.domain()[0] && event.year <= xScale.domain()[1]
    );

    const historicalGroup = g.append('g')
      .attr('class', 'historical-events');

    historicalGroup.selectAll('.historical-event')
      .data(filteredHistorical)
      .enter()
      .append('line')
      .attr('class', d => `historical-event ${d.type}`)
      .attr('x1', d => xScale(d.year))
      .attr('x2', d => xScale(d.year))
      .attr('y1', height - 40)
      .attr('y2', height - 20)
      .attr('stroke', '#999')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '2,2');

    // Add historical event labels (for major events)
    historicalGroup.selectAll('.historical-label')
      .data(filteredHistorical.filter(e => e.category === 'global' || e.category === 'canadian'))
      .enter()
      .append('text')
      .attr('class', 'historical-label')
      .attr('x', d => xScale(d.year))
      .attr('y', height - 45)
      .attr('text-anchor', 'middle')
      .style('font-size', '9px')
      .style('fill', '#666')
      .text(d => d.event)
      .attr('transform', d => `rotate(-45, ${xScale(d.year)}, ${height - 45})`);
  }

  drawFamilyEvents(g, xScale, height) {
    const eventGroup = g.append('g')
      .attr('class', 'family-events');

    // Group events by year and type for better visualization
    const eventsByYear = d3.group(this.filteredEvents, d => d.year);

    let currentY = 50;
    const eventHeight = 20;
    const typeColors = {
      birth: '#4CAF50',
      death: '#F44336',
      marriage: '#2196F3'
    };

    eventsByYear.forEach((yearEvents, year) => {
      const x = xScale(year);

      // Group by type
      const eventsByType = d3.group(yearEvents, d => d.type);

      let typeY = currentY;
      eventsByType.forEach((typeEvents, type) => {
        typeEvents.forEach((event, index) => {
          const y = typeY + (index * eventHeight);

          // Event circle
          eventGroup.append('circle')
            .attr('class', `family-event ${type}-event lineage-${event.lineage}`)
            .attr('cx', x)
            .attr('cy', y)
            .attr('r', 4)
            .attr('fill', typeColors[type] || '#999')
            .attr('stroke', '#fff')
            .attr('stroke-width', 1)
            .style('cursor', 'pointer')
            .on('click', () => this.showEventDetails(event))
            .on('mouseover', (e) => this.showEventTooltip(event, e))
            .on('mouseout', () => this.hideEventTooltip());

          // Event label (for major events or when zoomed in)
          if (this.currentView === 'year' || typeEvents.length <= 3) {
            eventGroup.append('text')
              .attr('class', 'event-label')
              .attr('x', x + 8)
              .attr('y', y + 3)
              .style('font-size', '10px')
              .style('fill', '#333')
              .text(`${event.person.name} (${type})`);
          }
        });

        typeY += typeEvents.length * eventHeight + 10;
      });

      currentY = Math.max(currentY, typeY);
    });
  }

  getFilteredEvents() {
    let filtered = [...this.timelineData];

    // Filter by date range
    filtered = filtered.filter(event =>
      event.year >= this.dateRange.start && event.year <= this.dateRange.end
    );

    // Filter by event types
    const activeEventTypes = this.getActiveEventTypes();
    if (activeEventTypes.length > 0) {
      filtered = filtered.filter(event =>
        activeEventTypes.includes(event.type)
      );
    }

    // Filter by lineages
    const activeLineages = this.getActiveLineages();
    if (activeLineages.length > 0) {
      filtered = filtered.filter(event =>
        activeLineages.includes(event.lineage?.toString())
      );
    }

    return filtered;
  }

  getActiveEventTypes() {
    const checkboxes = this.element?.querySelectorAll('.event-filter:checked') || [];
    return Array.from(checkboxes).map(cb => cb.dataset.type);
  }

  getActiveLineages() {
    const checkboxes = this.element?.querySelectorAll('.lineage-filter:checked') || [];
    return Array.from(checkboxes).map(cb => cb.dataset.lineage);
  }

  showEventDetails(event) {
    // Create event details modal or sidebar
    console.log('Show event details:', event);

    // Dispatch event for other components
    document.dispatchEvent(new CustomEvent('timeline-event-selected', {
      detail: { event, personId: event.person.id, person: event.person }
    }));
  }

  showEventTooltip(event, mouseEvent) {
    const tooltip = document.createElement('div');
    tooltip.className = 'timeline-tooltip';
    tooltip.innerHTML = `
      <div class="tooltip-header">${event.description}</div>
      <div class="tooltip-date">${event.date}</div>
      ${event.location ? `<div class="tooltip-location">${event.location}</div>` : ''}
      <div class="tooltip-lineage">${event.lineageName}</div>
    `;

    tooltip.style.position = 'absolute';
    tooltip.style.left = (mouseEvent.pageX + 10) + 'px';
    tooltip.style.top = (mouseEvent.pageY - 10) + 'px';
    tooltip.style.zIndex = '1000';
    tooltip.style.background = 'rgba(0,0,0,0.8)';
    tooltip.style.color = 'white';
    tooltip.style.padding = '8px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '12px';
    tooltip.style.pointerEvents = 'none';

    document.body.appendChild(tooltip);
    this.currentTooltip = tooltip;
  }

  hideEventTooltip() {
    if (this.currentTooltip) {
      document.body.removeChild(this.currentTooltip);
      this.currentTooltip = null;
    }
  }

  showNoDataMessage(container) {
    container.innerHTML = `
      <div class="timeline-no-data">
        <p>No events found for the selected criteria.</p>
        <p>Try adjusting your filters or date range.</p>
      </div>
    `;
  }

  updateEventCounts() {
    const totalElement = this.element?.querySelector('#total-events');
    const visibleElement = this.element?.querySelector('#visible-events');

    if (totalElement) totalElement.textContent = this.timelineData.length;
    if (visibleElement) visibleElement.textContent = this.filteredEvents.length;
  }

  attachEventListeners() {
    if (!this.element) return;

    // View controls
    const viewBtns = this.element.querySelectorAll('.view-btn');
    viewBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        this.currentView = btn.dataset.view;
        this.updateViewButtons();
        this.renderTimelineVisualization();
      });
    });

    // Filter toggle
    const filterBtn = this.element.querySelector('.filter-btn');
    const filtersPanel = this.element.querySelector('.timeline-filters');
    if (filterBtn && filtersPanel) {
      filterBtn.addEventListener('click', () => {
        filtersPanel.hidden = !filtersPanel.hidden;
      });
    }

    // Date range controls
    const startYearInput = this.element.querySelector('#start-year');
    const endYearInput = this.element.querySelector('#end-year');

    if (startYearInput) {
      startYearInput.addEventListener('change', () => {
        this.dateRange.start = parseInt(startYearInput.value);
        this.renderTimelineVisualization();
      });
    }

    if (endYearInput) {
      endYearInput.addEventListener('change', () => {
        this.dateRange.end = parseInt(endYearInput.value);
        this.renderTimelineVisualization();
      });
    }

    // Filter controls
    const applyFiltersBtn = this.element.querySelector('.apply-timeline-filters');
    if (applyFiltersBtn) {
      applyFiltersBtn.addEventListener('click', () => {
        this.renderTimelineVisualization();
        filtersPanel.hidden = true;
      });
    }

    const clearFiltersBtn = this.element.querySelector('.clear-timeline-filters');
    if (clearFiltersBtn) {
      clearFiltersBtn.addEventListener('click', () => {
        this.clearAllFilters();
        this.renderTimelineVisualization();
      });
    }
  }

  updateViewButtons() {
    const viewBtns = this.element?.querySelectorAll('.view-btn') || [];
    viewBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === this.currentView);
    });
  }

  clearAllFilters() {
    // Reset event type filters
    const eventFilters = this.element?.querySelectorAll('.event-filter') || [];
    eventFilters.forEach(filter => {
      filter.checked = true;
    });

    // Reset lineage filters
    const lineageFilters = this.element?.querySelectorAll('.lineage-filter') || [];
    lineageFilters.forEach(filter => {
      filter.checked = true;
    });

    // Reset date range
    this.dateRange = { start: 1800, end: 2025 };
    const startInput = this.element?.querySelector('#start-year');
    const endInput = this.element?.querySelector('#end-year');
    if (startInput) startInput.value = this.dateRange.start;
    if (endInput) endInput.value = this.dateRange.end;
  }

  showLoading() {
    const loading = this.element?.querySelector('.timeline-loading');
    if (loading) loading.hidden = false;
  }

  hideLoading() {
    const loading = this.element?.querySelector('.timeline-loading');
    if (loading) loading.hidden = true;
  }

  async loadD3Js() {
    return new Promise((resolve, reject) => {
      if (window.d3) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/d3@7';
      script.onload = resolve;
      script.onerror = () => {
        console.error('Failed to load D3.js');
        reject(new Error('Failed to load D3.js'));
      };

      document.head.appendChild(script);
    });
  }

  // Public API methods
  setDateRange(start, end) {
    this.dateRange = { start, end };
    this.renderTimelineVisualization();
  }

  focusOnYear(year) {
    const rangeSize = this.dateRange.end - this.dateRange.start;
    const newStart = Math.max(1800, year - Math.floor(rangeSize / 2));
    const newEnd = Math.min(2025, newStart + rangeSize);

    this.setDateRange(newStart, newEnd);
  }

  getEventsForPerson(personId) {
    return this.timelineData.filter(event => event.person.id === personId);
  }
}

export default TimelineComponent;