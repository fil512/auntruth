#!/usr/bin/env node

/**
 * Optimize Assets Script
 * Minifies JavaScript and CSS files for production
 */

const fs = require('fs').promises;
const path = require('path');
const { minify } = require('terser');
const CleanCSS = require('clean-css');

class AssetOptimizer {
  constructor() {
    this.jsDir = path.join(__dirname, '../docs/new/js');
    this.cssDir = path.join(__dirname, '../docs/new/css');
    this.cleanCSS = new CleanCSS({
      level: 2,
      returnPromise: true
    });
  }

  async run() {
    console.log('Starting asset optimization...');

    try {
      await this.optimizeJavaScript();
      await this.optimizeCSS();
      console.log('Asset optimization complete!');
    } catch (error) {
      console.error('Error during optimization:', error);
      process.exit(1);
    }
  }

  async optimizeJavaScript() {
    console.log('Optimizing JavaScript files...');

    const jsFiles = await this.findFiles(this.jsDir, '.js');

    for (const filePath of jsFiles) {
      // Skip already minified files
      if (filePath.includes('.min.js')) continue;

      try {
        const source = await fs.readFile(filePath, 'utf8');
        const result = await minify(source, {
          compress: {
            drop_console: false, // Keep console.log for debugging
            drop_debugger: true,
            pure_funcs: ['console.debug']
          },
          mangle: false, // Don't mangle for better debugging
          output: {
            comments: false
          }
        });

        if (result.error) {
          console.error(`Error minifying ${filePath}:`, result.error);
          continue;
        }

        const minifiedPath = filePath.replace('.js', '.min.js');
        await fs.writeFile(minifiedPath, result.code);

        const originalSize = Buffer.byteLength(source, 'utf8');
        const minifiedSize = Buffer.byteLength(result.code, 'utf8');
        const savings = ((originalSize - minifiedSize) / originalSize * 100).toFixed(1);

        console.log(`  ${path.basename(filePath)} -> ${path.basename(minifiedPath)} (${savings}% smaller)`);
      } catch (error) {
        console.error(`Failed to process ${filePath}:`, error);
      }
    }
  }

  async optimizeCSS() {
    console.log('Optimizing CSS files...');

    const cssFiles = await this.findFiles(this.cssDir, '.css');

    for (const filePath of cssFiles) {
      // Skip already minified files
      if (filePath.includes('.min.css')) continue;

      try {
        const source = await fs.readFile(filePath, 'utf8');
        const result = await this.cleanCSS.minify(source);

        if (result.errors.length > 0) {
          console.error(`Errors in ${filePath}:`, result.errors);
          continue;
        }

        const minifiedPath = filePath.replace('.css', '.min.css');
        await fs.writeFile(minifiedPath, result.styles);

        const originalSize = Buffer.byteLength(source, 'utf8');
        const minifiedSize = Buffer.byteLength(result.styles, 'utf8');
        const savings = ((originalSize - minifiedSize) / originalSize * 100).toFixed(1);

        console.log(`  ${path.basename(filePath)} -> ${path.basename(minifiedPath)} (${savings}% smaller)`);
      } catch (error) {
        console.error(`Failed to process ${filePath}:`, error);
      }
    }
  }

  async findFiles(dir, extension) {
    const files = [];

    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
          const subFiles = await this.findFiles(fullPath, extension);
          files.push(...subFiles);
        } else if (entry.isFile() && entry.name.endsWith(extension)) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      console.error(`Error reading directory ${dir}:`, error);
    }

    return files;
  }
}

// Run if called directly
if (require.main === module) {
  const optimizer = new AssetOptimizer();
  optimizer.run();
}

module.exports = AssetOptimizer;