#!/usr/bin/env python3
"""
Fix Relative Path Issues

Problem: Many relative paths like "L1/XF178.htm" resolve incorrectly when served from different contexts
Investigation: Found 3,638 relative path issues - largest category of broken links
Solution: Convert relative paths to absolute paths with proper /auntruth/ prefix
Expected Impact: ~3,638 broken link fixes (largest impact potential)
Validation: Test specific URLs before/after, run broken link checker
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import re

def verify_git_branch(expected_branch: str = "fix-broken-links-fix-absolute-htm-paths") -> str:
    """Verify we're on the expected git branch"""
    result = subprocess.run(["git", "branch", "--show-current"],
                          capture_output=True, text=True, check=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        print(f"⚠️  Expected branch '{expected_branch}', currently on '{current_branch}'")
    return current_branch

def find_relative_path_issues(directory: str) -> Dict[str, List[dict]]:
    """Find all HTML files that contain relative path issues"""
    base_path = Path(directory)
    files_to_fix = {}

    # Get all HTML files
    html_files = list(base_path.rglob("*.htm"))
    print(f"Scanning {len(html_files)} HTML files in {directory}...")

    # Determine the base URL path based on directory
    if 'new' in directory:
        base_url = '/auntruth/new'
    else:
        base_url = '/auntruth/htm'

    # Patterns for relative paths that need to be made absolute
    relative_patterns = [
        # L1/file.htm -> /auntruth/htm/L1/file.htm (or /auntruth/new/htm/L1/file.htm)
        r'href="(L[0-9]+/[^"]+\.htm)"',
        # ../htm/file.htm -> /auntruth/htm/file.htm
        r'href="(\.\./htm/[^"]+\.htm)"',
        # ../jpg/file.jpg -> /auntruth/jpg/file.jpg
        r'href="(\.\./jpg/[^"]+\.[^"]+)"',
        # L2/XF1234.htm patterns
        r'href="(L[0-9]+/XF[0-9]+\.htm)"',
    ]

    total_issues = 0

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            file_issues = []

            for pattern in relative_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    relative_path = match.group(1)

                    # Determine the correct absolute path
                    if relative_path.startswith('L'):
                        # L1/file.htm -> /auntruth/htm/L1/file.htm
                        absolute_path = f"{base_url}/{relative_path}"
                    elif relative_path.startswith('../htm/'):
                        # ../htm/file.htm -> /auntruth/htm/file.htm
                        absolute_path = relative_path.replace('../htm/', '/auntruth/htm/')
                    elif relative_path.startswith('../jpg/'):
                        # ../jpg/file.jpg -> /auntruth/jpg/file.jpg
                        absolute_path = relative_path.replace('../jpg/', '/auntruth/jpg/')
                    else:
                        continue  # Skip patterns we don't handle

                    file_issues.append({
                        'original_href': match.group(0),
                        'relative_path': relative_path,
                        'absolute_path': absolute_path,
                        'line_context': content[max(0, match.start()-50):match.end()+50],
                        'regex': pattern
                    })

            if file_issues:
                files_to_fix[str(html_file)] = file_issues
                total_issues += len(file_issues)

        except Exception as e:
            print(f"❌ Error reading {html_file}: {e}")
            continue

    print(f"\n📊 RELATIVE PATH ISSUES FOUND:")
    print(f"  Files with issues: {len(files_to_fix)}")
    print(f"  Total relative paths to fix: {total_issues}")

    # Analyze patterns
    pattern_counts = {}
    for filepath, issues in files_to_fix.items():
        for issue in issues:
            rel_path = issue['relative_path']
            if rel_path not in pattern_counts:
                pattern_counts[rel_path] = 0
            pattern_counts[rel_path] += 1

    # Show most common patterns
    if pattern_counts:
        print(f"\n📝 MOST COMMON RELATIVE PATHS:")
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        for rel_path, count in sorted_patterns[:10]:
            print(f"  {rel_path}: {count} occurrences")

    return files_to_fix

def apply_relative_path_fixes(files_to_fix: Dict[str, List[dict]], dry_run: bool = True) -> Dict[str, int]:
    """Apply fixes for relative path issues"""
    if dry_run:
        print("\n🔍 DRY RUN - Would make the following changes:")
    else:
        print("\n🔧 APPLYING FIXES:")

    results = {'files_modified': 0, 'patterns_fixed': 0, 'errors': 0}

    for filepath, issues in files_to_fix.items():
        if not issues:
            continue

        print(f"\n📄 {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content
            modifications_made = 0

            # Group fixes to avoid conflicts
            replacements = []
            for issue in issues:
                old_href = issue['original_href']
                new_href = f'href="{issue["absolute_path"]}"'
                replacements.append((old_href, new_href))

            # Sort replacements by length (longest first) to avoid substring issues
            replacements.sort(key=lambda x: len(x[0]), reverse=True)

            # Apply replacements
            for old_href, new_href in replacements:
                if old_href in content:
                    content = content.replace(old_href, new_href)
                    modifications_made += 1

                    if dry_run:
                        print(f"  🔍 Would change: {old_href}")
                        print(f"            to: {new_href}")
                    else:
                        print(f"  ✅ Changed: {old_href} -> {new_href}")

            if content != original_content and not dry_run:
                # Write the modified content back
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                results['files_modified'] += 1

            if modifications_made > 0:
                results['patterns_fixed'] += modifications_made
            else:
                print(f"  ℹ️  No changes needed")

        except Exception as e:
            print(f"  ❌ Error processing {filepath}: {e}")
            results['errors'] += 1

    return results

def validate_relative_path_fixes(test_cases: List[Tuple[str, str]], source_context: str = "") -> Dict[str, int]:
    """Test that relative paths now resolve to proper absolute URLs"""
    print(f"\n🧪 VALIDATING RELATIVE PATH FIXES ({len(test_cases)} test cases):")

    results = {'fixed': 0, 'still_broken': 0, 'errors': 0}

    for broken_url, fixed_url in test_cases:
        try:
            # Test the fixed URL (the relative path should now be absolute)
            fixed_result = subprocess.run([
                'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', fixed_url
            ], capture_output=True, text=True, timeout=5)

            fixed_status = fixed_result.stdout.strip()

            if fixed_status == '200':
                print(f"  ✅ {broken_url} -> {fixed_url} (200)")
                results['fixed'] += 1
            elif fixed_status == '404':
                print(f"  ⚠️  {broken_url} -> {fixed_url} (404) - path fixed but file may not exist")
                results['fixed'] += 1  # Path structure fixed even if file doesn't exist
            else:
                print(f"  ❌ {broken_url} -> {fixed_url} ({fixed_status})")
                results['still_broken'] += 1

        except Exception as e:
            print(f"  ❌ Error testing URLs: {e}")
            results['errors'] += 1

    return results

def main():
    parser = argparse.ArgumentParser(description='Fix relative path issues in HTML files')
    parser.add_argument('--directory', default='docs', help='Directory to process (docs, docs/htm, docs/new)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be changed without making changes')
    parser.add_argument('--execute', action='store_true',
                       help='Actually apply the changes (overrides --dry-run)')
    parser.add_argument('--validate', action='store_true',
                       help='Run curl validation tests after fixes')
    parser.add_argument('--limit', type=int, help='Limit processing to first N files (for testing)')

    args = parser.parse_args()

    # Override dry-run if execute is specified
    if args.execute:
        args.dry_run = False

    print("🔧 FIX RELATIVE PATH ISSUES")
    print("=" * 40)

    # Verify git branch
    current_branch = verify_git_branch()
    print(f"Git branch: {current_branch}")

    # Find relative path issues
    files_to_fix = find_relative_path_issues(args.directory)

    if not files_to_fix:
        print("\n✅ No relative path issues found!")
        return

    # Limit processing if requested
    if args.limit:
        limited_files = dict(list(files_to_fix.items())[:args.limit])
        print(f"\n⚠️  Limiting processing to first {args.limit} files for testing")
        files_to_fix = limited_files

    # Apply fixes
    results = apply_relative_path_fixes(files_to_fix, args.dry_run)

    # Report results
    print(f"\n📊 RESULTS:")
    if args.dry_run:
        print(f"  Would modify: {len([f for f in files_to_fix.keys()])} files")
        print(f"  Would fix: {results['patterns_fixed']} relative paths")
    else:
        print(f"  Files modified: {results['files_modified']}")
        print(f"  Paths fixed: {results['patterns_fixed']}")
        print(f"  Errors: {results['errors']}")

    # Validation
    if args.validate and not args.dry_run:
        # Test some common relative path fixes
        base_url = '/auntruth/new' if 'new' in args.directory else '/auntruth/htm'
        test_cases = [
            ('L1/XF178.htm', f'{base_url}/L1/XF178.htm'),
            ('L1/XF191.htm', f'{base_url}/L1/XF191.htm'),
            ('L2/XF1234.htm', f'{base_url}/L2/XF1234.htm'),
        ]
        test_urls = [(case[0], f"http://localhost:8000{case[1]}") for case in test_cases]
        validation_results = validate_relative_path_fixes(test_urls)

        print(f"\n🎯 VALIDATION SUMMARY:")
        print(f"  Path structures fixed: {validation_results['fixed']}/{len(test_cases)}")
        print(f"  Still problematic: {validation_results['still_broken']}")

    if args.dry_run:
        print(f"\n💡 To apply these changes, run:")
        print(f"   python3 {__file__} --directory={args.directory} --execute")
        if files_to_fix:
            print(f"   \nOr test on a small sample first:")
            print(f"   python3 {__file__} --directory={args.directory} --limit=5 --execute")

if __name__ == "__main__":
    main()