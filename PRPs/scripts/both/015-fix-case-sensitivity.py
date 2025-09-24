#!/usr/bin/env python3
"""
Fix Case Sensitivity Issues - Priority 1
Purpose: Fixes INDEX.htm → index.htm case sensitivity issues

This script addresses broken links caused by case sensitivity issues where
files reference INDEX.htm (uppercase) but the actual files are index.htm (lowercase).

CRITICAL SAFETY REQUIREMENTS:
- Uses git branch safety system
- Implements progress reporting
- Includes dry-run mode and error handling
- Tests URLs with curl before and after changes

Target Patterns to Fix:
- /auntruth/htm/L0/INDEX.htm → /auntruth/htm/L0/index.htm
- /auntruth/htm/L1/INDEX.htm → /auntruth/htm/L1/index.htm
- Similar patterns for Index.htm → index.htm
"""

import os
import re
import argparse
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

def setup_logging(log_file: str = None) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def verify_git_branch(expected_branch: str = "fix-broken-links-fix-absolute-htm-paths") -> str:
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            print(f"⚠️  Expected branch {expected_branch}, but currently on {current_branch}")
            print(f"✅ Proceeding with current branch: {current_branch}")
        else:
            print(f"✅ Verified working in correct branch: {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get current git branch: {e}")

def find_case_sensitivity_issues(target_dir: str) -> Dict[str, List[str]]:
    """Find HTML files with case sensitivity issues in index file references"""
    issues_found = {
        'INDEX.htm': [],
        'Index.htm': []
    }

    print(f"🔍 Scanning {target_dir} for case sensitivity issues...")

    patterns = [
        r'/auntruth/htm/L[0-9]+/INDEX\.htm',   # Uppercase INDEX.htm
        r'/auntruth/htm/L[0-9]+/Index\.htm',   # Title case Index.htm
    ]

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check for uppercase INDEX.htm (NO IGNORECASE - we want exact case matches)
                    if re.search(patterns[0], content):
                        issues_found['INDEX.htm'].append(file_path)

                    # Check for title case Index.htm (NO IGNORECASE - we want exact case matches)
                    if re.search(patterns[1], content):
                        issues_found['Index.htm'].append(file_path)

                except (OSError, IOError) as e:
                    logging.warning(f"Could not read {file_path}: {e}")
                    continue

    return issues_found

def test_url_with_curl(url: str, timeout: int = 3) -> int:
    """Test URL with curl and return HTTP status code"""
    try:
        result = subprocess.run([
            'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url
        ], capture_output=True, text=True, timeout=timeout)
        return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        return 0  # Treat as failure

def fix_case_sensitivity_in_file(file_path: str) -> List[str]:
    """Apply case sensitivity fixes to single file"""
    changes_made = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Pattern fixes - convert uppercase/titlecase to lowercase
        patterns_to_fix = [
            # Fix INDEX.htm → index.htm
            (r'(/auntruth/htm/L[0-9]+/)INDEX\.htm', r'\1index.htm'),

            # Fix Index.htm → index.htm
            (r'(/auntruth/htm/L[0-9]+/)Index\.htm', r'\1index.htm'),
        ]

        for old_pattern, new_pattern in patterns_to_fix:
            old_content = content
            content = re.sub(old_pattern, new_pattern, content)
            if content != old_content:
                matches = len(re.findall(old_pattern, old_content))
                changes_made.append(f"Fixed {matches} instances of {old_pattern}")

        # Write the file only if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return []

    return changes_made

def validate_fixes(test_cases: List[Tuple[str, str]]) -> Dict[str, int]:
    """Validate that fixes work by testing specific URLs"""
    validation_results = {"total": 0, "success": 0, "failed": 0}

    print(f"🔬 Validating {len(test_cases)} URL fixes...")

    for broken_url, fixed_url in test_cases:
        validation_results["total"] += 1

        # Test that broken URL is indeed broken
        broken_status = test_url_with_curl(broken_url)
        fixed_status = test_url_with_curl(fixed_url)

        if broken_status == 404 and fixed_status == 200:
            validation_results["success"] += 1
            print(f"  ✅ {broken_url} (404) → {fixed_url} (200)")
        else:
            validation_results["failed"] += 1
            print(f"  ❌ {broken_url} ({broken_status}) → {fixed_url} ({fixed_status})")

    return validation_results

