#!/usr/bin/env python3
"""
Complete the /AuntRuth/ path fixing task by handling remaining patterns.
This script handles the patterns missed by fix-path-format.py:
- /AuntRuth/index.htm -> /index.htm
- /AuntRuth/ -> / (when not already handled)
"""

import os
import re
from pathlib import Path

def complete_auntruuth_fixes(file_path):
    """Complete /AuntRuth/ path fixes in a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Fix /AuntRuth/index.htm references
        old_content = content
        content = re.sub(r'/AuntRuth/index\.htm', '/index.htm', content)
        if content != old_content:
            changes_made.append("Fixed /AuntRuth/index.htm -> /index.htm")

        # Fix standalone /AuntRuth/ references that aren't already handled
        old_content = content
        # This regex avoids matching patterns that should have already been fixed
        # Handle various spacing patterns around equals sign
        content = re.sub(r'href\s*=\s*"/AuntRuth/"', 'href="/"', content)
        content = re.sub(r"href\s*=\s*'/AuntRuth/'", "href='/'", content)
        if content != old_content:
            changes_made.append("Fixed remaining /AuntRuth/ home links")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        return []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def main():
    """Complete /AuntRuth/ path fixes in all remaining affected HTML files."""
    target_dir = Path("/home/ken/wip/fam/auntruth/docs/htm")

    # Find all HTML files that still contain /AuntRuth/ patterns
    affected_files = []

    # Walk through all subdirectories
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Check for remaining /AuntRuth/ patterns
                        if '/AuntRuth/' in content:
                            affected_files.append(file_path)
                except:
                    pass

    print(f"Found {len(affected_files)} files still containing /AuntRuth/ patterns")

    if not affected_files:
        print("No files need additional fixing.")
        return

    # Process files
    files_fixed = 0
    total_changes = 0

    for file_path in affected_files:
        changes = complete_auntruuth_fixes(file_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            print(f"Fixed {file_path}: {', '.join(changes)}")

    print(f"\nSummary:")
    print(f"- Files processed: {len(affected_files)}")
    print(f"- Files fixed: {files_fixed}")
    print(f"- Total change types applied: {total_changes}")
    print("Completion of /AuntRuth/ path corrections finished.")

if __name__ == "__main__":
    main()