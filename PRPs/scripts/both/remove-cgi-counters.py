#!/usr/bin/env python3
"""
CGI Counter Removal Script - remove-cgi-counters.py

Removes obsolete CGI counter references from both docs/htm and docs/new directories
for GitHub Pages compatibility. CGI scripts don't work in static hosting environments.

This script targets the patterns:
- <IMG SRC="\cgi-bin\counter.pl?AuntRuth" ...>
- <img src="\cgi-bin\counter.pl?AuntRuth" ...>

Usage: python3 remove-cgi-counters.py [--dry-run] [--target-dir docs/htm|docs/new] [--both]
"""

import os
import re
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path

def verify_git_branch():
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        print(f"✓ Working in branch: {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get current git branch: {e}")

def find_affected_files(target_dir):
    """Find all files containing CGI counter patterns"""
    affected_files = []
    total_files_checked = 0

    print(f"Scanning {target_dir} for CGI counter patterns...")

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                total_files_checked += 1

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Check for both backslash and forward slash versions
                        if ('\\cgi-bin\\counter.pl' in content or
                            '/cgi-bin/counter.pl' in content or
                            '\\AuntRuth\\cgi-bin\\counter.pl' in content):
                            affected_files.append(file_path)
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

                # Progress indicator for large scans
                if total_files_checked % 1000 == 0:
                    print(f"  Scanned {total_files_checked} files, found {len(affected_files)} with CGI counter references...")

    print(f"✓ Scan complete: checked {total_files_checked} files, found {len(affected_files)} files with CGI counter references")
    return affected_files

def remove_cgi_counter_patterns(content):
    """Remove all CGI counter IMG/img tags from HTML content"""

    # Pattern 1: <IMG SRC="\cgi-bin\counter.pl?AuntRuth" width = 0 length = 0 alt=" * ">
    pattern1 = r'<IMG\s+SRC\s*=\s*["\']?\\cgi-bin\\counter\.pl[^>]*>'

    # Pattern 2: <img src="\cgi-bin\counter.pl?AuntRuth" width="0" length="0" alt=" * ">
    pattern2 = r'<img\s+src\s*=\s*["\']?\\cgi-bin\\counter\.pl[^>]*>'

    # Pattern 3: Forward slash versions
    pattern3 = r'<IMG\s+SRC\s*=\s*["\']?/cgi-bin/counter\.pl[^>]*>'
    pattern4 = r'<img\s+src\s*=\s*["\']?/cgi-bin/counter\.pl[^>]*>'

    # Pattern 5: \AuntRuth\cgi-bin\counter.pl variations
    pattern5 = r'<IMG\s+SRC\s*=\s*["\']?\\AuntRuth\\cgi-bin\\counter\.pl[^>]*>'
    pattern6 = r'<img\s+src\s*=\s*["\']?\\AuntRuth\\cgi-bin\\counter\.pl[^>]*>'

    # Apply all patterns with case-insensitive matching
    cleaned_content = content
    for pattern in [pattern1, pattern2, pattern3, pattern4, pattern5, pattern6]:
        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)

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
                    if ('cgi-bin' in line and 'counter.pl' in line):
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
            new_content = remove_cgi_counter_patterns(original_content)

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

            processed_content = remove_cgi_counter_patterns(original_content)

            # Check if changes were made
            if processed_content != original_content:
                # Find what was removed
                original_lines = original_content.split('\n')
                processed_lines = processed_content.split('\n')

                for j, line in enumerate(original_lines):
                    if ('cgi-bin' in line and 'counter.pl' in line and
                        (j >= len(processed_lines) or line != processed_lines[j])):
                        print(f"  ✓ Would remove: {line.strip()}")
            else:
                print(f"  ⚠ No changes detected (unexpected)")

        except Exception as e:
            print(f"  ✗ Error testing {file_path}: {e}")

    return True

def select_test_urls(affected_files, target_dir):
    """Select representative test URLs for user validation"""
    test_urls = []

    # Get files from different subdirectories
    subdirs = {}
    for file_path in affected_files[:50]:  # Check first 50 for variety
        rel_path = os.path.relpath(file_path, target_dir)
        dirname = os.path.dirname(rel_path) if os.path.dirname(rel_path) != '.' else 'root'
        if dirname not in subdirs:
            subdirs[dirname] = []
        subdirs[dirname].append(file_path)

    # Select 1-2 files from each subdir, up to 10 total
    count = 0
    for dirname, files in list(subdirs.items())[:5]:  # Max 5 subdirs
        for file_path in files[:2]:  # Max 2 files per subdir
            if count >= 10:
                break

            rel_path = os.path.relpath(file_path, target_dir)
            filename = os.path.basename(file_path)

            if 'docs/htm' in target_dir:
                # Original site format
                url = f"http://localhost:8000/auntruth/htm/{rel_path}"
            else:  # docs/new
                # Modernized site format
                url = f"http://localhost:8000/auntruth/new/htm/{rel_path}"

            test_urls.append(url)
            count += 1

        if count >= 10:
            break

    return test_urls

