#!/usr/bin/env python3
"""
Fix Wrong Lineage Directory References - Script 021

Problem: Files like XF533.htm are referenced in wrong lineage directories
Investigation: curl tests showed XF533.htm is in L9/ but links point to L1/ (111 instances)
Solution: Find actual file locations and correct directory references
Expected Impact: ~131+ broken link fixes (111 in HTM, 20+ in NEW)
Validation: Test specific URLs before/after, run broken link checker

Based on analysis of broken link reports showing:
- http://localhost:8000/auntruth/htm/L1/XF533.htm (404 - 111 instances)
- Actual file is at: http://localhost:8000/auntruth/htm/L9/XF533.htm (200)
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

def verify_git_branch(expected_branch: str) -> str:
    """Verify we're on the expected git branch."""
    result = subprocess.run(["git", "branch", "--show-current"],
                          capture_output=True, text=True, check=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
    return current_branch

def find_actual_file_location(filename: str, search_dirs: List[str]) -> str:
    """Find the actual location of a file in the directory structure."""
    for search_dir in search_dirs:
        for root, dirs, files in os.walk(search_dir):
            if filename in files:
                # Convert absolute path to relative URL path
                rel_path = os.path.relpath(os.path.join(root, filename), 'docs')
                return '/' + rel_path.replace(os.path.sep, '/')
    return None

def build_file_location_map(search_dirs: List[str]) -> Dict[str, str]:
    """Build a map of filename to correct path for all files."""
    file_map = {}

    for search_dir in search_dirs:
        for root, dirs, files in os.walk(search_dir):
            for filename in files:
                if filename.endswith('.htm'):
                    # Convert to URL path relative to /auntruth/
                    rel_path = os.path.relpath(os.path.join(root, filename), 'docs')
                    url_path = '/auntruth/' + rel_path.replace(os.path.sep, '/')
                    file_map[filename] = url_path

    return file_map

def find_problematic_references(directory: str, file_map: Dict[str, str]) -> List[Tuple[str, str, str, str]]:
    """Find files with references to wrong lineage directories."""
    problems = []

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if not filename.endswith(('.htm', '.html')):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Look for href links to files that exist but in wrong directory
                href_pattern = r'href=["\']([^"\']+\.htm)["\']'
                matches = re.findall(href_pattern, content, re.IGNORECASE)

                for href in matches:
                    # Extract just the filename from the href
                    if '/' in href:
                        ref_filename = href.split('/')[-1]
                    else:
                        ref_filename = href

                    # Check if this file exists but the reference points to wrong location
                    if ref_filename in file_map:
                        correct_path = file_map[ref_filename]
                        # Convert href to full URL path for comparison
                        if href.startswith('/auntruth/'):
                            current_full_path = href
                        elif href.startswith('../'):
                            # Handle relative paths
                            continue  # Skip for now, focus on absolute paths
                        else:
                            # Relative path within same directory
                            dir_path = os.path.dirname(os.path.relpath(filepath, 'docs'))
                            current_full_path = '/auntruth/' + dir_path.replace(os.path.sep, '/') + '/' + href

                        if current_full_path != correct_path:
                            problems.append((filepath, href, current_full_path, correct_path))

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    return problems

def fix_wrong_references(problems: List[Tuple[str, str, str, str]], dry_run: bool = True) -> int:
    """Fix the wrong directory references."""
    fixes_made = 0

    # Group by file to make batch edits
    files_to_fix = {}
    for filepath, old_href, old_full_path, correct_path in problems:
        if filepath not in files_to_fix:
            files_to_fix[filepath] = []

        # Calculate the correct href from the correct full path
        correct_href = correct_path.replace('/auntruth/', '')
        if not correct_href.startswith('/'):
            correct_href = '/' + correct_href

        files_to_fix[filepath].append((old_href, correct_href))

    for filepath, replacements in files_to_fix.items():
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content

            # Apply all replacements for this file
            for old_href, new_href in replacements:
                # Be very specific with the replacement to avoid false matches
                old_pattern = f'href=["\']' + re.escape(old_href) + '["\']'
                new_replacement = f'href="{new_href}"'

                content = re.sub(old_pattern, new_replacement, content, flags=re.IGNORECASE)

            if content != original_content:
                if not dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)

                fixes_made += len(replacements)
                rel_path = os.path.relpath(filepath)
                print(f"{'[DRY RUN] ' if dry_run else ''}Fixed {len(replacements)} references in {rel_path}")

                for old_href, new_href in replacements:
                    print(f"  {old_href} → {new_href}")

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
    dry_run = '--dry-run' not in sys.argv
    if '--dry-run' in sys.argv:
        dry_run = True

    print("🔍 Building file location map...")
    search_dirs = ['docs/htm', 'docs/new']
    file_map = build_file_location_map(search_dirs)
    print(f"📁 Mapped {len(file_map)} .htm files")

    print("\n🔍 Finding problematic references...")
    all_problems = []

    for search_dir in search_dirs:
        problems = find_problematic_references(search_dir, file_map)
        all_problems.extend(problems)
        print(f"Found {len(problems)} problematic references in {search_dir}")

    if not all_problems:
        print("✅ No wrong directory references found!")
        return

    print(f"\n📊 Total problematic references found: {len(all_problems)}")

    # Show a few examples
    print("\n🔍 Sample problems:")
    for i, (filepath, old_href, old_path, correct_path) in enumerate(all_problems[:5]):
        rel_path = os.path.relpath(filepath)
        print(f"  {i+1}. {rel_path}")
        print(f"     Current: {old_href} → {old_path}")
        print(f"     Correct: → {correct_path}")

    if len(all_problems) > 5:
        print(f"     ... and {len(all_problems) - 5} more")

    print(f"\n🔧 {'Simulating fixes...' if dry_run else 'Applying fixes...'}")
    fixes_made = fix_wrong_references(all_problems, dry_run)

    if dry_run:
        print(f"\n✅ Dry run complete. Would fix {fixes_made} references.")
        print("Run with --no-dry-run to apply changes.")
    else:
        print(f"\n✅ Fixed {fixes_made} wrong directory references!")
        print("🔍 Re-run broken link checker to measure improvement.")

if __name__ == "__main__":
    main()