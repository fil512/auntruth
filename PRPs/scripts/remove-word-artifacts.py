#!/usr/bin/env python3
"""
Remove Microsoft Word Artifacts Script

This script removes references to Microsoft Word temporary files and artifacts
that were created during HTML generation from Word documents. These files
typically don't exist and create broken links.

Usage:
    python3 remove-word-artifacts.py [--dry-run] [path]

Arguments:
    path: Directory to process (default: docs/htm)
    --dry-run: Show what would be changed without making changes

Based on PRP analysis, this fixes Word temporary file references.
"""

import os
import sys
import re
import argparse
from pathlib import Path

def remove_word_artifacts(content):
    """
    Remove Microsoft Word artifact references from HTML content.

    Examples to remove:
    - <link href="./Walter_files/filelist.xml" rel="File-List">
    - <o:DocumentProperties>...</o:DocumentProperties>
    - <img src="./JohnII_files/image001.gif">
    - <script src="./Walter_files/editdata.mso"></script>
    """

    removed_count = 0
    new_content = content

    # Pattern 1: Remove references to *_files/ directories (Word temp files)
    patterns_to_remove = [
        # Remove links to *_files/filelist.xml
        r'<link[^>]*href\s*=\s*["\'][^"\']*_files[/\\]filelist\.xml[^"\']*["\'][^>]*>',

        # Remove links to *_files/*.mso files
        r'<[^>]*[^>]*\s*=\s*["\'][^"\']*_files[/\\][^"\']*\.mso[^"\']*["\'][^>]*>',

        # Remove img tags pointing to *_files/*.gif
        r'<img[^>]*src\s*=\s*["\'][^"\']*_files[/\\][^"\']*\.gif[^"\']*["\'][^>]*>',

        # Remove img tags pointing to *_files/*.png
        r'<img[^>]*src\s*=\s*["\'][^"\']*_files[/\\][^"\']*\.png[^"\']*["\'][^>]*>',

        # Remove img tags pointing to *_files/*.jpg
        r'<img[^>]*src\s*=\s*["\'][^"\']*_files[/\\][^"\']*\.jpg[^"\']*["\'][^>]*>',

        # Remove script tags pointing to *_files/
        r'<script[^>]*src\s*=\s*["\'][^"\']*_files[/\\][^"\']*["\'][^>]*>.*?</script>',

        # Remove any other references to *_files/ directories
        r'<[^>]*[^>]*\s*=\s*["\'][^"\']*_files[/\\][^"\']*["\'][^>]*>',
    ]

    # Pattern 2: Remove Office-specific XML namespaces and elements
    office_patterns = [
        # Remove o:DocumentProperties blocks
        r'<o:DocumentProperties>.*?</o:DocumentProperties>',

        # Remove w:WordDocument blocks
        r'<w:WordDocument>.*?</w:WordDocument>',

        # Remove Office XML namespace declarations
        r'xmlns:o\s*=\s*["\'][^"\']*["\']',
        r'xmlns:w\s*=\s*["\'][^"\']*["\']',
        r'xmlns:m\s*=\s*["\'][^"\']*["\']',
        r'xmlns:v\s*=\s*["\'][^"\']*["\']',

        # Remove Word-specific style attributes
        r'style\s*=\s*["\']mso-[^"\']*["\']',

        # Remove Word conditional comments
        r'<!--\[if [^>]*>.*?<!\[endif\]-->',
    ]

    # Apply all patterns
    all_patterns = patterns_to_remove + office_patterns

    for pattern in all_patterns:
        matches = re.findall(pattern, new_content, flags=re.IGNORECASE | re.DOTALL)
        removed_count += len(matches)
        new_content = re.sub(pattern, '', new_content, flags=re.IGNORECASE | re.DOTALL)

    # Clean up any empty lines left by removals
    new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)

    return new_content, removed_count

def process_file(file_path, dry_run=False):
    """Process a single HTML file to remove Word artifacts."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content, removed_count = remove_word_artifacts(content)

        if content != new_content:
            if dry_run:
                print(f"WOULD MODIFY: {file_path} ({removed_count} Word artifacts)")
                return removed_count
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"MODIFIED: {file_path} ({removed_count} Word artifacts removed)")
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
        print(f"Would remove {total_changes} Word artifacts")
    else:
        print(f"\nCOMPLETE:")
        print(f"Modified {files_changed} files")
        print(f"Removed {total_changes} Word artifacts")

    return files_changed, total_changes

def main():
    parser = argparse.ArgumentParser(description='Remove Microsoft Word artifacts from HTML files')
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
        print(f"\nSUCCESS: Removed {total_changes} Word artifacts from {files_changed} files")

if __name__ == '__main__':
    main()