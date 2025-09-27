/**
 * Search Export Component
 * Provides CSV export functionality for genealogy research workflows
 * Integrates with Papa Parse for client-side CSV generation
 */

import BaseComponent from '../core/base-component.js';

class SearchExportComponent extends BaseComponent {
  constructor(options = {}) {
    super(options);
    this.searchComponent = options.searchComponent;
    this.initialized = false;
  }

  async loadDependencies() {
    // Load Papa Parse for CSV generation
    if (!window.Papa) {
      await this.loadPapaParse();
    }
  }

  async loadPapaParse() {
    return new Promise((resolve, reject) => {
      if (window.Papa) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js';
      script.onload = resolve;
      script.onerror = () => {
        console.error('Failed to load Papa Parse - CSV export will not be available');
        reject(new Error('Failed to load Papa Parse'));
      };

      document.head.appendChild(script);
    });
  }

  async init() {
    if (this.initialized) return;

    try {
      await this.loadDependencies();
      this.initialized = true;
      console.log('SearchExport component initialized');
    } catch (error) {
      console.warn('SearchExport component failed to initialize:', error);
      // Don't throw - allow graceful degradation
    }
  }

  exportSearchResults(results, filename = null) {
    if (!results || results.length === 0) {
      this.showExportMessage('No results to export', 'warning');
      return;
    }

    if (!window.Papa) {
      this.showExportMessage('Export functionality unavailable - Papa Parse not loaded', 'error');
      return;
    }

    try {
      // Generate filename if not provided
      if (!filename) {
        const timestamp = new Date().toISOString().split('T')[0];
        const resultCount = results.length;
        filename = `auntruth-search-${resultCount}-results-${timestamp}.csv`;
      }

      // Prepare data for CSV export with genealogy-specific fields
      const exportData = results.map(person => ({
        'ID': person.id || '',
        'Name': person.name || '',
        'Birth Date': person.birthDate || '',
        'Birth Location': person.birthLocation || '',
        'Death Date': person.deathDate || '',
        'Death Location': person.deathLocation || '',
        'Spouse': person.spouse || '',
        'Father': person.father || '',
        'Mother': person.mother || '',
        'Occupation': person.occupation || '',
        'Lineage': person.lineageName || person.lineage || '',
        'Lineage Number': person.lineage || '',
        'Deceased': person.deceased || '',
        'Address': person.address || '',
        'Notes': person.notes || '',
        'Source': person.source || '',
        'Genetics': person.genetics || '',
        'URL': person.url || '',
        'Filename': person.filename || ''
      }));

      // Generate CSV using Papa Parse
      const csv = Papa.unparse(exportData, {
        header: true,
        delimiter: ',',
        newline: '\n',
        quotes: true,
        quoteChar: '"',
        escapeChar: '"'
      });

      // Download CSV file
      this.downloadFile(csv, filename, 'text/csv');

      // Show success message
      this.showExportMessage(`Exported ${results.length} records to ${filename}`, 'success');

    } catch (error) {
      console.error('CSV export failed:', error);
      this.showExportMessage('Export failed - please try again', 'error');
    }
  }

  exportToJSON(results, filename = null) {
    if (!results || results.length === 0) {
      this.showExportMessage('No results to export', 'warning');
      return;
    }

    try {
      // Generate filename if not provided
      if (!filename) {
        const timestamp = new Date().toISOString().split('T')[0];
        const resultCount = results.length;
        filename = `auntruth-search-${resultCount}-results-${timestamp}.json`;
      }

      // Create structured JSON data
      const exportData = {
        metadata: {
          exportDate: new Date().toISOString(),
          totalRecords: results.length,
          source: 'AuntieRuth.com Enhanced Search',
          version: '1.0'
        },
        people: results.map(person => ({
          ...person,
          // Ensure consistent field structure
          id: person.id || '',
          name: person.name || '',
          birthDate: person.birthDate || '',
          birthLocation: person.birthLocation || '',
          deathDate: person.deathDate || '',
          deathLocation: person.deathLocation || '',
          lineage: person.lineage || '',
          lineageName: person.lineageName || '',
          url: person.url || ''
        }))
      };

      const jsonData = JSON.stringify(exportData, null, 2);
      this.downloadFile(jsonData, filename, 'application/json');

      // Show success message
      this.showExportMessage(`Exported ${results.length} records to ${filename}`, 'success');

    } catch (error) {
      console.error('JSON export failed:', error);
      this.showExportMessage('Export failed - please try again', 'error');
    }
  }

