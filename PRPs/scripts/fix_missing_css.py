#!/usr/bin/env python3
"""
Fix Missing CSS Links Script

This script fixes HTML files that are missing CSS links after the navigation update.
It specifically targets files that have the navigation JS but are missing the CSS files.
"""

import os
import re
from pathlib import Path

def fix_css_links(file_path):
    """Fix missing CSS links in a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if file already has main.css
        if 'main.css' in content:
            return False, "Already has CSS"

        # Check if file has the basic HTML structure we expect
        if not ('<html lang="en">' in content and 'navigation.js' in content):
            return False, "Not a modernized file"

        # Find the position to insert CSS links - after viewport meta tag
        viewport_pattern = r'(<meta name="viewport"[^>]*>)'
        match = re.search(viewport_pattern, content)

        if not match:
            return False, "No viewport meta found"

        # CSS links to insert
        css_links = '''<link href="/auntruth/new/css/main.css" rel="stylesheet" type="text/css"><link href="/auntruth/new/css/navigation.css" rel="stylesheet">'''

        # Insert CSS links after viewport meta
        insert_pos = match.end()
        new_content = content[:insert_pos] + css_links + content[insert_pos:]

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, "CSS links added"

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("Fixing Missing CSS Links")
    print("=" * 30)

    base_dir = "htm"
    if not os.path.exists(base_dir):
        print(f"❌ Directory {base_dir} not found!")
        return

    files_processed = 0
    files_fixed = 0
    files_skipped = 0
    errors = 0

    # Find all HTML files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.htm') and not file.endswith('.backup'):
                file_path = os.path.join(root, file)
                files_processed += 1

                success, message = fix_css_links(file_path)

                if success:
                    files_fixed += 1
                    if files_fixed % 100 == 0:
                        print(f"Fixed {files_fixed} files...")
                elif "Already has CSS" in message:
                    files_skipped += 1
                else:
                    errors += 1
                    if errors <= 5:  # Show first few errors
                        relative_path = os.path.relpath(file_path, '.')
                        print(f"❌ {relative_path}: {message}")

    print(f"\nResults:")
    print(f"Files processed: {files_processed}")
    print(f"Files fixed: {files_fixed}")
    print(f"Files skipped (already have CSS): {files_skipped}")
    print(f"Errors: {errors}")

    if files_fixed > 0:
        print(f"✅ Successfully added CSS links to {files_fixed} files")
    else:
        print("ℹ️  No files needed CSS fixes")

if __name__ == "__main__":
    main()