#!/usr/bin/env python3
"""
Fix XI Lineage References Script

This script fixes references to XI files that exist in different lineage
directories or as XF files instead of XI files. For example, XI2627.htm
is referenced but actually exists as XF2627.htm in L4.

Usage:
    python3 fix-xi-lineage-refs.py [--dry-run] [path]

Arguments:
    path: Directory to process (default: docs/htm)
    --dry-run: Show what would be changed without making changes

Based on PRP analysis, this fixes XI references to point to correct locations.
"""

import os
import sys
import re
import argparse
from pathlib import Path

def build_file_index(base_directory):
    """
    Build an index of all XI and XF files with their actual locations.
    Returns a mapping of file numbers to their actual paths.
    """
    file_index = {}
    base_path = Path(base_directory)

    # Search all lineage directories
    for lineage_dir in base_path.glob('L*'):
        if lineage_dir.is_dir():
            # Find all XI and XF files
            for pattern in ['XI*.htm', 'XF*.htm']:
                for file_path in lineage_dir.glob(pattern):
                    # Extract the number from the filename
                    match = re.match(r'X[IF](\d+)\.htm', file_path.name)
                    if match:
                        file_number = match.group(1)
                        # Store the relative path from the base directory
                        relative_path = file_path.relative_to(base_path)
                        file_index[file_number] = str(relative_path)

    return file_index

def fix_xi_lineage_refs(content, file_index, base_path):
    """
    Fix XI lineage references in HTML content.

    Args:
        content: HTML content to process
        file_index: Mapping of file numbers to actual paths
        base_path: Base path for constructing relative URLs
    """

    fixes_made = 0
    new_content = content

    # Pattern to match XI file references
    # Look for href attributes pointing to XI files
    xi_pattern = r'(href\s*=\s*["\'])([^"\']*[/\\])(XI)(\d+)(\.htm)([^"\']*["\'])'

    def replace_xi_ref(match):
        nonlocal fixes_made

        prefix = match.group(1)  # href="
        path_part = match.group(2)  # path before filename
        xi_prefix = match.group(3)  # "XI"
        file_number = match.group(4)  # file number
        extension = match.group(5)  # ".htm"
        suffix = match.group(6)  # " or other attributes

        # Check if we have this file in our index
        if file_number in file_index:
            actual_path = file_index[file_number]

            # Check if the current reference is wrong
            current_ref = f"{xi_prefix}{file_number}{extension}"
            if actual_path.endswith(current_ref):
                # Reference is correct, no change needed
                return match.group(0)
            else:
                # Need to fix the reference
                # Extract the correct path
                if path_part.startswith('/auntruth/htm/'):
                    # Absolute path
                    new_ref = f"/auntruth/htm/{actual_path}"
                elif path_part.startswith('../'):
                    # Relative path going up
                    new_ref = f"../{actual_path}"
                elif path_part.startswith('./'):
                    # Current directory relative
                    # Need to figure out correct relative path
                    new_ref = f"./{actual_path}"
                else:
                    # Other relative path
                    new_ref = actual_path

                fixes_made += 1
                return f"{prefix}{new_ref}{suffix}"

        # If file not found in index, leave unchanged
        return match.group(0)

    # Apply the pattern replacement
    new_content = re.sub(xi_pattern, replace_xi_ref, new_content, flags=re.IGNORECASE)

    return new_content, fixes_made

def process_file(file_path, file_index, base_path, dry_run=False):
    """Process a single HTML file to fix XI lineage references."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content, fixes_made = fix_xi_lineage_refs(content, file_index, base_path)

        if content != new_content:
            if dry_run:
                print(f"WOULD MODIFY: {file_path} ({fixes_made} XI reference fixes)")
                return fixes_made
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"MODIFIED: {file_path} ({fixes_made} XI reference fixes)")
                return fixes_made

        return 0

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return 0

def process_directory(directory, dry_run=False):
    """Process all HTML files in a directory recursively."""
    directory = Path(directory)
    if not directory.exists():
        print(f"ERROR: Directory {directory} does not exist")
        return 0, 0

    print(f"Building file index for {directory}...")
    file_index = build_file_index(directory)
    print(f"Found {len(file_index)} XI/XF files in index")

    # Show some examples of what's in the index
    if len(file_index) > 0:
        print("Sample mappings:")
        for i, (num, path) in enumerate(list(file_index.items())[:5]):
            print(f"  {num} → {path}")
        if len(file_index) > 5:
            print(f"  ... and {len(file_index) - 5} more")

    print(f"\nProcessing HTML files in {directory}...")

    # Find all HTML files
    html_files = list(directory.glob('**/*.htm')) + list(directory.glob('**/*.html'))
    print(f"Found {len(html_files)} HTML files")

    total_changes = 0
    files_changed = 0

    for file_path in html_files:
        changes = process_file(file_path, file_index, directory, dry_run)
        if changes > 0:
            total_changes += changes
            files_changed += 1

    if dry_run:
        print(f"\nDRY RUN SUMMARY:")
        print(f"Would modify {files_changed} files")
        print(f"Would fix {total_changes} XI lineage references")
    else:
        print(f"\nCOMPLETE:")
        print(f"Modified {files_changed} files")
        print(f"Fixed {total_changes} XI lineage references")

    return files_changed, total_changes

def main():
    parser = argparse.ArgumentParser(description='Fix XI lineage references in HTML files')
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
        print(f"\nSUCCESS: Fixed {total_changes} XI lineage references in {files_changed} files")

if __name__ == '__main__':
    main()