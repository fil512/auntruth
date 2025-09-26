#!/usr/bin/env node

/**
 * Build Lunr.js Search Indices Script
 * Creates Lunr.js search indices for enhanced search functionality
 * Based on the Phase 2 PRP implementation blueprint
 */

const fs = require('fs').promises;
const path = require('path');
const lunr = require('lunr');

class SearchIndexBuilder {
  constructor() {
    this.dataDir = path.join(__dirname, '../docs/new/js/data');
    this.lineagesDir = path.join(this.dataDir, 'lineages');
    this.indicesDir = path.join(this.dataDir, 'indices');
  }

  async run() {
    console.log('Building Lunr.js search indices...');

    try {
      await this.createDirectories();

      // Build individual lineage indices
      for (let lineageId = 0; lineageId <= 9; lineageId++) {
        await this.buildLineageSearchIndex(lineageId);
      }

      console.log('Lunr.js search indices built successfully!');
    } catch (error) {
      console.error('Error building Lunr.js search indices:', error);
      process.exit(1);
    }
  }

  async createDirectories() {
    await fs.mkdir(this.indicesDir, { recursive: true });
  }

  async buildLineageSearchIndex(lineageId) {
    console.log(`Building search index for lineage ${lineageId}...`);

    try {
      const lineageData = await this.loadLineageData(lineageId);
      if (!lineageData || !lineageData.people || lineageData.people.length === 0) {
        console.log(`  No data found for lineage ${lineageId}, skipping`);
        return;
      }

      const index = lunr(function () {
        this.ref('id');
        this.field('name', { boost: 10 });
        this.field('birthLocation', { boost: 5 });
        this.field('deathLocation', { boost: 5 });
        this.field('occupation', { boost: 3 });
        this.field('spouse', { boost: 2 });
        this.field('children', { boost: 2 });
        this.field('birthDate');
        this.field('deathDate');
        this.field('notes');

        lineageData.people.forEach((person) => {
          this.add({
            id: person.id,
            name: person.name || '',
            birthLocation: person.birthLocation || '',
            deathLocation: person.deathLocation || '',
            occupation: person.occupation || '',
            spouse: [person.spouse, person.spouse2, person.spouse3, person.spouse4]
              .filter(Boolean).join(' '),
            children: person.children ? person.children.join(' ') : '',
            birthDate: person.birthDate || '',
            deathDate: person.deathDate || '',
            notes: person.notes || ''
          });
        });
      });

      // Save serialized index
      await this.saveSearchIndex(lineageId, index.toJSON());

      console.log(`  Created search index for lineage ${lineageId} with ${lineageData.people.length} people`);
    } catch (error) {
      console.error(`Failed to build search index for lineage ${lineageId}:`, error);
    }
  }

  async loadLineageData(lineageId) {
    try {
      const lineageFile = path.join(this.lineagesDir, `L${lineageId}.json`);
      const content = await fs.readFile(lineageFile, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      // File doesn't exist or is invalid - this is OK, some lineages might not exist
      return null;
    }
  }

  async saveSearchIndex(lineageId, indexData) {
    const indexPath = path.join(this.indicesDir, `search-L${lineageId}.json`);
    await fs.writeFile(indexPath, JSON.stringify(indexData, null, 2));
  }
}

// Run if called directly
if (require.main === module) {
  const builder = new SearchIndexBuilder();
  builder.run();
}

module.exports = SearchIndexBuilder;