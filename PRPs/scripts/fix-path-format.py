#!/usr/bin/env python3
"""
Comprehensive path format fixes for genealogy HTML files.
This is task 001: fix-absolute-paths with additional path format improvements.

Fixes applied:
1. Primary task: Replace \auntruth\htm\ with relative paths
2. Convert /AuntRuth/ absolute paths to relative paths
3. Convert Windows backslashes (\) to Unix forward slashes (/)
4. Fix case sensitivity: lowercase l0-l9 to uppercase L0-L9
5. Fix other Windows-style absolute paths
"""

import os
import re
from pathlib import Path

def fix_paths_in_file(file_path):
    """Fix path format issues in a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # 1. PRIMARY TASK: Fix \auntruth\htm\ (already done by agent, but included for completeness)
        old_content = content
        # Convert to relative paths based on file location
        if '/oldhtm/' in str(file_path):
            content = content.replace('\\auntruth\\htm\\', '../')
        else:
            content = content.replace('\\auntruth\\htm\\', './')
        if content != old_content:
            changes_made.append("Fixed primary pattern: \\auntruth\\htm\\")

        # 2. Fix /AuntRuth/ absolute paths to relative paths
        old_content = content
        # These need to be converted based on GitHub Pages structure
        # /AuntRuth/htm/ -> ./  (from docs/htm/)
        # /AuntRuth/css/ -> ../css/  (from docs/htm/ to docs/css/)
        # /AuntRuth/jpg/ -> ../jpg/  (from docs/htm/ to docs/jpg/)
        # /AuntRuth/mpg/ -> ../mpg/  (from docs/htm/ to docs/mpg/)
        # /AuntRuth/au/ -> ../au/   (from docs/htm/ to docs/au/)
        content = re.sub(r'/AuntRuth/htm/', './', content)
        content = re.sub(r'/AuntRuth/css/', '../css/', content)
        content = re.sub(r'/AuntRuth/jpg/', '../jpg/', content)
        content = re.sub(r'/AuntRuth/mpg/', '../mpg/', content)
        content = re.sub(r'/AuntRuth/au/', '../au/', content)
        content = re.sub(r"href='/AuntRuth/'", "href='../'", content)  # Home links
        if content != old_content:
            changes_made.append("Fixed /AuntRuth/ absolute paths to relative paths")

        # 3. Fix Windows backslashes to Unix forward slashes in all attributes
        old_content = content
        def replace_backslashes(match):
            full_attr = match.group(0)
            # Replace all backslashes with forward slashes within the attribute
            fixed_attr = full_attr.replace('\\', '/')
            return fixed_attr

        # Fix in href, src, and other attributes
        content = re.sub(r'(href|src|value)="[^"]*\\[^"]*"', replace_backslashes, content)
        content = re.sub(r"(href|src|value)='[^']*\\[^']*'", replace_backslashes, content)
        if content != old_content:
            changes_made.append("Converted Windows backslashes to Unix forward slashes")

        # 4. Fix case sensitivity: lowercase l0-l9 to uppercase L0-L9
        old_content = content
        content = re.sub(r'(href|src)="(\./|\.\./)l([0-9])([/\\])', r'\1="\2L\3\4', content)
        content = re.sub(r"(href|src)='(\./|\.\./)l([0-9])([/\\])", r"\1='\2L\3\4", content)
        if content != old_content:
            changes_made.append("Fixed case sensitivity: l0-l9 -> L0-L9")

        # 5. Fix other absolute Windows-style paths like \AuntRuth\htm\
        old_content = content
        content = re.sub(r'\\AuntRuth\\htm\\', './', content)
        content = re.sub(r'\\AuntRuth\\jpg\\', '../jpg/', content)
        content = re.sub(r'\\AuntRuth\\css\\', '../css/', content)
        if content != old_content:
            changes_made.append("Fixed \\AuntRuth\\ absolute paths")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        return []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def main():
    """Fix path formats in affected HTML files."""
    target_dir = Path("/home/ken/wip/fam/auntruth/docs/htm")

    # Find all HTML files with path format issues
    affected_files = []

    # Walk through all subdirectories
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Check for various problematic path patterns
                        if (re.search(r'\\auntruth\\htm\\', content) or
                            re.search(r'/AuntRuth/', content) or
                            re.search(r'\\AuntRuth\\', content) or
                            re.search(r'(href|src|value)="[^"]*\\[^"]*"', content) or
                            re.search(r'(href|src)="(\./|\.\./)l[0-9]([/\\])', content)):
                            affected_files.append(file_path)
                except:
                    pass

    print(f"Found {len(affected_files)} files needing path format fixes")

    if not affected_files:
        print("No files need fixing.")
        return

    # Process files
    files_fixed = 0
    total_changes = 0

    for file_path in affected_files:
        changes = fix_paths_in_file(file_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            print(f"Fixed {file_path}: {', '.join(changes)}")

    print(f"\nSummary:")
    print(f"- Files processed: {len(affected_files)}")
    print(f"- Files fixed: {files_fixed}")
    print(f"- Total change types applied: {total_changes}")
    print("Path format corrections complete.")

if __name__ == "__main__":
    main()