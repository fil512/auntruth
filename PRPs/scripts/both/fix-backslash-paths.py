#!/usr/bin/env python3
r"""
Fix backslash paths in HTML files for AuntieRuth.com genealogy site
Task 002 of systematic broken links fix plan

This script converts Windows-style backslash paths to forward slashes for GitHub Pages compatibility.
Handles patterns like ./L2\XF0.htm → ./L2/XF0.htm

Author: Claude Code Assistant
Date: 2025-09-23
"""

import os
import re
import argparse
import sys
from pathlib import Path
import logging

def setup_logging(log_file=None):
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if log_file:
        logging.basicConfig(level=logging.INFO, format=log_format,
                          handlers=[
                              logging.FileHandler(log_file),
                              logging.StreamHandler(sys.stdout)
                          ])
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

def count_backslash_patterns(target_dir):
    """Count files and total occurrences of backslash patterns"""
    file_count = 0
    total_occurrences = 0

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Count backslash patterns like .\L2\XF0.htm
                    backslash_matches = re.findall(r'\./L\d+\\[^"\'>\s]+\.htm', content, re.IGNORECASE)

                    if backslash_matches:
                        file_count += 1
                        total_occurrences += len(backslash_matches)

                except Exception as e:
                    logging.warning(f"Could not read {file_path}: {e}")

    return file_count, total_occurrences

def fix_backslash_paths(file_path, dry_run=False):
    r"""
    Fix backslash paths in a single HTML file

    Patterns fixed:
    - .\L2\XF0.htm → ./L2/XF0.htm
    - .\L6\INDEX.HTM → ./L6/INDEX.HTM
    - Similar patterns with backslashes
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        modified_content = original_content

        # Fix backslash paths like ./L2\XF0.htm → ./L2/XF0.htm
        backslash_pattern = r'\./L(\d+)\\([^"\'>\s]+\.htm[l]?)'
        modified_content = re.sub(backslash_pattern, r'./L\1/\2', modified_content, flags=re.IGNORECASE)

        # Count the changes made
        changes_made = len(re.findall(backslash_pattern, original_content, re.IGNORECASE))

        if changes_made > 0 and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

        return changes_made

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return 0

def process_directory(target_dir, dry_run=False):
    """Process all HTML files in target directory"""
    if not os.path.exists(target_dir):
        logging.error(f"Directory {target_dir} does not exist")
        return 0, 0

    files_modified = 0
    total_fixes = 0
    files_processed = 0

    logging.info(f"{'DRY RUN: ' if dry_run else ''}Processing directory: {target_dir}")

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                changes = fix_backslash_paths(file_path, dry_run)

                if changes > 0:
                    files_modified += 1
                    total_fixes += changes

                    if dry_run and files_modified <= 10:  # Show first 10 in dry run
                        logging.info(f"  Would fix {changes} paths in: {file_path}")

                files_processed += 1
                if files_processed % 100 == 0:
                    logging.info(f"  Processed {files_processed} files...")

    return files_modified, total_fixes

def main():
    parser = argparse.ArgumentParser(description='Fix backslash paths in HTML files')
    parser.add_argument('--target-dir',
                      choices=['docs/htm', 'docs/new', 'both'],
                      default='both',
                      help='Directory to process (default: both)')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be changed without making changes')
    parser.add_argument('--log-file',
                      help='Optional log file location')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_file)

    logging.info("=== AuntieRuth.com Backslash Path Fixer ===")
    logging.info(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    logging.info(f"Target: {args.target_dir}")

    # Determine directories to process
    if args.target_dir == 'both':
        target_dirs = ['docs/htm', 'docs/new']
    else:
        target_dirs = [args.target_dir]

    # Initial scope analysis
    if args.dry_run:
        logging.info("\n=== SCOPE ANALYSIS ===")
        for target_dir in target_dirs:
            file_count, occurrence_count = count_backslash_patterns(target_dir)
            logging.info(f"{target_dir}: {file_count} files, {occurrence_count} backslash patterns")

    # Process each directory
    total_files_modified = 0
    total_fixes_applied = 0

    for target_dir in target_dirs:
        logging.info(f"\n=== PROCESSING {target_dir.upper()} ===")
        files_modified, fixes_applied = process_directory(target_dir, args.dry_run)

        total_files_modified += files_modified
        total_fixes_applied += fixes_applied

        logging.info(f"Results for {target_dir}:")
        logging.info(f"  Files modified: {files_modified}")
        logging.info(f"  Fixes applied: {fixes_applied}")

    # Final summary
    logging.info("\n=== FINAL SUMMARY ===")
    logging.info(f"Total files modified: {total_files_modified}")
    logging.info(f"Total fixes applied: {total_fixes_applied}")

    if args.dry_run:
        logging.info("\nThis was a DRY RUN - no files were actually modified.")
        logging.info("Run without --dry-run to apply changes.")
    else:
        logging.info("\nChanges have been applied successfully!")
        logging.info("Recommend testing representative URLs before proceeding.")

    if not args.dry_run and total_fixes_applied > 0:
        logging.info("\n=== NEXT STEPS ===")
        logging.info("1. Test representative URLs from both sites")
        logging.info("2. Verify links work correctly")
        logging.info("3. Commit changes if validation passes")

if __name__ == "__main__":
    main()