def main():
    parser = argparse.ArgumentParser(description="Remove CGI counter script references for GitHub Pages compatibility")
    parser.add_argument('--target-dir', choices=['docs/htm', 'docs/new'],
                       help='Directory to process')
    parser.add_argument('--both', action='store_true',
                       help='Process both docs/htm and docs/new directories')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--test-sample', action='store_true',
                       help='Test on sample files first')

    args = parser.parse_args()

    # Determine target directories
    if args.both:
        target_dirs = ['docs/htm', 'docs/new']
    elif args.target_dir:
        target_dirs = [args.target_dir]
    else:
        print("Error: Must specify either --target-dir or --both")
        return 1

    print("=" * 60)
    print("CGI Counter Removal Script - remove-cgi-counters.py")
    print("=" * 60)
    print(f"Target directories: {', '.join(target_dirs)}")
    print(f"Dry run mode: {args.dry_run}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. Verify git branch
        current_branch = verify_git_branch()

        all_affected_files = []
        all_test_urls = []
        processing_summary = {}

        # Process each target directory
        for target_dir in target_dirs:
            print(f"\n{'='*40}")
            print(f"Processing: {target_dir}")
            print(f"{'='*40}")

            # 2. Verify target directory exists
            target_path = Path(target_dir)
            if not target_path.exists():
                raise ValueError(f"Target directory does not exist: {target_dir}")

            # 3. Find all affected files
            affected_files = find_affected_files(target_dir)

            if not affected_files:
                print(f"✓ No files found with CGI counter references in {target_dir}")
                processing_summary[target_dir] = {'files': 0, 'processed': 0}
                continue

            all_affected_files.extend(affected_files)

            # 4. Test on sample files if requested
            if args.test_sample and not args.dry_run:
                test_on_sample_files(affected_files)

                response = input(f"\nSample test complete for {target_dir}. Continue with processing? [y/N]: ")
                if response.lower() != 'y':
                    print("Processing cancelled by user.")
                    return 0

            # 5. Process files (dry-run or real)
            if args.dry_run:
                process_files_batch(affected_files, dry_run=True)
                processing_summary[target_dir] = {'files': len(affected_files), 'processed': 0}
            else:
                processed, errors = process_files_batch(affected_files, dry_run=False)
                processing_summary[target_dir] = {
                    'files': len(affected_files),
                    'processed': processed,
                    'errors': len(errors)
                }

            # 6. Select test URLs
            if not args.dry_run:
                test_urls = select_test_urls(affected_files, target_dir)
                all_test_urls.extend(test_urls)

        # Summary and test URLs
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")

        total_files = sum(info['files'] for info in processing_summary.values())
        total_processed = sum(info.get('processed', 0) for info in processing_summary.values())

        for target_dir, info in processing_summary.items():
            if args.dry_run:
                print(f"{target_dir}: {info['files']} files would be processed")
            else:
                print(f"{target_dir}: {info['processed']}/{info['files']} files processed")
                if 'errors' in info and info['errors'] > 0:
                    print(f"  ⚠ {info['errors']} errors encountered")

        print(f"\nTotal across all directories:")
        if args.dry_run:
            print(f"  {total_files} files would be processed")
        else:
            print(f"  {total_processed}/{total_files} files processed")

        # Display test URLs for user validation
        if not args.dry_run and all_test_urls:
            print(f"\n{'='*60}")
            print("REPRESENTATIVE TEST URLs FOR VALIDATION")
            print(f"{'='*60}")
            print("Please test these URLs to verify functionality is not broken:")
            print()

            for i, url in enumerate(all_test_urls, 1):
                print(f"{i:2d}. {url}")

            print(f"\n⚠ CRITICAL: Test these URLs before proceeding!")
            print("   Verify that pages load correctly and no functionality is broken.")
            print("   The CGI counter images should no longer appear.")

        if args.dry_run:
            print(f"\n✓ Dry run complete. Use without --dry-run to perform actual changes.")
        else:
            if total_processed > 0:
                print(f"\n✓ Processing complete! Ready for user validation.")
            else:
                print(f"\n✓ No files needed processing.")

        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())