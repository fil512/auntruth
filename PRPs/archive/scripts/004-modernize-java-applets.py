#!/usr/bin/env python3
"""
Task 004: Modernize Java applet sound players to HTML5 audio elements

This script replaces Java applet sound players with modern HTML5 audio elements.
Processes exactly 12 files in docs/htm directory.

Required transformations:
- Java applet: <APPLET CODE='hcslsond.class'...><PARAM NAME='sondfile' VALUE='/au/file.au'></APPLET>
- HTML5 audio: <audio controls preload="none"><source src="/au/file.au" type="audio/basic">Your browser does not support the audio element.</audio>
"""

import os
import re
import sys
from pathlib import Path

def verify_git_branch(expected_branch):
    """Verify we're working in the correct branch"""
    import subprocess
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
    return current_branch

def modernize_java_applets(target_dir="docs/htm", dry_run=False):
    """Replace Java applet sound players with HTML5 audio elements"""

    # List of files we know contain Java applets (from our scope analysis)
    affected_files = [
        "docs/htm/L0/index.htm",
        "docs/htm/L1/index.htm",
        "docs/htm/L2/index.htm",
        "docs/htm/L3/index.htm",
        "docs/htm/L3/PRINGCEM.htm",
        "docs/htm/L4/index.htm",
        "docs/htm/L4/LATHBOOK.htm",
        "docs/htm/L5/index.htm",
        "docs/htm/L6/index.htm",
        "docs/htm/L7/index.htm",
        "docs/htm/L8/index.htm",
        "docs/htm/L9/index.htm"
    ]

    # Java applet pattern - matches the exact format found in files
    java_applet_pattern = re.compile(
        r'<APPLET CODE\s*=\s*[\'"]hcslsond\.class[\'"][^>]*>'
        r'<PARAM NAME\s*=\s*[\'"]sondfile[\'"] VALUE\s*=\s*[\'"]([^\'\"]+\.au)[\'"]>'
        r'</APPLET>',
        re.IGNORECASE
    )

    processed_files = 0
    total_replacements = 0

    print(f"Modernizing Java applets in {len(affected_files)} files...")

    if dry_run:
        print("DRY RUN - showing what would be changed:")

    for file_path in affected_files:
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue

        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Find and replace Java applets
            def replace_applet(match):
                audio_file = match.group(1)
                html5_audio = (
                    f'<audio controls preload="none">\n'
                    f'  <source src="{audio_file}" type="audio/basic">\n'
                    f'  Your browser does not support the audio element.\n'
                    f'</audio>'
                )
                return html5_audio

            # Count matches first
            matches = java_applet_pattern.findall(content)
            if matches:
                print(f"  {file_path}: Found {len(matches)} Java applet(s)")
                for audio_file in matches:
                    print(f"    - Converting /au/{audio_file.split('/')[-1]} to HTML5 audio")

                if not dry_run:
                    # Perform replacement
                    new_content = java_applet_pattern.sub(replace_applet, content)

                    # Write file back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                total_replacements += len(matches)
                processed_files += 1
            else:
                print(f"  {file_path}: No Java applets found")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nSummary:")
    print(f"  Files processed: {processed_files}")
    print(f"  Total Java applets modernized: {total_replacements}")

    if dry_run:
        print(f"\nThis was a dry run. No files were modified.")
        print(f"Run without --dry-run to apply changes.")
    else:
        print(f"\nJava applets successfully modernized to HTML5 audio elements.")
        print(f"All .au audio files remain preserved in docs/au/ directory.")

    return processed_files, total_replacements

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Modernize Java applet sound players to HTML5 audio')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    parser.add_argument('--target-dir', default='docs/htm',
                       help='Target directory to process (default: docs/htm)')

    args = parser.parse_args()

    try:
        # Verify we're in the correct git branch
        branch = verify_git_branch("task-004-modernize-java-applets")
        print(f"✓ Working in correct git branch: {branch}")

        # Process files
        processed, replacements = modernize_java_applets(args.target_dir, args.dry_run)

        if not args.dry_run and replacements > 0:
            print(f"\nNext steps:")
            print(f"1. Verify changes look correct by testing a few files")
            print(f"2. Commit changes with: git add . && git commit -m 'Task 004: Modernize Java applets to HTML5 audio'")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()