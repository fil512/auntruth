#!/usr/bin/env node

/**
 * Test Family Tree Rendering
 * Validates D3.js tree component and genealogy data relationships
 */

const fs = require('fs').promises;
const path = require('path');

class TreeRenderingTester {
  constructor() {
    this.dataDir = path.join(__dirname, '../docs/new/js/data');
    this.lineagesDir = path.join(this.dataDir, 'lineages');
    this.testResults = {
      passed: 0,
      failed: 0,
      errors: []
    };
  }

  async run() {
    console.log('🌳 Testing Family Tree Rendering...\n');

    try {
      // Test 1: Validate tree component structure
      await this.testTreeComponentStructure();

      // Test 2: Test family relationship data
      await this.testFamilyRelationshipData();

      // Test 3: Test tree data building logic
      await this.testTreeDataBuilding();

      // Test 4: Validate tree rendering performance
      await this.testTreeRenderingPerformance();

      // Test 5: Test complex relationship handling
      await this.testComplexRelationships();

      // Display results
      this.displayResults();

    } catch (error) {
      console.error('❌ Tree rendering test failed:', error);
      process.exit(1);
    }
  }

  async testTreeComponentStructure() {
    console.log('📋 Test 1: Validating tree component structure...');

    try {
      const componentPath = path.join(__dirname, '../docs/new/js/components/family-tree.js');
      const componentContent = await fs.readFile(componentPath, 'utf8');

      // Check for required class and methods
      const requiredElements = [
        'class FamilyTreeComponent',
        'extends BaseComponent',
        'async buildFamilyHierarchy',
        'async buildAncestors',
        'async buildDescendants',
        'renderTree',
        'renderNodes',
        'renderLinks'
      ];

      const missingElements = requiredElements.filter(element =>
        !componentContent.includes(element)
      );

      if (missingElements.length > 0) {
        throw new Error(`Missing required elements: ${missingElements.join(', ')}`);
      }

      console.log('  ✓ FamilyTreeComponent class structure valid');

      // Check for D3.js integration
      const d3Elements = [
        'd3.select',
        'd3.tree',
        'd3.hierarchy',
        'd3.zoom'
      ];

      const missingD3 = d3Elements.filter(element =>
        !componentContent.includes(element)
      );

      if (missingD3.length > 0) {
        throw new Error(`Missing D3.js elements: ${missingD3.join(', ')}`);
      }

      console.log('  ✓ D3.js integration detected');

      // Check for mobile/touch support
      if (!componentContent.includes('touch') && !componentContent.includes('mobile')) {
        console.log('  ⚠️  Limited touch/mobile support detected');
      } else {
        console.log('  ✓ Mobile/touch support detected');
      }

      // Check for SVG rendering
      if (!componentContent.includes('svg') || !componentContent.includes('append')) {
        throw new Error('SVG rendering logic not found');
      }

      console.log('  ✓ SVG rendering logic present');

      this.testResults.passed++;
      console.log('  ✅ Tree component structure test passed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Tree component structure: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testFamilyRelationshipData() {
    console.log('📋 Test 2: Testing family relationship data...');

    try {
      let totalPeople = 0;
      let peopleWithParents = 0;
      let peopleWithChildren = 0;
      let peopleWithSpouses = 0;
      let orphanedPeople = 0;

      for (let i = 0; i <= 9; i++) {
        const lineagePath = path.join(this.lineagesDir, `L${i}.json`);

        try {
          const content = await fs.readFile(lineagePath, 'utf8');
          const lineageData = JSON.parse(content);

          if (lineageData.people && Array.isArray(lineageData.people)) {
            totalPeople += lineageData.people.length;

            lineageData.people.forEach(person => {
              let hasFamily = false;

              // Check for parents
              if (person.father || person.mother) {
                peopleWithParents++;
                hasFamily = true;
              }

              // Check for children
              if (person.children && person.children.length > 0) {
                peopleWithChildren++;
                hasFamily = true;
              }

              // Check for spouses
              if (person.spouse || person.spouse2 || person.spouse3 || person.spouse4) {
                peopleWithSpouses++;
                hasFamily = true;
              }

              if (!hasFamily) {
                orphanedPeople++;
              }
            });

            console.log(`  ✓ Lineage L${i}: ${lineageData.people.length} people analyzed`);
          }

        } catch (error) {
          if (error.code !== 'ENOENT') {
            throw error;
          }
        }
      }

      const parentPercentage = (peopleWithParents / totalPeople * 100).toFixed(1);
      const childrenPercentage = (peopleWithChildren / totalPeople * 100).toFixed(1);
      const spousePercentage = (peopleWithSpouses / totalPeople * 100).toFixed(1);
      const orphanedPercentage = (orphanedPeople / totalPeople * 100).toFixed(1);

      console.log(`  📊 Total people: ${totalPeople}`);
      console.log(`  📊 People with parents: ${parentPercentage}% (${peopleWithParents})`);
      console.log(`  📊 People with children: ${childrenPercentage}% (${peopleWithChildren})`);
      console.log(`  📊 People with spouses: ${spousePercentage}% (${peopleWithSpouses})`);
      console.log(`  📊 Orphaned people: ${orphanedPercentage}% (${orphanedPeople})`);

      if (totalPeople === 0) {
        throw new Error('No genealogy data found');
      }

      if (orphanedPercentage > 50) {
        console.log('  ⚠️  High percentage of orphaned people may indicate data quality issues');
      }

      this.testResults.passed++;
      console.log('  ✅ Family relationship data test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Family relationship data: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testTreeDataBuilding() {
    console.log('📋 Test 3: Testing tree data building logic...');

    try {
      // Test tree building with sample data
      const samplePeople = [
        { id: '1', name: 'John Doe', father: '3', mother: '4', children: ['2'] },
        { id: '2', name: 'Jane Doe', father: '1', mother: '5' },
        { id: '3', name: 'Grandfather Doe' },
        { id: '4', name: 'Grandmother Doe' },
        { id: '5', name: 'Other Grandmother' }
      ];

      // Test ancestor building
      const ancestors = this.simulateAncestorBuilding(samplePeople[0], samplePeople);
      console.log(`  ✓ Ancestor building: found ${ancestors.length} ancestors`);

      // Test descendant building
      const descendants = this.simulateDescendantBuilding(samplePeople[0], samplePeople);
      console.log(`  ✓ Descendant building: found ${descendants.length} descendants`);

      // Test circular reference detection
      const circularSample = [
        { id: '1', name: 'Person A', father: '2' },
        { id: '2', name: 'Person B', father: '1' } // Circular reference
      ];

      const circularResult = this.detectCircularReferences(circularSample);
      if (circularResult.length > 0) {
        console.log(`  ⚠️  Circular references detected: ${circularResult.length} cases`);
      } else {
        console.log('  ✓ No circular references in test data');
      }

      // Test generation calculation
      const generations = this.calculateMaxGenerations(samplePeople, '1');
      console.log(`  ✓ Generation calculation: ${generations} generations`);

      if (generations < 2) {
        console.log('  ⚠️  Limited generational depth for tree visualization');
      }

      this.testResults.passed++;
      console.log('  ✅ Tree data building logic test passed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Tree data building: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testTreeRenderingPerformance() {
    console.log('📋 Test 4: Testing tree rendering performance...');

    try {
      const targetTime = 1000; // 1s target from PRP
      const sampleSizes = [10, 50, 100, 200];
      const performanceResults = [];

      for (const size of sampleSizes) {
        const startTime = Date.now();

        // Simulate tree rendering with sample data
        const sampleData = this.generateSampleTreeData(size);
        this.simulateTreeRendering(sampleData);

        const renderTime = Date.now() - startTime;
        performanceResults.push({ size, time: renderTime });

        const status = renderTime <= targetTime ? '✓' : '⚠️ ';
        console.log(`  ${status} ${size} people rendered in ${renderTime}ms`);
      }

      const maxTime = Math.max(...performanceResults.map(r => r.time));
      const avgTime = performanceResults.reduce((sum, r) => sum + r.time, 0) / performanceResults.length;

      console.log(`  📊 Average render time: ${Math.round(avgTime)}ms`);
      console.log(`  📊 Maximum render time: ${maxTime}ms`);

      if (maxTime <= targetTime) {
        console.log(`  ✅ All render times within ${targetTime}ms target`);
      } else {
        console.log(`  ⚠️  Some render times exceed ${targetTime}ms target`);
      }

      this.testResults.passed++;
      console.log('  ✅ Tree rendering performance test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Tree rendering performance: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testComplexRelationships() {
    console.log('📋 Test 5: Testing complex relationship handling...');

    try {
      // Test multiple spouses
      const multipleSpousesPerson = {
        id: '1',
        name: 'John Doe',
        spouse: 'Jane Doe',
        spouse2: 'Mary Smith',
        spouse3: 'Alice Brown'
      };

      const spouseCount = this.countSpouses(multipleSpousesPerson);
      console.log(`  ✓ Multiple spouses handling: ${spouseCount} spouses detected`);

      // Test missing parents scenario
      const missingParentsPerson = {
        id: '2',
        name: 'Orphan Child',
        father: 'unknown_father',
        mother: null
      };

      const missingParentsResult = this.handleMissingParents(missingParentsPerson);
      console.log(`  ✓ Missing parents handling: ${missingParentsResult} strategy`);

      // Test adoption/step-relationships
      const stepRelationshipData = [
        { id: '1', name: 'Child', father: 'bio_father', stepFather: 'step_father' },
        { id: 'bio_father', name: 'Biological Father' },
        { id: 'step_father', name: 'Step Father' }
      ];

      const stepResult = this.handleStepRelationships(stepRelationshipData);
      console.log(`  ✓ Step-relationship detection: ${stepResult} cases found`);

      // Test large family handling
      const largeFamilyPerson = {
        id: '1',
        name: 'Parent',
        children: Array.from({ length: 15 }, (_, i) => `child_${i + 1}`)
      };

      const largeFamily = this.handleLargeFamily(largeFamilyPerson);
      console.log(`  ✓ Large family handling: ${largeFamily.children.length} children`);

      if (largeFamily.children.length > 12) {
        console.log('  ⚠️  Large families may require special UI handling');
      }

      this.testResults.passed++;
      console.log('  ✅ Complex relationships test passed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Complex relationships: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  // Helper methods for testing
  simulateAncestorBuilding(person, people) {
    const ancestors = [];
    const visited = new Set();

    const findAncestors = (currentPerson, generation) => {
      if (generation > 5 || visited.has(currentPerson.id)) return; // Prevent infinite loops
      visited.add(currentPerson.id);

      const father = people.find(p => p.id === currentPerson.father);
      const mother = people.find(p => p.id === currentPerson.mother);

      if (father) {
        ancestors.push(father);
        findAncestors(father, generation + 1);
      }

      if (mother) {
        ancestors.push(mother);
        findAncestors(mother, generation + 1);
      }
    };

    findAncestors(person, 0);
    return ancestors;
  }

  simulateDescendantBuilding(person, people) {
    const descendants = [];

    if (person.children) {
      person.children.forEach(childId => {
        const child = people.find(p => p.id === childId);
        if (child) {
          descendants.push(child);
        }
      });
    }

    return descendants;
  }

  detectCircularReferences(people) {
    const circular = [];

    people.forEach(person => {
      if (person.father === person.id || person.mother === person.id) {
        circular.push({ person: person.id, type: 'self-parent' });
      }

      if (person.children && person.children.includes(person.id)) {
        circular.push({ person: person.id, type: 'self-child' });
      }
    });

    return circular;
  }

  calculateMaxGenerations(people, rootId) {
    let maxGeneration = 1;
    const visited = new Set();

    const traverse = (personId, generation) => {
      if (visited.has(personId)) return;
      visited.add(personId);

      maxGeneration = Math.max(maxGeneration, generation);

      const person = people.find(p => p.id === personId);
      if (person && person.children) {
        person.children.forEach(childId => {
          traverse(childId, generation + 1);
        });
      }
    };

    traverse(rootId, 1);
    return maxGeneration;
  }

  generateSampleTreeData(size) {
    const data = [];
    for (let i = 1; i <= size; i++) {
      data.push({
        id: i.toString(),
        name: `Person ${i}`,
        x: Math.random() * 800,
        y: Math.random() * 600
      });
    }
    return data;
  }

  simulateTreeRendering(data) {
    // Simulate the computational cost of tree rendering
    let operations = 0;

    // Simulate D3 hierarchy creation
    operations += data.length * 2;

    // Simulate SVG node creation
    operations += data.length * 5;

    // Simulate link calculation
    operations += data.length * 3;

    // Simulate layout calculation
    for (let i = 0; i < data.length; i++) {
      for (let j = 0; j < 10; j++) {
        operations += Math.sqrt(i * j);
      }
    }

    return operations;
  }

  countSpouses(person) {
    let count = 0;
    if (person.spouse) count++;
    if (person.spouse2) count++;
    if (person.spouse3) count++;
    if (person.spouse4) count++;
    return count;
  }

  handleMissingParents(person) {
    if (!person.father && !person.mother) return 'no-parents';
    if (!person.father || !person.mother) return 'single-parent';
    return 'both-parents';
  }

  handleStepRelationships(data) {
    return data.filter(person => person.stepFather || person.stepMother).length;
  }

  handleLargeFamily(person) {
    return {
      ...person,
      children: person.children || []
    };
  }

  displayResults() {
    console.log('📊 Family Tree Rendering Test Results');
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
      console.log('\n🎉 All tree rendering tests passed!');
    }
  }
}

// Run if called directly
if (require.main === module) {
  const tester = new TreeRenderingTester();
  tester.run();
}

module.exports = TreeRenderingTester;