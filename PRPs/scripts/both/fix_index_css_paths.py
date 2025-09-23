#!/usr/bin/env python3
"""
Fix CSS paths in index.htm files to use correct /auntruth/new/css/ paths
and add missing navigation.css link
"""

import os
import re
from pathlib import Path

def fix_css_paths_in_file(file_path):
    """Fix CSS paths in a single HTML file"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix the main.css path: /auntruth/css/main.css -> /auntruth/new/css/main.css
        content = content.replace(
            'href="/auntruth/css/main.css"',
            'href="/auntruth/new/css/main.css"'
        )

        # Add navigation.css if it's missing
        if 'navigation.css' not in content:
            # Insert navigation.css after main.css
            content = content.replace(
                '<link href="/auntruth/new/css/main.css" rel="stylesheet" type="text/css">',
                '<link href="/auntruth/new/css/main.css" rel="stylesheet" type="text/css"><link href="/auntruth/new/css/navigation.css" rel="stylesheet">'
            )

        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed CSS paths in {file_path}")
            return True
        else:
            print(f"- No changes needed in {file_path}")
            return False

    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Fix CSS paths in all index.htm files"""
    base_dir = Path('/home/ken/wip/fam/auntruth/docs/new/htm')

    # Find all index.htm files
    index_files = list(base_dir.glob('**/index.htm'))

    print(f"Found {len(index_files)} index.htm files to check:")

    fixed_count = 0
    for file_path in sorted(index_files):
        if fix_css_paths_in_file(file_path):
            fixed_count += 1

    print(f"\nSummary: Fixed CSS paths in {fixed_count} out of {len(index_files)} files")

if __name__ == '__main__':
    main()