#!/usr/bin/env python3
"""
Remove Duplicate Elements from HTML Files

This script removes duplicate skip links, noscript sections, and main tags
that may have been created during the cleanup process.
"""

import os
import re

def clean_duplicates(file_path):
    """Remove duplicate elements from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Remove duplicate skip links
        content = re.sub(
            r'(<!-- Skip link for accessibility -->\s*<a href="#main-content" class="skip-link">Skip to main content</a>\s*){2,}',
            r'\1',
            content,
            flags=re.DOTALL
        )

        # Remove duplicate noscript sections
        content = re.sub(
            r'(<!-- Fallback navigation for no-JS users -->\s*<noscript>.*?</noscript>\s*){2,}',
            r'\1',
            content,
            flags=re.DOTALL
        )

        # Remove duplicate main tags
        content = re.sub(
            r'(<!-- Main content will be wrapped by JavaScript -->\s*<main id="main-content">\s*){2,}',
            r'\1',
            content,
            flags=re.DOTALL
        )

        # Remove extra closing main tags
        content = re.sub(r'</main>\s*</main>', '</main>', content)

        # Remove duplicate script tags
        content = re.sub(
            r'(<script src="/auntruth/new/js/search\.js" defer></script>\s*){2,}',
            r'\1',
            content
        )

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Duplicates removed"
        else:
            return False, "No duplicates found"

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("Removing Duplicate Elements")
    print("=" * 30)

    base_dir = "htm"
    if not os.path.exists(base_dir):
        print(f"❌ Directory {base_dir} not found!")
        return

    files_processed = 0
    files_fixed = 0
    errors = 0

    # Process all HTML files with MODERNIZED comment
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.htm') and not file.endswith('.backup'):
                file_path = os.path.join(root, file)

                # Only process files that have been modernized
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if '<!-- MODERNIZED -->' in f.read():
                            files_processed += 1
                            success, message = clean_duplicates(file_path)

                            if success:
                                files_fixed += 1
                                if files_fixed % 100 == 0:
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
        print(f"✅ Successfully removed duplicates from {files_fixed} files!")

if __name__ == "__main__":
    main()