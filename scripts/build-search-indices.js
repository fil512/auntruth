#!/usr/bin/env node

/**
 * Build Search Indices Script
 * Creates search indices for future search functionality
 */

const fs = require('fs').promises;
const path = require('path');

class SearchIndexBuilder {
  constructor() {
    this.dataDir = path.join(__dirname, '../docs/new/js/data');
    this.lineagesDir = path.join(this.dataDir, 'lineages');
    this.indicesDir = path.join(this.dataDir, 'indices');
  }

  async run() {
    console.log('Building search indices...');

    try {
      await this.createDirectories();
      const metadata = await this.loadMetadata();

      if (!metadata) {
        console.log('No metadata found, skipping search index creation');
        return;
      }

      await this.buildNameIndex();
      await this.buildLocationIndex();

      console.log('Search indices built successfully!');
    } catch (error) {
      console.error('Error building search indices:', error);
      process.exit(1);
    }
  }

  async createDirectories() {
    await fs.mkdir(this.indicesDir, { recursive: true });
  }

  async loadMetadata() {
    try {
      const metadataPath = path.join(this.dataDir, 'metadata.json');
      const content = await fs.readFile(metadataPath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      console.error('Failed to load metadata:', error);
      return null;
    }
  }

  async buildNameIndex() {
    console.log('Building name search index...');

    const nameIndex = {};
    const lineageFiles = await fs.readdir(this.lineagesDir);

    for (const filename of lineageFiles) {
      if (!filename.endsWith('.json')) continue;

      try {
        const filePath = path.join(this.lineagesDir, filename);
        const content = await fs.readFile(filePath, 'utf8');
        const lineageData = JSON.parse(content);

        if (lineageData.people) {
          for (const person of lineageData.people) {
            if (person.name && person.id) {
              const nameLower = person.name.toLowerCase();
              const words = nameLower.split(/\s+/);

              for (const word of words) {
                if (word.length > 2) { // Skip very short words
                  if (!nameIndex[word]) {
                    nameIndex[word] = [];
                  }
                  nameIndex[word].push({
                    id: person.id,
                    name: person.name,
                    lineage: person.lineage
                  });
                }
              }
            }
          }
        }
      } catch (error) {
        console.error(`Error processing ${filename}:`, error);
      }
    }

    // Remove duplicates and sort
    for (const word in nameIndex) {
      const unique = nameIndex[word].filter((item, index, self) =>
        index === self.findIndex(i => i.id === item.id)
      );
      nameIndex[word] = unique.sort((a, b) => a.name.localeCompare(b.name));
    }

    const indexPath = path.join(this.indicesDir, 'names.json');
    await fs.writeFile(indexPath, JSON.stringify(nameIndex, null, 2));

    const wordCount = Object.keys(nameIndex).length;
    console.log(`  Created name index with ${wordCount} unique words`);
  }

  async buildLocationIndex() {
    console.log('Building location search index...');

    const locationIndex = {};
    const lineageFiles = await fs.readdir(this.lineagesDir);

    for (const filename of lineageFiles) {
      if (!filename.endsWith('.json')) continue;

      try {
        const filePath = path.join(this.lineagesDir, filename);
        const content = await fs.readFile(filePath, 'utf8');
        const lineageData = JSON.parse(content);

        if (lineageData.people) {
          for (const person of lineageData.people) {
            const locations = [
              person.birthLocation,
              person.deathLocation,
              person.address
            ].filter(Boolean);

            for (const location of locations) {
              if (location && location.length > 3) {
                const locationLower = location.toLowerCase();
                const words = locationLower.split(/[\s,]+/);

                for (const word of words) {
                  if (word.length > 2) {
                    if (!locationIndex[word]) {
                      locationIndex[word] = [];
                    }
                    locationIndex[word].push({
                      id: person.id,
                      name: person.name,
                      location: location,
                      type: this.getLocationType(location, person),
                      lineage: person.lineage
                    });
                  }
                }
              }
            }
          }
        }
      } catch (error) {
        console.error(`Error processing ${filename}:`, error);
      }
    }

    // Remove duplicates and sort
    for (const word in locationIndex) {
      const unique = locationIndex[word].filter((item, index, self) =>
        index === self.findIndex(i => i.id === item.id && i.location === item.location)
      );
      locationIndex[word] = unique.sort((a, b) => a.name.localeCompare(b.name));
    }

    const indexPath = path.join(this.indicesDir, 'locations.json');
    await fs.writeFile(indexPath, JSON.stringify(locationIndex, null, 2));

    const wordCount = Object.keys(locationIndex).length;
    console.log(`  Created location index with ${wordCount} unique location words`);
  }

  getLocationType(location, person) {
    if (person.birthLocation === location) return 'birth';
    if (person.deathLocation === location) return 'death';
    if (person.address === location) return 'address';
    return 'unknown';
  }
}

// Run if called directly
if (require.main === module) {
  const builder = new SearchIndexBuilder();
  builder.run();
}

module.exports = SearchIndexBuilder;