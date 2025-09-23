#!/usr/bin/env python3
"""
Update Carousel CSS Script

This script updates existing image carousels to ensure proper thumbnail display
by updating the CSS and adding the thumbnail-image class.
"""

import os
import re
from pathlib import Path

def update_carousel_css_in_file(file_path):
    """Update carousel CSS and image classes in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if file has a carousel
        if 'image-carousel' not in content:
            return False, "No carousel found"

        modified = False

        # Update image tags to include thumbnail-image class
        old_img_pattern = r'<img src="([^"]*)"(\s+alt="[^"]*")?(\s+onclick="[^"]*")?(\s+title="[^"]*")?(\s+loading="[^"]*")?>'
        new_img_replacement = r'<img src="\1"\2\3\4\5 class="thumbnail-image">'

        if re.search(old_img_pattern, content):
            content = re.sub(old_img_pattern, new_img_replacement, content)
            modified = True

        # Update CSS if it exists
        old_css_pattern = r'\.thumbnail-item img \{'
        new_css_replacement = '.thumbnail-item .thumbnail-image {'

        if re.search(old_css_pattern, content):
            content = re.sub(old_css_pattern, new_css_replacement, content)
            modified = True

        # Update the specific CSS properties for better thumbnail display
        css_updates = [
            (r'width: 60px;', 'width: 50px;'),
            (r'height: 60px;', 'height: 50px;'),
            (r'transform: scale\(1\.1\);', 'transform: scale(1.2);'),
            (r'grid-template-columns: repeat\(auto-fit, minmax\(80px, 1fr\)\);', 'grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));'),
            (r'width: 50px;\s*height: 50px;', 'width: 45px;\n    height: 45px;')
        ]

        for old_pattern, new_replacement in css_updates:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_replacement, content)
                modified = True

        # Add justify-items: center to carousel-page if not present
        carousel_page_pattern = r'(\.carousel-page \{[^}]+)(gap: 10px;\s*padding: 15px;)([^}]*\})'
        if re.search(carousel_page_pattern, content):
            def add_justify_items(match):
                prefix = match.group(1)
                gap_padding = match.group(2)
                suffix = match.group(3)
                if 'justify-items' not in prefix + gap_padding + suffix:
                    return prefix + gap_padding + '\n    justify-items: center;' + suffix
                return match.group(0)

            new_content = re.sub(carousel_page_pattern, add_justify_items, content)
            if new_content != content:
                content = new_content
                modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Updated successfully"

        return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function to update all HTML files with carousels"""
    current_path = Path(".")
    htm_path = current_path / "htm"

    if not htm_path.exists():
        docs_new_path = Path("docs/new")
        htm_path = docs_new_path / "htm"
        if not htm_path.exists():
            print(f"Error: Neither ./htm nor docs/new/htm exists")
            return

    print("Updating carousel CSS in HTML files...")

    total_files = 0
    modified_files = 0
    errors = 0

    # Process all HTML files in htm directory
    for html_file in htm_path.rglob("*.htm"):
        # Skip THF files themselves
        if html_file.name.startswith("THF"):
            continue

        total_files += 1
        success, message = update_carousel_css_in_file(html_file)

        if success:
            modified_files += 1
            print(f"Updated carousel CSS in {html_file.name}")
        elif "Error:" in message:
            errors += 1
            print(f"Error processing {html_file.name}: {message}")

        # Progress indicator
        if total_files % 500 == 0:
            print(f"Processed {total_files} files...")

    print(f"\nCSS update complete:")
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {modified_files}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()