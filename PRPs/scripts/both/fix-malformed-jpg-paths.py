#!/usr/bin/env python3
"""
Fix Malformed JPG Paths with Spaces - Script 019

Problem: Links to JPG files have malformed paths with spaces like "/auntruth/jpg/ .jpg" or "/auntruth/jpg/ sn206.jpg"
Investigation: Analysis showed 10 broken links with malformed JPG paths containing spaces
Solution: Fix malformed JPG path references by removing/fixing the problematic space patterns
Expected Impact: Fix 10 broken link references (low priority but systematic cleanup)

This addresses paths like:
  /auntruth/jpg/ .jpg → (likely malformed, needs investigation)
  /auntruth/jpg/ sn206.jpg → /auntruth/jpg/sn206.jpg
"""

import os
import re
import sys
import glob
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict


def verify_git_branch(expected_branch: str = "main") -> str:
    """Verify we're on the expected git branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking git branch: {e}")
        return "unknown"


def find_files_with_malformed_jpg_paths(base_dirs: List[str] = None) -> Dict[str, List[str]]:
    """Find files containing malformed JPG path references"""
    if base_dirs is None:
        base_dirs = ["docs/htm", "docs/new"]

    files_with_issues = {}

    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            print(f"⚠️  Directory not found: {base_dir}")
            continue

        print(f"🔍 Scanning {base_dir} for malformed JPG path issues...")

        pattern = os.path.join(base_dir, "**/*.htm")
        files = glob.glob(pattern, recursive=True)

        # Filter out backup files
        files = [f for f in files if not any(f.endswith(ext) for ext in ['.backup', '.bak', '.orig'])]

        found_files = []

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Look for malformed JPG paths with spaces
                malformed_patterns = [
                    r'/auntruth/jpg/\s+[^"\'>\s]*\.jpg',  # Space after jpg/
                    r'/auntruth/jpg/\s+\.jpg',           # Space + .jpg only
                ]

                found_patterns = []
                for pattern in malformed_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    found_patterns.extend(matches)

                if found_patterns:
                    found_files.append(file_path)
                    print(f"  📄 Found malformed JPG paths in: {file_path}")

                    # Show examples
                    for match in found_patterns[:3]:  # Show first 3 matches
                        print(f"    Example: {match}")
                    if len(found_patterns) > 3:
                        print(f"    ... and {len(found_patterns) - 3} more")

            except Exception as e:
                print(f"  ❌ Error reading {file_path}: {e}")

        files_with_issues[base_dir] = found_files
        print(f"📊 Found {len(found_files)} files with malformed JPG issues in {base_dir}")

    return files_with_issues


def process_file(file_path: str, dry_run: bool = True) -> Dict[str, int]:
    """Process a single file to fix malformed JPG path issues"""
    stats = {"lines_processed": 0, "lines_modified": 0, "patterns_found": 0, "fixes_applied": 0}

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        modified_content = content

        # Fix patterns for malformed JPG paths
        fixes_applied = 0

        # Pattern 1: Fix "/auntruth/jpg/ filename.jpg" → "/auntruth/jpg/filename.jpg"
        pattern1 = r'(/auntruth/jpg/)\s+([^"\'>\s]+\.jpg)'
        replacement1 = r'\1\2'

        matches1 = list(re.finditer(pattern1, content, re.IGNORECASE))
        if matches1:
            modified_content = re.sub(pattern1, replacement1, modified_content, flags=re.IGNORECASE)
            fixes_applied += len(matches1)

            print(f"    Pattern 1 - Remove space after /jpg/: {len(matches1)} matches")
            for i, match in enumerate(matches1, 1):
                original = match.group(0)
                fixed = re.sub(pattern1, replacement1, original, flags=re.IGNORECASE)
                print(f"      {i}. {original}")
                print(f"         → {fixed}")

        # Pattern 2: Fix "/auntruth/jpg/ .jpg" → remove entirely or fix based on context
        pattern2 = r'["\']([^"\']*)/auntruth/jpg/\s+\.jpg["\']'
        matches2 = list(re.finditer(pattern2, content, re.IGNORECASE))

        if matches2:
            print(f"    Pattern 2 - Malformed .jpg only: {len(matches2)} matches")
            print("    ⚠️  These may need manual review - they appear to be corrupted paths:")
            for i, match in enumerate(matches2, 1):
                print(f"      {i}. {match.group(0)}")
                print(f"         → [REQUIRES MANUAL REVIEW - may be corrupted]")

            # Don't automatically fix these - they need manual review
            print("    ⚠️  Skipping automatic fix for ' .jpg' patterns - manual review needed")

        # Pattern 3: General cleanup of multiple spaces in JPG paths
        pattern3 = r'(/auntruth/jpg/)\s{2,}([^"\'>\s]+\.jpg)'
        replacement3 = r'\1\2'

        matches3 = list(re.finditer(pattern3, modified_content, re.IGNORECASE))
        if matches3:
            modified_content = re.sub(pattern3, replacement3, modified_content, flags=re.IGNORECASE)
            fixes_applied += len(matches3)

            print(f"    Pattern 3 - Multiple spaces cleanup: {len(matches3)} matches")
            for i, match in enumerate(matches3, 1):
                original = match.group(0)
                fixed = re.sub(pattern3, replacement3, original, flags=re.IGNORECASE)
                print(f"      {i}. {original}")
                print(f"         → {fixed}")

        total_patterns = len(matches1) + len(matches2) + len(matches3)
        stats["patterns_found"] = total_patterns
        stats["fixes_applied"] = fixes_applied

        if modified_content != original_content:
            stats["lines_modified"] = 1

            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print(f"  ✅ Modified {file_path}")
            else:
                print(f"  [DRY RUN] Would modify {file_path}")

        stats["lines_processed"] = content.count('\n') + 1

    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")

    return stats


def main():
    parser = argparse.ArgumentParser(description='Fix malformed JPG paths with spaces')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--base-dirs', nargs='+', default=['docs/htm', 'docs/new'],
                       help='Base directories to process (default: docs/htm docs/new)')

    args = parser.parse_args()

    print("🔧 Fix Malformed JPG Paths with Spaces - Script 019")
    print("=" * 70)

    # Check git branch
    current_branch = verify_git_branch("main")
    print(f"📝 Current git branch: {current_branch}")

    # Find files with malformed JPG issues
    files_with_issues = find_files_with_malformed_jpg_paths(args.base_dirs)

    all_files_to_process = []
    for base_dir, files in files_with_issues.items():
        all_files_to_process.extend(files)

    if not all_files_to_process:
        print("✅ No files found with malformed JPG path issues")
        print("🎉 This issue may already be resolved!")
        sys.exit(0)

    print(f"\n📋 Total files to process: {len(all_files_to_process)}")

    # Process files
    total_stats = {"files_processed": 0, "files_modified": 0, "patterns_found": 0, "fixes_applied": 0}

    print(f"\n🚀 Processing {len(all_files_to_process)} files...")
    if args.dry_run:
        print("📋 DRY RUN MODE - No files will be modified")

    for i, file_path in enumerate(all_files_to_process, 1):
        print(f"\n[{i}/{len(all_files_to_process)}] Processing: {file_path}")

        file_stats = process_file(file_path, dry_run=args.dry_run)

        total_stats["files_processed"] += 1
        total_stats["patterns_found"] += file_stats["patterns_found"]
        total_stats["fixes_applied"] += file_stats["fixes_applied"]

        if file_stats["patterns_found"] > 0:
            total_stats["files_modified"] += 1

    # Print summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Files processed: {total_stats['files_processed']}")
    print(f"Files modified: {total_stats['files_modified']}")
    print(f"Malformed JPG patterns found: {total_stats['patterns_found']}")
    print(f"Automatic fixes applied: {total_stats['fixes_applied']}")
    print(f"Manual review cases: {total_stats['patterns_found'] - total_stats['fixes_applied']}")

    if args.dry_run:
        print(f"\n💡 This was a dry run. Use without --dry-run to apply changes.")
        print(f"💡 Expected impact: Fix {total_stats['fixes_applied']} malformed JPG path references")
        print(f"💡 Manual review needed for {total_stats['patterns_found'] - total_stats['fixes_applied']} cases")
    else:
        print(f"\n✅ Changes applied successfully!")
        print(f"🎯 Fixed {total_stats['fixes_applied']} malformed JPG path issues")

        if total_stats["files_modified"] > 0:
            print(f"\n📝 Next steps:")
            print(f"  1. Review any patterns that required manual attention")
            print(f"  2. Test fixed URLs manually if needed")
            print(f"  3. Run broken link checker to measure improvement")
            print(f"  4. Commit changes if results are satisfactory")

    print(f"\n🎯 Expected improvement: Up to 10 broken links → working links")

    if total_stats['patterns_found'] - total_stats['fixes_applied'] > 0:
        print(f"\n⚠️  IMPORTANT: Some patterns require manual review")
        print(f"   Paths like '/auntruth/jpg/ .jpg' may be corrupted and need manual investigation")


if __name__ == '__main__':
    main()