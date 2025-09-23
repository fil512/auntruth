#!/usr/bin/env python3
"""
Fix Gallery JSON Syntax Error

This script fixes the JavaScript syntax error in the gallery data by
properly formatting the JSON array instead of using Python's string representation.
"""

import os
import re
import json
from pathlib import Path

def fix_gallery_json_in_file(file_path):
    """Fix gallery JSON syntax in a carousel file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if 'gallery_carousel_' not in content:
            return False, "No gallery data found"

        # Find and fix the gallery data
        pattern = r'const gallery_([^=]+) = (\[.*?\]);'

        def fix_gallery_data(match):
            var_name = match.group(1)
            python_array = match.group(2)

            try:
                # Convert Python string representation to proper data structure
                # Replace single quotes with double quotes and handle Python syntax
                json_str = python_array.replace("'", '"').replace('False', 'false').replace('True', 'true').replace('None', 'null')

                # Parse as JSON to validate
                gallery_data = json.loads(json_str)

                # Convert back to proper JSON
                proper_json = json.dumps(gallery_data, separators=(',', ':'))

                return f'const gallery_{var_name} = {proper_json};'
            except Exception as e:
                print(f"Error fixing gallery data: {e}")
                return match.group(0)  # Return original if we can't fix it

        new_content = re.sub(pattern, fix_gallery_data, content, flags=re.DOTALL)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "Fixed gallery JSON syntax"

        return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function to fix gallery JSON syntax"""
    current_path = Path(".")
    htm_path = current_path / "htm"

    if not htm_path.exists():
        docs_new_path = Path("docs/new")
        htm_path = docs_new_path / "htm"
        if not htm_path.exists():
            print(f"Error: Neither ./htm nor docs/new/htm exists")
            return

    print("Fixing gallery JSON syntax errors...")

    total_files = 0
    fixed_files = 0
    errors = 0

    # Process files that have gallery data
    for html_file in htm_path.rglob("XF*.htm"):
        total_files += 1
        success, message = fix_gallery_json_in_file(html_file)

        if success:
            fixed_files += 1
            if fixed_files <= 10:  # Show first few fixes
                print(f"Fixed {html_file.name}")
        elif "Error:" in message:
            errors += 1

        # Progress indicator
        if total_files % 500 == 0:
            print(f"Processed {total_files} files...")

    print(f"\nGallery JSON fix complete:")
    print(f"Total files processed: {total_files}")
    print(f"Files fixed: {fixed_files}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()