#!/usr/bin/env python3
"""
Remove CGI Counter References Fix Script

This script removes obsolete CGI counter references from HTML files.
CGI counters were 1990s technology used to track page visits and are
no longer functional or needed.

Usage:
    python3 remove-cgi-counters.py [--dry-run] [path]

Arguments:
    path: Directory to process (default: docs/htm)
    --dry-run: Show what would be changed without making changes

Based on PRP analysis, this should fix 797 broken links.
"""

import os
import sys
import re
import argparse
from pathlib import Path

def remove_cgi_counters(content):
    """
    Remove CGI counter references from HTML content.

    Examples to remove:
    - <img src="\cgi-bin\counter.pl?AuntRuth" width="1" height="1">
    - <img src="\AuntRuth\cgi-bin\counter.pl" alt="">
    - Any variations with forward/backward slashes
    """

    # Pattern 1: \cgi-bin\counter.pl?AuntRuth
    pattern1 = r'<img[^>]*src\s*=\s*["\'][^"\']*\\cgi-bin\\counter\.pl\?[^"\']*["\'][^>]*>'

    # Pattern 2: \AuntRuth\cgi-bin\counter.pl
    pattern2 = r'<img[^>]*src\s*=\s*["\'][^"\']*\\AuntRuth\\cgi-bin\\counter\.pl[^"\']*["\'][^>]*>'

    # Pattern 3: /cgi-bin/counter.pl variations (just in case)
    pattern3 = r'<img[^>]*src\s*=\s*["\'][^"\']*[/\\]cgi-bin[/\\]counter\.pl[^"\']*["\'][^>]*>'

    # Pattern 4: Any other counter.pl references
    pattern4 = r'<img[^>]*src\s*=\s*["\'][^"\']*counter\.pl[^"\']*["\'][^>]*>'

    # Apply all patterns
    new_content = content
    removed_count = 0

    for pattern in [pattern1, pattern2, pattern3, pattern4]:
        matches = re.findall(pattern, new_content, flags=re.IGNORECASE)
        removed_count += len(matches)
        new_content = re.sub(pattern, '', new_content, flags=re.IGNORECASE)

    return new_content, removed_count

def process_file(file_path, dry_run=False):
    """Process a single HTML file to remove CGI counter references."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content, removed_count = remove_cgi_counters(content)

        if content != new_content:
            if dry_run:
                print(f"WOULD MODIFY: {file_path} ({removed_count} CGI counter references)")
                return removed_count
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"MODIFIED: {file_path} ({removed_count} CGI counter references removed)")
                return removed_count

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
        print(f"Would remove {total_changes} CGI counter references")
    else:
        print(f"\nCOMPLETE:")
        print(f"Modified {files_changed} files")
        print(f"Removed {total_changes} CGI counter references")

    return files_changed, total_changes

def main():
    parser = argparse.ArgumentParser(description='Remove CGI counter references from HTML files')
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
        print(f"\nSUCCESS: Fixed {total_changes} CGI counter broken links in {files_changed} files")

if __name__ == '__main__':
    main()