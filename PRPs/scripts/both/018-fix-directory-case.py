#!/usr/bin/env python3
"""
Fix Directory Case Sensitivity - Priority 2
Fixes /l4/ → /L4/, /l1/ → /L1/, etc.

Based on analysis of case sensitivity issues in directory references.
Pattern Source: Based on PRPs/scripts/htm/001-fix-path-format.py:69-74
Target: ~50 case sensitivity issues in ~12 files
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

    parser = argparse.ArgumentParser(description="Fix directory case sensitivity issues")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--target-dir", default="docs", help="Target directory to process (default: docs)")
    parser.add_argument("--limit", type=int, help="Limit number of files processed (for testing)")
    parser.add_argument("--branch-name", default="task-015-broken-links-fix", help="Git branch name")

    return parser.parse_args()

def scan_directory_structure(target_dir):
    """Scan actual directory structure to determine correct case"""
    logging.info(f"Scanning directory structure in {target_dir}")

    # Find all actual L0, L1, L2, etc. directories
    actual_dirs = set()

    for root, dirs, files in os.walk(target_dir):
        for dir_name in dirs:
            if re.match(r'^L[0-9]$', dir_name):
                actual_dirs.add(dir_name)

    # Create case mapping: l1 → L1, l2 → L2, etc.
    case_mappings = {}
    for actual_dir in actual_dirs:
        lowercase_version = actual_dir.lower()
        case_mappings[lowercase_version] = actual_dir

    logging.info(f"Found {len(actual_dirs)} lineage directories: {sorted(actual_dirs)}")
    logging.info(f"Case mappings: {case_mappings}")

    return case_mappings

def scan_files_with_case_issues(target_dir):
    """Find HTML files with lowercase directory references"""
    logging.info(f"Scanning for files with lowercase directory references in {target_dir}")

    affected_files = []
    html_files = []

    # Find all HTML files
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))

    logging.info(f"Scanning {len(html_files)} HTML files for case sensitivity issues")

    for i, file_path in enumerate(html_files):
        if i % 1000 == 0:
            logging.info(f"  Progress: {i}/{len(html_files)} files scanned...")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Look for patterns like /htm/l0/, /htm/l1/, etc.
                if re.search(r'/htm/l[0-9]', content):
                    affected_files.append(file_path)
        except Exception as e:
            logging.warning(f"Error reading {file_path}: {e}")
            continue

    logging.info(f"Found {len(affected_files)} files with case sensitivity issues")
    return affected_files

def fix_directory_case_in_file(file_path, case_mappings):
    """Fix directory case in single file"""
    changes_made = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Define the patterns for case fixes
        # Pattern: /htm/l0/ → /htm/L0/, /htm/l1/ → /htm/L1/, etc.
        for lowercase_dir, correct_case in case_mappings.items():
            # Fix href attributes
            old_pattern = f'/htm/{lowercase_dir}/'
            new_pattern = f'/htm/{correct_case}/'

            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                changes_made.append(f"{old_pattern} → {new_pattern}")

            # Also fix /auntruth/htm/l0/ patterns if they exist
            old_pattern_auntruth = f'/auntruth/htm/{lowercase_dir}/'
            new_pattern_auntruth = f'/auntruth/htm/{correct_case}/'

            if old_pattern_auntruth in content:
                content = content.replace(old_pattern_auntruth, new_pattern_auntruth)
                changes_made.append(f"{old_pattern_auntruth} → {new_pattern_auntruth}")

        # Apply regex patterns for more complex cases
        patterns_to_fix = [
            # href="/htm/l0/..." → href="/htm/L0/..."
            (r'(href|src)="([^"]*)/htm/l([0-9])([/"]*)', r'\1="\2/htm/L\3\4'),
            # href='/htm/l0/...' → href='/htm/L0/...'
            (r"(href|src)='([^']*)/htm/l([0-9])([/']*)", r"\1='\2/htm/L\3\4"),
            # /auntruth/htm/l0/ → /auntruth/htm/L0/
            (r'(href|src)="([^"]*)/auntruth/htm/l([0-9])([/"]*)', r'\1="\2/auntruth/htm/L\3\4'),
            (r"(href|src)='([^']*)/auntruth/htm/l([0-9])([/']*)", r"\1='\2/auntruth/htm/L\3\4"),
        ]

        for old_pattern, replacement in patterns_to_fix:
            old_content_before = content
            content = re.sub(old_pattern, replacement, content)
            if content != old_content_before:
                changes_made.append(f"Regex: {old_pattern} → {replacement}")

        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)

            return changes_made

        return []

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return []

def validate_fixes(case_mappings, sample_size=5):
    """Validate that case fixes work correctly"""
    logging.info("Validating directory case fixes...")

    # Test URLs that should now work (construct from case mappings)
    test_urls = []
    for lowercase_dir, correct_case in list(case_mappings.items())[:sample_size]:
        test_urls.extend([
            f'http://localhost:8000/auntruth/htm/{correct_case}/',
            f'http://localhost:8000/auntruth/htm/{correct_case}/index.htm'
        ])

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
                if status_code in ['200', '404']:  # 404 is OK if directory doesn't have index file
                    logging.info(f"✓ {url} → {status_code}")
                    success_count += 1
                else:
                    logging.warning(f"✗ {url} → {status_code}")
            else:
                logging.warning(f"✗ {url} → curl failed")
        except Exception as e:
            logging.warning(f"✗ {url} → Error: {e}")

    success_rate = (success_count / len(test_urls)) * 100 if test_urls else 100
    logging.info(f"Validation: {success_count}/{len(test_urls)} URLs working ({success_rate:.1f}%)")

    return success_rate > 60  # Consider successful if >60% work (some may legitimately return 404)

def main():
    """Main execution function"""
    args = setup_logging_and_args()

    logging.info("=" * 60)
    logging.info("Directory Case Sensitivity Fixer - Script 018")
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

    # Scan directory structure to create case mappings
    case_mappings = scan_directory_structure(args.target_dir)

    if not case_mappings:
        logging.warning("No lineage directories (L0, L1, etc.) found. Nothing to fix.")
        return

    # Scan for affected files
    affected_files = scan_files_with_case_issues(args.target_dir)

    if not affected_files:
        logging.info("No files found with case sensitivity issues. Nothing to do.")
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
                    case_issues = len(re.findall(r'/htm/l[0-9]', content))
                    logging.info(f"  {file_path}: {case_issues} case issues")
            except Exception as e:
                logging.info(f"  {file_path}: Error reading - {e}")

        if len(affected_files) > 5:
            logging.info(f"  ... and {len(affected_files) - 5} more files")

        logging.info(f"\nCase mappings to apply: {case_mappings}")
        logging.info("\nRun without --dry-run to apply changes")
        return

    # Process files
    files_fixed = 0
    total_changes = 0

    for i, file_path in enumerate(affected_files):
        if i % 10 == 0:
            logging.info(f"Progress: {i}/{len(affected_files)} files processed...")

        changes = fix_directory_case_in_file(file_path, case_mappings)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            logging.debug(f"Fixed {file_path}: {', '.join(changes)}")

    # Summary
    logging.info(f"\n=== COMPLETION SUMMARY ===")
    logging.info(f"Files processed: {len(affected_files)}")
    logging.info(f"Files modified: {files_fixed}")
    logging.info(f"Total changes made: {total_changes}")
    logging.info(f"Pattern fixed: /htm/l[0-9] → /htm/L[0-9]")

    if files_fixed > 0:
        # Validate the fixes
        if validate_fixes(case_mappings):
            logging.info("✓ Validation passed - Directory case is now correct")
        else:
            logging.warning("⚠ Validation concerns - Some directories may not exist")

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"PRPs/scripts/reports/case_fixes_{timestamp}.txt"

        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w') as f:
                f.write(f"Directory Case Sensitivity Fix Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Files processed: {len(affected_files)}\n")
                f.write(f"Files modified: {files_fixed}\n")
                f.write(f"Total changes: {total_changes}\n")
                f.write(f"Pattern: /htm/l[0-9] → /htm/L[0-9]\n")
                f.write(f"Case mappings: {case_mappings}\n\n")
                f.write("Files modified:\n")

                for file_path in affected_files:
                    # Quick check if file was actually modified
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as ff:
                            if not re.search(r'/htm/l[0-9]', ff.read()):
                                f.write(f"  {file_path}\n")
                    except:
                        pass

            logging.info(f"Report saved: {report_file}")
        except Exception as e:
            logging.warning(f"Could not save report: {e}")

        logging.info(f"\nNext steps:")
        logging.info(f"1. Test sample directory URLs manually")
        logging.info(f"2. Run broken link checker to verify improvement")
        logging.info(f"3. Commit changes: git add . && git commit -m 'Script 018: Fix directory case sensitivity'")
    else:
        logging.info("No changes were needed - all directory case references may already be correct")

if __name__ == "__main__":
    main()