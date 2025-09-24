#!/usr/bin/env python3
"""
Fix Double HTM Path Issues - Script 022

Problem: Links contain double htm paths like /htm/htm/L0/ instead of /htm/L0/
Investigation: curl tests showed /htm/htm/L0/XI1029.htm → 404, /htm/L0/XI1029.htm → 200
Solution: Remove redundant /htm/ from paths containing /htm/htm/
Expected Impact: Many broken link fixes based on pattern analysis
Validation: Test specific URLs before/after, run broken link checker

Based on analysis showing:
- /auntruth/htm/htm/L0/XI1029.htm (404)
- /auntruth/htm/L0/XI1029.htm (200)
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

def find_double_htm_paths(directory: str) -> List[Tuple[str, List[str]]]:
    """Find files containing double htm paths."""
    files_with_problems = []

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if not filename.endswith(('.htm', '.html')):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Look for double htm paths in various contexts
                patterns = [
                    r'href=["\']([^"\']*)/htm/htm/([^"\']*)["\']',  # href="/auntruth/htm/htm/L0/file.htm"
                    r'src=["\']([^"\']*)/htm/htm/([^"\']*)["\']',   # src="/auntruth/htm/htm/..."
                    r'url\(["\']?([^"\'()]*)/htm/htm/([^"\'()]*)["\']?\)',  # CSS url()
                ]

                found_patterns = []
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            # Reconstruct the full problematic path
                            full_path = match[0] + '/htm/htm/' + match[1]
                            found_patterns.append(full_path)

                # Also look for standalone /htm/htm/ patterns
                htm_htm_pattern = r'/htm/htm/[^"\'\s<>]+'
                htm_matches = re.findall(htm_htm_pattern, content, re.IGNORECASE)
                found_patterns.extend(htm_matches)

                if found_patterns:
                    files_with_problems.append((filepath, found_patterns))

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    return files_with_problems

def fix_double_htm_paths(files_with_problems: List[Tuple[str, List[str]]], dry_run: bool = True) -> int:
    """Fix double htm paths by removing the redundant /htm/."""
    fixes_made = 0

    for filepath, problematic_paths in files_with_problems:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content
            file_fixes = 0

            # Fix each problematic path
            for problem_path in problematic_paths:
                # Convert /htm/htm/ to /htm/
                fixed_path = problem_path.replace('/htm/htm/', '/htm/')

                # Be careful with replacement - use word boundaries and escape special chars
                escaped_problem = re.escape(problem_path)
                content = re.sub(escaped_problem, fixed_path, content)

                if problem_path in original_content:
                    file_fixes += 1

            if content != original_content and file_fixes > 0:
                if not dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)

                fixes_made += file_fixes
                rel_path = os.path.relpath(filepath)
                print(f"{'[DRY RUN] ' if dry_run else ''}Fixed {file_fixes} double htm paths in {rel_path}")

                # Show what was fixed
                for problem_path in problematic_paths[:3]:  # Show first few
                    fixed_path = problem_path.replace('/htm/htm/', '/htm/')
                    print(f"  {problem_path} → {fixed_path}")

                if len(problematic_paths) > 3:
                    print(f"  ... and {len(problematic_paths) - 3} more")

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

    print("🔍 Scanning for double htm path issues...")

    all_problems = []
    search_dirs = ['docs/htm', 'docs/new']

    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            problems = find_double_htm_paths(search_dir)
            all_problems.extend(problems)
            print(f"Found {len(problems)} files with double htm paths in {search_dir}")

    if not all_problems:
        print("✅ No double htm path issues found!")
        return

    # Count total problematic paths
    total_problems = sum(len(paths) for _, paths in all_problems)
    print(f"\n📊 Total files with problems: {len(all_problems)}")
    print(f"📊 Total problematic paths: {total_problems}")

    # Show examples
    print("\n🔍 Sample problems:")
    for i, (filepath, paths) in enumerate(all_problems[:3]):
        rel_path = os.path.relpath(filepath)
        print(f"  {i+1}. {rel_path}")
        for path in paths[:2]:
            fixed = path.replace('/htm/htm/', '/htm/')
            print(f"     {path} → {fixed}")
        if len(paths) > 2:
            print(f"     ... and {len(paths) - 2} more in this file")

    if len(all_problems) > 3:
        print(f"     ... and {len(all_problems) - 3} more files")

    print(f"\n🔧 {'Simulating fixes...' if dry_run else 'Applying fixes...'}")
    fixes_made = fix_double_htm_paths(all_problems, dry_run)

    if dry_run:
        print(f"\n✅ Dry run complete. Would fix {fixes_made} double htm paths.")
        print("Run with --no-dry-run to apply changes.")
    else:
        print(f"\n✅ Fixed {fixes_made} double htm path issues!")
        print("🔍 Re-run broken link checker to measure improvement.")

if __name__ == "__main__":
    main()