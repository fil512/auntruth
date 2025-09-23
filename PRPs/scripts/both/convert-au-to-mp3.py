#!/usr/bin/env python3
"""
Convert AU audio files to MP3 format.

This script converts all .au files from docs/au/ directory to MP3 format
and saves them in docs/mp3/ directory.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Check if ffmpeg is available."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_au_to_mp3(input_file, output_file):
    """Convert a single AU file to MP3 using ffmpeg."""
    try:
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-acodec', 'mp3',
            '-ab', '192k',
            '-y',  # Overwrite output files without asking
            str(output_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ Converted: {input_file.name} -> {output_file.name}")
            return True
        else:
            print(f"✗ Failed to convert {input_file.name}: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error converting {input_file.name}: {e}")
        return False

def main():
    """Main conversion function."""
    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed or not available in PATH.")
        print("Please install ffmpeg to use this script.")
        print("On Ubuntu/Debian: sudo apt install ffmpeg")
        print("On macOS: brew install ffmpeg")
        sys.exit(1)

    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    au_dir = project_root / 'docs' / 'au'
    mp3_dir = project_root / 'docs' / 'mp3'

    # Check if AU directory exists
    if not au_dir.exists():
        print(f"Error: AU directory not found at {au_dir}")
        sys.exit(1)

    # Create MP3 directory if it doesn't exist
    mp3_dir.mkdir(parents=True, exist_ok=True)

    # Find all .au files
    au_files = list(au_dir.glob('*.au')) + list(au_dir.glob('*.AU'))

    if not au_files:
        print(f"No .au files found in {au_dir}")
        return

    print(f"Found {len(au_files)} AU files to convert...")
    print(f"Input directory: {au_dir}")
    print(f"Output directory: {mp3_dir}")
    print()

    # Convert each file
    converted = 0
    failed = 0

    for au_file in au_files:
        # Skip non-AU files (like the existing MP3 and log files)
        if au_file.suffix.lower() not in ['.au']:
            continue

        mp3_file = mp3_dir / f"{au_file.stem}.mp3"

        if convert_au_to_mp3(au_file, mp3_file):
            converted += 1
        else:
            failed += 1

    print()
    print(f"Conversion complete!")
    print(f"✓ Successfully converted: {converted} files")
    if failed > 0:
        print(f"✗ Failed to convert: {failed} files")

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())