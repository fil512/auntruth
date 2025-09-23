#!/usr/bin/env python3
"""
Fix Backslash Path Issues Script

This script fixes Windows-style backslash paths in HTML files,
converting them to forward slashes for web compatibility.

Usage:
    python3 fix-backslash-paths.py [--dry-run] [path]

Arguments:
    path: Directory to process (default: docs/htm)
    --dry-run: Show what would be changed without making changes

Based on PRP analysis, this should fix 500+ broken links.
"""

import os
import sys
import re
import argparse
from pathlib import Path

def fix_backslash_paths(content):
    """
    Fix backslash paths in HTML content.

    Examples to fix:
    - \\AuntRuth\\cgi-bin\\counter.pl → /auntruth/cgi-bin/counter.pl
    - ./L0\\XF0.htm → ./L0/XF0.htm
    - ../L1\\XI123.htm → ../L1/XI123.htm
    - /auntruth/htm/htm/ → /auntruth/htm/
    """

    fixes_made = 0
    new_content = content

    # Fix 1: Replace backslashes in paths with forward slashes
    # Pattern for paths with backslashes (but not in content, only in hrefs and src)
    patterns_to_fix = [
        # Fix href attributes with backslashes
        (r'(href\s*=\s*["\'][^"\']*?)\\([^"\']*["\'])', r'\1/\2'),
        # Fix src attributes with backslashes
        (r'(src\s*=\s*["\'][^"\']*?)\\([^"\']*["\'])', r'\1/\2'),
        # Fix action attributes with backslashes
        (r'(action\s*=\s*["\'][^"\']*?)\\([^"\']*["\'])', r'\1/\2'),
    ]

    for pattern, replacement in patterns_to_fix:
        old_content = new_content
        new_content = re.sub(pattern, replacement, new_content, flags=re.IGNORECASE)
        # Keep applying until no more changes (for multiple backslashes)
        while old_content != new_content:
            old_content = new_content
            new_content = re.sub(pattern, replacement, new_content, flags=re.IGNORECASE)

    # Fix 2: Double htm paths: /htm/htm/ → /htm/
    double_htm_pattern = r'/htm/htm/'
    if re.search(double_htm_pattern, new_content):
        new_content = re.sub(double_htm_pattern, '/htm/', new_content)
        fixes_made += len(re.findall(double_htm_pattern, content))

    # Fix 3: Wrong base paths: /auntruth/AuntRuth/ → /auntruth/htm/
    wrong_base_pattern = r'/auntruth/AuntRuth/'
    if re.search(wrong_base_pattern, new_content):
        new_content = re.sub(wrong_base_pattern, '/auntruth/htm/', new_content)
        fixes_made += len(re.findall(wrong_base_pattern, content))

    # Count total backslash fixes
    original_backslashes = content.count('\\')
    new_backslashes = new_content.count('\\')
    backslash_fixes = original_backslashes - new_backslashes

    total_fixes = backslash_fixes + fixes_made

    return new_content, total_fixes

def process_file(file_path, dry_run=False):
    """Process a single HTML file to fix backslash paths."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content, fixes_made = fix_backslash_paths(content)

        if content != new_content:
            if dry_run:
                print(f"WOULD MODIFY: {file_path} ({fixes_made} path fixes)")
                return fixes_made
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"MODIFIED: {file_path} ({fixes_made} path fixes)")
                return fixes_made

        return 0

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return 0

def process_directory(directory, dry_run=False):
    """Process all HTML files in a directory recursively."""
    total_changes = 0
    files_changed = 0

    directory = Path(directory)
    if not directory.exists():
        print(f"ERROR: Directory {directory} does not exist")
        return 0, 0

    print(f"Processing HTML files in {directory}...")

    # Find all HTML files
    html_files = list(directory.glob('**/*.htm')) + list(directory.glob('**/*.html'))

    print(f"Found {len(html_files)} HTML files")

    for file_path in html_files:
        changes = process_file(file_path, dry_run)
        if changes > 0:
            total_changes += changes
            files_changed += 1

    if dry_run:
        print(f"\nDRY RUN SUMMARY:")
        print(f"Would modify {files_changed} files")
        print(f"Would fix {total_changes} path issues")
    else:
        print(f"\nCOMPLETE:")
        print(f"Modified {files_changed} files")
        print(f"Fixed {total_changes} path issues")

    return files_changed, total_changes

def main():
    parser = argparse.ArgumentParser(description='Fix backslash paths in HTML files')
    parser.add_argument('path', nargs='?', default='docs/htm',
                       help='Directory to process (default: docs/htm)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')

    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")

    # Process the specified directory
    files_changed, total_changes = process_directory(args.path, args.dry_run)

    if not args.dry_run and total_changes > 0:
        print(f"\nSUCCESS: Fixed {total_changes} path issues in {files_changed} files")

if __name__ == '__main__':
    main()