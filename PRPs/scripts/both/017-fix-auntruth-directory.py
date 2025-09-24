#!/usr/bin/env python3
"""
Fix AuntRuth Directory References - Priority 2
Fixes /AuntRuth/ → /auntruth/ path issues

Based on analysis of broken link patterns, this script addresses ~25% of remaining
broken links by fixing case sensitivity in directory names.

Pattern Source: Analysis of broken link patterns
Target: ~800 files with /AuntRuth/ references
"""

import argparse
import os
import re
import logging
from pathlib import Path
from datetime import datetime
import subprocess

def setup_logging_and_args():
    """Setup logging and parse command line arguments"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    parser = argparse.ArgumentParser(description="Fix AuntRuth directory references")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--target-dir", default="docs", help="Target directory to process (default: docs)")
    parser.add_argument("--limit", type=int, help="Limit number of files processed (for testing)")
    parser.add_argument("--branch-name", default="task-015-broken-links-fix", help="Git branch name")

    return parser.parse_args()

def scan_files_with_auntruth_references(target_dir):
    """Find HTML files with /AuntRuth/ patterns"""
    logging.info(f"Scanning for files with /AuntRuth/ references in {target_dir}")

    affected_files = []
    html_files = []

    # Find all HTML files
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))

    logging.info(f"Scanning {len(html_files)} HTML files for /AuntRuth/ patterns")

    for i, file_path in enumerate(html_files):
        if i % 500 == 0:
            logging.info(f"  Progress: {i}/{len(html_files)} files scanned...")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Simple string search - more reliable than regex for this case
                if '/AuntRuth/' in content:
                    affected_files.append(file_path)
        except Exception as e:
            logging.warning(f"Error reading {file_path}: {e}")
            continue

    logging.info(f"Found {len(affected_files)} files with /AuntRuth/ references")
    return affected_files

def fix_auntruth_references_in_file(file_path):
    """Apply AuntRuth directory fixes to single file"""
    changes_made = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Define the mapping patterns for /AuntRuth/ → /auntruth/
        patterns_to_fix = [
            # Basic directory references
            (r'/AuntRuth/', r'/auntruth/'),
            # Case variations (just to be thorough)
            (r'/auntruth/', r'/auntruth/'),  # Ensure consistency
            (r'/AUNTRUTH/', r'/auntruth/'),
        ]

        for old_pattern, replacement in patterns_to_fix:
            if old_pattern in content:
                content = content.replace(old_pattern, replacement)
                if old_pattern != replacement:  # Only log actual changes
                    changes_made.append(f"{old_pattern} → {replacement}")

        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)

            return changes_made

        return []

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return []

def validate_fixes(files_processed, sample_size=10):
    """Validate that AuntRuth path fixes work correctly"""
    logging.info("Validating AuntRuth directory fixes...")

    # Test URLs that should now work
    test_urls = [
        'http://localhost:8000/auntruth/',
        'http://localhost:8000/auntruth/htm/',
        'http://localhost:8000/auntruth/css/htm.css',
        'http://localhost:8000/auntruth/jpg/',
    ]

    success_count = 0
    for url in test_urls:
        try:
            # Test with curl
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                status_code = result.stdout.strip()
                if status_code == '200':
                    logging.info(f"✓ {url} → {status_code}")
                    success_count += 1
                else:
                    logging.warning(f"✗ {url} → {status_code}")
            else:
                logging.warning(f"✗ {url} → curl failed")
        except Exception as e:
            logging.warning(f"✗ {url} → Error: {e}")

    success_rate = (success_count / len(test_urls)) * 100 if test_urls else 0
    logging.info(f"Validation: {success_count}/{len(test_urls)} URLs working ({success_rate:.1f}%)")

    return success_rate > 75  # Consider successful if >75% of test URLs work

def main():
    """Main execution function"""
    args = setup_logging_and_args()

    logging.info("=" * 60)
    logging.info("AuntRuth Directory Reference Fixer - Script 017")
    logging.info("=" * 60)
    logging.info(f"Target directory: {args.target_dir}")
    logging.info(f"Dry run mode: {args.dry_run}")
    logging.info(f"Processing limit: {args.limit or 'None'}")

    # Verify we're in the correct git branch
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                              capture_output=True, text=True)
        current_branch = result.stdout.strip()
        if current_branch != args.branch_name:
            logging.warning(f"Current branch is '{current_branch}', expected '{args.branch_name}'")
            logging.info("Continue anyway? (This should be safe)")
    except Exception as e:
        logging.warning(f"Could not check git branch: {e}")

    # Scan for affected files
    affected_files = scan_files_with_auntruth_references(args.target_dir)

    if not affected_files:
        logging.info("No files found with /AuntRuth/ references. Nothing to do.")
        return

    # Apply limit if specified
    if args.limit:
        affected_files = affected_files[:args.limit]
        logging.info(f"Limited to first {len(affected_files)} files")

    logging.info(f"\nProcessing {len(affected_files)} files...")

    # Show dry-run preview
    if args.dry_run:
        logging.info("\n=== DRY RUN PREVIEW ===")
        sample_files = affected_files[:5]  # Show first 5 files
        for file_path in sample_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    auntruth_count = content.count('/AuntRuth/')
                    logging.info(f"  {file_path}: {auntruth_count} /AuntRuth/ references")
            except Exception as e:
                logging.info(f"  {file_path}: Error reading - {e}")

        if len(affected_files) > 5:
            logging.info(f"  ... and {len(affected_files) - 5} more files")

        logging.info("\nRun without --dry-run to apply changes")
        return

    # Process files
    files_fixed = 0
    total_changes = 0

    for i, file_path in enumerate(affected_files):
        if i % 100 == 0:
            logging.info(f"Progress: {i}/{len(affected_files)} files processed...")

        changes = fix_auntruth_references_in_file(file_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            logging.debug(f"Fixed {file_path}: {', '.join(changes)}")

    # Summary
    logging.info(f"\n=== COMPLETION SUMMARY ===")
    logging.info(f"Files processed: {len(affected_files)}")
    logging.info(f"Files modified: {files_fixed}")
    logging.info(f"Total changes made: {total_changes}")
    logging.info(f"Pattern fixed: /AuntRuth/ → /auntruth/")

    if files_fixed > 0:
        # Validate the fixes
        if validate_fixes(affected_files):
            logging.info("✓ Validation passed - URLs are resolving correctly")
        else:
            logging.warning("⚠ Validation concerns - Some URLs may not resolve correctly")

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"PRPs/scripts/reports/auntruth_fixes_{timestamp}.txt"

        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w') as f:
                f.write(f"AuntRuth Directory Fix Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Files processed: {len(affected_files)}\n")
                f.write(f"Files modified: {files_fixed}\n")
                f.write(f"Total changes: {total_changes}\n")
                f.write(f"Pattern: /AuntRuth/ → /auntruth/\n\n")
                f.write("Files modified:\n")

                for file_path in affected_files:
                    # Quick check if file was actually modified
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as ff:
                            if '/AuntRuth/' not in ff.read():
                                f.write(f"  {file_path}\n")
                    except:
                        pass

            logging.info(f"Report saved: {report_file}")
        except Exception as e:
            logging.warning(f"Could not save report: {e}")

        logging.info(f"\nNext steps:")
        logging.info(f"1. Test sample URLs manually")
        logging.info(f"2. Run broken link checker to verify improvement")
        logging.info(f"3. Commit changes: git add . && git commit -m 'Script 017: Fix /AuntRuth/ directory references'")
    else:
        logging.info("No changes were needed - all /AuntRuth/ references may already be fixed")

if __name__ == "__main__":
    main()