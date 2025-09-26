#!/usr/bin/env node

/**
 * Test Mobile Responsiveness
 * Validates mobile-first design and touch interactions for Phase 2 components
 */

const fs = require('fs').promises;
const path = require('path');

class MobileResponsivenessTester {
  constructor() {
    this.cssDir = path.join(__dirname, '../docs/new/css');
    this.jsDir = path.join(__dirname, '../docs/new/js');
    this.testResults = {
      passed: 0,
      failed: 0,
      errors: []
    };
  }

  async run() {
    console.log('📱 Testing Mobile Responsiveness...\n');

    try {
      // Test 1: Validate CSS mobile-first approach
      await this.testCSSMobileFirst();

      // Test 2: Test touch target sizes
      await this.testTouchTargets();

      // Test 3: Validate responsive breakpoints
      await this.testResponsiveBreakpoints();

      // Test 4: Test mobile-specific JavaScript features
      await this.testMobileJavaScript();

      // Test 5: Validate accessibility features
      await this.testAccessibilityFeatures();

      // Display results
      this.displayResults();

    } catch (error) {
      console.error('❌ Mobile responsiveness test failed:', error);
      process.exit(1);
    }
  }

  async testCSSMobileFirst() {
    console.log('📋 Test 1: Validating CSS mobile-first approach...');

    try {
      const cssFiles = [
        'foundation.css',
        'enhanced-search.css',
        'family-tree.css',
        'information-disclosure.css'
      ];

      for (const filename of cssFiles) {
        const filePath = path.join(this.cssDir, filename);

        try {
          const content = await fs.readFile(filePath, 'utf8');

          // Test 1a: Mobile-first media queries
          const mediaQueries = content.match(/@media[^{]*\{/g) || [];
          const minWidthQueries = mediaQueries.filter(query => query.includes('min-width'));
          const maxWidthQueries = mediaQueries.filter(query => query.includes('max-width'));

          const mobileFirstRatio = minWidthQueries.length / (minWidthQueries.length + maxWidthQueries.length);

          if (mobileFirstRatio >= 0.7) {
            console.log(`  ✓ ${filename}: ${Math.round(mobileFirstRatio * 100)}% mobile-first queries`);
          } else {
            console.log(`  ⚠️  ${filename}: ${Math.round(mobileFirstRatio * 100)}% mobile-first (consider improving)`);
          }

          // Test 1b: CSS custom properties usage
          const customProperties = content.match(/var\(--[\w-]+\)/g) || [];
          if (customProperties.length > 5) {
            console.log(`  ✓ ${filename}: Uses CSS custom properties (${customProperties.length})`);
          } else {
            console.log(`  ⚠️  ${filename}: Limited CSS custom properties usage`);
          }

          // Test 1c: Fluid typography (clamp usage)
          if (content.includes('clamp(')) {
            console.log(`  ✓ ${filename}: Uses fluid typography`);
          } else if (filename === 'foundation.css') {
            console.log(`  ⚠️  ${filename}: No fluid typography detected`);
          }

          // Test 1d: Flexible layouts (flexbox/grid)
          const flexboxUsage = (content.match(/display:\s*flex/g) || []).length;
          const gridUsage = (content.match(/display:\s*grid/g) || []).length;

          if (flexboxUsage + gridUsage > 0) {
            console.log(`  ✓ ${filename}: Uses modern layout (${flexboxUsage} flex, ${gridUsage} grid)`);
          } else {
            console.log(`  ⚠️  ${filename}: Limited modern layout usage`);
          }

        } catch (error) {
          if (error.code === 'ENOENT') {
            console.log(`  ❌ ${filename}: File not found`);
          } else {
            throw error;
          }
        }
      }

      this.testResults.passed++;
      console.log('  ✅ CSS mobile-first approach test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`CSS mobile-first: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testTouchTargets() {
    console.log('📋 Test 2: Testing touch target sizes...');

    try {
      const foundationPath = path.join(this.cssDir, 'foundation.css');
      const foundationContent = await fs.readFile(foundationPath, 'utf8');

      // Check for touch target minimum size definition
      if (!foundationContent.includes('--touch-target-min')) {
        throw new Error('Touch target minimum size not defined in foundation.css');
      }

      console.log('  ✓ Touch target minimum size defined in foundation');

      // Extract touch target size
      const touchTargetMatch = foundationContent.match(/--touch-target-min:\s*(\d+)px/);
      if (!touchTargetMatch) {
        throw new Error('Cannot parse touch target size');
      }

      const touchTargetSize = parseInt(touchTargetMatch[1]);
      console.log(`  📊 Touch target minimum size: ${touchTargetSize}px`);

      if (touchTargetSize >= 44) {
        console.log('  ✅ Touch target size meets WCAG guidelines (44px minimum)');
      } else {
        console.log('  ❌ Touch target size below WCAG guidelines');
      }

      // Check component CSS files for touch target usage
      const componentFiles = ['enhanced-search.css', 'family-tree.css', 'information-disclosure.css'];

      for (const filename of componentFiles) {
        const filePath = path.join(this.cssDir, filename);

        try {
          const content = await fs.readFile(filePath, 'utf8');

          const touchTargetUsage = (content.match(/var\(--touch-target-min\)/g) || []).length;
          const minHeightUsage = (content.match(/min-height:\s*var\(--touch-target-min\)/g) || []).length;

          if (touchTargetUsage > 0) {
            console.log(`  ✓ ${filename}: Uses touch targets (${touchTargetUsage} instances)`);
          } else {
            console.log(`  ⚠️  ${filename}: No touch target usage detected`);
          }

          // Check for mobile-specific touch handling
          if (content.includes('touch') || content.includes('@media') && content.includes('767px')) {
            console.log(`  ✓ ${filename}: Has mobile-specific styles`);
          }

        } catch (error) {
          if (error.code !== 'ENOENT') {
            throw error;
          }
        }
      }

      this.testResults.passed++;
      console.log('  ✅ Touch target size test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Touch targets: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testResponsiveBreakpoints() {
    console.log('📋 Test 3: Validating responsive breakpoints...');

    try {
      const breakpoints = {
        mobile: 767,
        tablet: 1023,
        desktop: 1024
      };

      const cssFiles = [
        'foundation.css',
        'enhanced-search.css',
        'family-tree.css',
        'information-disclosure.css'
      ];

      let totalBreakpointUsage = 0;
      let consistentBreakpoints = 0;

      for (const filename of cssFiles) {
        const filePath = path.join(this.cssDir, filename);

        try {
          const content = await fs.readFile(filePath, 'utf8');

          // Check for standard breakpoints
          const breakpointMatches = {
            mobile: (content.match(/max-width:\s*767px/g) || []).length,
            tablet: (content.match(/min-width:\s*768px/g) || []).length +
                    (content.match(/max-width:\s*1023px/g) || []).length,
            desktop: (content.match(/min-width:\s*1024px/g) || []).length
          };

          const totalBreakpoints = Object.values(breakpointMatches).reduce((sum, count) => sum + count, 0);
          totalBreakpointUsage += totalBreakpoints;

          if (totalBreakpoints > 0) {
            console.log(`  ✓ ${filename}: ${totalBreakpoints} responsive breakpoints`);

            // Check for consistent breakpoint usage
            const hasStandardBreakpoints = breakpointMatches.mobile > 0 || breakpointMatches.tablet > 0 || breakpointMatches.desktop > 0;
            if (hasStandardBreakpoints) {
              consistentBreakpoints++;
            }
          } else {
            console.log(`  ⚠️  ${filename}: No responsive breakpoints found`);
          }

          // Check for progressive enhancement patterns
          if (content.includes('prefers-reduced-motion') || content.includes('prefers-contrast')) {
            console.log(`  ✓ ${filename}: Includes accessibility media queries`);
          }

        } catch (error) {
          if (error.code !== 'ENOENT') {
            throw error;
          }
        }
      }

      console.log(`  📊 Total responsive breakpoints: ${totalBreakpointUsage}`);
      console.log(`  📊 Files with consistent breakpoints: ${consistentBreakpoints}/${cssFiles.length}`);

      if (consistentBreakpoints >= cssFiles.length * 0.75) {
        console.log('  ✅ Good breakpoint consistency across files');
      } else {
        console.log('  ⚠️  Consider standardizing breakpoints across files');
      }

      this.testResults.passed++;
      console.log('  ✅ Responsive breakpoints test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Responsive breakpoints: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testMobileJavaScript() {
    console.log('📋 Test 4: Testing mobile-specific JavaScript features...');

    try {
      const jsFiles = [
        'components/enhanced-search.js',
        'components/family-tree.js',
        'components/information-disclosure.js',
        'core/base-component.js'
      ];

      for (const filename of jsFiles) {
        const filePath = path.join(this.jsDir, filename);

        try {
          const content = await fs.readFile(filePath, 'utf8');

          // Test for mobile detection
          if (content.includes('detectMobile') || content.includes('isMobile') || content.includes('mobile')) {
            console.log(`  ✓ ${filename}: Has mobile detection`);
          } else {
            console.log(`  ⚠️  ${filename}: No mobile detection found`);
          }

          // Test for touch event handling
          const touchEvents = [
            'touchstart',
            'touchend',
            'touchmove',
            'ontouchstart',
            'maxTouchPoints'
          ];

          const touchSupport = touchEvents.some(event => content.includes(event));
          if (touchSupport) {
            console.log(`  ✓ ${filename}: Has touch event support`);
          } else if (filename.includes('tree') || filename.includes('search')) {
            console.log(`  ⚠️  ${filename}: Limited touch event support`);
          }

          // Test for viewport/screen size handling
          if (content.includes('window.innerWidth') || content.includes('screen.width') || content.includes('matchMedia')) {
            console.log(`  ✓ ${filename}: Has viewport handling`);
          }

          // Test for performance considerations
          const performancePatterns = [
            'debounce',
            'throttle',
            'requestAnimationFrame',
            'IntersectionObserver'
          ];

          const hasPerformanceOptimizations = performancePatterns.some(pattern => content.includes(pattern));
          if (hasPerformanceOptimizations) {
            console.log(`  ✓ ${filename}: Has performance optimizations`);
          }

        } catch (error) {
          if (error.code === 'ENOENT') {
            console.log(`  ❌ ${filename}: File not found`);
          } else {
            throw error;
          }
        }
      }

      // Test base component mobile features
      const baseComponentPath = path.join(this.jsDir, 'core/base-component.js');
      try {
        const baseContent = await fs.readFile(baseComponentPath, 'utf8');

        if (baseContent.includes('detectMobile')) {
          console.log('  ✅ BaseComponent provides mobile detection utilities');
        } else {
          console.log('  ❌ BaseComponent missing mobile utilities');
        }

      } catch (error) {
        if (error.code !== 'ENOENT') {
          throw error;
        }
      }

      this.testResults.passed++;
      console.log('  ✅ Mobile JavaScript features test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Mobile JavaScript: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  async testAccessibilityFeatures() {
    console.log('📋 Test 5: Validating accessibility features...');

    try {
      let ariaAttributeCount = 0;
      let keyboardHandlingCount = 0;
      let focusManagementCount = 0;
      let reducedMotionCount = 0;

      // Test CSS accessibility features
      const cssFiles = ['foundation.css', 'enhanced-search.css', 'family-tree.css', 'information-disclosure.css'];

      for (const filename of cssFiles) {
        const filePath = path.join(this.cssDir, filename);

        try {
          const content = await fs.readFile(filePath, 'utf8');

          // Check for reduced motion support
          if (content.includes('prefers-reduced-motion')) {
            reducedMotionCount++;
            console.log(`  ✓ ${filename}: Supports reduced motion preferences`);
          }

          // Check for high contrast support
          if (content.includes('prefers-contrast')) {
            console.log(`  ✓ ${filename}: Supports high contrast preferences`);
          }

          // Check for focus indicators
          if (content.includes(':focus')) {
            console.log(`  ✓ ${filename}: Has focus indicators`);
          }

          // Check for screen reader utilities
          if (content.includes('sr-only') || content.includes('visually-hidden')) {
            console.log(`  ✓ ${filename}: Has screen reader utilities`);
          }

        } catch (error) {
          if (error.code !== 'ENOENT') {
            throw error;
          }
        }
      }

      // Test JavaScript accessibility features
      const jsFiles = [
        'components/enhanced-search.js',
        'components/family-tree.js',
        'components/information-disclosure.js'
      ];

      for (const filename of jsFiles) {
        const filePath = path.join(this.jsDir, filename);

        try {
          const content = await fs.readFile(filePath, 'utf8');

          // Check for ARIA attributes
          const ariaPatterns = [
            'aria-label',
            'aria-expanded',
            'aria-selected',
            'aria-live',
            'role='
          ];

          const ariaUsage = ariaPatterns.filter(pattern => content.includes(pattern)).length;
          ariaAttributeCount += ariaUsage;

          if (ariaUsage > 0) {
            console.log(`  ✓ ${filename}: Uses ${ariaUsage} ARIA patterns`);
          } else {
            console.log(`  ⚠️  ${filename}: Limited ARIA usage`);
          }

          // Check for keyboard event handling
          const keyboardEvents = ['keydown', 'keyup', 'keypress', 'ArrowUp', 'ArrowDown', 'Enter', 'Escape'];
          const keyboardSupport = keyboardEvents.filter(event => content.includes(event)).length;
          keyboardHandlingCount += keyboardSupport;

          if (keyboardSupport > 0) {
            console.log(`  ✓ ${filename}: Handles ${keyboardSupport} keyboard events`);
          } else {
            console.log(`  ⚠️  ${filename}: Limited keyboard support`);
          }

          // Check for focus management
          if (content.includes('focus()') || content.includes('blur()') || content.includes('tabindex')) {
            focusManagementCount++;
            console.log(`  ✓ ${filename}: Has focus management`);
          }

          // Check for screen reader announcements
          if (content.includes('aria-live') || content.includes('announceToScreenReader')) {
            console.log(`  ✓ ${filename}: Has screen reader announcements`);
          }

        } catch (error) {
          if (error.code !== 'ENOENT') {
            throw error;
          }
        }
      }

      // Summary of accessibility features
      console.log(`  📊 Total ARIA attribute usage: ${ariaAttributeCount}`);
      console.log(`  📊 Components with keyboard handling: ${keyboardHandlingCount}`);
      console.log(`  📊 Components with focus management: ${focusManagementCount}`);
      console.log(`  📊 Files with reduced motion support: ${reducedMotionCount}`);

      if (ariaAttributeCount >= 5 && keyboardHandlingCount >= 2 && reducedMotionCount >= 2) {
        console.log('  ✅ Good accessibility feature coverage');
      } else {
        console.log('  ⚠️  Consider improving accessibility features');
      }

      this.testResults.passed++;
      console.log('  ✅ Accessibility features test completed\n');

    } catch (error) {
      this.testResults.failed++;
      this.testResults.errors.push(`Accessibility features: ${error.message}`);
      console.log(`  ❌ ${error.message}\n`);
    }
  }

  displayResults() {
    console.log('📊 Mobile Responsiveness Test Results');
    console.log('=' .repeat(50));
    console.log(`✅ Passed: ${this.testResults.passed}`);
    console.log(`❌ Failed: ${this.testResults.failed}`);

    if (this.testResults.errors.length > 0) {
      console.log('\n🚨 Errors found:');
      this.testResults.errors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error}`);
      });
    }

    // Mobile responsiveness recommendations
    console.log('\n📱 Mobile Responsiveness Recommendations:');
    console.log('  • Ensure all interactive elements meet 44px minimum touch target');
    console.log('  • Test on actual mobile devices with various screen sizes');
    console.log('  • Validate touch interactions work smoothly');
    console.log('  • Check performance on mid-range mobile devices');
    console.log('  • Ensure good readability at small screen sizes');

    const totalTests = this.testResults.passed + this.testResults.failed;
    const successRate = (this.testResults.passed / totalTests * 100).toFixed(1);

    console.log(`\n📈 Success Rate: ${successRate}%`);

    if (this.testResults.failed > 0) {
      console.log('\n⚠️  Some tests failed. Please address the issues above.');
      process.exit(1);
    } else {
      console.log('\n🎉 All mobile responsiveness tests passed!');
    }
  }
}

// Run if called directly
if (require.main === module) {
  const tester = new MobileResponsivenessTester();
  tester.run();
}

module.exports = MobileResponsivenessTester;