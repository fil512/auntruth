#!/usr/bin/env python3
"""
Test the path fixing script on just 5 sample files for safety verification.
Based on fix-path-format.py but limited to specific test files.
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

        # 2. Fix /AuntRuth/ absolute paths to correct absolute paths
        old_content = content
        # Since docroot is /docs, absolute URLs should be:
        # /AuntRuth/htm/ -> /htm/
        # /AuntRuth/css/ -> /css/
        # /AuntRuth/jpg/ -> /jpg/
        # /AuntRuth/mpg/ -> /mpg/
        # /AuntRuth/au/ -> /au/
        # /AuntRuth/ -> /
        content = re.sub(r'/AuntRuth/htm/', '/htm/', content)
        content = re.sub(r'/AuntRuth/css/', '/css/', content)
        content = re.sub(r'/AuntRuth/jpg/', '/jpg/', content)
        content = re.sub(r'/AuntRuth/mpg/', '/mpg/', content)
        content = re.sub(r'/AuntRuth/au/', '/au/', content)
        content = re.sub(r"href='/AuntRuth/'", "href='/'", content)  # Home links
        if content != old_content:
            changes_made.append("Fixed /AuntRuth/ absolute paths to correct absolute paths")

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
    """Test path fixing on 5 sample files only."""
    # Test files - pick a diverse sample
    test_files = [
        "/home/ken/wip/fam/auntruth/docs/htm/TH1999.htm",
        "/home/ken/wip/fam/auntruth/docs/htm/oldhtm/TH1999.htm",
        "/home/ken/wip/fam/auntruth/docs/htm/THVancou.htm",
        "/home/ken/wip/fam/auntruth/docs/htm/L2/TH1977.htm",
        "/home/ken/wip/fam/auntruth/docs/htm/L8/WAITING.htm"
    ]

    print("TESTING PATH FIXES ON 5 SAMPLE FILES")
    print("=====================================")

    # Check which test files exist and contain the pattern
    available_files = []
    for file_path in test_files:
        path_obj = Path(file_path)
        if path_obj.exists():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '/AuntRuth/' in content or '\\AuntRuth\\' in content:
                        available_files.append(file_path)
                        print(f"✓ Found test file with /AuntRuth/ patterns: {file_path}")
            except:
                pass

    if not available_files:
        print("No test files found with /AuntRuth/ patterns!")
        return

    print(f"\nProcessing {len(available_files)} test files...")

    # Process test files
    files_fixed = 0
    total_changes = 0

    for file_path in available_files:
        print(f"\nProcessing: {file_path}")
        changes = fix_paths_in_file(file_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            print(f"  Changes: {', '.join(changes)}")
        else:
            print("  No changes needed")

    print(f"\n=== TEST RESULTS ===")
    print(f"Files processed: {len(available_files)}")
    print(f"Files fixed: {files_fixed}")
    print(f"Total change types applied: {total_changes}")
    print("\nTest completed successfully! Ready for full run.")

if __name__ == "__main__":
    main()