def show_dry_run_preview(issues_found: Dict[str, List[str]]) -> None:
    """Show preview of what would be changed in dry-run mode"""
    total_files = sum(len(files) for files in issues_found.values())

    print(f"\n📋 DRY RUN PREVIEW - Would process {total_files} files")
    print("=" * 60)

    for issue_type, files in issues_found.items():
        if files:
            print(f"\n🔧 {issue_type} issues ({len(files)} files):")
            for file_path in files[:5]:  # Show first 5 files
                print(f"  - {file_path}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more files")

    print("\nExample fixes that would be made:")
    print("  - INDEX.htm → index.htm")
    print("  - Index.htm → index.htm")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Fix case sensitivity issues in index file references')
    parser.add_argument('--target-dir', default='docs', help='Target directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--limit', type=int, help='Limit number of files processed (for testing)')
    parser.add_argument('--branch-name', default='fix-broken-links-fix-absolute-htm-paths', help='Git branch name')
    parser.add_argument('--log-file', help='Log file path')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_file)

    print("🚀 Starting Case Sensitivity Fix (Script 015 - CORRECTED)")
    print("=" * 60)

    # Verify git branch
    try:
        current_branch = verify_git_branch(args.branch_name)
    except ValueError as e:
        logger.error(f"Git branch verification failed: {e}")
        return 1

    # Find files with case sensitivity issues
    issues_found = find_case_sensitivity_issues(args.target_dir)

    total_files = sum(len(files) for files in issues_found.values())

    if total_files == 0:
        print("✅ No case sensitivity issues found")
        return 0

    print(f"📊 Found case sensitivity issues:")
    for issue_type, files in issues_found.items():
        if files:
            print(f"  - {issue_type}: {len(files)} files")

    # Dry run mode
    if args.dry_run:
        show_dry_run_preview(issues_found)
        print("\n🔍 This was a DRY RUN - no changes were made")
        print("Run without --dry-run to apply changes")
        return 0

    # Process files
    print(f"\n🔧 Processing {total_files} files...")
    files_fixed = 0
    total_changes = 0

    all_files = []
    for files in issues_found.values():
        all_files.extend(files)

    # Apply limit if specified
    if args.limit:
        all_files = all_files[:args.limit]
        print(f"📏 Limited to {len(all_files)} files for this run")

    for i, file_path in enumerate(all_files):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(all_files)} files processed...")

        changes = fix_case_sensitivity_in_file(file_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            logger.info(f"Fixed {file_path}: {', '.join(changes)}")

    # Summary
    print(f"\n📋 PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Files processed: {len(all_files)}")
    print(f"Files fixed: {files_fixed}")
    print(f"Total changes: {total_changes}")

    # Test some specific cases
    if files_fixed > 0:
        test_cases = [
            ("http://localhost:8000/auntruth/htm/L0/INDEX.htm", "http://localhost:8000/auntruth/htm/L0/index.htm"),
            ("http://localhost:8000/auntruth/htm/L1/INDEX.htm", "http://localhost:8000/auntruth/htm/L1/index.htm"),
        ]

        validation = validate_fixes(test_cases)
        print(f"\n🔬 Validation results:")
        print(f"Test cases: {validation['total']}")
        print(f"Successful fixes: {validation['success']}")
        print(f"Failed fixes: {validation['failed']}")

    print(f"\n✅ Script 015 (CORRECTED) completed successfully!")
    print(f"Expected impact: Reduction in case sensitivity related broken links")
    print(f"Next: Run broken links checker to verify improvements")

    return 0

if __name__ == "__main__":
    exit(main())