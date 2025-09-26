# Testing & Quality Assurance Standards

## Testing Strategy Overview

### Testing Pyramid
1. **Unit Tests:** Individual component functionality
2. **Integration Tests:** Component interaction and data flow
3. **End-to-End Tests:** Complete user workflows
4. **Performance Tests:** Speed and responsiveness
5. **Accessibility Tests:** WCAG compliance and usability
6. **Cross-Browser Tests:** Compatibility across target browsers

## Component Testing Requirements

### Functional Testing Checklist
- [ ] **Component Initialization:** Component loads and initializes without errors
- [ ] **Data Loading:** Component correctly loads and processes genealogy data
- [ ] **User Interactions:** All interactive elements respond correctly
- [ ] **State Management:** Component state updates correctly
- [ ] **Error Handling:** Graceful error handling and fallback content
- [ ] **Memory Management:** No memory leaks during component lifecycle

### Data Accuracy Testing
```javascript
// Example test pattern for genealogy data
class DataAccuracyTest {
  testPersonRelationships(personId) {
    const person = dataManager.getPersonData(personId);

    // Verify all family relationships are bidirectional
    if (person.father) {
      const father = dataManager.getPersonData(person.father);
      assert(father.children.includes(personId));
    }

    // Verify cross-lineage relationships
    if (person.spouse) {
      const spouse = dataManager.getPersonData(person.spouse);
      assert(spouse.lineage !== person.lineage); // Cross-lineage marriage
    }
  }
}
```

## Cross-Browser Testing Matrix

### Required Browser Testing
| Browser | Desktop | Mobile | Priority |
|---------|---------|---------|----------|
| Chrome | 80+ | 80+ | Critical |
| Firefox | 75+ | 75+ | High |
| Safari | 13+ | 13+ | Critical |
| Edge | 80+ | - | Medium |
| Samsung Internet | - | 12+ | Medium |

### Progressive Enhancement Testing
```javascript
// Test without JavaScript
function testNoJavaScript() {
  // Disable JavaScript in browser
  // Verify core functionality:
  // - Navigation works
  // - Person pages display
  // - Basic search works
  // - All content accessible
}

// Test with limited JavaScript
function testPartialJavaScript() {
  // Test with older browser capabilities
  // Verify graceful degradation
}
```

## Performance Testing Standards

### Performance Metrics
- **Initial Page Load:** < 2 seconds on 3G
- **Component Load:** < 500ms
- **User Interaction Response:** < 100ms
- **Search Response:** < 200ms
- **Family Tree Render:** < 500ms for 3 generations
- **Timeline Render:** < 500ms for typical date range

### Performance Testing Tools
```javascript
// Performance measurement
function measurePerformance(operation, expectedTime) {
  const startTime = performance.now();

  operation().then(() => {
    const duration = performance.now() - startTime;
    console.log(`Operation completed in ${duration}ms`);

    if (duration > expectedTime) {
      console.warn(`Performance threshold exceeded: ${duration}ms > ${expectedTime}ms`);
    }
  });
}

// Memory usage monitoring
function monitorMemoryUsage() {
  if (performance.memory) {
    const { usedJSHeapSize, totalJSHeapSize } = performance.memory;
    console.log(`Memory usage: ${usedJSHeapSize} / ${totalJSHeapSize}`);
  }
}
```

## Mobile Testing Requirements

### Device Testing Matrix
- **iPhone SE (375px)** - Small mobile screen
- **iPhone 12 (390px)** - Standard mobile screen
- **Samsung Galaxy S21 (384px)** - Android standard
- **iPad (768px)** - Tablet breakpoint
- **iPad Pro (1024px)** - Large tablet

### Touch Interaction Testing
```javascript
class TouchTestSuite {
  testTouchTargets() {
    const interactiveElements = document.querySelectorAll('button, a, input');

    interactiveElements.forEach(element => {
      const rect = element.getBoundingClientRect();
      const minSize = 44; // WCAG minimum

      assert(rect.width >= minSize, `Touch target too small: ${rect.width}px`);
      assert(rect.height >= minSize, `Touch target too small: ${rect.height}px`);
    });
  }

  testSwipeGestures() {
    // Test swipe navigation between family members
    // Test photo gallery swipes
    // Test timeline pan gestures
  }

  testPinchZoom() {
    // Test family tree zoom
    // Test image zoom
    // Test timeline zoom
  }
}
```

## Accessibility Testing Standards

### WCAG 2.1 AA Compliance
- **Keyboard Navigation:** All functionality accessible via keyboard
- **Screen Reader Support:** Proper ARIA labels and semantic HTML
- **Color Contrast:** Minimum 4.5:1 ratio for normal text
- **Focus Management:** Visible focus indicators and logical focus order
- **Alternative Text:** Images have descriptive alt text

### Accessibility Testing Tools
```javascript
// Automated accessibility testing
function runAccessibilityTests() {
  // Use axe-core for automated testing
  axe.run(document, (err, results) => {
    if (results.violations.length > 0) {
      console.error('Accessibility violations found:', results.violations);
    }
  });
}

// Manual testing checklist
const accessibilityChecklist = [
  'Tab navigation works through all interactive elements',
  'Screen reader announces all important information',
  'All images have alt text or are marked decorative',
  'Color is not the only way to convey information',
  'All form elements have labels',
  'Page has proper heading structure',
  'Focus indicators are visible',
  'No keyboard traps exist'
];
```

## Integration Testing Patterns

### Component Integration Testing
```javascript
class IntegrationTestSuite {
  async testSearchToFamilyTree() {
    // Test: Search for person → Click result → View family tree
    const searchComponent = new SearchComponent();
    const treeComponent = new FamilyTreeComponent();

    await searchComponent.performSearch('Hagborg');
    const firstResult = searchComponent.getFirstResult();

    // Simulate click on search result
    firstResult.click();

    // Verify family tree loads with correct person
    assert(treeComponent.focusPersonId === firstResult.personId);
  }

  async testNavigationToTimeline() {
    // Test: Person page → Navigation → Timeline → Filtered view
    const navigation = new NavigationComponent();
    const timeline = new TimelineComponent();

    // Navigate from person page to timeline
    navigation.navigateToTimeline();

    // Verify timeline loads with person's events highlighted
    assert(timeline.hasPersonEvents(currentPersonId));
  }
}
```

### Data Consistency Testing
```javascript
class DataConsistencyTests {
  testCrossLineageReferences() {
    // Verify all cross-lineage family references are valid
    // Test that L1 person's spouse in L2 references back correctly
  }

  testPhotoReferences() {
    // Verify all THF and XI references are valid
    // Test that photo galleries link to existing images
  }

  testURLConsistency() {
    // Verify all person URLs are valid and accessible
    // Test that lineage paths are correct
  }
}
```

## Test Automation Framework

### Continuous Integration Testing
```yaml
# GitHub Actions test workflow
name: Quality Assurance Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration

      - name: Run accessibility tests
        run: npm run test:accessibility

      - name: Run performance tests
        run: npm run test:performance

      - name: Cross-browser testing
        run: npm run test:browsers
```

## Quality Gates

### Definition of Done
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Cross-browser testing complete
- [ ] Mobile testing on real devices complete
- [ ] Accessibility testing passes WCAG 2.1 AA
- [ ] Performance metrics meet requirements
- [ ] Code review completed
- [ ] Documentation updated
- [ ] No breaking changes to existing functionality
- [ ] Legacy URL compatibility verified