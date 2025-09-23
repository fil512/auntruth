#!/usr/bin/env python3
"""
Fix Nested Main Tags Issue

The comprehensive cleanup created nested <main> tags in some files,
causing massive vertical spacing. This script removes the inner main tags.
"""

import os
import re

def fix_nested_main_tags(file_path):
    """Remove nested main tags and excessive spacing that is causing layout issues"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        changes_made = False

        # Pattern 1: Find nested main pattern
        nested_pattern = r'(<main[^>]*class="page-content"[^>]*>)(.*?)(<main[^>]*>)(.*?)(</main>\s*</main>)'
        if re.search(nested_pattern, content, re.DOTALL):
            content = re.sub(
                nested_pattern,
                r'\1\2\4</main>',
                content,
                flags=re.DOTALL
            )
            changes_made = True

        # Pattern 2: Remove excessive <br> tags at start of main content
        br_pattern = r'(<main[^>]*class="page-content"[^>]*>\s*)(<br>\s*){2,}'
        if re.search(br_pattern, content):
            content = re.sub(br_pattern, r'\1', content)
            changes_made = True

        # Pattern 3: Remove <center> tags that create spacing at start
        center_pattern = r'(<main[^>]*class="page-content"[^>]*>\s*)(<center>\s*</center>)'
        if re.search(center_pattern, content):
            content = re.sub(center_pattern, r'\1', content)
            changes_made = True

        if changes_made:
            print(f"Fixed spacing issues in: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed spacing issues"
        else:
            return False, "No spacing issues found"

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("Fixing Nested Main Tags")
    print("=" * 25)

    base_dir = "htm"
    if not os.path.exists(base_dir):
        print(f"❌ Directory {base_dir} not found!")
        return

    files_processed = 0
    files_fixed = 0
    errors = 0

    # Test on the specific problematic file first
    test_file = "htm/L1/XF182.htm"
    if os.path.exists(test_file):
        print(f"Testing fix on: {test_file}")
        success, message = fix_nested_main_tags(test_file)
        print(f"Result: {message}")

    # Process all HTML files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.htm') and not file.endswith('.backup'):
                file_path = os.path.join(root, file)

                # Only process modernized files
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if '<!-- MODERNIZED -->' in f.read():
                            files_processed += 1
                            success, message = fix_nested_main_tags(file_path)

                            if success:
                                files_fixed += 1
                                if files_fixed % 10 == 0:
                                    print(f"Fixed {files_fixed} files...")
                            elif "Error:" in message:
                                errors += 1
                except:
                    pass

    print(f"\nResults:")
    print(f"Files processed: {files_processed}")
    print(f"Files fixed: {files_fixed}")
    print(f"Errors: {errors}")

    if files_fixed > 0:
        print(f"✅ Successfully fixed nested main tags in {files_fixed} files!")
        print("🔄 Refresh your browser to see the fix!")

if __name__ == "__main__":
    main()