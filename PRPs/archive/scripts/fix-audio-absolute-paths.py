#!/usr/bin/env python3
"""
Fix audio paths to use absolute paths that work with localhost:8000/auntruth/ setup
"""

import os
import re
from pathlib import Path

def fix_audio_absolute_paths():
    """Fix audio source paths to use absolute paths for localhost testing"""

    # Define the target directory
    target_dir = Path("docs/htm")

    # Files that need fixing
    files_to_fix = [
        "L0/index.htm", "L1/index.htm", "L2/index.htm", "L3/index.htm",
        "L4/index.htm", "L5/index.htm", "L6/index.htm", "L7/index.htm",
        "L8/index.htm", "L9/index.htm", "L3/PRINGCEM.htm", "L4/LATHBOOK.htm"
    ]

    for file_rel_path in files_to_fix:
        file_path = target_dir / file_rel_path

        if not file_path.exists():
            print(f"Skipping {file_path} - does not exist")
            continue

        print(f"Processing {file_path}")

        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Fix the audio source path to absolute path for localhost
        # From: src="../../au/filename.au"
        # To: src="/auntruth/au/filename.au"
        new_content = content.replace('src="../../au/', 'src="/auntruth/au/')

        # Write the file back
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  Fixed audio path to absolute in {file_path}")
        else:
            print(f"  No changes needed in {file_path}")

if __name__ == "__main__":
    fix_audio_absolute_paths()
    print("Audio absolute path fixing complete!")