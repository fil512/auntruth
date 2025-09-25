#!/usr/bin/env python3
"""
Phase 5 Script 1: Fix Case Sensitivity Issues

Problem: References to files with wrong case fail due to case-sensitive servers
Investigation: curl tests confirmed files exist with different capitalization:
- hh1.htm → HH1.htm (404 → 200)
- pringcem.htm → PRINGCEM.htm
- lathbook.htm → LATHBOOK.htm
- F208.jpg → f208.jpg
- F404.jpg → f404.jpg

Solution: Convert incorrect case references to actual file case
Expected Impact: ~40+ broken link fixes based on PRP analysis
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

def apply_case_fixes(content: str) -> Tuple[str, List[str]]:
    """Apply case sensitivity fixes and return modified content with change log"""
    fixes_applied = []
    original_content = content

    # HTML file case fixes
    html_case_fixes = [
        # Fix hh1.htm → HH1.htm
        (r'(\bhref=["\'])([^"\']*/)hh1\.htm(["\'])', r'\1\2HH1.htm\3'),
        (r'(\bsrc=["\'])([^"\']*/)hh1\.htm(["\'])', r'\1\2HH1.htm\3'),

        # Fix pringcem.htm → PRINGCEM.htm
        (r'(\bhref=["\'])([^"\']*/)pringcem\.htm(["\'])', r'\1\2PRINGCEM.htm\3'),
        (r'(\bsrc=["\'])([^"\']*/)pringcem\.htm(["\'])', r'\1\2PRINGCEM.htm\3'),

        # Fix lathbook.htm → LATHBOOK.htm
        (r'(\bhref=["\'])([^"\']*/)lathbook\.htm(["\'])', r'\1\2LATHBOOK.htm\3'),
        (r'(\bsrc=["\'])([^"\']*/)lathbook\.htm(["\'])', r'\1\2LATHBOOK.htm\3'),
    ]

    # Image file case fixes
    image_case_fixes = [
        # Fix F208.jpg → f208.jpg
        (r'(\bhref=["\'])([^"\']*/)F208\.jpg(["\'])', r'\1\2f208.jpg\3'),
        (r'(\bsrc=["\'])([^"\']*/)F208\.jpg(["\'])', r'\1\2f208.jpg\3'),

        # Fix F404.jpg → f404.jpg
        (r'(\bhref=["\'])([^"\']*/)F404\.jpg(["\'])', r'\1\2f404.jpg\3'),
        (r'(\bsrc=["\'])([^"\']*/)F404\.jpg(["\'])', r'\1\2f404.jpg\3'),
    ]

    all_fixes = html_case_fixes + image_case_fixes

    for pattern, replacement in all_fixes:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            # Count how many matches were replaced
            matches = len(re.findall(pattern, content))
            fix_name = pattern.split('/')[-1].split(r'\.')[0]  # Extract filename part
            fixes_applied.append(f"{fix_name} case fix: {matches} instances")
            content = new_content

    return content, fixes_applied

def process_file(filepath: str, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """Process a single file for case sensitivity fixes"""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        # Apply fixes
        modified_content, fixes_applied = apply_case_fixes(original_content)

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

def validate_sample_fixes() -> Dict[str, Tuple[int, int]]:
    """Validate that our fixes work by testing sample URLs"""
    test_cases = [
        # (broken_url, fixed_url)
        ("http://localhost:8000/auntruth/htm/L1/hh1.htm",
         "http://localhost:8000/auntruth/htm/L1/HH1.htm"),
        ("http://localhost:8000/auntruth/htm/L3/pringcem.htm",
         "http://localhost:8000/auntruth/htm/L3/PRINGCEM.htm"),
        ("http://localhost:8000/auntruth/htm/L4/lathbook.htm",
         "http://localhost:8000/auntruth/htm/L4/LATHBOOK.htm"),
        ("http://localhost:8000/auntruth/jpg/F208.jpg",
         "http://localhost:8000/auntruth/jpg/f208.jpg"),
        ("http://localhost:8000/auntruth/jpg/F404.jpg",
         "http://localhost:8000/auntruth/jpg/f404.jpg"),
    ]

    results = {}
    print("🧪 Validating case sensitivity fixes...")

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
    parser = argparse.ArgumentParser(description="Fix case sensitivity issues in broken links")
    parser.add_argument("--directory", default="/home/ken/wip/fam/auntruth/docs",
                       help="Target directory to process")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be changed without making changes")
    parser.add_argument("--validate", action="store_true",
                       help="Run URL validation tests")
    parser.add_argument("--limit", type=int,
                       help="Limit processing to N files (for testing)")

    args = parser.parse_args()

    print("🔧 Phase 5 Script 1: Fix Case Sensitivity Issues")
    print("=" * 60)

    # Verify git branch
    current_branch = verify_git_branch()
    print(f"📂 Current git branch: {current_branch}")
    print(f"📁 Target directory: {args.directory}")
    print(f"🔍 Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print()

    if args.validate:
        validation_results = validate_sample_fixes()
        print()
        return

    # Define case-sensitive patterns to search for
    patterns_to_find = [
        "hh1.htm", "pringcem.htm", "lathbook.htm",
        "F208.jpg", "F404.jpg"
    ]

    all_files_to_process = set()

    print("🔍 Scanning for files with case sensitivity issues...")
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
        print("✅ No files found with case sensitivity issues!")
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
            modified_content, fixes = apply_case_fixes(content)
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
            changed, fixes = process_file(filepath, dry_run=False)
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
            fix_counts[fix_type] += int(fix.split(':')[1].split()[0])

        for fix_type, count in fix_counts.items():
            print(f"   - {fix_type}: {count} instances")

    if changed_count > 0:
        print(f"\n💾 Commit these changes:")
        print(f"   git add .")
        print(f"   git commit -m 'Phase 5-1: Fix case sensitivity issues - {changed_count} files'")

    print(f"\n🧪 Run with --validate to test URL fixes")

if __name__ == "__main__":
    main()