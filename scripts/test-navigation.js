#!/usr/bin/env node

/**
 * Test Navigation Script
 * Tests navigation components for proper functionality
 */

const fs = require('fs').promises;
const path = require('path');

class NavigationTester {
  constructor() {
    this.jsDir = path.join(__dirname, '../docs/new/js');
    this.testResults = {
      passed: 0,
      failed: 0,
      tests: []
    };
  }

  async run() {
    console.log('Testing navigation components...');

    try {
      await this.testComponentFiles();
      await this.testDataManager();

      this.printResults();

      if (this.testResults.failed > 0) {
        process.exit(1);
      }
    } catch (error) {
      console.error('Error during testing:', error);
      process.exit(1);
    }
  }

  async testComponentFiles() {
    const components = [
      'core/base-component.js',
      'core/data-manager.js',
      'core/app.js',
      'components/navigation-enhanced.js'
    ];

    for (const component of components) {
      await this.testFileExists(component);
      await this.testFileStructure(component);
    }
  }

  async testFileExists(filename) {
    const testName = `File exists: ${filename}`;

    try {
      const filePath = path.join(this.jsDir, filename);
      await fs.access(filePath);
      this.pass(testName);
    } catch (error) {
      this.fail(testName, `File not found: ${filename}`);
    }
  }

  async testFileStructure(filename) {
    const testName = `File structure: ${filename}`;

    try {
      const filePath = path.join(this.jsDir, filename);
      const content = await fs.readFile(filePath, 'utf8');

      // Check for class definition
      if (!content.includes('class ')) {
        this.fail(testName, 'No class definition found');
        return;
      }

      // Check for export statements
      if (!content.includes('export default') && !content.includes('window.')) {
        this.fail(testName, 'No export statements found');
        return;
      }

      this.pass(testName);
    } catch (error) {
      this.fail(testName, `Failed to read file: ${error.message}`);
    }
  }

  async testDataManager() {
    const testName = 'DataManager functionality';

    try {
      // Check if data chunks exist
      const dataDir = path.join(__dirname, '../docs/new/js/data');
      const lineagesDir = path.join(dataDir, 'lineages');

      // Check metadata
      const metadataPath = path.join(dataDir, 'metadata.json');
      await fs.access(metadataPath);

      // Check lineage files
      const lineageFiles = await fs.readdir(lineagesDir);
      const jsonFiles = lineageFiles.filter(f => f.endsWith('.json'));

      if (jsonFiles.length === 0) {
        this.fail(testName, 'No lineage files found');
        return;
      }

      // Test a sample lineage file
      const sampleFile = path.join(lineagesDir, jsonFiles[0]);
      const content = await fs.readFile(sampleFile, 'utf8');
      const data = JSON.parse(content);

      if (!data.people || !Array.isArray(data.people)) {
        this.fail(testName, 'Lineage file missing people array');
        return;
      }

      this.pass(testName);
    } catch (error) {
      this.fail(testName, `DataManager test failed: ${error.message}`);
    }
  }

  pass(testName) {
    this.testResults.passed++;
    this.testResults.tests.push({ name: testName, status: 'PASS' });
    console.log(`  ✅ ${testName}`);
  }

  fail(testName, message) {
    this.testResults.failed++;
    this.testResults.tests.push({ name: testName, status: 'FAIL', message });
    console.log(`  ❌ ${testName}: ${message}`);
  }

  printResults() {
    console.log('\n=== Test Results ===');
    console.log(`Tests run: ${this.testResults.passed + this.testResults.failed}`);
    console.log(`Passed: ${this.testResults.passed}`);
    console.log(`Failed: ${this.testResults.failed}`);

    if (this.testResults.failed === 0) {
      console.log('\n🎉 All tests passed!');
    } else {
      console.log('\n❌ Some tests failed');
    }
  }
}

// Run if called directly
if (require.main === module) {
  const tester = new NavigationTester();
  tester.run();
}

module.exports = NavigationTester;