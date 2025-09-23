#!/usr/bin/env python3
"""
Fix Duplicate Script Tags Issue

Remove duplicate script tags that are causing JavaScript errors.
"""

import os
import re

def fix_duplicate_scripts(file_path):
    """Remove duplicate script tags"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        changes_made = False

        # Pattern to find duplicate search.js scripts in the middle of content
        duplicate_search_pattern = r'<script src="/auntruth/new/js/search\.js" defer></script>\s*</main>\s*\n\s*<!-- Navigation and search scripts -->\s*\n\s*<script src="/auntruth/new/js/navigation\.js" defer></script>\s*\n<script src="/auntruth/new/js/search\.js" defer></script>'

        if re.search(duplicate_search_pattern, content):
            content = re.sub(
                duplicate_search_pattern,
                '</main>\n\n    <!-- Navigation and search scripts -->\n    <script src="/auntruth/new/js/navigation.js" defer></script>\n    <script src="/auntruth/new/js/search.js" defer></script>',
                content
            )
            changes_made = True

        # Also check for any other duplicate patterns
        # Remove any search.js that appears in the middle of content
        middle_script_pattern = r'<script src="/auntruth/new/js/search\.js" defer></script>\s*</main>'
        if re.search(middle_script_pattern, content):
            content = re.sub(middle_script_pattern, '</main>', content)
            changes_made = True

        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed duplicate scripts"
        else:
            return False, "No duplicate scripts found"

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("Fixing Duplicate Script Tags")
    print("=" * 28)

    base_dir = "htm"
    if not os.path.exists(base_dir):
        print(f"❌ Directory {base_dir} not found!")
        return

    files_processed = 0
    files_fixed = 0
    errors = 0

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
                            success, message = fix_duplicate_scripts(file_path)

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
        print(f"✅ Successfully fixed duplicate scripts in {files_fixed} files!")

if __name__ == "__main__":
    main()