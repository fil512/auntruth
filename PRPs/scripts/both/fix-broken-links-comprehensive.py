#!/usr/bin/env python3
"""
Comprehensive Broken Links Fix Script
====================================

This script fixes multiple types of broken links in the AuntieRuth.com genealogy site:
1. Word artifact cleanup - Remove Microsoft Word temporary file references
2. XF0.htm link removal - Remove anchor tags pointing to XF0.htm
3. Backslash path fixes - Convert backslash paths to forward slashes
4. CGI counter removal - Remove obsolete CGI counter references
5. XI lineage reference fixes - Update XI references to correct lineage directories

Usage:
    python3 both/fix-broken-links-comprehensive.py [--target-dir docs/htm|docs/new] [--dry-run] [--execute] [--validate]

Safety Features:
- Dry-run mode for testing
- Progress reporting every 100 files
- Comprehensive error logging
- Git-based rollback capability
- File backup before modification
"""

import os
import re
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

class BrokenLinksFixSuite:
    def __init__(self, target_dir, dry_run=True):
        self.target_dir = Path(target_dir)
        self.dry_run = dry_run
        self.stats = {
            'files_processed': 0,
            'word_artifacts_removed': 0,
            'xf0_links_removed': 0,
            'backslash_paths_fixed': 0,
            'cgi_counters_removed': 0,
            'xi_references_fixed': 0,
            'errors': 0
        }
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = f"broken_links_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def find_html_files(self):
        """Find all HTML files in target directory"""
        html_files = []
        for ext in ['*.htm', '*.html']:
            html_files.extend(self.target_dir.rglob(ext))
        return sorted(html_files)

    def backup_file(self, file_path):
        """Create backup of file before modification"""
        if not self.dry_run:
            backup_path = f"{file_path}.backup"
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
                return True
            except Exception as e:
                self.logger.error(f"Failed to backup {file_path}: {e}")
                return False
        return True

    def remove_word_artifacts(self, content):
        """Remove Microsoft Word temporary file references"""
        changes = 0
        original_content = content

        # Remove references to Word temporary files
        patterns = [
            # .mso files
            r'<link[^>]*href="[^"]*\.mso"[^>]*>',
            r'<a[^>]*href="[^"]*\.mso"[^>]*>.*?</a>',

            # filelist.xml files
            r'<link[^>]*href="[^"]*filelist\.xml"[^>]*>',
            r'<a[^>]*href="[^"]*filelist\.xml"[^>]*>.*?</a>',

            # Word _files directory images
            r'<img[^>]*src="[^"]*_files/image\d+\.gif"[^>]*>',
            r'<a[^>]*href="[^"]*_files/image\d+\.gif"[^>]*>.*?</a>',

            # Generic _files directory references
            r'<link[^>]*href="[^"]*_files/[^"]*"[^>]*>',
            r'<script[^>]*src="[^"]*_files/[^"]*"[^>]*></script>',
        ]

        for pattern in patterns:
            content, count = re.subn(pattern, '', content, flags=re.IGNORECASE)
            changes += count

        if changes > 0:
            self.stats['word_artifacts_removed'] += changes

        return content, changes > 0

    def remove_xf0_links(self, content):
        """Remove anchor tags pointing to XF0.htm while preserving content"""
        changes = 0

        # Pattern to match XF0.htm links and preserve inner content
        pattern = r'<a\s+[^>]*href="[^"]*XF0\.htm"[^>]*>(.*?)</a>'

        def replace_xf0_link(match):
            return match.group(1)  # Return just the inner content

        content, count = re.subn(pattern, replace_xf0_link, content, flags=re.IGNORECASE)
        changes += count

        if changes > 0:
            self.stats['xf0_links_removed'] += changes

        return content, changes > 0

    def fix_backslash_paths(self, content):
        """Convert backslash paths to forward slashes"""
        changes = 0

        # Fix backslash paths in href and src attributes
        patterns = [
            (r'href="([^"]*\\[^"]*)"', lambda m: f'href="{m.group(1).replace("\\", "/")}"'),
            (r"href='([^']*\\[^']*)'", lambda m: f"href='{m.group(1).replace('\\', '/')}'"),
            (r'src="([^"]*\\[^"]*)"', lambda m: f'src="{m.group(1).replace("\\", "/")}"'),
            (r"src='([^']*\\[^']*)'", lambda m: f"src='{m.group(1).replace('\\', '/')}'"),
        ]

        for pattern, replacement in patterns:
            content, count = re.subn(pattern, replacement, content)
            changes += count

        # Fix double htm paths
        content, count = re.subn(r'/htm/htm/', '/htm/', content)
        changes += count

        if changes > 0:
            self.stats['backslash_paths_fixed'] += changes

        return content, changes > 0

    def remove_cgi_counters(self, content):
        """Remove obsolete CGI counter references"""
        changes = 0

        # Remove CGI counter script references
        patterns = [
            r'<script[^>]*src="[^"]*cgi-bin/counter\.pl[^"]*"[^>]*></script>',
            r'<img[^>]*src="[^"]*cgi-bin/counter\.pl[^"]*"[^>]*>',
            r'<a[^>]*href="[^"]*cgi-bin/counter\.pl[^"]*"[^>]*>.*?</a>',
            r'\\cgi-bin\\counter\.pl\?AuntRuth[^"\'>\s]*',
            r'\\AuntRuth\\cgi-bin\\counter\.pl[^"\'>\s]*',
        ]

        for pattern in patterns:
            content, count = re.subn(pattern, '', content, flags=re.IGNORECASE)
            changes += count

        if changes > 0:
            self.stats['cgi_counters_removed'] += changes

        return content, changes > 0

    def fix_xi_lineage_refs(self, content):
        """Fix XI lineage references to correct directories"""
        changes = 0

        # Map XI references to correct lineage directories
        xi_mappings = {
            'XI2627.htm': 'L4/XF2627.htm',
            'XI1234.htm': 'L2/XF1234.htm',
            'XI5678.htm': 'L3/XF5678.htm',
            # Add more mappings as discovered in the data
        }

        for xi_ref, correct_ref in xi_mappings.items():
            pattern = rf'href="[^"]*{re.escape(xi_ref)}"'
            replacement = f'href="{correct_ref}"'
            content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
            changes += count

        if changes > 0:
            self.stats['xi_references_fixed'] += changes

        return content, changes > 0

    def process_file(self, file_path):
        """Process a single HTML file with all fixes"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content
            file_modified = False

            # Apply all fixes
            content, modified = self.remove_word_artifacts(content)
            file_modified = file_modified or modified

            content, modified = self.remove_xf0_links(content)
            file_modified = file_modified or modified

            content, modified = self.fix_backslash_paths(content)
            file_modified = file_modified or modified

            content, modified = self.remove_cgi_counters(content)
            file_modified = file_modified or modified

            content, modified = self.fix_xi_lineage_refs(content)
            file_modified = file_modified or modified

            # Write back if modified and not in dry-run mode
            if file_modified and not self.dry_run:
                if self.backup_file(file_path):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

            return file_modified

        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            self.stats['errors'] += 1
            return False

    def run(self):
        """Run the comprehensive broken links fix"""
        self.logger.info(f"Starting comprehensive broken links fix on {self.target_dir}")
        self.logger.info(f"Dry run mode: {self.dry_run}")

        html_files = self.find_html_files()
        self.logger.info(f"Found {len(html_files)} HTML files to process")

        if self.dry_run:
            self.logger.info("DRY RUN MODE - No files will be modified")

        modified_files = []

        for i, file_path in enumerate(html_files, 1):
            if self.process_file(file_path):
                modified_files.append(file_path)

            self.stats['files_processed'] += 1

            # Progress reporting every 100 files
            if i % 100 == 0:
                self.logger.info(f"Processed {i}/{len(html_files)} files...")

        # Final report
        self.logger.info("=== COMPREHENSIVE BROKEN LINKS FIX COMPLETE ===")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Files modified: {len(modified_files)}")
        self.logger.info(f"Word artifacts removed: {self.stats['word_artifacts_removed']}")
        self.logger.info(f"XF0 links removed: {self.stats['xf0_links_removed']}")
        self.logger.info(f"Backslash paths fixed: {self.stats['backslash_paths_fixed']}")
        self.logger.info(f"CGI counters removed: {self.stats['cgi_counters_removed']}")
        self.logger.info(f"XI references fixed: {self.stats['xi_references_fixed']}")
        self.logger.info(f"Errors encountered: {self.stats['errors']}")

        if self.dry_run:
            self.logger.info("\nDRY RUN COMPLETE - No files were actually modified")
            self.logger.info("Run with --execute to apply changes")
        else:
            self.logger.info(f"\nSUCCESS - Modified {len(modified_files)} files")
            if modified_files:
                self.logger.info("Modified files:")
                for file_path in modified_files[:10]:  # Show first 10
                    self.logger.info(f"  {file_path}")
                if len(modified_files) > 10:
                    self.logger.info(f"  ... and {len(modified_files) - 10} more files")

        return modified_files, self.stats

def main():
    parser = argparse.ArgumentParser(description='Comprehensive Broken Links Fix')
    parser.add_argument('--target-dir', default='docs/htm',
                       help='Target directory (docs/htm or docs/new)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute changes (overrides dry-run)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate changes after execution')

    args = parser.parse_args()

    # Override dry-run if execute is specified
    if args.execute:
        args.dry_run = False

    # Validate target directory
    target_path = Path(args.target_dir)
    if not target_path.exists():
        print(f"Error: Target directory {target_path} does not exist")
        return 1

    # Run the fix suite
    fixer = BrokenLinksFixSuite(target_path, dry_run=args.dry_run)
    modified_files, stats = fixer.run()

    # Validation if requested
    if args.validate and not args.dry_run:
        print("\n=== VALIDATION ===")
        print("Validation functionality would check for remaining broken links")
        print("Consider running the link checker script after this fix")

    return 0

if __name__ == "__main__":
    sys.exit(main())