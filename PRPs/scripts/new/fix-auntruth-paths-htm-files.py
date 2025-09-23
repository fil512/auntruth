#!/usr/bin/env python3
"""
Fix /AuntRuth/ absolute paths in .HTM files in docs/new directory.

This script fixes absolute path issues where links reference /AuntRuth/
but the correct path should be /auntruth/ (lowercase).

Scope: 291 .HTM files affected with ~287 occurrences total
Critical for proper resource loading (CSS, images, links)

Usage:
    python3 new/fix-auntruth-paths-htm-files.py [--dry-run] [--test-mode] [--execute] [--yes]

Features:
- Fixes /AuntRuth/ to /auntruth/ path issues in .HTM files
- Phased execution with checkpoint commits for scale
- Progress reporting every 50 files
- Comprehensive error logging and recovery
- Dry-run mode with detailed preview
- Test mode for 5 sample files first
- Auto-confirmation mode for non-interactive environments
- Post-execution validation
"""

import os
import re
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def get_git_branch():
    """Get current git branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def create_feature_branch():
    """Create feature branch for this task"""
    branch_name = "fix-auntruth-paths-htm"
    try:
        # Check if branch already exists
        result = subprocess.run(["git", "rev-parse", "--verify", branch_name],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Branch {branch_name} already exists. Switching to it.")
            subprocess.run(["git", "checkout", branch_name], check=True)
        else:
            print(f"Creating feature branch: {branch_name}")
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        return branch_name
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
        return None


def find_htm_files(target_dir):
    """Find all .HTM files in target directory"""
    htm_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.HTM'):
                htm_files.append(os.path.join(root, file))
    return sorted(htm_files)


def fix_auntruth_paths_in_file(file_path, dry_run=False):
    """Fix /AuntRuth/ path issues in a single .HTM file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Fix /AuntRuth/ paths to /auntruth/
        old_content = content

        # Main patterns to fix:
        # 1. /AuntRuth/css/ → /auntruth/css/
        # 2. /AuntRuth/htm/ → /auntruth/htm/
        # 3. /AuntRuth/jpg/ → /auntruth/jpg/
        # 4. /AuntRuth/mpg/ → /auntruth/mpg/
        # 5. /AuntRuth/au/ → /auntruth/au/
        # 6. /AuntRuth/ → /auntruth/

        replacements = [
            (r'/AuntRuth/css/', '/auntruth/css/'),
            (r'/AuntRuth/htm/', '/auntruth/htm/'),
            (r'/AuntRuth/jpg/', '/auntruth/jpg/'),
            (r'/AuntRuth/mpg/', '/auntruth/mpg/'),
            (r'/AuntRuth/au/', '/auntruth/au/'),
            (r"href='/AuntRuth/'", "href='/auntruth/'"),
            (r'href="/AuntRuth/"', 'href="/auntruth/"'),
        ]

        total_replacements = 0
        for old_pattern, new_pattern in replacements:
            before_count = content.count(old_pattern)
            content = content.replace(old_pattern, new_pattern)
            after_count = content.count(old_pattern)
            replaced_count = before_count - after_count
            if replaced_count > 0:
                total_replacements += replaced_count

        if total_replacements > 0:
            changes_made.append(f"Fixed /AuntRuth/ paths: {total_replacements} occurrences")

        if content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            return changes_made
        return []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def commit_changes(message, file_count):
    """Commit changes with descriptive message"""
    try:
        subprocess.run(["git", "add", "."], check=True)

        commit_message = f"""Fix /AuntRuth/ path issues: {message}

- Processed {file_count} .HTM files
- Fixed /AuntRuth/ -> /auntruth/ absolute paths
- Ensures proper resource loading (CSS, images, links)
- Critical for GitHub Pages compatibility

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f"✓ Committed changes for {file_count} files")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git commit error: {e}")
        return False


def validate_changes(target_dir):
    """Validate that changes were applied correctly"""
    print("\\n=== Validating Changes ===")

    # Count remaining /AuntRuth/ references in .HTM files
    try:
        result = subprocess.run([
            "grep", "-r", "/AuntRuth/", target_dir,
            "--include=*.HTM"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            remaining_count = len(result.stdout.strip().split('\\n'))
            print(f"⚠️  WARNING: {remaining_count} /AuntRuth/ references still found!")
            return False
        else:
            print("✓ No /AuntRuth/ references found in .HTM files - all fixed!")
            return True

    except Exception as e:
        print(f"Validation error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Fix /AuntRuth/ path issues in .HTM files in docs/new')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--test-mode', action='store_true',
                       help='Process only 5 test files first')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the full operation')
    parser.add_argument('--yes', action='store_true',
                       help='Auto-confirm all prompts')
    parser.add_argument('--target-dir', default='/home/ken/wip/fam/auntruth/docs/new',
                       help='Target directory to process')

    args = parser.parse_args()

    # Safety check: require explicit execution flag for operations
    if not args.dry_run and not args.test_mode and not args.execute:
        print("ERROR: This operation affects 291 .HTM files!")
        print("You must specify one of: --dry-run, --test-mode, or --execute")
        print("\\nRecommended workflow:")
        print("1. python3 new/fix-auntruth-paths-htm-files.py --dry-run")
        print("2. python3 new/fix-auntruth-paths-htm-files.py --test-mode")
        print("3. python3 new/fix-auntruth-paths-htm-files.py --execute")
        sys.exit(1)

    target_dir = Path(args.target_dir)
    if not target_dir.exists():
        print(f"Error: Target directory {target_dir} does not exist")
        sys.exit(1)

    print(f"/AuntRuth/ Path Fix - .HTM files in docs/new")
    print(f"Target directory: {target_dir}")
    print(f"Git branch: {get_git_branch()}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'TEST' if args.test_mode else 'EXECUTE'}")
    print("=" * 50)

    # Find affected files
    htm_files = find_htm_files(target_dir)
    print(f"Found {len(htm_files)} .HTM files to scan")

    # Count files that actually need fixes
    affected_files = []
    print("Scanning .HTM files for /AuntRuth/ patterns...")

    for i, file_path in enumerate(htm_files):
        if i % 100 == 0:
            print(f"Scanned {i}/{len(htm_files)} files...")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check if file contains /AuntRuth/ patterns
            if '/AuntRuth/' in content:
                affected_files.append(file_path)

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    print(f"\\n📊 Scope Analysis Results:")
    print(f"   Total .HTM files: {len(htm_files)}")
    print(f"   Files needing fixes: {len(affected_files)}")

    if len(affected_files) == 0:
        print("✓ No .HTM files need /AuntRuth/ path fixes!")
        sys.exit(0)

    # Show sample of affected files in dry-run mode
    if args.dry_run:
        print(f"\\n📋 Sample of affected files (first 10):")
        for file_path in affected_files[:10]:
            rel_path = os.path.relpath(file_path, target_dir)
            print(f"   {rel_path}")

        print(f"\\n🔍 Sample changes that would be made:")
        for file_path in affected_files[:3]:
            rel_path = os.path.relpath(file_path, target_dir)
            changes = fix_auntruth_paths_in_file(file_path, dry_run=True)
            if changes:
                print(f"   {rel_path}: {changes}")

        print(f"\\n📈 Summary:")
        print(f"   Would process {len(affected_files)} .HTM files")
        print(f"   Estimated fixes: ~287 occurrences")
        print(f"   Use --test-mode to test on 5 files first")
        sys.exit(0)

    # Test mode: process only 5 files
    if args.test_mode:
        test_files = affected_files[:5]
        print(f"\\n🧪 TEST MODE: Processing {len(test_files)} .HTM files")

        if not args.yes:
            response = input("Proceed with test on 5 .HTM files? (y/N): ")
            if response.lower() != 'y':
                print("Test cancelled.")
                sys.exit(0)

        processed_count = 0
        total_changes = 0

        for file_path in test_files:
            rel_path = os.path.relpath(file_path, target_dir)
            changes = fix_auntruth_paths_in_file(file_path, dry_run=False)
            if changes:
                print(f"✓ {rel_path}: {changes}")
                total_changes += len(changes)
            processed_count += 1

        print(f"\\n✅ Test completed:")
        print(f"   Files processed: {processed_count}")
        print(f"   Changes made: {total_changes}")
        print(f"\\nTo process all {len(affected_files)} .HTM files, use --execute")
        sys.exit(0)

    # Full execution mode
    if args.execute:
        print(f"\\n⚠️  FULL EXECUTION MODE")
        print(f"   Will process {len(affected_files)} .HTM files")
        print(f"   Estimated {len(affected_files) // 100 + 1} checkpoint commits")

        if not args.yes:
            response = input(f"Proceed with full execution? (y/N): ")
            if response.lower() != 'y':
                print("Execution cancelled.")
                sys.exit(0)

        # Create feature branch
        branch_name = create_feature_branch()
        if not branch_name:
            print("Failed to create feature branch. Aborting.")
            sys.exit(1)

        processed_count = 0
        total_changes = 0
        checkpoint_interval = 100  # Commit every 100 files

        print(f"\\n🚀 Starting full execution...")
        print(f"Branch: {branch_name}")
        print(f"Checkpoint commits every {checkpoint_interval} files")

        for i, file_path in enumerate(affected_files):
            rel_path = os.path.relpath(file_path, target_dir)
            changes = fix_auntruth_paths_in_file(file_path, dry_run=False)

            if changes:
                total_changes += len(changes)

            processed_count += 1

            # Progress reporting
            if processed_count % 50 == 0:
                percentage = (processed_count / len(affected_files)) * 100
                print(f"Progress: {processed_count}/{len(affected_files)} ({percentage:.1f}%)")

            # Checkpoint commits
            if processed_count % checkpoint_interval == 0:
                commit_changes(f"Checkpoint {processed_count//checkpoint_interval}", processed_count)

        # Final commit
        if processed_count % checkpoint_interval != 0:
            commit_changes("Final batch", processed_count)

        print(f"\\n✅ Execution completed:")
        print(f"   Files processed: {processed_count}")
        print(f"   Total changes: {total_changes}")
        print(f"   Branch: {branch_name}")

        # Validate changes
        if validate_changes(target_dir):
            print("\\n🎉 All /AuntRuth/ path issues fixed successfully!")
        else:
            print("\\n⚠️  Some issues may remain. Check validation output.")

        print(f"\\n📋 Next steps:")
        print(f"   1. Review changes: git log --oneline")
        print(f"   2. Push branch: git push -u origin {branch_name}")
        print(f"   3. Test the website functionality")
        print(f"   4. Create pull request when satisfied")


if __name__ == "__main__":
    main()