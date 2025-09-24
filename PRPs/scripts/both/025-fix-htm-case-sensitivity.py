#!/usr/bin/env python3
"""
Fix HTM Case Sensitivity Issues - Script 025

Problem: Files in docs/new/htm exist as .HTM (uppercase) but links point to .htm (lowercase)
Solution: Rename all .HTM files to .htm in docs/new/htm directory

Expected Impact: Fix 291 broken links due to case sensitivity issues
"""

import os
import sys
import argparse

def find_htm_files_to_rename(base_dir):
    """Find all .HTM files that need to be renamed to .htm"""
    htm_files_to_rename = []

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.HTM'):
                # Check if corresponding .htm file exists
                htm_file = file[:-4] + '.htm'
                htm_path = os.path.join(root, htm_file)
                if not os.path.exists(htm_path):
                    HTM_path = os.path.join(root, file)
                    htm_files_to_rename.append((HTM_path, htm_path))

    return htm_files_to_rename

def main():
    parser = argparse.ArgumentParser(description='Fix HTM case sensitivity by renaming .HTM to .htm')
    parser.add_argument('--no-dry-run', action='store_true', help='Actually perform the renames')
    parser.add_argument('--target-dir', default='docs/new/htm', help='Target directory to process')

    args = parser.parse_args()

    # Verify we're in the right directory
    if not os.path.exists('docs'):
        print("❌ Error: Must run from project root (docs directory not found)")
        sys.exit(1)

    target_dir = args.target_dir
    if not os.path.exists(target_dir):
        print(f"❌ Error: Target directory {target_dir} does not exist")
        sys.exit(1)

    print("🔍 Finding .HTM files to rename...")
    htm_files_to_rename = find_htm_files_to_rename(target_dir)

    if not htm_files_to_rename:
        print("✅ No .HTM files found that need renaming!")
        return

    print(f"📊 Found {len(htm_files_to_rename)} .HTM files to rename to .htm")

    # Show sample files
    print("\n🔍 Sample files to rename:")
    for i, (old_path, new_path) in enumerate(htm_files_to_rename[:10]):
        print(f"  {i+1:2d}. {old_path} → {new_path}")

    if len(htm_files_to_rename) > 10:
        print(f"     ... and {len(htm_files_to_rename) - 10} more files")

    if not args.no_dry_run:
        print(f"\n🧪 Dry run complete. Use --no-dry-run to rename {len(htm_files_to_rename)} files.")
        return

    # Actually perform the renames
    print(f"\n🔧 Renaming {len(htm_files_to_rename)} files...")

    success_count = 0
    error_count = 0

    for old_path, new_path in htm_files_to_rename:
        try:
            os.rename(old_path, new_path)
            success_count += 1
            if success_count <= 5:  # Show first 5 renames
                print(f"✅ Renamed: {os.path.basename(old_path)} → {os.path.basename(new_path)}")
            elif success_count % 50 == 0:  # Progress every 50 files
                print(f"📈 Progress: {success_count}/{len(htm_files_to_rename)} files renamed...")
        except Exception as e:
            print(f"❌ Error renaming {old_path}: {e}")
            error_count += 1

    print(f"\n✅ Rename complete!")
    print(f"   Successfully renamed: {success_count} files")
    if error_count > 0:
        print(f"   Errors: {error_count} files")

    print(f"\n🧪 Testing sample URLs...")
    # Test a few sample URLs
    test_urls = [
        "http://localhost:8000/auntruth/new/htm/L1/XI2718.htm",
        "http://localhost:8000/auntruth/new/htm/L1/XI2717.htm",
        "http://localhost:8000/auntruth/new/htm/L1/XI2716.htm"
    ]

    import subprocess
    for url in test_urls:
        try:
            result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                                  capture_output=True, text=True, timeout=5)
            status = result.stdout.strip()
            if status == '200':
                print(f"✅ {url} → {status}")
            else:
                print(f"❌ {url} → {status}")
        except Exception as e:
            print(f"❌ {url} → Error: {e}")

if __name__ == "__main__":
    main()