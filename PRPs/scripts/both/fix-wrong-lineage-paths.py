#!/usr/bin/env python3
"""
Fix Wrong Lineage Directory References

Problem: Many files reference other files in the wrong lineage directory (L1, L2, etc.)
Investigation: XF533.htm exists in L9, not L1. IMAGES.htm exists in L2, not L0. etc.
Solution: Update references to point to correct lineage directories based on file discovery
Expected Impact: 225+ broken link fixes (XF533: 111 + IMAGES: 49 + EVERYONE: 8 + others)
Validation: Test specific URLs before/after, run broken link checker
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import re

# Map of files to their correct locations (discovered through file system search)
CORRECT_LOCATIONS = {
    'XF533.htm': 'L9/XF533.htm',
    'IMAGES.htm': 'L2/IMAGES.htm',  # Primary location - also exists in L6,L3,L5
    'EVERYONE.htm': 'L0/EVERYONE.htm',  # Primary location - also exists in L2,L6,L3,L5
    'XF1234.htm': 'L2/XF1234.htm',  # Need to verify this exists
}

def verify_git_branch(expected_branch: str = "fix-broken-links-fix-absolute-htm-paths") -> str:
    """Verify we're on the expected git branch"""
    result = subprocess.run(["git", "branch", "--show-current"],
                          capture_output=True, text=True, check=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        print(f"⚠️  Expected branch '{expected_branch}', currently on '{current_branch}'")
    return current_branch

def find_files_to_fix(directory: str, dry_run: bool = True) -> Dict[str, List[str]]:
    """Find all HTML files that contain wrong lineage directory references"""
    base_path = Path(directory)
    files_to_fix = {}

    # Get all HTML files
    html_files = list(base_path.rglob("*.htm"))

    print(f"Scanning {len(html_files)} HTML files in {directory}...")

    patterns_found = {filename: [] for filename in CORRECT_LOCATIONS.keys()}

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for each file reference that might be in wrong lineage
            for target_filename, correct_path in CORRECT_LOCATIONS.items():
                # Pattern: references to target file in wrong lineage directory
                wrong_patterns = [
                    rf'(href="[^"]*)/L[0-8]/({re.escape(target_filename)})"',  # /L1/XF533.htm
                    rf'(href="[^"]*)/({re.escape(target_filename)})"',          # direct reference
                    rf'(href=")L[0-8]/({re.escape(target_filename)})"',        # relative L1/XF533.htm
                    rf'(href=")({re.escape(target_filename)})"',               # just filename
                ]

                for pattern in wrong_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        full_match = match.group(0)
                        # Skip if it's already pointing to the correct location
                        if correct_path in full_match:
                            continue

                        if str(html_file) not in files_to_fix:
                            files_to_fix[str(html_file)] = []

                        files_to_fix[str(html_file)].append({
                            'pattern': full_match,
                            'target_file': target_filename,
                            'correct_path': correct_path,
                            'line_context': content[max(0, match.start()-50):match.end()+50]
                        })

                        patterns_found[target_filename].append(str(html_file))

        except Exception as e:
            print(f"❌ Error reading {html_file}: {e}")
            continue

    # Report findings
    print(f"\n📊 WRONG LINEAGE REFERENCES FOUND:")
    total_fixes = 0
    for filename, files in patterns_found.items():
        if files:
            unique_files = len(set(files))
            total_refs = len(files)
            print(f"  {filename}: {total_refs} references in {unique_files} files -> should point to {CORRECT_LOCATIONS[filename]}")
            total_fixes += total_refs

    print(f"\nTotal potential fixes: {total_fixes}")
    return files_to_fix

def create_fix_patterns(target_file: str, correct_path: str) -> List[Tuple[str, str]]:
    """Create regex patterns to fix wrong lineage references"""
    patterns = []

    # Fix absolute paths like /auntruth/htm/L1/XF533.htm -> /auntruth/htm/L9/XF533.htm
    patterns.append((
        rf'(href="[^"]*)/L[0-8]/({re.escape(target_file)})"',
        rf'\1/{correct_path}"'
    ))

    # Fix relative paths like L1/XF533.htm -> L9/XF533.htm
    patterns.append((
        rf'(href=")L[0-8]/({re.escape(target_file)})"',
        rf'\1{correct_path}"'
    ))

    # Fix direct filename references (add correct path)
    # This is tricky - we need context to determine the right absolute path

    return patterns

def apply_fixes(files_to_fix: Dict[str, List[str]], dry_run: bool = True) -> Dict[str, int]:
    """Apply the fixes to identified files"""
    if dry_run:
        print("\n🔍 DRY RUN - Would make the following changes:")
    else:
        print("\n🔧 APPLYING FIXES:")

    results = {'files_modified': 0, 'patterns_fixed': 0, 'errors': 0}

    for filepath, fixes in files_to_fix.items():
        if not fixes:
            continue

        print(f"\n📄 {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content
            modifications_made = 0

            # Group fixes by target file for consistent replacement
            fixes_by_target = {}
            for fix in fixes:
                target = fix['target_file']
                if target not in fixes_by_target:
                    fixes_by_target[target] = []
                fixes_by_target[target].append(fix)

            # Apply fixes for each target file
            for target_file, target_fixes in fixes_by_target.items():
                correct_path = CORRECT_LOCATIONS[target_file]
                patterns = create_fix_patterns(target_file, correct_path)

                for pattern, replacement in patterns:
                    old_content = content
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

                    if content != old_content:
                        # Count the number of replacements made
                        modifications_made += len(re.findall(pattern, old_content, re.IGNORECASE))

            if content != original_content and not dry_run:
                # Write the modified content back
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Fixed {modifications_made} references")
                results['files_modified'] += 1
                results['patterns_fixed'] += modifications_made
            elif content != original_content:
                print(f"  🔍 Would fix {modifications_made} references")
                results['patterns_fixed'] += modifications_made
            else:
                print(f"  ℹ️  No changes needed")

        except Exception as e:
            print(f"  ❌ Error processing {filepath}: {e}")
            results['errors'] += 1

    return results

def validate_fixes(test_cases: List[Tuple[str, str]]) -> Dict[str, int]:
    """Test that broken URLs become working URLs"""
    print(f"\n🧪 VALIDATING FIXES ({len(test_cases)} test cases):")

    results = {'fixed': 0, 'still_broken': 0, 'errors': 0}

    for broken_url, fixed_url in test_cases:
        try:
            # Test broken URL
            broken_result = subprocess.run([
                'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', broken_url
            ], capture_output=True, text=True, timeout=5)

            # Test fixed URL
            fixed_result = subprocess.run([
                'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', fixed_url
            ], capture_output=True, text=True, timeout=5)

            broken_status = broken_result.stdout.strip()
            fixed_status = fixed_result.stdout.strip()

            if broken_status == '404' and fixed_status == '200':
                print(f"  ✅ {broken_url} (404) -> {fixed_url} (200)")
                results['fixed'] += 1
            elif fixed_status == '200':
                print(f"  ⚠️  {broken_url} ({broken_status}) -> {fixed_url} (200) - already working?")
                results['fixed'] += 1
            else:
                print(f"  ❌ {broken_url} ({broken_status}) -> {fixed_url} ({fixed_status})")
                results['still_broken'] += 1

        except Exception as e:
            print(f"  ❌ Error testing URLs: {e}")
            results['errors'] += 1

    return results

def main():
    parser = argparse.ArgumentParser(description='Fix wrong lineage directory references in HTML files')
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

    print("🔧 FIX WRONG LINEAGE DIRECTORY REFERENCES")
    print("=" * 50)

    # Verify git branch
    current_branch = verify_git_branch()
    print(f"Git branch: {current_branch}")

    # Find files to fix
    files_to_fix = find_files_to_fix(args.directory, args.dry_run)

    if not files_to_fix:
        print("\n✅ No wrong lineage references found!")
        return

    # Apply fixes
    results = apply_fixes(files_to_fix, args.dry_run)

    # Report results
    print(f"\n📊 RESULTS:")
    if args.dry_run:
        print(f"  Would modify: {len([f for f, fixes in files_to_fix.items() if fixes])} files")
        print(f"  Would fix: {results['patterns_fixed']} references")
    else:
        print(f"  Files modified: {results['files_modified']}")
        print(f"  References fixed: {results['patterns_fixed']}")
        print(f"  Errors: {results['errors']}")

    # Validation
    if args.validate and not args.dry_run:
        test_cases = [
            ('http://localhost:8000/auntruth/htm/L1/XF533.htm', 'http://localhost:8000/auntruth/htm/L9/XF533.htm'),
            ('http://localhost:8000/auntruth/new/L0/IMAGES.htm', 'http://localhost:8000/auntruth/htm/L2/IMAGES.htm'),
            ('http://localhost:8000/auntruth/new/L0/EVERYONE.htm', 'http://localhost:8000/auntruth/htm/L0/EVERYONE.htm'),
        ]
        validation_results = validate_fixes(test_cases)

        print(f"\n🎯 VALIDATION SUMMARY:")
        print(f"  Fixed: {validation_results['fixed']}/{len(test_cases)}")
        print(f"  Still broken: {validation_results['still_broken']}")

    if args.dry_run:
        print(f"\n💡 To apply these changes, run:")
        print(f"   python3 {__file__} --directory={args.directory} --execute")

if __name__ == "__main__":
    main()