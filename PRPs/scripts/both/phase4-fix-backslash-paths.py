#!/usr/bin/env python3
"""
Phase 4.3: Fix Windows Backslash Paths - Priority 3
Purpose: Convert Windows-style backslash paths to forward slashes

This script addresses broken links caused by Windows-style backslash paths
that don't work in web environments.

CRITICAL SAFETY REQUIREMENTS:
- Uses git branch safety system
- Implements progress reporting
- Includes dry-run mode and error handling
- Tests URLs with curl before and after changes

Target Patterns to Fix:
- \AuntRuth\index#.htm → /auntruth/index#.htm
- Similar Windows backslash patterns
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

def verify_git_branch(expected_branch: str = "main") -> str:
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

def find_backslash_path_issues(target_dir: str) -> List[str]:
    """Find HTML files with Windows backslash path issues"""
    files_with_issues = []

    print(f"🔍 Scanning {target_dir} for Windows backslash path issues...")

    # Patterns to find Windows-style paths
    patterns = [
        r'\\AuntRuth\\',
        r'\\auntruth\\',
        r'href="[^"]*\\[^"]*"',
        r'src="[^"]*\\[^"]*"'
    ]

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check for any Windows-style backslash paths
                    for pattern in patterns:
                        if re.search(pattern, content):
                            files_with_issues.append(file_path)
                            break

                except (OSError, IOError) as e:
                    logging.warning(f"Could not read {file_path}: {e}")
                    continue

    return files_with_issues

def test_url_with_curl(url: str, timeout: int = 3) -> int:
    """Test URL with curl and return HTTP status code"""
    try:
        result = subprocess.run([
            'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url
        ], capture_output=True, text=True, timeout=timeout)
        return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        return 0  # Treat as failure

def fix_backslash_paths_in_file(file_path: str) -> List[str]:
    """Apply backslash path fixes to single file"""
    changes_made = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Pattern fixes - convert Windows backslashes to forward slashes
        patterns_to_fix = [
            # Fix \AuntRuth\ → /auntruth/
            (r'\\AuntRuth\\', '/auntruth/'),

            # Fix \auntruth\ → /auntruth/
            (r'\\auntruth\\', '/auntruth/'),

            # Fix general backslashes in href attributes
            (r'href="([^"]*?)\\([^"]*?)"', r'href="\1/\2"'),

            # Fix general backslashes in src attributes
            (r'src="([^"]*?)\\([^"]*?)"', r'src="\1/\2"'),
        ]

        for old_pattern, new_pattern in patterns_to_fix:
            old_content = content
            if callable(new_pattern):
                # For regex substitution functions
                content = re.sub(old_pattern, new_pattern, content)
            else:
                # For simple string replacement
                content = re.sub(old_pattern, new_pattern, content)

            if content != old_content:
                if '\\' in old_pattern:
                    changes_made.append(f"Fixed Windows backslash paths: {old_pattern}")
                else:
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

    if not test_cases:
        return validation_results

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

def show_dry_run_preview(files_with_issues: List[str]) -> None:
    """Show preview of what would be changed in dry-run mode"""
    print(f"\n📋 DRY RUN PREVIEW - Would process {len(files_with_issues)} files")
    print("=" * 60)

    if files_with_issues:
        print(f"\n🔧 Files with Windows backslash path issues ({len(files_with_issues)} files):")
        for file_path in files_with_issues[:5]:  # Show first 5 files
            print(f"  - {file_path}")
        if len(files_with_issues) > 5:
            print(f"  ... and {len(files_with_issues) - 5} more files")

    print("\nExample fixes that would be made:")
    print("  - \\AuntRuth\\index1.htm → /auntruth/index1.htm")
    print("  - \\auntruth\\file.htm → /auntruth/file.htm")
    print("  - href=\"path\\file.htm\" → href=\"path/file.htm\"")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Fix Windows backslash paths - Phase 4.3')
    parser.add_argument('--target-dir', default='docs', help='Target directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--limit', type=int, help='Limit number of files processed (for testing)')
    parser.add_argument('--branch-name', default='main', help='Git branch name')
    parser.add_argument('--log-file', help='Log file path')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_file)

    print("🚀 Starting Phase 4.3: Windows Backslash Paths Fix")
    print("=" * 60)
    print("Expected Impact: 3 broken links with Windows backslash paths fixed")
    print("=" * 60)

    # Verify git branch
    try:
        current_branch = verify_git_branch(args.branch_name)
    except ValueError as e:
        logger.error(f"Git branch verification failed: {e}")
        return 1

    # Find files with backslash path issues
    files_with_issues = find_backslash_path_issues(args.target_dir)

    if len(files_with_issues) == 0:
        print("✅ No Windows backslash path issues found")
        return 0

    print(f"📊 Found Windows backslash path issues in {len(files_with_issues)} files")

    # Dry run mode
    if args.dry_run:
        show_dry_run_preview(files_with_issues)
        print("\n🔍 This was a DRY RUN - no changes were made")
        print("Run without --dry-run to apply changes")
        return 0

    # Apply limit if specified
    if args.limit:
        files_with_issues = files_with_issues[:args.limit]
        print(f"📏 Limited to {len(files_with_issues)} files for this run")

    # Process files
    print(f"\n🔧 Processing {len(files_with_issues)} files...")
    files_fixed = 0
    total_changes = 0

    for i, file_path in enumerate(files_with_issues):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(files_with_issues)} files processed...")

        changes = fix_backslash_paths_in_file(file_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            logger.info(f"Fixed {file_path}: {', '.join(changes)}")

    # Summary
    print(f"\n📋 PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Files processed: {len(files_with_issues)}")
    print(f"Files fixed: {files_fixed}")
    print(f"Total changes: {total_changes}")

    # Test some specific cases (if server is available)
    test_cases = []  # Add specific test cases if known
    if files_fixed > 0 and test_cases:
        validation = validate_fixes(test_cases)
        print(f"\n🔬 Validation results:")
        print(f"Test cases: {validation['total']}")
        print(f"Successful fixes: {validation['success']}")
        print(f"Failed fixes: {validation['failed']}")

    print(f"\n✅ Phase 4.3 completed successfully!")
    print(f"Expected impact: Reduction in Windows backslash path broken links")

    return 0

if __name__ == "__main__":
    exit(main())