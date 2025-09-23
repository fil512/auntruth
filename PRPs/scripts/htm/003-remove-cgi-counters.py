#!/usr/bin/env python3
"""
Task 003: Remove CGI Counter Script References

This script removes all instances of /cgi-bin/counter.pl references from HTML files
for GitHub Pages compatibility. CGI scripts don't work in static hosting environments.

Usage: python3 003-remove-cgi-counters.py [--dry-run] [--target-dir docs/htm]
"""

import os
import re
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path

def verify_git_branch(expected_branch):
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
        print(f"✓ Verified working in correct branch: {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get current git branch: {e}")

def find_affected_files(target_dir, pattern):
    """Find all files containing the CGI counter pattern"""
    affected_files = []
    total_files_checked = 0

    print(f"Scanning {target_dir} for pattern: {pattern}")

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                total_files_checked += 1

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if pattern in content:
                            affected_files.append(file_path)
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

                # Progress indicator for large scans
                if total_files_checked % 1000 == 0:
                    print(f"  Scanned {total_files_checked} files, found {len(affected_files)} with pattern...")

    print(f"✓ Scan complete: checked {total_files_checked} files, found {len(affected_files)} files with CGI counter references")
    return affected_files

def remove_cgi_counter_pattern(content):
    """Remove CGI counter IMG tags from HTML content"""
    # Pattern matches: <IMG SRC="/cgi-bin/counter.pl?AuntRuth" width = 0 length = 0 alt=" * ">
    # and similar variations with different spacing and attributes
    pattern = r'<IMG\s+SRC\s*=\s*["\']?/cgi-bin/counter\.pl[^>]*>'

    # Use re.IGNORECASE to catch IMG, img, Img variations
    cleaned_content = re.sub(pattern, '', content, flags=re.IGNORECASE)

    return cleaned_content

def process_files_batch(affected_files, dry_run=True):
    """Process files with safety measures and progress tracking"""

    if dry_run:
        print(f"\n=== DRY RUN MODE ===")
        print(f"Would process {len(affected_files)} files")
        print(f"First 10 files that would be changed:")
        for i, file_path in enumerate(affected_files[:10]):
            rel_path = os.path.relpath(file_path, "/home/ken/wip/fam/auntruth")
            print(f"  {i+1:2d}. {rel_path}")

        if len(affected_files) > 10:
            print(f"  ... and {len(affected_files) - 10} more files")

        # Show sample of what would be removed
        if affected_files:
            sample_file = affected_files[0]
            print(f"\nSample content from {os.path.basename(sample_file)}:")
            try:
                with open(sample_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Find and show the CGI counter line
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '/cgi-bin/counter.pl' in line:
                        print(f"  Line {i+1}: {line.strip()}")
                        print(f"  Would be REMOVED")
                        break

            except Exception as e:
                print(f"  Could not read sample file: {e}")

        return affected_files

    # REAL PROCESSING MODE
    print(f"\n=== PROCESSING {len(affected_files)} FILES ===")
    processed = 0
    errors = []

    for file_path in affected_files:
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            # Remove CGI counter references
            new_content = remove_cgi_counter_pattern(original_content)

            # Only write if content actually changed
            if new_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            processed += 1

            # Progress reporting every 100 files
            if processed % 100 == 0:
                rel_path = os.path.relpath(file_path, "/home/ken/wip/fam/auntruth")
                print(f"  Processed {processed}/{len(affected_files)} files... (last: {rel_path})")

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            errors.append(error_msg)
            print(f"  ERROR: {error_msg}")

    print(f"✓ Processing complete: {processed}/{len(affected_files)} files processed")

    if errors:
        print(f"⚠ Encountered {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")

    return processed, errors

def test_on_sample_files(affected_files, sample_size=5):
    """Test the processing on a small sample of files first"""
    if len(affected_files) < sample_size:
        sample_files = affected_files
    else:
        # Take files from different parts of the list
        step = len(affected_files) // sample_size
        sample_files = [affected_files[i * step] for i in range(sample_size)]

    print(f"\n=== TESTING ON {len(sample_files)} SAMPLE FILES ===")

    for i, file_path in enumerate(sample_files):
        rel_path = os.path.relpath(file_path, "/home/ken/wip/fam/auntruth")
        print(f"Testing {i+1}/{len(sample_files)}: {rel_path}")

        try:
            # Read and process content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            processed_content = remove_cgi_counter_pattern(original_content)

            # Check if changes were made
            if processed_content != original_content:
                # Find what was removed
                original_lines = original_content.split('\n')
                processed_lines = processed_content.split('\n')

                for j, line in enumerate(original_lines):
                    if '/cgi-bin/counter.pl' in line and (j >= len(processed_lines) or line != processed_lines[j]):
                        print(f"  ✓ Would remove: {line.strip()}")
            else:
                print(f"  ⚠ No changes detected (unexpected)")

        except Exception as e:
            print(f"  ✗ Error testing {file_path}: {e}")

    return True

def main():
    parser = argparse.ArgumentParser(description="Remove CGI counter script references for GitHub Pages compatibility")
    parser.add_argument('--target-dir', default='docs/htm', help='Directory to process (default: docs/htm)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--branch-name', default='task-003-remove-cgi-counters', help='Expected git branch name')
    parser.add_argument('--test-sample', action='store_true', help='Test on sample files first')

    args = parser.parse_args()

    print("=" * 60)
    print("Task 003: Remove CGI Counter Script References")
    print("=" * 60)
    print(f"Target directory: {args.target_dir}")
    print(f"Expected branch: {args.branch_name}")
    print(f"Dry run mode: {args.dry_run}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. Verify git branch
        verify_git_branch(args.branch_name)

        # 2. Verify target directory exists
        target_path = Path(args.target_dir)
        if not target_path.exists():
            raise ValueError(f"Target directory does not exist: {args.target_dir}")

        # 3. Find all affected files
        pattern = "/cgi-bin/counter.pl"
        affected_files = find_affected_files(args.target_dir, pattern)

        if not affected_files:
            print("✓ No files found with CGI counter references. Task complete!")
            return 0

        # 4. Test on sample files if requested
        if args.test_sample and not args.dry_run:
            test_on_sample_files(affected_files)

            response = input("\nSample test complete. Continue with full processing? [y/N]: ")
            if response.lower() != 'y':
                print("Processing cancelled by user.")
                return 0

        # 5. Process files (dry-run or real)
        if args.dry_run:
            process_files_batch(affected_files, dry_run=True)
            print(f"\n✓ Dry run complete. Use --no-dry-run to perform actual changes.")
        else:
            processed, errors = process_files_batch(affected_files, dry_run=False)

            # 6. Commit changes if successful
            if processed > 0 and len(errors) == 0:
                print(f"\n=== COMMITTING CHANGES ===")
                try:
                    subprocess.run(['git', 'add', args.target_dir], check=True)

                    commit_msg = f"""Remove CGI counter script references

- Removed /cgi-bin/counter.pl references from {processed} HTML files
- CGI scripts not compatible with GitHub Pages static hosting
- Pattern: <IMG SRC="/cgi-bin/counter.pl?AuntRuth" ...>
- Files affected across all subdirectories: L2, L3, L6, L7, L8, L9, oldhtm

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

                    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                    print(f"✓ Changes committed successfully")

                except subprocess.CalledProcessError as e:
                    print(f"⚠ Error committing changes: {e}")
                    print("Changes have been made but not committed. Please commit manually.")
            elif errors:
                print(f"⚠ Processing completed with {len(errors)} errors. Please review before committing.")

        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())