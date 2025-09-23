#!/usr/bin/env python3
"""
Update audio links from AU files to MP3 files with modern HTML5 audio tags
"""

import os
import re
from pathlib import Path

def update_audio_to_mp3():
    """Update audio source paths from AU to MP3 files"""

    # Define the target directory
    target_dir = Path("docs/htm")

    # Files that need updating
    files_to_update = [
        "L0/index.htm", "L1/index.htm", "L2/index.htm", "L3/index.htm",
        "L4/index.htm", "L5/index.htm", "L6/index.htm", "L7/index.htm",
        "L8/index.htm", "L9/index.htm", "L3/PRINGCEM.htm", "L4/LATHBOOK.htm"
    ]

    for file_rel_path in files_to_update:
        file_path = target_dir / file_rel_path

        if not file_path.exists():
            print(f"Skipping {file_path} - does not exist")
            continue

        print(f"Processing {file_path}")

        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Update the audio element to use MP3 files with modern HTML5 attributes
        # From: <audio controls preload="none">
        #         <source src="/auntruth/au/filename.au" type="audio/basic">
        #         Your browser does not support the audio element.
        #       </audio>
        # To: <audio controls preload="metadata">
        #       <source src="/auntruth/mp3/filename.mp3" type="audio/mpeg">
        #       Your browser does not support the audio element.
        #     </audio>

        # Replace the audio source path and type
        new_content = re.sub(
            r'<audio controls preload="none">\s*<source src="/auntruth/au/([^"]+)\.au" type="audio/basic">\s*Your browser does not support the audio element\.\s*</audio>',
            r'<audio controls preload="metadata">\n  <source src="/auntruth/mp3/\1.mp3" type="audio/mpeg">\n  Your browser does not support the audio element.\n</audio>',
            content,
            flags=re.DOTALL
        )

        # Write the file back
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  Updated audio to MP3 in {file_path}")
        else:
            print(f"  No changes needed in {file_path}")

if __name__ == "__main__":
    update_audio_to_mp3()
    print("Audio MP3 update complete!")