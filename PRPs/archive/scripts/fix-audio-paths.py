#!/usr/bin/env python3
"""
Fix audio paths in HTML files to use relative paths instead of absolute paths.
This ensures audio works when running locally at localhost:8000/auntruth/
"""

import os
import re
from pathlib import Path

def fix_audio_paths():
    """Fix audio source paths from absolute to relative"""

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

        # Fix the audio source path
        # From: src="/au/filename.au"
        # To: src="../../au/filename.au" (for files in L*/index.htm)
        # To: src="../../../au/filename.au" (for files in L*/FILENAME.htm)

        if file_rel_path.endswith('/index.htm'):
            # Files in L*/index.htm need ../../au/
            new_content = content.replace('src="/au/', 'src="../../au/')
        else:
            # Files like L3/PRINGCEM.htm or L4/LATHBOOK.htm need ../../au/
            new_content = content.replace('src="/au/', 'src="../../au/')

        # Write the file back
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  Fixed audio path in {file_path}")
        else:
            print(f"  No changes needed in {file_path}")

if __name__ == "__main__":
    fix_audio_paths()
    print("Audio path fixing complete!")