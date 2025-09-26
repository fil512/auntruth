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
    if (!metadata || !metadata.personToLineage) {
      // Fallback to legacy data if metadata not available
      return this.getPersonFromLegacy(personId);
    }

    const lineageId = metadata.personToLineage[personId];
    if (!lineageId) return null;

    const lineageData = await this.getLineageData(lineageId);
    if (!lineageData) return null;

    return lineageData.people.find(person => person.id === personId);
  }

  async getPersonFromLegacy(personId) {
    try {
      const legacyData = await this.loadLegacyData();
      if (legacyData && legacyData.people) {
        return legacyData.people.find(person => person.id === personId);
      }
      return null;
    } catch (error) {
      console.error('Failed to get person from legacy data:', error);
      return null;
    }
  }

  async searchPeople(query, options = {}) {
    const metadata = await this.getMetadata();
    if (!metadata) {
      // Fallback to legacy search
      return this.searchLegacyData(query);
    }

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

  async searchLegacyData(query) {
    try {
      const legacyData = await this.loadLegacyData();
      if (legacyData && legacyData.people) {
        const searchTerm = query.toLowerCase();
        return legacyData.people.filter(person =>
          person.name.toLowerCase().includes(searchTerm)
        );
      }
      return [];
    } catch (error) {
      console.error('Failed to search legacy data:', error);
      return [];
    }
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