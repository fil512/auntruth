#!/usr/bin/env python3
"""
Fix Missing /htm/ Prefix in NEW Site Paths - Script 016

Problem: Links in NEW site reference /auntruth/new/L1/file.htm but should be /auntruth/new/htm/L1/file.htm
Investigation: curl tests showed /new/L1/ → 404, /new/htm/L1/ → 200
Solution: Add missing /htm/ component to NEW site paths
Expected Impact: ~3,933+ broken link fixes (majority of NEW site issues)
Validation: Test specific URLs before/after, run broken link checker
"""

import os
import re
import sys
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict

def verify_git_branch(expected_branch: str) -> str:
    """Verify we're on the expected git branch."""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            print(f"⚠️  Expected branch '{expected_branch}', currently on '{current_branch}'")
        return current_branch
    except subprocess.CalledProcessError:
        print("❌ Error checking git branch")
        return "unknown"

def test_url_with_curl(url: str, timeout: int = 3) -> int:
    """Test URL with curl and return HTTP status code."""
    try:
        result = subprocess.run([
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "--max-time", str(timeout), url
        ], capture_output=True, text=True, timeout=timeout + 2)
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
        return 0

def find_html_files(directory: str) -> list:
    """Find all HTML files in directory."""
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))
    return html_files

def fix_missing_htm_prefix(file_path: str, dry_run: bool = True) -> int:
    """Fix missing /htm/ prefix in NEW site paths within a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return 0

    original_content = content
    fixes_made = 0

    # Pattern: /auntruth/new/L[0-9]+/ → /auntruth/new/htm/L[0-9]+/
    patterns_to_fix = [
        (r'(/auntruth/new/)L([0-9]+/)', r'\1htm/L\2'),
        (r'(/auntruth/new/)L([0-9]+\.htm)', r'\1htm/L\2'),
        (r'(/auntruth/new/)L([0-9]+/[^"]*\.htm)', r'\1htm/L\2'),
        (r'(/auntruth/new/)L([0-9]+/[^"]*\.jpg)', r'\1htm/L\2'),
    ]

    for pattern, replacement in patterns_to_fix:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            fixes_made += count

    if fixes_made > 0 and not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return 0

    return fixes_made

def validate_sample_fixes(sample_cases: list, dry_run: bool = True) -> dict:
    """Validate that our fixes actually work for sample cases."""
    print("\n🧪 VALIDATING SAMPLE FIXES:")
    results = {"success": 0, "failed": 0, "details": []}

    for broken_url, fixed_url, description in sample_cases:
        if not dry_run:
            broken_status = test_url_with_curl(broken_url)
            fixed_status = test_url_with_curl(fixed_url)

            result = {
                "broken_url": broken_url,
                "fixed_url": fixed_url,
                "broken_status": broken_status,
                "fixed_status": fixed_status,
                "description": description
            }

            if broken_status == 404 and fixed_status == 200:
                print(f"✅ {description}: {broken_url} (404) → {fixed_url} (200)")
                results["success"] += 1
            else:
                print(f"❌ {description}: {broken_url} ({broken_status}) → {fixed_url} ({fixed_status})")
                results["failed"] += 1

            results["details"].append(result)
        else:
            print(f"🔍 {description}: {broken_url} → {fixed_url}")

    return results

def main():
    parser = argparse.ArgumentParser(description="Fix missing /htm/ prefix in NEW site paths")
    parser.add_argument("--directory", default="docs/new",
                       help="Directory to process (default: docs/new)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be changed without making changes")
    parser.add_argument("--execute", action="store_true",
                       help="Execute the fixes (opposite of dry-run)")
    parser.add_argument("--limit", type=int,
                       help="Limit processing to first N files (for testing)")

    args = parser.parse_args()

    # Determine mode
    if args.execute:
        dry_run = False
        mode_str = "EXECUTE"
    else:
        dry_run = True
        mode_str = "DRY RUN"

    print(f"🔧 FIXING MISSING /htm/ PREFIX IN NEW SITE PATHS")
    print(f"==================================================")

    # Check git branch
    current_branch = verify_git_branch("fix-broken-links-fix-absolute-htm-paths")
    print(f"Git branch: {current_branch}")

    print(f"Directory: {args.directory}")
    print(f"Mode: {mode_str}")

    # Validate directory exists
    if not os.path.exists(args.directory):
        print(f"❌ Directory {args.directory} does not exist")
        return 1

    # Sample validation cases
    sample_cases = [
        ("http://localhost:8000/auntruth/new/L1/XF191.htm",
         "http://localhost:8000/auntruth/new/htm/L1/XF191.htm",
         "XF191.htm lineage L1"),
        ("http://localhost:8000/auntruth/new/L1/XF178.htm",
         "http://localhost:8000/auntruth/new/htm/L1/XF178.htm",
         "XF178.htm lineage L1"),
        ("http://localhost:8000/auntruth/new/L2/IMAGES.htm",
         "http://localhost:8000/auntruth/new/htm/L2/IMAGES.htm",
         "IMAGES.htm lineage L2")
    ]

    # Validate our assumptions
    validation_results = validate_sample_fixes(sample_cases, dry_run)

    if not dry_run and validation_results["failed"] > 0:
        print(f"❌ {validation_results['failed']} sample validations failed. Stopping.")
        return 1

    # Find HTML files
    print(f"\n📁 FINDING HTML FILES:")
    html_files = find_html_files(args.directory)
    print(f"Found {len(html_files)} HTML files")

    if args.limit:
        html_files = html_files[:args.limit]
        print(f"Limited to first {len(html_files)} files")

    # Process files
    print(f"\n🔄 PROCESSING FILES:")
    total_fixes = 0
    files_modified = 0

    for i, file_path in enumerate(html_files):
        if i % 1000 == 0 and i > 0:
            print(f"  Progress: {i}/{len(html_files)} files processed...")

        fixes_made = fix_missing_htm_prefix(file_path, dry_run)
        if fixes_made > 0:
            files_modified += 1
            total_fixes += fixes_made
            rel_path = os.path.relpath(file_path, args.directory)
            if dry_run:
                print(f"  Would fix {fixes_made} paths in: {rel_path}")
            else:
                print(f"  ✅ Fixed {fixes_made} paths in: {rel_path}")

    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"Files processed: {len(html_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total path fixes: {total_fixes}")

    if dry_run:
        print(f"\n💡 To execute fixes, run with --execute flag")
    else:
        print(f"\n✅ All fixes completed!")
        print(f"Recommend testing with broken link checker to measure improvement")

    return 0

if __name__ == "__main__":
    sys.exit(main())