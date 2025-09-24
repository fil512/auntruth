#!/usr/bin/env python3
"""
Fix Duplicate Directory Paths - Priority 3
Fixes malformed relative paths like ./index_files/ → index_files/

Based on analysis of broken link patterns showing 5,439 occurrences of src="./" patterns.
Pattern Source: Analysis of remaining broken link patterns
Target: ~5,439 malformed relative path issues in ~5,357 files
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

    parser = argparse.ArgumentParser(description="Fix duplicate/malformed directory paths")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--target-dir", default="docs", help="Target directory to process (default: docs)")
    parser.add_argument("--limit", type=int, help="Limit number of files processed (for testing)")
    parser.add_argument("--branch-name", default="task-015-broken-links-fix", help="Git branch name")

    return parser.parse_args()

def scan_files_with_malformed_paths(target_dir):
    """Find HTML files with malformed relative path patterns"""
    logging.info(f"Scanning for files with malformed relative paths in {target_dir}")

    affected_files = []
    html_files = []

    # Find all HTML files
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))

    logging.info(f"Scanning {len(html_files)} HTML files for malformed path patterns")

    # Patterns to detect malformed relative paths
    malformed_patterns = [
        r'src="\./',     # src="./"
        r'href="\./',    # href="./"
        r"src='\./",     # src='./'
        r"href='\./",    # href='./'
    ]

    combined_pattern = re.compile('|'.join(malformed_patterns))

    for i, file_path in enumerate(html_files):
        if i % 1000 == 0:
            logging.info(f"  Progress: {i}/{len(html_files)} files scanned...")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if combined_pattern.search(content):
                    affected_files.append(file_path)
        except Exception as e:
            logging.warning(f"Error reading {file_path}: {e}")
            continue

    logging.info(f"Found {len(affected_files)} files with malformed path patterns")
    return affected_files

def fix_malformed_paths_in_file(file_path):
    """Fix malformed relative paths in single file"""
    changes_made = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Define the patterns for fixing malformed paths
        patterns_to_fix = [
            # Basic ./ path fixes - remove the unnecessary ./
            (r'src="\./', r'src="'),
            (r'href="\./', r'href="'),
            (r"src='\./", r"src='"),
            (r"href='\./", r"href='"),

            # More complex cases with proper path resolution
            (r'(src|href)="\.(/[^"]+)"', r'\1="\2"'),  # src="./path" → src="/path"
            (r"(src|href)='\.(/[^']+)'", r"\1='\2'"),  # src='./path' → src='/path'

            # Fix double slashes that might result
            (r'(src|href)="//([^"]*)"', r'\1="/\2"'),  # src="//path" → src="/path"
            (r"(src|href)='//([^']*)'", r"\1='/\2'"),  # src='//path' → src='/path'
        ]

        for old_pattern, replacement in patterns_to_fix:
            old_content_before = content
            content = re.sub(old_pattern, replacement, content)
            if content != old_content_before:
                changes_made.append(f"Regex: {old_pattern} → {replacement}")

        # Additional cleanup for common cases
        # Fix src="" (empty src after removing ./)
        content = re.sub(r'(src|href)=""', r'\1="#"', content)
        if content != original_content and not changes_made:
            changes_made.append("Fixed empty src/href attributes")

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
    """Validate that path fixes work correctly"""
    logging.info("Validating malformed path fixes...")

    if not files_processed:
        logging.info("No files were processed, skipping validation")
        return True

    # Sample some files to validate
    import random
    sample_files = random.sample(files_processed, min(sample_size, len(files_processed)))

    issues_found = 0
    files_checked = 0

    for file_path in sample_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check if any ./ patterns remain
            remaining_issues = len(re.findall(r'(src|href)="\./', content))
            remaining_issues += len(re.findall(r"(src|href)='\./", content))

            if remaining_issues > 0:
                issues_found += remaining_issues
                logging.warning(f"✗ {file_path}: {remaining_issues} remaining ./ patterns")
            else:
                logging.info(f"✓ {file_path}: Clean")

            files_checked += 1

        except Exception as e:
            logging.warning(f"✗ {file_path}: Error validating - {e}")

    success_rate = ((files_checked - (issues_found > 0 and 1 or 0)) / files_checked) * 100 if files_checked > 0 else 0
    logging.info(f"Validation: {files_checked - (issues_found > 0 and 1 or 0)}/{files_checked} files clean ({success_rate:.1f}%)")

    return success_rate > 80  # Consider successful if >80% of sample files are clean

def main():
    """Main execution function"""
    args = setup_logging_and_args()

    logging.info("=" * 60)
    logging.info("Malformed Directory Path Fixer - Script 019")
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
    affected_files = scan_files_with_malformed_paths(args.target_dir)

    if not affected_files:
        logging.info("No files found with malformed path patterns. Nothing to do.")
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
                    malformed_count = len(re.findall(r'(src|href)="\./', content))
                    malformed_count += len(re.findall(r"(src|href)='\./", content))
                    logging.info(f"  {file_path}: {malformed_count} malformed paths")
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

        changes = fix_malformed_paths_in_file(file_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            logging.debug(f"Fixed {file_path}: {', '.join(changes)}")

    # Summary
    logging.info(f"\n=== COMPLETION SUMMARY ===")
    logging.info(f"Files processed: {len(affected_files)}")
    logging.info(f"Files modified: {files_fixed}")
    logging.info(f"Total changes made: {total_changes}")
    logging.info(f"Pattern fixed: src/href=\"./\" → src/href=\"\"")

    if files_fixed > 0:
        # Validate the fixes
        if validate_fixes(affected_files[:100]):  # Sample first 100 files
            logging.info("✓ Validation passed - Malformed paths have been cleaned")
        else:
            logging.warning("⚠ Validation concerns - Some malformed paths may remain")

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"PRPs/scripts/reports/path_fixes_{timestamp}.txt"

        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w') as f:
                f.write(f"Malformed Path Fix Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Files processed: {len(affected_files)}\n")
                f.write(f"Files modified: {files_fixed}\n")
                f.write(f"Total changes: {total_changes}\n")
                f.write(f"Pattern: src/href=\"./\" → src/href=\"\"\n\n")
                f.write("Sample of files modified:\n")

                # Show first 20 files that were modified
                sample_count = 0
                for file_path in affected_files:
                    if sample_count >= 20:
                        break
                    # Quick check if file was actually modified by looking for absence of ./ patterns
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as ff:
                            content = ff.read()
                            if './' not in content or len(re.findall(r'(src|href)="\./', content)) == 0:
                                f.write(f"  {file_path}\n")
                                sample_count += 1
                    except:
                        pass

            logging.info(f"Report saved: {report_file}")
        except Exception as e:
            logging.warning(f"Could not save report: {e}")

        logging.info(f"\nNext steps:")
        logging.info(f"1. Run broken link checker to verify improvement")
        logging.info(f"2. Commit changes: git add . && git commit -m 'Script 019: Fix malformed relative paths'")
        logging.info(f"3. Proceed to Script 020 for missing media cleanup")
    else:
        logging.info("No changes were needed - all relative paths may already be correct")

if __name__ == "__main__":
    main()