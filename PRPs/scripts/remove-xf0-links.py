#!/usr/bin/env python3
"""
Remove XF0.htm Links Fix Script

This script removes anchor tags pointing to the non-existent XF0.htm file
while preserving any content inside the tags. XF0.htm is used as a placeholder
for empty person slots in family trees (empty spouse slots, parent slots, etc.).

Usage:
    python3 remove-xf0-links.py [--dry-run] [path]

Arguments:
    path: Directory to process (default: docs/htm)
    --dry-run: Show what would be changed without making changes

Based on PRP analysis, this should fix 6,276+ broken links.
"""

import os
import sys
import re
import argparse
from pathlib import Path

def remove_xf0_links(content):
    """
    Remove anchor tags pointing to XF0.htm while preserving content.

    Examples:
    <a href="/auntruth/htm/L0/XF0.htm"><strong></strong></a> → <strong></strong>
    <a href="./L0/XF0.htm">Some Text</a> → Some Text
    """
    # Pattern to match anchor tags pointing to XF0.htm
    # This handles various path formats:
    # - /auntruth/htm/L0/XF0.htm
    # - ./L0/XF0.htm
    # - ../L0/XF0.htm
    # - L0/XF0.htm
    pattern = r'<a\s+[^>]*href\s*=\s*["\'][^"\']*L0[/\\]XF0\.htm[^"\']*["\'][^>]*>(.*?)</a>'

    def replace_func(match):
        # Return just the content inside the anchor tag
        inner_content = match.group(1)
        return inner_content

    # Remove the anchor tags but keep the content
    new_content = re.sub(pattern, replace_func, content, flags=re.IGNORECASE | re.DOTALL)

    return new_content

def process_file(file_path, dry_run=False):
    """Process a single HTML file to remove XF0.htm links."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content = remove_xf0_links(content)

        if content != new_content:
            changes = content.count('XF0.htm') - new_content.count('XF0.htm')
            if dry_run:
                print(f"WOULD MODIFY: {file_path} ({changes} XF0.htm links)")
                return changes
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"MODIFIED: {file_path} ({changes} XF0.htm links removed)")
                return changes

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
        print(f"Would remove {total_changes} XF0.htm links")
    else:
        print(f"\nCOMPLETE:")
        print(f"Modified {files_changed} files")
        print(f"Removed {total_changes} XF0.htm links")

    return files_changed, total_changes

def main():
    parser = argparse.ArgumentParser(description='Remove XF0.htm links from HTML files')
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
        print(f"\nSUCCESS: Fixed {total_changes} XF0.htm broken links in {files_changed} files")

if __name__ == '__main__':
    main()