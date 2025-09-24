#!/usr/bin/env python3
"""
Fix Missing /auntruth/ Prefix in Links - Script 024

Problem: Links use /htm/L0/file.htm but get resolved as /htm/htm/L0/file.htm (404)
Investigation: curl tests showed /htm/htm/L0/XI1029.htm → 404, /htm/L0/XI1029.htm → 404, /auntruth/htm/L0/XI1029.htm → 200
Solution: Change /htm/ to /auntruth/htm/ in href attributes
Expected Impact: Fix double htm path issues (dozens of broken links)
Validation: Test specific URLs before/after, run broken link checker

Based on analysis showing links like:
- Source: href="/htm/L0/XI1029.htm"
- Resolves to: http://localhost:8000/auntruth/htm/htm/L0/XI1029.htm (404)
- Should be: http://localhost:8000/auntruth/htm/L0/XI1029.htm (200)
"""

import os
import re
import subprocess
import sys
from typing import List, Tuple

def verify_git_branch(expected_branch: str) -> str:
    """Verify we're on the expected git branch."""
    result = subprocess.run(["git", "branch", "--show-current"],
                          capture_output=True, text=True, check=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
    return current_branch

def find_missing_auntruth_prefix(directory: str) -> List[Tuple[str, List[str]]]:
    """Find files with /htm/ links that need /auntruth/ prefix."""
    files_with_problems = []

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if not filename.endswith(('.htm', '.html')):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Look for href="/htm/..." patterns (missing /auntruth/)
                problem_patterns = []

                # Pattern 1: href="/htm/L0/file.htm" (most common)
                pattern1 = r'href=["\'](/htm/L[0-9]+/[^"\']+)["\']'
                matches = re.findall(pattern1, content, re.IGNORECASE)
                for match in matches:
                    problem_patterns.append(('href="' + match + '"', 'href="/auntruth' + match + '"'))

                # Pattern 2: src="/htm/..." for images/scripts
                pattern2 = r'src=["\'](/htm/[^"\']+)["\']'
                matches = re.findall(pattern2, content, re.IGNORECASE)
                for match in matches:
                    problem_patterns.append(('src="' + match + '"', 'src="/auntruth' + match + '"'))

                # Pattern 3: Other attributes that might contain /htm/ paths
                pattern3 = r'(action|data-[a-z-]+)=["\'](/htm/[^"\']+)["\']'
                matches = re.findall(pattern3, content, re.IGNORECASE)
                for attr, path in matches:
                    problem_patterns.append((f'{attr}="{path}"', f'{attr}="/auntruth{path}"'))

                if problem_patterns:
                    files_with_problems.append((filepath, problem_patterns))

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    return files_with_problems

def test_sample_fixes(sample_patterns: List[Tuple[str, str]]) -> None:
    """Test a few sample URL fixes with curl."""
    print("\n🧪 Testing sample URL fixes...")

    for i, (old_pattern, new_pattern) in enumerate(sample_patterns[:3]):
        # Extract the path from href patterns
        old_match = re.search(r'"/([^"]+)"', old_pattern)
        new_match = re.search(r'"/([^"]+)"', new_pattern)

        if old_match and new_match:
            old_url = f"http://localhost:8000/{old_match.group(1)}"
            new_url = f"http://localhost:8000/{new_match.group(1)}"

            print(f"  Test {i+1}:")
            print(f"    Old: {old_url}")
            print(f"    New: {new_url}")

            # Test URLs
            try:
                import urllib.request

                # Test old URL (should be 404)
                try:
                    response = urllib.request.urlopen(old_url)
                    old_status = response.getcode()
                except:
                    old_status = 404

                # Test new URL (should be 200)
                try:
                    response = urllib.request.urlopen(new_url)
                    new_status = response.getcode()
                except:
                    new_status = 404

                status_icon = "✅" if (old_status == 404 and new_status == 200) else "❌"
                print(f"    {status_icon} {old_status} → {new_status}")

            except Exception as e:
                print(f"    ❌ Error testing: {e}")

def fix_missing_auntruth_prefix(files_with_problems: List[Tuple[str, List[Tuple[str, str]]]], dry_run: bool = True) -> int:
    """Fix missing /auntruth/ prefix in links."""
    fixes_made = 0

    for filepath, pattern_fixes in files_with_problems:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content
            file_fixes = 0

            # Apply all pattern fixes for this file
            for old_pattern, new_pattern in pattern_fixes:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    file_fixes += 1

            if content != original_content and file_fixes > 0:
                if not dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)

                fixes_made += file_fixes
                rel_path = os.path.relpath(filepath)
                print(f"{'[DRY RUN] ' if dry_run else ''}Fixed {file_fixes} missing /auntruth/ prefixes in {rel_path}")

                # Show first few fixes
                for old_pattern, new_pattern in pattern_fixes[:3]:
                    print(f"  {old_pattern} → {new_pattern}")

                if len(pattern_fixes) > 3:
                    print(f"  ... and {len(pattern_fixes) - 3} more")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    return fixes_made

def main():
    # Verify we're in the right place
    if not os.path.exists('docs/htm') or not os.path.exists('docs/new'):
        print("Error: Must run from repository root (docs/htm and docs/new should exist)")
        sys.exit(1)

    # Verify git branch
    current_branch = verify_git_branch("fix-broken-links-fix-absolute-htm-paths")

    # Parse arguments
    dry_run = '--no-dry-run' not in sys.argv

    print("🔍 Scanning for missing /auntruth/ prefixes...")

    all_problems = []
    search_dirs = ['docs/htm', 'docs/new']

    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            problems = find_missing_auntruth_prefix(search_dir)
            all_problems.extend(problems)
            print(f"Found {len(problems)} files with missing /auntruth/ prefixes in {search_dir}")

    if not all_problems:
        print("✅ No missing /auntruth/ prefix issues found!")
        return

    # Count total problematic patterns
    total_problems = sum(len(patterns) for _, patterns in all_problems)
    print(f"\n📊 Total files with problems: {len(all_problems)}")
    print(f"📊 Total problematic patterns: {total_problems}")

    # Show examples
    print("\n🔍 Sample problems:")
    all_patterns = []
    for i, (filepath, patterns) in enumerate(all_problems[:3]):
        rel_path = os.path.relpath(filepath)
        print(f"  {i+1}. {rel_path}")
        for old_pattern, new_pattern in patterns[:2]:
            print(f"     {old_pattern} → {new_pattern}")
            all_patterns.append((old_pattern, new_pattern))
        if len(patterns) > 2:
            print(f"     ... and {len(patterns) - 2} more in this file")

    if len(all_problems) > 3:
        print(f"     ... and {len(all_problems) - 3} more files")

    # Test a few sample fixes
    if all_patterns:
        test_sample_fixes(all_patterns)

    print(f"\n🔧 {'Simulating fixes...' if dry_run else 'Applying fixes...'}")
    fixes_made = fix_missing_auntruth_prefix(all_problems, dry_run)

    if dry_run:
        print(f"\n✅ Dry run complete. Would fix {fixes_made} missing /auntruth/ prefixes.")
        print("Run with --no-dry-run to apply changes.")
    else:
        print(f"\n✅ Fixed {fixes_made} missing /auntruth/ prefix issues!")
        print("🔍 Re-run broken link checker to measure improvement.")

if __name__ == "__main__":
    main()