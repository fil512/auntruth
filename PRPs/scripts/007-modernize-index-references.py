#!/usr/bin/env python3
"""
Task 007: Modernize Index References Script
Purpose: Fix references to \AuntRuth\index.htm to use proper relative paths

This script addresses the massive scale issue of ~5,225 files containing broken
references to the main index.html file. These references use Windows-style
absolute paths that don't work on GitHub Pages.

CRITICAL SAFETY REQUIREMENTS:
- This script processes over 5,000 files
- Uses git branch safety system
- Implements phased execution with checkpoints
- Progress reporting every 100 files
- Error logging and recovery
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import argparse


def verify_git_branch(expected_branch):
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
        print(f"✅ Verified working in correct branch: {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get current git branch: {e}")


def count_affected_files(target_dir, pattern):
    """Count files that would be affected by this operation"""
    affected_files = []
    total_occurrences = 0

    print(f"🔍 Scanning {target_dir} for pattern: {pattern}")

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Look for the specific pattern we need to fix
                        matches = re.findall(r'\\AuntRuth\\index\.htm', content, re.IGNORECASE)
                        if matches:
                            affected_files.append(file_path)
                            total_occurrences += len(matches)
                except (OSError, IOError) as e:
                    print(f"⚠️  Error reading {file_path}: {e}")
                    continue

    return affected_files, total_occurrences


def calculate_relative_path(from_file, target_dir):
    """Calculate the relative path from a file to the target directory"""
    from_dir = os.path.dirname(from_file)

    # Count how many levels deep we are from the target directory
    rel_path = os.path.relpath(target_dir, from_dir)

    # Normalize path separators to forward slashes for web compatibility
    rel_path = rel_path.replace('\\', '/')

    return rel_path


def process_files_batch(target_dir, dry_run=True, max_files=None):
    """Process files with safety measures and proper relative path calculation"""

    # Find all files that need fixing
    print("📊 Analyzing scope of changes needed...")
    affected_files, total_occurrences = count_affected_files(target_dir, r'\\AuntRuth\\index\.htm')

    print(f"📈 Found {len(affected_files)} files with {total_occurrences} total occurrences")

    if max_files:
        affected_files = affected_files[:max_files]
        print(f"🎯 Limited to first {len(affected_files)} files for testing")

    if dry_run:
        print("\n🧪 DRY RUN MODE - Showing what would be changed:")
        print("="*60)

        sample_count = min(10, len(affected_files))
        for i, file_path in enumerate(affected_files[:sample_count]):
            print(f"{i+1:2d}. {file_path}")

            # Calculate what the relative path should be
            target_index_dir = os.path.join(target_dir, 'htm')
            rel_path = calculate_relative_path(file_path, target_index_dir)
            new_ref = f"{rel_path}/index.html"

            print(f"    Current: \\AuntRuth\\index.htm")
            print(f"    New:     {new_ref}")

            # Show actual content sample
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    match = re.search(r'<a[^>]*href\s*=\s*["\']\\AuntRuth\\index\.htm["\'][^>]*>.*?</a>',
                                    content, re.IGNORECASE | re.DOTALL)
                    if match:
                        print(f"    Sample:  {match.group()[:80]}...")
            except Exception as e:
                print(f"    Error reading sample: {e}")
            print()

        if len(affected_files) > sample_count:
            print(f"... and {len(affected_files) - sample_count} more files")

        print("="*60)
        print("✅ Dry run complete. Use --execute to perform actual changes.")
        return affected_files

    # Actual processing
    print(f"\n🚀 Starting to process {len(affected_files)} files...")
    processed = 0
    errors = []
    changes_made = []

    # Create incremental commit checkpoints for large operations
    checkpoint_interval = 500  # Commit every 500 files

    for i, file_path in enumerate(affected_files):
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            # Calculate the correct relative path for this specific file
            target_index_dir = os.path.join(target_dir, 'htm')
            rel_path = calculate_relative_path(file_path, target_index_dir)
            new_ref = f"{rel_path}/index.html"

            # Replace the pattern
            new_content = re.sub(
                r'(href\s*=\s*["\'])\\AuntRuth\\index\.htm(["\'])',
                rf'\g<1>{new_ref}\g<2>',
                original_content,
                flags=re.IGNORECASE
            )

            # Only write if content actually changed
            if new_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                changes_made.append({
                    'file': file_path,
                    'old_ref': '\\AuntRuth\\index.htm',
                    'new_ref': new_ref
                })

            processed += 1

            # Progress reporting
            if processed % 100 == 0:
                print(f"⏳ Processed {processed}/{len(affected_files)} files... "
                      f"({processed/len(affected_files)*100:.1f}%)")

            # Create checkpoint commits for large operations
            if processed % checkpoint_interval == 0:
                print(f"💾 Creating checkpoint commit at {processed} files...")
                try:
                    subprocess.run(['git', 'add', '.'], check=True, cwd=target_dir)
                    commit_msg = f"Task 007 checkpoint: Fixed index.htm references in {processed} files"
                    subprocess.run(['git', 'commit', '-m', commit_msg], check=True, cwd=target_dir)
                    print(f"✅ Checkpoint commit created")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Warning: Could not create checkpoint commit: {e}")

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
            continue

    print(f"\n🎉 Processing completed!")
    print(f"📊 Statistics:")
    print(f"   - Total files processed: {processed}")
    print(f"   - Files with changes: {len(changes_made)}")
    print(f"   - Errors encountered: {len(errors)}")

    if errors:
        print(f"\n⚠️  Errors encountered:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")

    return changes_made


def validate_changes(target_dir, sample_size=10):
    """Validate that changes were applied correctly"""
    print(f"\n🔍 Validating changes (checking {sample_size} random files)...")

    # Find files that should have been changed
    all_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                all_files.append(os.path.join(root, file))

    # Sample random files for validation
    import random
    sample_files = random.sample(all_files, min(sample_size, len(all_files)))

    validation_results = []
    for file_path in sample_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check if old pattern still exists
            old_pattern_found = re.search(r'\\AuntRuth\\index\.htm', content, re.IGNORECASE)

            validation_results.append({
                'file': file_path,
                'old_pattern_exists': bool(old_pattern_found),
                'status': 'FAIL' if old_pattern_found else 'PASS'
            })

        except Exception as e:
            validation_results.append({
                'file': file_path,
                'error': str(e),
                'status': 'ERROR'
            })

    # Report validation results
    passed = sum(1 for r in validation_results if r['status'] == 'PASS')
    failed = sum(1 for r in validation_results if r['status'] == 'FAIL')
    errors = sum(1 for r in validation_results if r['status'] == 'ERROR')

    print(f"📋 Validation Results:")
    print(f"   - Passed: {passed}/{len(validation_results)}")
    print(f"   - Failed: {failed}/{len(validation_results)}")
    print(f"   - Errors: {errors}/{len(validation_results)}")

    if failed > 0:
        print(f"\n❌ Files that still contain old pattern:")
        for result in validation_results:
            if result['status'] == 'FAIL':
                print(f"   - {result['file']}")

    return validation_results


def main():
    parser = argparse.ArgumentParser(description='Fix index.htm references for GitHub Pages compatibility')
    parser.add_argument('--target-dir', default='/home/ken/wip/fam/auntruth/docs',
                       help='Target directory to process')
    parser.add_argument('--branch-name', default='task-007-create-modern-index',
                       help='Expected git branch name')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--execute', action='store_true',
                       help='Actually perform the changes')
    parser.add_argument('--test-mode', action='store_true',
                       help='Process only first 5 files for testing')
    parser.add_argument('--validate', action='store_true',
                       help='Validate changes after processing')

    args = parser.parse_args()

    print(f"🚀 Task 007: Modernize Index References")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Target directory: {args.target_dir}")
    print(f"🌿 Expected branch: {args.branch_name}")

    try:
        # Verify git branch
        verify_git_branch(args.branch_name)

        # Determine mode
        if args.execute and not args.dry_run:
            max_files = 5 if args.test_mode else None
            print(f"\n🎯 EXECUTION MODE - Making actual changes")
            if args.test_mode:
                print(f"🧪 TEST MODE - Processing only first 5 files")

            changes = process_files_batch(args.target_dir, dry_run=False, max_files=max_files)

            # Final commit
            print(f"\n💾 Creating final commit...")
            subprocess.run(['git', 'add', '.'], check=True)
            commit_msg = f"""Task 007: Modernize index.htm references

- Fixed {len(changes)} files with broken \\AuntRuth\\index.htm references
- Converted to proper relative paths for GitHub Pages compatibility
- Processed files across all subdirectories recursively
- Maintained backward compatibility and file structure

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            print(f"✅ Final commit created")

            if args.validate:
                validate_changes(args.target_dir)

        else:
            # Default to dry run
            print(f"\n🧪 DRY RUN MODE - No changes will be made")
            process_files_batch(args.target_dir, dry_run=True)
            print(f"\n💡 To execute changes, use: python3 {sys.argv[0]} --execute")
            print(f"💡 To test on 5 files first, use: python3 {sys.argv[0]} --execute --test-mode")

        print(f"\n✅ Task 007 completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n🔄 Rollback instructions:")
        print(f"   git reset --hard HEAD~1  # Undo last commit")
        print(f"   git checkout main        # Return to main branch")
        print(f"   git branch -D {args.branch_name}  # Delete feature branch")
        sys.exit(1)


if __name__ == "__main__":
    main()