#!/usr/bin/env python3

import os
import re
import sys

def get_relative_path_to_home(level):
    """Calculate relative path from Lx directory to htm directory (home)"""
    # From /auntruth/htm/L5/ to /auntruth/htm/ is just ../
    # All Lx directories are one level deep within htm
    return "../"

def fix_home_links_in_file(file_path, relative_path):
    """Fix home links in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Fix excessive relative paths like ../../../../../../ back to ../
        content = re.sub(
            r'<a href=[\'"](\.\.\/)+[\'"]>Home \|</a>',
            f'<a href=\'{relative_path}\'>Home |</a>',
            content
        )

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    docs_root = "/home/ken/wip/fam/auntruth/docs"
    htm_root = os.path.join(docs_root, "htm")

    if not os.path.exists(htm_root):
        print(f"Error: {htm_root} does not exist")
        return 1

    files_processed = 0
    files_changed = 0

    # Process all L* directories - they all need ../
    for level_dir in os.listdir(htm_root):
        if level_dir.startswith('L') and os.path.isdir(os.path.join(htm_root, level_dir)):
            try:
                level = int(level_dir[1:])
                relative_path = get_relative_path_to_home(level)

                level_path = os.path.join(htm_root, level_dir)
                print(f"Processing {level_dir} with relative path: {relative_path}")

                for filename in os.listdir(level_path):
                    if filename.endswith('.htm'):
                        file_path = os.path.join(level_path, filename)
                        files_processed += 1

                        if fix_home_links_in_file(file_path, relative_path):
                            files_changed += 1

                        if files_processed % 500 == 0:
                            print(f"Processed {files_processed} files, changed {files_changed}")

            except ValueError:
                print(f"Skipping non-numeric level directory: {level_dir}")
                continue

    print(f"\nCompleted: Processed {files_processed} files, changed {files_changed}")
    return 0

if __name__ == "__main__":
    sys.exit(main())