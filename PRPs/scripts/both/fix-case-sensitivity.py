#!/usr/bin/env python3
"""
Fix Case Sensitivity Issues

Problem: References to INDEX.htm (uppercase) fail because files are index.htm (lowercase)
Investigation: curl tests showed INDEX.htm -> 404, index.htm -> 200
Solution: Convert INDEX.htm and Index.htm to index.htm in href attributes
Expected Impact: ~36 broken link fixes based on pattern analysis
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

def find_case_sensitivity_issues(directory: str) -> Dict[str, List[str]]:
    """Find all HTML files that contain case sensitivity issues"""
    base_path = Path(directory)
    files_to_fix = {}

    # Get all HTML files
    html_files = list(base_path.rglob("*.htm"))
    print(f"Scanning {len(html_files)} HTML files in {directory}...")

    case_patterns = [
        r'(href="[^"]*/)INDEX(\.htm)"',     # /path/INDEX.htm -> /path/index.htm
        r'(href="[^"]*/)Index(\.htm)"',     # /path/Index.htm -> /path/index.htm
        r'(href=")INDEX(\.htm)"',           # INDEX.htm -> index.htm
        r'(href=")Index(\.htm)"',           # Index.htm -> index.htm
        r'(href="[^"]*/)INDEX([0-9]+\.htm)"', # INDEX6.htm -> index6.htm
    ]

    total_issues = 0

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            file_issues = []

            for pattern in case_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    file_issues.append({
                        'pattern': match.group(0),
                        'line_context': content[max(0, match.start()-50):match.end()+50],
                        'regex': pattern
                    })

            if file_issues:
                files_to_fix[str(html_file)] = file_issues
                total_issues += len(file_issues)

        except Exception as e:
            print(f"❌ Error reading {html_file}: {e}")
            continue

    print(f"\n📊 CASE SENSITIVITY ISSUES FOUND:")
    print(f"  Files with issues: {len(files_to_fix)}")
    print(f"  Total references to fix: {total_issues}")

    # Show examples
    if files_to_fix:
        print(f"\n📝 EXAMPLES:")
        count = 0
        for filepath, issues in files_to_fix.items():
            if count >= 5:  # Show only first 5 examples
                break
            print(f"  {filepath}:")
            for issue in issues[:3]:  # Show first 3 issues per file
                print(f"    {issue['pattern']}")
            count += 1

    return files_to_fix

def apply_case_fixes(files_to_fix: Dict[str, List[str]], dry_run: bool = True) -> Dict[str, int]:
    """Apply case sensitivity fixes to identified files"""
    if dry_run:
        print("\n🔍 DRY RUN - Would make the following changes:")
    else:
        print("\n🔧 APPLYING FIXES:")

    results = {'files_modified': 0, 'patterns_fixed': 0, 'errors': 0}

    # Define the fix patterns (from -> to)
    fix_patterns = [
        (r'(href="[^"]*/)INDEX(\.htm)"', r'\1index\2"'),        # /path/INDEX.htm -> /path/index.htm
        (r'(href="[^"]*/)Index(\.htm)"', r'\1index\2"'),        # /path/Index.htm -> /path/index.htm
        (r'(href=")INDEX(\.htm)"', r'\1index\2"'),              # INDEX.htm -> index.htm
        (r'(href=")Index(\.htm)"', r'\1index\2"'),              # Index.htm -> index.htm
        (r'(href="[^"]*/)INDEX([0-9]+\.htm)"', r'\1index\2"'),  # INDEX6.htm -> index6.htm
    ]

    for filepath, issues in files_to_fix.items():
        if not issues:
            continue

        print(f"\n📄 {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content
            modifications_made = 0

            # Apply each fix pattern
            for pattern, replacement in fix_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    old_content = content
                    content = re.sub(pattern, replacement, content)
                    new_matches = len(matches)
                    modifications_made += new_matches

                    if dry_run:
                        print(f"  🔍 Would fix {new_matches} occurrences of pattern: {pattern[:50]}...")
                    else:
                        print(f"  ✅ Fixed {new_matches} occurrences of pattern: {pattern[:50]}...")

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

def validate_case_fixes(test_cases: List[Tuple[str, str]]) -> Dict[str, int]:
    """Test that broken case-sensitive URLs become working URLs"""
    print(f"\n🧪 VALIDATING CASE FIXES ({len(test_cases)} test cases):")

    results = {'fixed': 0, 'still_broken': 0, 'errors': 0}

    for broken_url, fixed_url in test_cases:
        try:
            # Test broken URL (uppercase)
            broken_result = subprocess.run([
                'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', broken_url
            ], capture_output=True, text=True, timeout=5)

            # Test fixed URL (lowercase)
            fixed_result = subprocess.run([
                'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', fixed_url
            ], capture_output=True, text=True, timeout=5)

            broken_status = broken_result.stdout.strip()
            fixed_status = fixed_result.stdout.strip()

            if broken_status == '404' and fixed_status == '200':
                print(f"  ✅ {broken_url} (404) -> {fixed_url} (200)")
                results['fixed'] += 1
            elif fixed_status == '200':
                print(f"  ⚠️  {broken_url} ({broken_status}) -> {fixed_url} (200)")
                results['fixed'] += 1
            else:
                print(f"  ❌ {broken_url} ({broken_status}) -> {fixed_url} ({fixed_status})")
                results['still_broken'] += 1

        except Exception as e:
            print(f"  ❌ Error testing URLs: {e}")
            results['errors'] += 1

    return results

def main():
    parser = argparse.ArgumentParser(description='Fix case sensitivity issues in HTML files')
    parser.add_argument('--directory', default='docs', help='Directory to process (docs, docs/htm, docs/new)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be changed without making changes')
    parser.add_argument('--execute', action='store_true',
                       help='Actually apply the changes (overrides --dry-run)')
    parser.add_argument('--validate', action='store_true',
                       help='Run curl validation tests after fixes')

    args = parser.parse_args()

    # Override dry-run if execute is specified
    if args.execute:
        args.dry_run = False

    print("🔧 FIX CASE SENSITIVITY ISSUES")
    print("=" * 40)

    # Verify git branch
    current_branch = verify_git_branch()
    print(f"Git branch: {current_branch}")

    # Find case sensitivity issues
    files_to_fix = find_case_sensitivity_issues(args.directory)

    if not files_to_fix:
        print("\n✅ No case sensitivity issues found!")
        return

    # Apply fixes
    results = apply_case_fixes(files_to_fix, args.dry_run)

    # Report results
    print(f"\n📊 RESULTS:")
    if args.dry_run:
        print(f"  Would modify: {len(files_to_fix)} files")
        print(f"  Would fix: {results['patterns_fixed']} references")
    else:
        print(f"  Files modified: {results['files_modified']}")
        print(f"  References fixed: {results['patterns_fixed']}")
        print(f"  Errors: {results['errors']}")

    # Validation
    if args.validate and not args.dry_run:
        # Test common case sensitivity issues
        test_cases = [
            ('http://localhost:8000/auntruth/new/L1/INDEX.htm', 'http://localhost:8000/auntruth/new/L1/index.htm'),
            ('http://localhost:8000/auntruth/new/L6/INDEX.htm', 'http://localhost:8000/auntruth/new/L6/index.htm'),
            ('http://localhost:8000/auntruth/new/L7/INDEX.htm', 'http://localhost:8000/auntruth/new/L7/index.htm'),
        ]
        validation_results = validate_case_fixes(test_cases)

        print(f"\n🎯 VALIDATION SUMMARY:")
        print(f"  Fixed: {validation_results['fixed']}/{len(test_cases)}")
        print(f"  Still broken: {validation_results['still_broken']}")

    if args.dry_run:
        print(f"\n💡 To apply these changes, run:")
        print(f"   python3 {__file__} --directory={args.directory} --execute")

if __name__ == "__main__":
    main()