#!/usr/bin/env python3
"""
Fix absolute paths for GitHub Pages deployment.
GitHub Pages URL structure: https://fil512.github.io/auntruth/

This means absolute paths should be:
- /htm/ → /auntruth/htm/
- /jpg/ → /auntruth/jpg/
- /css/ → /auntruth/css/
- /mpg/ → /auntruth/mpg/
- /au/ → /auntruth/au/
- / → /auntruth/
"""

import os
import re
from pathlib import Path

def fix_github_pages_paths_in_file(file_path):
    """Fix GitHub Pages absolute paths in a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Fix absolute paths for GitHub Pages deployment
        # GitHub Pages serves from /auntruth/ base path
        old_content = content

        # Fix various absolute path patterns - handle both with and without spaces around =
        content = re.sub(r'(href|src|value)\s*=\s*"(/htm/)', r'\1="/auntruth\2', content)
        content = re.sub(r'(href|src|value)\s*=\s*"(/jpg/)', r'\1="/auntruth\2', content)
        content = re.sub(r'(href|src|value)\s*=\s*"(/css/)', r'\1="/auntruth\2', content)
        content = re.sub(r'(href|src|value)\s*=\s*"(/mpg/)', r'\1="/auntruth\2', content)
        content = re.sub(r'(href|src|value)\s*=\s*"(/au/)', r'\1="/auntruth\2', content)

        # Fix single quotes too
        content = re.sub(r"(href|src|value)\s*=\s*'(/htm/)", r"\1='/auntruth\2", content)
        content = re.sub(r"(href|src|value)\s*=\s*'(/jpg/)", r"\1='/auntruth\2", content)
        content = re.sub(r"(href|src|value)\s*=\s*'(/css/)", r"\1='/auntruth\2", content)
        content = re.sub(r"(href|src|value)\s*=\s*'(/mpg/)", r"\1='/auntruth\2", content)
        content = re.sub(r"(href|src|value)\s*=\s*'(/au/)", r"\1='/auntruth\2", content)

        # Fix home links - be careful not to double-fix
        content = re.sub(r'href="/"(?!auntruth)', 'href="/auntruth/"', content)
        content = re.sub(r"href='/'(?!auntruth)", "href='/auntruth/'", content)

        if content != old_content:
            changes_made.append("Fixed absolute paths for GitHub Pages (/path/ → /auntruth/path/)")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        return []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def main():
    """Fix GitHub Pages paths in all HTML files."""
    target_dir = Path("/home/ken/wip/fam/auntruth/docs/htm")

    # Find all HTML files that need fixing
    affected_files = []

    # Walk through all subdirectories
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Check for absolute paths that need GitHub Pages prefix
                        if (re.search(r'(href|src|value)\s*=\s*"(/htm/|/jpg/|/css/|/mpg/|/au/)', content) or
                            re.search(r"(href|src|value)\s*=\s*'(/htm/|/jpg/|/css/|/mpg/|/au/)", content) or
                            re.search(r'href="/"(?!auntruth)', content) or
                            re.search(r"href='/'(?!auntruth)", content)):
                            affected_files.append(file_path)
                except:
                    pass

    print(f"Found {len(affected_files)} files needing GitHub Pages path fixes")

    if not affected_files:
        print("No files need fixing.")
        return

    # Process files
    files_fixed = 0
    total_changes = 0

    for file_path in affected_files:
        changes = fix_github_pages_paths_in_file(file_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            print(f"Fixed {file_path}: {', '.join(changes)}")

    print(f"\nSummary:")
    print(f"- Files processed: {len(affected_files)}")
    print(f"- Files fixed: {files_fixed}")
    print(f"- Total change types applied: {total_changes}")
    print("GitHub Pages path corrections complete.")

if __name__ == "__main__":
    main()