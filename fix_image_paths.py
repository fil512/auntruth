#!/usr/bin/env python3
"""
Fix broken image paths in genealogy HTML files.
Converts absolute paths to relative paths for proper local serving.
"""

import os
import re
import glob
from pathlib import Path

def fix_old_site_images(file_path):
    """Fix image paths for files in docs/htm/"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Replace /auntruth/jpg/ with relative path from htm subdirectories
    # For files in docs/htm/L1/ -> ../../jpg/
    # For files in docs/htm/L2/ -> ../../jpg/
    # etc.

    # First check what level we're at
    relative_path = file_path.replace('\\', '/')

    if '/htm/L' in relative_path:
        # Files in subdirectories like L0, L1, L2, etc.
        replacement = '../../jpg/'
    else:
        # Files directly in htm directory
        replacement = '../jpg/'

    # Replace absolute image paths
    content = re.sub(r'/auntruth/jpg/', replacement, content)

    return content

def fix_new_site_images(file_path):
    """Fix image paths for files in docs/new/htm/"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # For files in docs/new/htm/L1/ -> ../../../jpg/
    relative_path = file_path.replace('\\', '/')

    if '/new/htm/L' in relative_path:
        # Files in subdirectories like L0, L1, L2, etc.
        replacement = '../../../jpg/'
    else:
        # Files directly in new/htm directory
        replacement = '../../jpg/'

    # Replace absolute image paths
    content = re.sub(r'/auntruth/jpg/', replacement, content)

    return content

def process_files(directory, fix_function, dry_run=True):
    """Process all HTML files in a directory"""
    html_files = glob.glob(os.path.join(directory, '**/*.htm'), recursive=True)

    print(f"Found {len(html_files)} HTML files in {directory}")

    for file_path in html_files:
        try:
            original_content = open(file_path, 'r', encoding='utf-8', errors='ignore').read()
            fixed_content = fix_function(file_path)

            if original_content != fixed_content:
                print(f"Fixing: {file_path}")
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

def main():
    import sys
    base_dir = "/home/ken/wip/fam/auntruth/docs"

    print("=== Fixing Image Paths ===")
    print("This script will update absolute image paths to relative paths")
    print()

    # Check for command line argument
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        dry_run = False

    if dry_run:
        print("DRY RUN MODE - No files will be modified")
        print("Use --live to actually modify files")
    else:
        print("LIVE MODE - Files will be modified")

    print()

    # Process old site
    old_site_dir = os.path.join(base_dir, "htm")
    if os.path.exists(old_site_dir):
        print("Processing old site (docs/htm/)...")
        process_files(old_site_dir, fix_old_site_images, dry_run)
        print()

    # Process new site
    new_site_dir = os.path.join(base_dir, "new/htm")
    if os.path.exists(new_site_dir):
        print("Processing new site (docs/new/htm/)...")
        process_files(new_site_dir, fix_new_site_images, dry_run)
        print()

    if dry_run:
        print("Dry run complete. Run with 'n' to actually modify files.")
    else:
        print("Files updated successfully!")

if __name__ == "__main__":
    main()