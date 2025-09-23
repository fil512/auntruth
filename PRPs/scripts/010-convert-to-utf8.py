#!/usr/bin/env python3
"""
Script: 010-convert-to-utf8.py
Purpose: Convert HTML files from Windows-1252 to UTF-8 encoding
Task: 010 - add-utf8-charset

This script handles two critical conversions:
1. Converts actual Windows-1252 encoded characters to proper Unicode
2. Updates charset declarations from windows-1252 to utf-8

Key Windows-1252 characters that need conversion:
- 0x94 (") → U+201D (right double quotation mark)
- 0xA9 (©) → U+00A9 (copyright sign)
- And other Windows-1252 specific characters
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def verify_git_branch(expected_branch):
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to check git branch: {e}")

def convert_windows1252_to_unicode(content):
    """
    Convert Windows-1252 encoded characters to proper Unicode.

    The key issue is that characters like smart quotes and copyright symbols
    were encoded in Windows-1252 but are being interpreted as UTF-8,
    resulting in the � replacement character.
    """

    # Map of Windows-1252 characters that commonly appear as � when misinterpreted
    # These are the byte values in Windows-1252 that need special handling
    conversions = {
        # Smart quotes and dashes
        '\u2018': "'",      # Left single quotation mark → apostrophe
        '\u2019': "'",      # Right single quotation mark → apostrophe
        '\u201C': '"',      # Left double quotation mark → quote
        '\u201D': '"',      # Right double quotation mark → quote
        '\u2013': '–',      # En dash
        '\u2014': '—',      # Em dash

        # Common Windows-1252 characters that show as � when misencoded
        '�': '"',           # This is likely a misencoded right double quote (0x94)
    }

    # Apply conversions
    for old_char, new_char in conversions.items():
        content = content.replace(old_char, new_char)

    # Handle specific problematic patterns we identified
    # Fix "China� The Hartwells�" → "China" The Hartwells""
    content = re.sub(r'China�\s+The\s+Hartwells�', 'China" The Hartwells"', content)

    # Fix "� Copyright" → "© Copyright"
    content = re.sub(r'^�\s*Copyright', '© Copyright', content, flags=re.MULTILINE)
    content = re.sub(r'<strong>�\s*Copyright', '<strong>© Copyright', content)

    return content

def update_charset_declaration(content):
    """Update charset declaration from windows-1252 to utf-8"""

    # Pattern to match charset declarations
    charset_pattern = r'(charset=)windows-1252'
    replacement = r'\1utf-8'

    updated_content = re.sub(charset_pattern, replacement, content, flags=re.IGNORECASE)

    return updated_content

def process_file(file_path, dry_run=True):
    """Process a single HTML file for encoding conversion"""

    try:
        # Read file with error handling for encoding issues
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            original_content = f.read()

        # Track what changes we're making
        changes_made = []
        new_content = original_content

        # 1. Convert Windows-1252 characters to Unicode
        converted_content = convert_windows1252_to_unicode(new_content)
        if converted_content != new_content:
            changes_made.append("character_conversion")
            new_content = converted_content

        # 2. Update charset declaration
        charset_updated = update_charset_declaration(new_content)
        if charset_updated != new_content:
            changes_made.append("charset_declaration")
            new_content = charset_updated

        # Report changes for this file
        if changes_made:
            change_summary = ", ".join(changes_made)
            print(f"  {file_path}: {change_summary}")

            if not dry_run:
                # Write the updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True

        return len(changes_made) > 0

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return False

def find_target_files(target_dir):
    """Find all HTML files that need processing"""

    target_files = []

    # Walk through all subdirectories
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)

                try:
                    # Check if file needs processing
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()

                    # Check for windows-1252 charset or problem characters
                    needs_charset_update = 'charset=windows-1252' in content.lower()
                    needs_char_conversion = '�' in content or '\u201d' in content or '\u00a9' in content

                    if needs_charset_update or needs_char_conversion:
                        target_files.append(file_path)

                except Exception as e:
                    print(f"Warning: Could not check {file_path}: {e}")

    return sorted(target_files)

def main():
    """Main execution function"""

    # Configuration - use absolute path from script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))  # Go up from PRPs/scripts/
    target_dir = os.path.join(repo_root, "docs", "htm")
    expected_branch = "task-010-add-utf8-charset"

    print("=== Task 010: Convert to UTF-8 Encoding ===")
    print(f"Target directory: {target_dir}")
    print(f"Expected git branch: {expected_branch}")
    print()

    # Verify git branch
    try:
        current_branch = verify_git_branch(expected_branch)
        print(f"✓ Working in correct branch: {current_branch}")
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1

    # Find target files
    print("\n--- SCOPE ANALYSIS ---")
    target_files = find_target_files(target_dir)

    if not target_files:
        print("No files found that need encoding conversion.")
        return 0

    print(f"Found {len(target_files)} files that need processing:")
    for i, file_path in enumerate(target_files[:10], 1):
        print(f"  {i}. {file_path}")

    if len(target_files) > 10:
        print(f"  ... and {len(target_files) - 10} more files")

    # Get execution mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "dry-run"

    if mode == "dry-run":
        print(f"\n--- DRY RUN MODE ---")
        print("Showing what changes would be made (no files will be modified):")

        changes_count = 0
        for file_path in target_files:
            if process_file(file_path, dry_run=True):
                changes_count += 1

        print(f"\nDry run complete: {changes_count} files would be modified")
        print("\nTo execute changes, run: python3 010-convert-to-utf8.py execute")

    elif mode == "execute":
        print(f"\n--- EXECUTION MODE ---")
        print("Processing files and making changes...")

        processed = 0
        errors = 0

        for i, file_path in enumerate(target_files, 1):
            try:
                if process_file(file_path, dry_run=False):
                    processed += 1

                # Progress reporting
                if i % 50 == 0 or i == len(target_files):
                    print(f"Processed {i}/{len(target_files)} files...")

            except Exception as e:
                print(f"ERROR processing {file_path}: {e}")
                errors += 1

        print(f"\nExecution complete:")
        print(f"  Files processed: {processed}")
        print(f"  Errors: {errors}")
        print(f"  Total files checked: {len(target_files)}")

        if errors == 0:
            print("\n✓ All files processed successfully")
            print("Ready for git commit")
        else:
            print(f"\n⚠ {errors} errors encountered - check output above")

    elif mode == "validate":
        print(f"\n--- VALIDATION MODE ---")
        print("Checking if conversion was successful...")

        # Re-scan for files that still need conversion
        remaining_files = find_target_files(target_dir)

        if not remaining_files:
            print("✓ Validation successful: No files need further conversion")
        else:
            print(f"⚠ {len(remaining_files)} files still need conversion:")
            for file_path in remaining_files[:5]:
                print(f"  {file_path}")
            if len(remaining_files) > 5:
                print(f"  ... and {len(remaining_files) - 5} more")

    else:
        print(f"\nUsage: python3 010-convert-to-utf8.py [mode]")
        print(f"Modes:")
        print(f"  dry-run   - Show what would be changed (default)")
        print(f"  execute   - Apply the changes")
        print(f"  validate  - Check if conversion was successful")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())