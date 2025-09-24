#!/usr/bin/env python3
"""
Fix absolute path prefixes for genealogy HTML files.
This script fixes broken links by adding /auntruth prefix to absolute paths.

Primary fixes:
1. /jpg/ -> /auntruth/jpg/
2. /htm/ -> /auntruth/htm/
3. /css/ -> /auntruth/css/
4. /au/ -> /auntruth/au/
5. /mpg/ -> /auntruth/mpg/

Based on broken link analysis showing 13,191 broken links with missing /auntruth prefix.
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime

def fix_absolute_prefixes_in_file(file_path):
    """Fix absolute path prefix issues in a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Fix /jpg/ links - add /auntruth prefix
        old_content = content
        # Match various patterns: href="/jpg/...", src="/jpg/...", etc.
        content = re.sub(r'(href|src|action|value)=["\']\/jpg\/', r'\1="/auntruth/jpg/', content)
        if content != old_content:
            changes_made.append("Fixed /jpg/ -> /auntruth/jpg/")

        # Fix /htm/ links - add /auntruth prefix
        old_content = content
        content = re.sub(r'(href|src|action|value)=["\']\/htm\/', r'\1="/auntruth/htm/', content)
        if content != old_content:
            changes_made.append("Fixed /htm/ -> /auntruth/htm/")

        # Fix /css/ links - add /auntruth prefix
        old_content = content
        content = re.sub(r'(href|src|action|value)=["\']\/css\/', r'\1="/auntruth/css/', content)
        if content != old_content:
            changes_made.append("Fixed /css/ -> /auntruth/css/")

        # Fix /au/ links - add /auntruth prefix
        old_content = content
        content = re.sub(r'(href|src|action|value)=["\']\/au\/', r'\1="/auntruth/au/', content)
        if content != old_content:
            changes_made.append("Fixed /au/ -> /auntruth/au/")

        # Fix /mpg/ links - add /auntruth prefix
        old_content = content
        content = re.sub(r'(href|src|action|value)=["\']\/mpg\/', r'\1="/auntruth/mpg/', content)
        if content != old_content:
            changes_made.append("Fixed /mpg/ -> /auntruth/mpg/")

        # Additional common paths that might be missing prefix
        # Fix /jpg without trailing slash (like /jpg/image.jpg)
        old_content = content
        content = re.sub(r'(href|src|action|value)=["\']\/jpg([^\/])', r'\1="/auntruth/jpg\2', content)
        if content != old_content:
            changes_made.append("Fixed /jpg files -> /auntruth/jpg files")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        return []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def find_affected_files(target_dir, dry_run=True):
    """Find all HTML files that contain absolute paths needing prefix fixes."""
    affected_files = []
    patterns = [
        r'(href|src|action|value)=["\']\/jpg\/',
        r'(href|src|action|value)=["\']\/htm\/',
        r'(href|src|action|value)=["\']\/css\/',
        r'(href|src|action|value)=["\']\/au\/',
        r'(href|src|action|value)=["\']\/mpg\/',
        r'(href|src|action|value)=["\']\/jpg[^\/]'  # /jpg without trailing slash
    ]

    combined_pattern = '|'.join(patterns)

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    if re.search(combined_pattern, content):
                        affected_files.append(file_path)

                        if dry_run and len(affected_files) <= 5:
                            # Show sample matches for first few files
                            matches = re.findall(combined_pattern, content)
                            print(f"Sample from {file_path.relative_to(target_dir)}: {len(matches)} matches")

                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return affected_files

def main():
    """Fix absolute path prefixes in HTML files."""
    parser = argparse.ArgumentParser(description='Fix absolute path prefixes in HTML files')
    parser.add_argument('--target-dir', default='docs', help='Target directory (default: docs)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--execute', action='store_true', help='Execute the fixes')
    parser.add_argument('--test-mode', action='store_true', help='Process only first 5 files for testing')
    parser.add_argument('--validate', action='store_true', help='Validate changes after execution')

    args = parser.parse_args()

    # Convert to absolute path
    target_dir = Path(args.target_dir).resolve()
    if not target_dir.exists():
        print(f"Error: Target directory {target_dir} does not exist")
        return 1

    print(f"=== Fix Absolute Path Prefixes ===")
    print(f"Target directory: {target_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Find affected files
    print("Scanning for files with absolute path prefix issues...")
    affected_files = find_affected_files(target_dir, dry_run=True)

    print(f"\nFound {len(affected_files)} files with absolute path prefix issues")

    if len(affected_files) == 0:
        print("No files need fixing. Exiting.")
        return 0

    if args.dry_run:
        print("\n=== DRY RUN MODE ===")
        print("The following files would be modified:")
        for i, file_path in enumerate(affected_files[:10]):  # Show first 10
            print(f"  {file_path.relative_to(target_dir)}")
        if len(affected_files) > 10:
            print(f"  ... and {len(affected_files) - 10} more files")

        print(f"\nTo execute these changes, run with --execute")
        return 0

    if not args.execute:
        print("\nNo action specified. Use --dry-run to preview or --execute to apply changes.")
        return 0

    # Test mode - limit to first 5 files
    if args.test_mode:
        affected_files = affected_files[:5]
        print(f"\n=== TEST MODE - Processing first {len(affected_files)} files ===")

    # Process files
    print(f"\n=== EXECUTING FIXES ===")
    print(f"Processing {len(affected_files)} files...")

    total_changes = 0
    files_modified = 0

    for i, file_path in enumerate(affected_files):
        if i % 100 == 0 and i > 0:
            print(f"Progress: {i}/{len(affected_files)} files processed")

        changes = fix_absolute_prefixes_in_file(file_path)
        if changes:
            files_modified += 1
            total_changes += len(changes)
            if args.test_mode:  # Show details in test mode
                print(f"Fixed {file_path.relative_to(target_dir)}: {', '.join(changes)}")

    print(f"\n=== EXECUTION COMPLETE ===")
    print(f"Files processed: {len(affected_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total changes made: {total_changes}")

    if args.validate:
        print(f"\n=== VALIDATION ===")
        remaining_files = find_affected_files(target_dir, dry_run=False)
        print(f"Files still needing fixes: {len(remaining_files)}")
        if len(remaining_files) == 0:
            print("✅ All absolute path prefix issues have been resolved!")
        else:
            print("⚠️  Some files still need fixing")

    return 0

if __name__ == "__main__":
    exit(main())