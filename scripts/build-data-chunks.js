#!/usr/bin/env node

/**
 * Build Data Chunks Script
 * Splits large data.json into lineage-based chunks for efficient loading
 */

const fs = require('fs').promises;
const path = require('path');

class DataChunker {
  constructor() {
    this.sourceFile = path.join(__dirname, '../docs/new/js/data.json');
    this.outputDir = path.join(__dirname, '../docs/new/js/data');
    this.lineagesDir = path.join(this.outputDir, 'lineages');
  }

  async run() {
    console.log('Starting data chunking process...');

    try {
      // Create output directories
      await this.createDirectories();

      // Load original data
      const originalData = await this.loadOriginalData();

      // Process and chunk data
      const chunks = await this.processData(originalData);

      // Write chunked files
      await this.writeChunks(chunks);

      console.log('Data chunking complete!');
      console.log(`Created ${chunks.lineages.size} lineage files`);
      console.log(`Total people processed: ${chunks.totalPeople}`);

    } catch (error) {
      console.error('Error during data chunking:', error);
      process.exit(1);
    }
  }

  async createDirectories() {
    await fs.mkdir(this.outputDir, { recursive: true });
    await fs.mkdir(this.lineagesDir, { recursive: true });
  }

  async loadOriginalData() {
    try {
      const content = await fs.readFile(this.sourceFile, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      console.error('Failed to load original data.json:', error);
      throw error;
    }
  }

  async processData(data) {
    const metadata = {
      generated: new Date().toISOString(),
      version: '2.0',
      totalPeople: 0,
      totalLineages: 0,
      personToLineage: {},
      lineageNames: {}
    };

    const lineages = new Map();

    // Process people array
    if (data.people && Array.isArray(data.people)) {
      for (const person of data.people) {
        // Get lineage ID from the existing data structure
        const lineageId = person.lineage || '0';

        if (!lineages.has(lineageId)) {
          lineages.set(lineageId, {
            lineageId,
            lineageName: this.getLineageName(lineageId),
            people: []
          });
        }

        lineages.get(lineageId).people.push(person);
        metadata.personToLineage[person.id] = lineageId;
        metadata.totalPeople++;
      }
    }

    metadata.totalLineages = lineages.size;

    // Add lineage names to metadata
    for (const [id, data] of lineages) {
      metadata.lineageNames[id] = data.lineageName;
    }

    return { metadata, lineages, totalPeople: metadata.totalPeople };
  }

  getLineageName(lineageId) {
    const names = {
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
    return names[lineageId] || `Lineage ${lineageId}`;
  }

  async writeChunks(chunks) {
    // Write metadata file
    const metadataPath = path.join(this.outputDir, 'metadata.json');
    await fs.writeFile(
      metadataPath,
      JSON.stringify(chunks.metadata, null, 2)
    );
    console.log(`Created metadata.json`);

    // Write lineage files
    for (const [lineageId, lineageData] of chunks.lineages) {
      const filename = `L${lineageId}.json`;
      const filepath = path.join(this.lineagesDir, filename);

      await fs.writeFile(
        filepath,
        JSON.stringify(lineageData, null, 2)
      );

      console.log(`Created ${filename} with ${lineageData.people.length} people`);
    }
  }
}

// Run if called directly
if (require.main === module) {
  const chunker = new DataChunker();
  chunker.run();
}

module.exports = DataChunker;