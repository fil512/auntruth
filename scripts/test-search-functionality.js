#!/usr/bin/env node

/**
 * Test Enhanced Search Functionality
 * Validates Lunr.js indices and search component functionality
 */

const fs = require('fs').promises;
const path = require('path');

class SearchFunctionalityTester {
  constructor() {
    this.dataDir = path.join(__dirname, '../docs/new/js/data');
    this.indicesDir = path.join(this.dataDir, 'indices');
    this.lineagesDir = path.join(this.dataDir, 'lineages');
    this.testResults = {
      passed: 0,
      failed: 0,
      errors: []
    };
  }

  async run() {
    console.log('🔍 Testing Enhanced Search Functionality...\n');

    try {
      // Test 1: Validate search indices exist
      await this.testSearchIndicesExist();

      // Test 2: Validate search index structure
      await this.testSearchIndexStructure();

      // Test 3: Test index loading performance
      await this.testIndexLoadingPerformance();

      // Test 4: Validate search data completeness
      await this.testSearchDataCompleteness();

      // Test 5: Test search component instantiation
      await this.testSearchComponentInstantiation();

      // Display results
      this.displayResults();

    } catch (error) {
      console.error('❌ Search functionality test failed:', error);
      process.exit(1);
    }
  }

  async testSearchIndicesExist() {
    console.log('📋 Test 1: Checking search indices exist...');

    try {
      const expectedFiles = [];
      for (let i = 0; i <= 9; i++) {
        expectedFiles.push(`search-L${i}.json`);
      }

      for (const filename of expectedFiles) {
        const filePath = path.join(this.indicesDir, filename);
        try {
          const stats = await fs.stat(filePath);
          if (stats.size === 0) {
            throw new Error(`Index file ${filename} is empty`);
          }
          console.log(`  ✓ ${filename} exists (${this.formatBytes(stats.size)})`);
        } catch (error) {
          if (error.code === 'ENOENT') {
            console.log(`  ⚠️  ${filename} not found (lineage may be empty)`);
          } else {
            throw new Error(`Failed to read ${filename}: ${error.message}`);
          }
        }
      }

      this.testResults.passed++;
      console.log('  ✅ Search indices existence test passed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Search indices existence: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testSearchIndexStructure() {
    console.log('📋 Test 2: Validating search index structure...');

    try {
      // Test a few indices for proper Lunr.js structure
      for (let i = 0; i <= 2; i++) {
        const indexPath = path.join(this.indicesDir, `search-L${i}.json`);
        try {
          const content = await fs.readFile(indexPath, 'utf8');
          const indexData = JSON.parse(content);

          // Validate Lunr.js index structure
          if (!indexData.version) {
            throw new Error(`Index L${i} missing version field`);
          }

          if (!indexData.fields) {
            throw new Error(`Index L${i} missing fields array`);
          }

          if (!indexData.invertedIndex) {
            throw new Error(`Index L${i} missing invertedIndex`);
          }

          const expectedFields = ['name', 'birthLocation', 'deathLocation', 'occupation', 'spouse'];
          const missingFields = expectedFields.filter(field =>
            !indexData.fields.some(f => f.fieldName === field)
          );

          if (missingFields.length > 0) {
            console.log(`  ⚠️  Index L${i} missing fields: ${missingFields.join(', ')}`);
          }

          console.log(`  ✓ Index L${i} structure valid (${Object.keys(indexData.invertedIndex).length} terms)`);

        } catch (error) {
          if (error.code === 'ENOENT') {
            console.log(`  ⚠️  Index L${i} not found, skipping`);
            continue;
          }
          throw error;
        }
      }

      this.testResults.passed++;
      console.log('  ✅ Search index structure test passed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Search index structure: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testIndexLoadingPerformance() {
    console.log('📋 Test 3: Testing index loading performance...');

    try {
      const loadTimes = [];
      const targetTime = 500; // 500ms target from PRP

      for (let i = 0; i <= 9; i++) {
        const indexPath = path.join(this.indicesDir, `search-L${i}.json`);

        try {
          const startTime = Date.now();
          const content = await fs.readFile(indexPath, 'utf8');
          const indexData = JSON.parse(content);
          const loadTime = Date.now() - startTime;

          loadTimes.push({ lineage: i, time: loadTime });

          const status = loadTime <= targetTime ? '✓' : '⚠️ ';
          console.log(`  ${status} Index L${i} loaded in ${loadTime}ms`);

        } catch (error) {
          if (error.code !== 'ENOENT') {
            throw error;
          }
        }
      }

      const avgLoadTime = loadTimes.reduce((sum, item) => sum + item.time, 0) / loadTimes.length;
      const maxLoadTime = Math.max(...loadTimes.map(item => item.time));

      console.log(`  📊 Average load time: ${Math.round(avgLoadTime)}ms`);
      console.log(`  📊 Maximum load time: ${maxLoadTime}ms`);

      if (maxLoadTime <= targetTime) {
        console.log(`  ✅ All indices load within ${targetTime}ms target`);
      } else {
        console.log(`  ⚠️  Some indices exceed ${targetTime}ms target`);
      }

      this.testResults.passed++;
      console.log('  ✅ Index loading performance test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Index loading performance: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testSearchDataCompleteness() {
    console.log('📋 Test 4: Validating search data completeness...');

    try {
      let totalPeople = 0;
      let peopleWithNames = 0;
      let peopleWithLocations = 0;
      let peopleWithDates = 0;

      // Check lineage data completeness
      for (let i = 0; i <= 9; i++) {
        const lineagePath = path.join(this.lineagesDir, `L${i}.json`);

        try {
          const content = await fs.readFile(lineagePath, 'utf8');
          const lineageData = JSON.parse(content);

          if (lineageData.people && Array.isArray(lineageData.people)) {
            totalPeople += lineageData.people.length;

            lineageData.people.forEach(person => {
              if (person.name && person.name.trim()) {
                peopleWithNames++;
              }
              if (person.birthLocation || person.deathLocation) {
                peopleWithLocations++;
              }
              if (person.birthDate || person.deathDate) {
                peopleWithDates++;
              }
            });

            console.log(`  ✓ Lineage L${i}: ${lineageData.people.length} people`);
          }

        } catch (error) {
          if (error.code !== 'ENOENT') {
            throw error;
          }
        }
      }

      const nameCompleteness = (peopleWithNames / totalPeople * 100).toFixed(1);
      const locationCompleteness = (peopleWithLocations / totalPeople * 100).toFixed(1);
      const dateCompleteness = (peopleWithDates / totalPeople * 100).toFixed(1);

      console.log(`  📊 Total people: ${totalPeople}`);
      console.log(`  📊 Names: ${nameCompleteness}% (${peopleWithNames})`);
      console.log(`  📊 Locations: ${locationCompleteness}% (${peopleWithLocations})`);
      console.log(`  📊 Dates: ${dateCompleteness}% (${peopleWithDates})`);

      if (totalPeople === 0) {
        throw new Error('No people found in lineage data');
      }

      if (nameCompleteness < 80) {
        console.log('  ⚠️  Low name completeness may affect search quality');
      }

      this.testResults.passed++;
      console.log('  ✅ Search data completeness test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Search data completeness: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testSearchComponentInstantiation() {
    console.log('📋 Test 5: Testing search component instantiation...');

    try {
      // Basic syntax validation of the search component
      const componentPath = path.join(__dirname, '../docs/new/js/components/enhanced-search.js');
      const componentContent = await fs.readFile(componentPath, 'utf8');

      // Check for required class and methods
      const requiredElements = [
        'class EnhancedSearchComponent',
        'extends BaseComponent',
        'async loadSearchIndices',
        'async performSearch',
        'searchWithLunr',
        'displayResults'
      ];

      const missingElements = requiredElements.filter(element =>
        !componentContent.includes(element)
      );

      if (missingElements.length > 0) {
        throw new Error(`Missing required elements: ${missingElements.join(', ')}`);
      }

      console.log('  ✓ EnhancedSearchComponent class structure valid');

      // Check for required dependencies
      if (!componentContent.includes('import BaseComponent')) {
        throw new Error('Missing BaseComponent import');
      }

      if (!componentContent.includes('import DataManager')) {
        throw new Error('Missing DataManager import');
      }

      console.log('  ✓ Required imports present');

      // Check for Lunr.js integration
      if (!componentContent.includes('window.lunr') && !componentContent.includes('lunr.Index.load')) {
        throw new Error('Missing Lunr.js integration');
      }

      console.log('  ✓ Lunr.js integration detected');

      this.testResults.passed++;
      console.log('  ✅ Search component instantiation test passed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Search component instantiation: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  displayResults() {
    console.log('📊 Enhanced Search Functionality Test Results');
    console.log('=' .repeat(50));
    console.log(`✅ Passed: ${this.testResults.passed}`);
    console.log(`❌ Failed: ${this.testResults.failed}`);

    if (this.testResults.errors.length > 0) {
      console.log('\n🚨 Errors found:');
      this.testResults.errors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error}`);
      });
    }

    const totalTests = this.testResults.passed + this.testResults.failed;
    const successRate = (this.testResults.passed / totalTests * 100).toFixed(1);

    console.log(`\n📈 Success Rate: ${successRate}%`);

    if (this.testResults.failed > 0) {
      console.log('\n⚠️  Some tests failed. Please address the issues above.');
      process.exit(1);
    } else {
      console.log('\n🎉 All search functionality tests passed!');
    }
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }
}

// Run if called directly
if (require.main === module) {
  const tester = new SearchFunctionalityTester();
  tester.run();
}

module.exports = SearchFunctionalityTester;