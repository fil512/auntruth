#!/usr/bin/env python3
"""
Fix onclick syntax error in carousel files
"""

import os
import re
from pathlib import Path

def fix_onclick_syntax(file_path):
    """Fix onclick syntax in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Fix the onclick syntax error: extra ')' and quotes
        pattern = r"onclick=\"openFullImage\('([^']+)', 0, 'carousel_id'\)'\)\""
        replacement = r'onclick="openFullImage(\'\1\', 0, \'carousel_id\')"'

        new_content = re.sub(pattern, replacement, content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "Fixed onclick syntax"

        return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function"""
    current_path = Path(".")
    htm_path = current_path / "htm"

    if not htm_path.exists():
        docs_new_path = Path("docs/new")
        htm_path = docs_new_path / "htm"

    print("Fixing onclick syntax in carousel files...")

    fixed_files = 0
    for html_file in htm_path.rglob("XF*.htm"):
        success, message = fix_onclick_syntax(html_file)
        if success:
            fixed_files += 1

    print(f"Fixed onclick syntax in {fixed_files} files")

if __name__ == "__main__":
    main()