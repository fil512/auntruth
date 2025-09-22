#!/usr/bin/env python3
"""
Final cleanup script for remaining /AuntRuth/ references
Handles .HTM files (uppercase) and CSS references that were missed in previous runs
"""

import os
import re
import sys
from pathlib import Path

def process_file(filepath):
    """Process a single file to fix /AuntRuth/ references"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        original_content = content

        # Apply all /AuntRuth/ path fixes
        content = re.sub(r'/AuntRuth/htm/', '/htm/', content)
        content = re.sub(r'/AuntRuth/css/', '/css/', content)
        content = re.sub(r'/AuntRuth/jpg/', '/jpg/', content)
        content = re.sub(r'/AuntRuth/mpg/', '/mpg/', content)
        content = re.sub(r'/AuntRuth/au/', '/au/', content)

        # Fix home page references with various spacing patterns
        content = re.sub(r'href\s*=\s*"/AuntRuth/"', 'href="/"', content)
        content = re.sub(r"href\s*=\s*'/AuntRuth/'", "href='/'", content)

        # Fix /AuntRuth/index.htm references
        content = re.sub(r'/AuntRuth/index\.htm', '/index.htm', content)

        # Write back if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main processing function"""
    base_dir = Path('docs/htm')

    if not base_dir.exists():
        print(f"Directory {base_dir} does not exist")
        sys.exit(1)

    # Find all files with remaining /AuntRuth/ references
    print("Finding files with remaining /AuntRuth/ references...")

    files_to_process = []

    # Get all .HTM and .htm files that contain /AuntRuth/
    for filepath in base_dir.rglob('*'):
        if filepath.is_file() and filepath.suffix.lower() in ['.htm', '.css']:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    if '/AuntRuth/' in content:
                        files_to_process.append(filepath)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    print(f"Found {len(files_to_process)} files to process")

    if not files_to_process:
        print("No files found with /AuntRuth/ references")
        return

    # Process files
    processed_count = 0

    for filepath in files_to_process:
        if process_file(filepath):
            processed_count += 1
            print(f"Processed: {filepath}")

    print(f"\nCompleted processing {processed_count} files")

    # Final verification
    print("\nFinal verification...")
    remaining_files = []
    for filepath in base_dir.rglob('*'):
        if filepath.is_file() and filepath.suffix.lower() in ['.htm', '.css']:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    if '/AuntRuth/' in content:
                        remaining_files.append(filepath)
            except Exception:
                pass

    print(f"Files still containing /AuntRuth/ after processing: {len(remaining_files)}")
    if remaining_files and len(remaining_files) <= 10:
        for f in remaining_files:
            print(f"  {f}")

if __name__ == "__main__":
    main()