  downloadFile(content, filename, mimeType) {
    try {
      // Create blob and download URL
      const blob = new Blob([content], { type: mimeType + ';charset=utf-8;' });
      const url = URL.createObjectURL(blob);

      // Create temporary download link
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.style.display = 'none';

      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up URL
      setTimeout(() => URL.revokeObjectURL(url), 1000);

    } catch (error) {
      console.error('File download failed:', error);
      throw error;
    }
  }

  showExportMessage(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `export-notification export-${type}`;
    notification.innerHTML = `
      <div class="export-message">
        ${this.getIconForType(type)} ${this.escapeHtml(message)}
      </div>
      <button class="export-close" aria-label="Close notification">&times;</button>
    `;

    // Style the notification
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${this.getBackgroundForType(type)};
      color: ${this.getTextColorForType(type)};
      padding: 12px 16px;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      max-width: 400px;
      display: flex;
      align-items: center;
      gap: 12px;
      border: 1px solid ${this.getBorderColorForType(type)};
      font-size: 14px;
      animation: slideInRight 0.3s ease-out;
    `;

    // Add to DOM
    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
          if (notification.parentNode) {
            document.body.removeChild(notification);
          }
        }, 300);
      }
    }, 5000);

    // Add close button handler
    const closeBtn = notification.querySelector('.export-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        if (notification.parentNode) {
          document.body.removeChild(notification);
        }
      });
    }
  }

  getIconForType(type) {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return 'ℹ️';
    }
  }

  getBackgroundForType(type) {
    switch (type) {
      case 'success': return '#d4edda';
      case 'warning': return '#fff3cd';
      case 'error': return '#f8d7da';
      default: return '#d1ecf1';
    }
  }

  getTextColorForType(type) {
    switch (type) {
      case 'success': return '#155724';
      case 'warning': return '#856404';
      case 'error': return '#721c24';
      default: return '#0c5460';
    }
  }

  getBorderColorForType(type) {
    switch (type) {
      case 'success': return '#c3e6cb';
      case 'warning': return '#ffeaa7';
      case 'error': return '#f5c6cb';
      default: return '#bee5eb';
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Public API for external integration
  async exportCurrentResults(format = 'csv') {
    if (!this.searchComponent || !this.searchComponent.currentResults) {
      this.showExportMessage('No search results available to export', 'warning');
      return;
    }

    const results = this.searchComponent.currentResults;

    if (format === 'json') {
      this.exportToJSON(results);
    } else {
      this.exportSearchResults(results);
    }
  }

  // Integration helper for search components
  attachToSearchComponent(searchComponent) {
    this.searchComponent = searchComponent;

    // Find and attach to export button
    const exportButton = document.querySelector('.export-results');
    if (exportButton) {
      exportButton.addEventListener('click', () => {
        this.exportCurrentResults('csv');
      });
    }
  }
}

// Add CSS animations if not already present
if (!document.querySelector('#export-animations')) {
  const style = document.createElement('style');
  style.id = 'export-animations';
  style.textContent = `
    @keyframes slideInRight {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
    .export-close {
      background: none;
      border: none;
      cursor: pointer;
      font-size: 18px;
      line-height: 1;
      padding: 0;
      opacity: 0.7;
    }
    .export-close:hover {
      opacity: 1;
    }
  `;
  document.head.appendChild(style);
}

export default SearchExportComponent;