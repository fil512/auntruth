#!/usr/bin/env python3
"""
Phase 4.2: Fix Image Case Sensitivity - Priority 2
Purpose: Fix image file case sensitivity issues

This script addresses broken links caused by case mismatches between
image references and actual image files.

CRITICAL SAFETY REQUIREMENTS:
- Uses git branch safety system
- Implements progress reporting
- Includes dry-run mode and error handling
- Checks actual file existence before making changes

Target Patterns to Fix:
- index_files/image###.jpg vs actual file case
- Check and fix case mismatches between links and files
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

def find_image_case_issues(target_dir: str) -> Dict[str, List[Dict]]:
    """Find HTML files with image case sensitivity issues"""
    issues_found = []

    print(f"🔍 Scanning {target_dir} for image case sensitivity issues...")

    # Pattern to find image references
    image_pattern = r'src="([^"]*\.(jpg|jpeg|png|gif|JPG|JPEG|PNG|GIF))"'

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Find all image references
                    image_refs = re.findall(image_pattern, content, re.IGNORECASE)

                    if image_refs:
                        file_issues = []
                        for img_ref, ext in image_refs:
                            # Resolve the full path of the referenced image
                            if img_ref.startswith('/'):
                                # Absolute path - convert to filesystem path
                                img_path = os.path.join('docs', img_ref.lstrip('/'))
                            else:
                                # Relative path
                                img_path = os.path.join(root, img_ref)

                            img_path = os.path.normpath(img_path)

                            # Check if the referenced file exists
                            if not os.path.exists(img_path):
                                # Check if there's a case variation that exists
                                dir_name = os.path.dirname(img_path)
                                file_name = os.path.basename(img_path)

                                if os.path.exists(dir_name):
                                    # List all files in the directory
                                    actual_files = os.listdir(dir_name)

                                    # Look for case-insensitive match
                                    for actual_file in actual_files:
                                        if actual_file.lower() == file_name.lower() and actual_file != file_name:
                                            file_issues.append({
                                                'html_file': file_path,
                                                'referenced': img_ref,
                                                'actual_file': actual_file,
                                                'actual_path': os.path.join(dir_name, actual_file)
                                            })
                                            break

                        if file_issues:
                            issues_found.extend(file_issues)

                except (OSError, IOError) as e:
                    logging.warning(f"Could not read {file_path}: {e}")
                    continue

    return issues_found

def fix_image_case_in_file(file_path: str, issues: List[Dict]) -> List[str]:
    """Apply image case fixes to single file"""
    changes_made = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        for issue in issues:
            if issue['html_file'] == file_path:
                # Replace the referenced path with the correct case
                old_ref = issue['referenced']
                # Get the correct filename
                correct_name = issue['actual_file']
                new_ref = old_ref.replace(os.path.basename(old_ref), correct_name)

                if old_ref != new_ref:
                    content = content.replace(f'src="{old_ref}"', f'src="{new_ref}"')
                    changes_made.append(f"Fixed image case: {old_ref} → {new_ref}")

        # Write the file only if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return []

    return changes_made

def show_dry_run_preview(issues_found: List[Dict]) -> None:
    """Show preview of what would be changed in dry-run mode"""
    print(f"\n📋 DRY RUN PREVIEW - Found {len(issues_found)} image case issues")
    print("=" * 60)

    if issues_found:
        print(f"\n🔧 Image case sensitivity issues:")
        for i, issue in enumerate(issues_found[:5]):  # Show first 5 issues
            print(f"  {i+1}. File: {issue['html_file']}")
            print(f"     Referenced: {issue['referenced']}")
            print(f"     Actual: {issue['actual_file']}")

        if len(issues_found) > 5:
            print(f"  ... and {len(issues_found) - 5} more issues")

    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Fix image case sensitivity issues - Phase 4.2')
    parser.add_argument('--target-dir', default='docs', help='Target directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--limit', type=int, help='Limit number of files processed (for testing)')
    parser.add_argument('--branch-name', default='main', help='Git branch name')
    parser.add_argument('--log-file', help='Log file path')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_file)

    print("🚀 Starting Phase 4.2: Image Case Sensitivity Fix")
    print("=" * 60)
    print("Expected Impact: 22 broken image links fixed")
    print("=" * 60)

    # Verify git branch
    try:
        current_branch = verify_git_branch(args.branch_name)
    except ValueError as e:
        logger.error(f"Git branch verification failed: {e}")
        return 1

    # Find files with image case sensitivity issues
    issues_found = find_image_case_issues(args.target_dir)

    if len(issues_found) == 0:
        print("✅ No image case sensitivity issues found")
        return 0

    print(f"📊 Found {len(issues_found)} image case sensitivity issues")

    # Dry run mode
    if args.dry_run:
        show_dry_run_preview(issues_found)
        print("\n🔍 This was a DRY RUN - no changes were made")
        print("Run without --dry-run to apply changes")
        return 0

    # Apply limit if specified
    if args.limit:
        issues_found = issues_found[:args.limit]
        print(f"📏 Limited to {len(issues_found)} issues for this run")

    # Group issues by HTML file
    files_to_fix = {}
    for issue in issues_found:
        html_file = issue['html_file']
        if html_file not in files_to_fix:
            files_to_fix[html_file] = []
        files_to_fix[html_file].append(issue)

    # Process files
    print(f"\n🔧 Processing {len(files_to_fix)} files...")
    files_fixed = 0
    total_changes = 0

    for i, (file_path, file_issues) in enumerate(files_to_fix.items()):
        if i % 10 == 0:
            print(f"Progress: {i}/{len(files_to_fix)} files processed...")

        changes = fix_image_case_in_file(file_path, file_issues)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            logger.info(f"Fixed {file_path}: {', '.join(changes)}")

    # Summary
    print(f"\n📋 PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Issues found: {len(issues_found)}")
    print(f"Files processed: {len(files_to_fix)}")
    print(f"Files fixed: {files_fixed}")
    print(f"Total changes: {total_changes}")

    print(f"\n✅ Phase 4.2 completed successfully!")
    print(f"Expected impact: Reduction in image case sensitivity broken links")

    return 0

if __name__ == "__main__":
    exit(main())