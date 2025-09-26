#!/usr/bin/env node

/**
 * Validate Data Script
 * Validates data integrity and consistency
 */

const fs = require('fs').promises;
const path = require('path');

class DataValidator {
  constructor() {
    this.dataDir = path.join(__dirname, '../docs/new/js/data');
    this.lineagesDir = path.join(this.dataDir, 'lineages');
    this.errors = [];
    this.warnings = [];
  }

  async run() {
    console.log('Starting data validation...');

    try {
      await this.validateMetadata();
      await this.validateLineageFiles();
      await this.validateDataConsistency();

      this.printResults();

      if (this.errors.length > 0) {
        process.exit(1);
      }
    } catch (error) {
      console.error('Error during validation:', error);
      process.exit(1);
    }
  }

  async validateMetadata() {
    console.log('Validating metadata...');

    try {
      const metadataPath = path.join(this.dataDir, 'metadata.json');
      const content = await fs.readFile(metadataPath, 'utf8');
      const metadata = JSON.parse(content);

      // Check required fields
      const requiredFields = ['generated', 'version', 'totalPeople', 'totalLineages', 'personToLineage', 'lineageNames'];
      for (const field of requiredFields) {
        if (!metadata[field]) {
          this.errors.push(`Missing required field in metadata: ${field}`);
        }
      }

      // Validate personToLineage mappings
      if (metadata.personToLineage && typeof metadata.personToLineage === 'object') {
        const personCount = Object.keys(metadata.personToLineage).length;
        if (personCount !== metadata.totalPeople) {
          this.warnings.push(`Person count mismatch: metadata says ${metadata.totalPeople}, but personToLineage has ${personCount} entries`);
        }
      }

      console.log('  Metadata validation complete');
    } catch (error) {
      this.errors.push(`Failed to validate metadata: ${error.message}`);
    }
  }

  async validateLineageFiles() {
    console.log('Validating lineage files...');

    try {
      const lineageFiles = await fs.readdir(this.lineagesDir);
      const jsonFiles = lineageFiles.filter(f => f.endsWith('.json'));

      console.log(`  Found ${jsonFiles.length} lineage files`);

      for (const filename of jsonFiles) {
        await this.validateLineageFile(filename);
      }
    } catch (error) {
      this.errors.push(`Failed to read lineages directory: ${error.message}`);
    }
  }

  async validateLineageFile(filename) {
    try {
      const filePath = path.join(this.lineagesDir, filename);
      const content = await fs.readFile(filePath, 'utf8');
      const lineageData = JSON.parse(content);

      // Check structure
      if (!lineageData.lineageId) {
        this.errors.push(`${filename}: Missing lineageId`);
      }

      if (!lineageData.lineageName) {
        this.errors.push(`${filename}: Missing lineageName`);
      }

      if (!Array.isArray(lineageData.people)) {
        this.errors.push(`${filename}: People is not an array`);
        return;
      }

      // Validate people
      for (const person of lineageData.people) {
        this.validatePerson(person, filename);
      }

      console.log(`    ${filename}: ${lineageData.people.length} people validated`);
    } catch (error) {
      this.errors.push(`${filename}: Failed to parse JSON - ${error.message}`);
    }
  }

  validatePerson(person, filename) {
    if (!person.id) {
      this.errors.push(`${filename}: Person missing ID`);
      return;
    }

    if (!person.name) {
      this.warnings.push(`${filename}: Person ${person.id} missing name`);
    }

    if (!person.filename) {
      this.warnings.push(`${filename}: Person ${person.id} missing filename`);
    }

    // Check filename consistency
    if (person.filename && person.id) {
      const expectedFilename = `XF${person.id}.htm`;
      if (person.filename !== expectedFilename) {
        this.warnings.push(`${filename}: Person ${person.id} filename mismatch: expected ${expectedFilename}, got ${person.filename}`);
      }
    }

    // Check lineage consistency
    if (person.lineage) {
      const fileLineage = filename.replace('L', '').replace('.json', '');
      if (person.lineage !== fileLineage) {
        this.warnings.push(`${filename}: Person ${person.id} lineage mismatch: person says ${person.lineage}, file is ${fileLineage}`);
      }
    }
  }

  async validateDataConsistency() {
    console.log('Validating data consistency...');

    try {
      // Load all people and check for duplicates
      const allPeople = await this.loadAllPeople();
      const seenIds = new Set();
      const duplicates = [];

      for (const person of allPeople) {
        if (seenIds.has(person.id)) {
          duplicates.push(person.id);
        }
        seenIds.add(person.id);
      }

      if (duplicates.length > 0) {
        this.errors.push(`Duplicate person IDs found: ${duplicates.join(', ')}`);
      }

      console.log(`  Checked ${allPeople.length} total people for consistency`);
    } catch (error) {
      this.errors.push(`Failed to validate consistency: ${error.message}`);
    }
  }

  async loadAllPeople() {
    const allPeople = [];
    const lineageFiles = await fs.readdir(this.lineagesDir);

    for (const filename of lineageFiles) {
      if (!filename.endsWith('.json')) continue;

      try {
        const filePath = path.join(this.lineagesDir, filename);
        const content = await fs.readFile(filePath, 'utf8');
        const lineageData = JSON.parse(content);

        if (lineageData.people) {
          allPeople.push(...lineageData.people);
        }
      } catch (error) {
        console.error(`Error loading ${filename}:`, error);
      }
    }

    return allPeople;
  }

  printResults() {
    console.log('\n=== Validation Results ===');

    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log('✅ All validation checks passed!');
      return;
    }

    if (this.errors.length > 0) {
      console.log(`\n❌ Errors (${this.errors.length}):`);
      for (const error of this.errors) {
        console.log(`  - ${error}`);
      }
    }

    if (this.warnings.length > 0) {
      console.log(`\n⚠️  Warnings (${this.warnings.length}):`);
      for (const warning of this.warnings) {
        console.log(`  - ${warning}`);
      }
    }

    if (this.errors.length === 0) {
      console.log('\n✅ No critical errors found');
    }
  }
}

// Run if called directly
if (require.main === module) {
  const validator = new DataValidator();
  validator.run();
}

module.exports = DataValidator;