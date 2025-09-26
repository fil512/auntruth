#!/usr/bin/env node

/**
 * Integrate Enhanced Navigation Script
 * Adds enhanced navigation to existing HTML pages
 */

const fs = require('fs').promises;
const path = require('path');

class NavigationIntegrator {
  constructor(options = {}) {
    this.targetDir = options.targetDir || path.join(__dirname, '../docs/new/htm');
    this.dryRun = options.dryRun || false;
    this.processedCount = 0;
    this.errorCount = 0;
  }

  async run() {
    console.log('Starting enhanced navigation integration...');
    console.log(`Target directory: ${this.targetDir}`);
    console.log(`Dry run mode: ${this.dryRun}`);

    try {
      const htmlFiles = await this.findHtmlFiles(this.targetDir);
      console.log(`Found ${htmlFiles.length} HTML files to process`);

      if (this.dryRun) {
        console.log('\n=== DRY RUN MODE - No files will be modified ===\n');
      }

      for (const filePath of htmlFiles.slice(0, 5)) { // Process first 5 for testing
        await this.processFile(filePath);
      }

      console.log('\n=== Integration Complete ===');
      console.log(`Files processed: ${this.processedCount}`);
      console.log(`Errors: ${this.errorCount}`);

    } catch (error) {
      console.error('Error during integration:', error);
      process.exit(1);
    }
  }

  async findHtmlFiles(dir) {
    const files = [];

    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
          const subFiles = await this.findHtmlFiles(fullPath);
          files.push(...subFiles);
        } else if (entry.isFile() && entry.name.endsWith('.htm')) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      console.error(`Error reading directory ${dir}:`, error);
    }

    return files;
  }

  async processFile(filePath) {
    try {
      const content = await fs.readFile(filePath, 'utf8');
      const updatedContent = this.addEnhancedNavigation(content, filePath);

      if (updatedContent !== content) {
        if (!this.dryRun) {
          await fs.writeFile(filePath, updatedContent);
        }

        console.log(`✅ ${path.basename(filePath)} - Enhanced navigation added`);
        this.processedCount++;
      } else {
        console.log(`⏭️  ${path.basename(filePath)} - No changes needed`);
      }
    } catch (error) {
      console.error(`❌ ${path.basename(filePath)} - Error: ${error.message}`);
      this.errorCount++;
    }
  }

  addEnhancedNavigation(content, filePath) {
    // Check if already has enhanced navigation
    if (content.includes('foundation.css') || content.includes('navigation-enhanced.js')) {
      return content; // Already enhanced
    }

    // Add foundation.css after existing CSS
    let updatedContent = content;

    // Add foundation.css link
    const cssInsert = `    <!-- Foundation CSS for mobile-first responsive design -->
    <link href="/auntruth/new/css/foundation.css" rel="stylesheet">`;

    if (content.includes('</head>')) {
      updatedContent = updatedContent.replace('</head>', `${cssInsert}
</head>`);
    }

    // Add enhanced navigation script
    const scriptInsert = `
    <!-- Enhanced Navigation System -->
    <script type="module">
        // Import enhanced components
        import '/auntruth/new/js/core/base-component.js';
        import '/auntruth/new/js/core/data-manager.js';
        import '/auntruth/new/js/components/navigation-enhanced.js';

        // Initialize enhanced navigation
        document.addEventListener('DOMContentLoaded', async () => {
            try {
                const dataManager = new DataManager();
                const navigation = new NavigationEnhanced({ dataManager });
                await navigation.init();
            } catch (error) {
                console.error('Enhanced navigation failed:', error);
                // Fallback to existing navigation
            }
        });
    </script>`;

    if (updatedContent.includes('</head>')) {
      updatedContent = updatedContent.replace('</head>', `${scriptInsert}
</head>`);
    }

    return updatedContent;
  }
}

// Command line interface
const args = process.argv.slice(2);
const options = {};

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--dry-run':
      options.dryRun = true;
      break;
    case '--target-dir':
      options.targetDir = args[i + 1];
      i++; // Skip next argument
      break;
  }
}

// Run if called directly
if (require.main === module) {
  const integrator = new NavigationIntegrator(options);
  integrator.run();
}

module.exports = NavigationIntegrator;