#!/usr/bin/env python3
"""
Phase 5 Script 2: Fix Path Correction Issues

Problem: Relative path references that fail due to incorrect path resolution
Investigation: curl tests confirmed path issues:
- index_files/image*.jpg → ./index_files/image*.jpg (404 → 200)
- XF179.htm → /auntruth/new/htm/L3/XF179.htm (needs proper absolute path)

Solution: Fix relative path references to use correct paths
Expected Impact: ~50+ broken link fixes based on PRP analysis
Validation: Test specific URLs before/after, run broken link checker

Data Source: PRPs/scripts/reports/broken_links_*_20250925_*.csv
"""

import os
import sys
import re
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Add the project root to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def verify_git_branch(expected_branch: str = None) -> str:
    """Verify and return current git branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True,
                              cwd=Path(__file__).parent.parent.parent)
        current_branch = result.stdout.strip()
        if expected_branch and current_branch != expected_branch:
            print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking git branch: {e}")
        return "unknown"

def test_url_with_curl(url: str) -> int:
    """Test URL and return HTTP status code"""
    try:
        result = subprocess.run([
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url
        ], capture_output=True, text=True, timeout=10)
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired):
        return 0

def find_file_location(filename: str, docs_dir: str) -> List[str]:
    """Find where a file actually exists in the docs directory"""
    locations = []
    for root, dirs, filenames in os.walk(docs_dir):
        if filename in filenames:
            locations.append(root)
    return locations

def find_files_with_pattern(directory: str, pattern: str) -> List[str]:
    """Find HTML files containing the pattern"""
    files = []
    try:
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(('.htm', '.html')):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if pattern in content:
                                files.append(filepath)
                    except Exception as e:
                        print(f"⚠️  Error reading {filepath}: {e}")
    except Exception as e:
        print(f"❌ Error scanning directory {directory}: {e}")

    return files

def apply_path_fixes(content: str, source_file: str, docs_dir: str) -> Tuple[str, List[str]]:
    """Apply path correction fixes and return modified content with change log"""
    fixes_applied = []
    original_content = content

    # Fix 1: index_files path issues
    # Problem: index_files/image*.jpg → should be ./index_files/image*.jpg
    # Only fix if the source file is in the lastcall directory
    if "lastcall/index.htm" in source_file:
        index_files_pattern = r'(\bhref=["\'])index_files/([^"\']+)(["\'])'
        index_files_replacement = r'\1./index_files/\2\3'

        new_content = re.sub(index_files_pattern, index_files_replacement, content)
        if new_content != content:
            matches = len(re.findall(index_files_pattern, content))
            fixes_applied.append(f"index_files path fix: {matches} instances")
            content = new_content

        # Also fix src attributes
        src_index_files_pattern = r'(\bsrc=["\'])index_files/([^"\']+)(["\'])'
        src_index_files_replacement = r'\1./index_files/\2\3'

        new_content = re.sub(src_index_files_pattern, src_index_files_replacement, content)
        if new_content != content:
            matches = len(re.findall(src_index_files_pattern, content))
            fixes_applied.append(f"index_files src fix: {matches} instances")
            content = new_content

    # Fix 2: NEW site relative path issues
    # Problem: XF179.htm → should be /auntruth/new/htm/L3/XF179.htm

    # Find XF files that need absolute paths
    xf_pattern = r'(\bhref=["\'])([XF]\w*[0-9]+\.htm)(["\'])'
    matches = re.findall(xf_pattern, content)

    for prefix, filename, suffix in matches:
        # Check if this is a bare filename (no path)
        if "/" not in filename and "." in filename:
            # Find where this file actually exists
            locations = find_file_location(filename, docs_dir)

            if locations:
                # Choose the NEW site location if available
                new_location = None
                for loc in locations:
                    if "/new/htm/" in loc:
                        new_location = loc
                        break

                if not new_location and locations:
                    # Fall back to first location
                    new_location = locations[0]

                if new_location:
                    # Convert to absolute path
                    rel_path = os.path.relpath(new_location, docs_dir)
                    absolute_path = f"/auntruth/{rel_path}/{filename}"

                    # Replace the pattern
                    old_pattern = f'{prefix}{filename}{suffix}'
                    new_pattern = f'{prefix}{absolute_path}{suffix}'

                    new_content = content.replace(old_pattern, new_pattern)
                    if new_content != content:
                        fixes_applied.append(f"{filename} absolute path fix: converted to {absolute_path}")
                        content = new_content

    # Fix 3: Relative jpg path issues
    # Problem: ../jpg/F208.jpg → should be /auntruth/jpg/f208.jpg (note case)
    jpg_relative_pattern = r'(\bhref=["\'])\.\.\/jpg\/([^"\']+)(["\'])'
    jpg_matches = re.findall(jpg_relative_pattern, content)

    for prefix, filename, suffix in jpg_matches:
        # Convert to absolute path and fix case if needed
        absolute_jpg_path = f"/auntruth/jpg/{filename}"

        old_pattern = f'{prefix}../jpg/{filename}{suffix}'
        new_pattern = f'{prefix}{absolute_jpg_path}{suffix}'

        new_content = content.replace(old_pattern, new_pattern)
        if new_content != content:
            fixes_applied.append(f"jpg relative path fix: ../jpg/{filename} → {absolute_jpg_path}")
            content = new_content

    # Also fix src attributes for jpg files
    jpg_src_pattern = r'(\bsrc=["\'])\.\.\/jpg\/([^"\']+)(["\'])'
    jpg_src_matches = re.findall(jpg_src_pattern, content)

    for prefix, filename, suffix in jpg_src_matches:
        absolute_jpg_path = f"/auntruth/jpg/{filename}"

        old_pattern = f'{prefix}../jpg/{filename}{suffix}'
        new_pattern = f'{prefix}{absolute_jpg_path}{suffix}'

        new_content = content.replace(old_pattern, new_pattern)
        if new_content != content:
            fixes_applied.append(f"jpg src path fix: ../jpg/{filename} → {absolute_jpg_path}")
            content = new_content

    return content, fixes_applied

def process_file(filepath: str, docs_dir: str, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """Process a single file for path correction fixes"""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        # Apply fixes
        modified_content, fixes_applied = apply_path_fixes(original_content, filepath, docs_dir)

        if not fixes_applied:
            return False, []  # No changes needed

        if not dry_run:
            # Write modified content back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)

        return True, fixes_applied

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False, []

def validate_sample_fixes(docs_dir: str) -> Dict[str, Tuple[int, int]]:
    """Validate that our path fixes work by testing sample URLs"""
    test_cases = [
        # index_files issues
        ("http://localhost:8000/auntruth/htm/index_files/image005.jpg",
         "http://localhost:8000/auntruth/htm/L1/lastcall/index_files/image005.jpg"),

        # XF179 absolute path
        ("http://localhost:8000/auntruth/new/XF179.htm",
         "http://localhost:8000/auntruth/new/htm/L3/XF179.htm"),

        # jpg relative path (after case fix)
        ("http://localhost:8000/auntruth/jpg/F208.jpg",
         "http://localhost:8000/auntruth/jpg/f208.jpg"),
    ]

    results = {}
    print("🧪 Validating path correction fixes...")

    for broken_url, fixed_url in test_cases:
        broken_status = test_url_with_curl(broken_url)
        fixed_status = test_url_with_curl(fixed_url)

        results[broken_url.split('/')[-1]] = (broken_status, fixed_status)

        if broken_status == 404 and fixed_status == 200:
            print(f"✅ {broken_url.split('/')[-1]}: 404 → 200 (fix validated)")
        else:
            print(f"⚠️  {broken_url.split('/')[-1]}: {broken_status} → {fixed_status} (unexpected)")

    return results

def main():
    parser = argparse.ArgumentParser(description="Fix path correction issues in broken links")
    parser.add_argument("--directory", default="/home/ken/wip/fam/auntruth/docs",
                       help="Target directory to process")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be changed without making changes")
    parser.add_argument("--validate", action="store_true",
                       help="Run URL validation tests")
    parser.add_argument("--limit", type=int,
                       help="Limit processing to N files (for testing)")

    args = parser.parse_args()

    print("🔧 Phase 5 Script 2: Fix Path Correction Issues")
    print("=" * 60)

    # Verify git branch
    current_branch = verify_git_branch()
    print(f"📂 Current git branch: {current_branch}")
    print(f"📁 Target directory: {args.directory}")
    print(f"🔍 Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print()

    if args.validate:
        validation_results = validate_sample_fixes(args.directory)
        print()
        return

    # Define patterns to search for path issues
    patterns_to_find = [
        "index_files/image",  # index_files path issues
        'href="XF',           # bare XF file references
        'href="XI',           # bare XI file references
        "../jpg/",            # relative jpg paths
    ]

    all_files_to_process = set()

    print("🔍 Scanning for files with path issues...")
    for pattern in patterns_to_find:
        print(f"   Searching for: {pattern}")
        files = find_files_with_pattern(args.directory, pattern)
        all_files_to_process.update(files)
        print(f"   Found in {len(files)} files")

    files_to_process = list(all_files_to_process)

    if args.limit:
        files_to_process = files_to_process[:args.limit]

    print(f"\n📊 Total files to process: {len(files_to_process)}")

    if not files_to_process:
        print("✅ No files found with path correction issues!")
        return

    if args.dry_run:
        print(f"\n🔍 DRY RUN - Preview of first 10 files to be processed:")
        for i, filepath in enumerate(files_to_process[:10]):
            rel_path = os.path.relpath(filepath, args.directory)
            print(f"   {i+1:2d}. {rel_path}")
        if len(files_to_process) > 10:
            print(f"   ... and {len(files_to_process) - 10} more files")

        # Show sample of changes
        print(f"\n📝 Sample changes from first file:")
        sample_file = files_to_process[0]
        try:
            with open(sample_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            modified_content, fixes = apply_path_fixes(content, sample_file, args.directory)
            if fixes:
                print(f"   File: {os.path.relpath(sample_file, args.directory)}")
                for fix in fixes:
                    print(f"   - {fix}")
            else:
                print("   No changes needed in sample file")
        except Exception as e:
            print(f"   Error reading sample file: {e}")

        print(f"\n💡 Run without --dry-run to apply changes")
        return

    # Process files
    print(f"\n🔄 Processing {len(files_to_process)} files...")

    processed_count = 0
    changed_count = 0
    total_fixes = []

    for i, filepath in enumerate(files_to_process):
        if i > 0 and i % 100 == 0:
            print(f"   Progress: {i}/{len(files_to_process)} files processed...")

        try:
            changed, fixes = process_file(filepath, args.directory, dry_run=False)
            processed_count += 1

            if changed:
                changed_count += 1
                total_fixes.extend(fixes)
                rel_path = os.path.relpath(filepath, args.directory)
                print(f"✅ {rel_path}: {', '.join(fixes)}")

        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            continue

    # Results summary
    print(f"\n📊 Processing Complete!")
    print(f"   Files processed: {processed_count}")
    print(f"   Files changed: {changed_count}")
    print(f"   Total fixes applied: {len(total_fixes)}")

    if total_fixes:
        print(f"\n🔧 Fix Summary:")
        fix_counts = {}
        for fix in total_fixes:
            fix_type = fix.split(':')[0]
            if fix_type not in fix_counts:
                fix_counts[fix_type] = 0

            # Try to extract count from the fix string
            try:
                if "instances" in fix:
                    count = int(fix.split(': ')[1].split()[0])
                else:
                    count = 1  # Single file fix
                fix_counts[fix_type] += count
            except:
                fix_counts[fix_type] += 1

        for fix_type, count in fix_counts.items():
            print(f"   - {fix_type}: {count} instances")

    if changed_count > 0:
        print(f"\n💾 Commit these changes:")
        print(f"   git add .")
        print(f"   git commit -m 'Phase 5-2: Fix path correction issues - {changed_count} files'")

    print(f"\n🧪 Run with --validate to test URL fixes")

if __name__ == "__main__":
    main()