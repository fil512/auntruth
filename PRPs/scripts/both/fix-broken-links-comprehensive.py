#!/usr/bin/env python3
"""
Comprehensive Broken Links Fix - Master Script

This script coordinates all targeted broken link fixes in optimal order
based on the analysis from analyze-broken-links.py

Fixes applied in order:
1. Wrong Lineage Paths (1,228+ fixes) - High impact, low risk
2. Case Sensitivity (138+ fixes) - High impact, low risk
3. Malformed Spaces (10+ fixes) - Medium impact, low risk
4. Relative Paths (6,577+ fixes) - Highest impact, medium risk

Total potential fixes: 7,953+ broken links
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import time

def verify_git_branch(expected_branch: str = "fix-broken-links-fix-absolute-htm-paths") -> str:
    """Verify we're on the expected git branch"""
    result = subprocess.run(["git", "branch", "--show-current"],
                          capture_output=True, text=True, check=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        print(f"⚠️  Expected branch '{expected_branch}', currently on '{current_branch}'")
    return current_branch

def run_script(script_path: str, args: List[str]) -> Tuple[int, str]:
    """Run a Python script and return (exit_code, output)"""
    cmd = ['python3', script_path] + args
    print(f"🚀 Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "Script timed out after 5 minutes"
    except Exception as e:
        return 1, f"Error running script: {e}"

def run_broken_links_analysis(reports_dir: str = "PRPs/scripts/reports") -> Tuple[int, int]:
    """Get current broken link counts from latest reports"""
    reports_path = Path(reports_dir)

    htm_reports = list(reports_path.glob('broken_links_htm_*.csv'))
    new_reports = list(reports_path.glob('broken_links_new_*.csv'))

    htm_count = 0
    new_count = 0

    if htm_reports:
        latest_htm = sorted(htm_reports)[-1]
        try:
            with open(latest_htm, 'r') as f:
                htm_count = len(f.readlines()) - 1  # Subtract header
        except Exception:
            pass

    if new_reports:
        latest_new = sorted(new_reports)[-1]
        try:
            with open(latest_new, 'r') as f:
                new_count = len(f.readlines()) - 1  # Subtract header
        except Exception:
            pass

    return htm_count, new_count

def main():
    parser = argparse.ArgumentParser(description='Run all broken link fixes comprehensively')
    parser.add_argument('--directory', default='docs', help='Base directory to process')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be changed without making changes')
    parser.add_argument('--execute', action='store_true',
                       help='Actually apply the changes (overrides --dry-run)')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='Skip initial broken links analysis')
    parser.add_argument('--htm-only', action='store_true',
                       help='Process only docs/htm directory')
    parser.add_argument('--new-only', action='store_true',
                       help='Process only docs/new directory')

    args = parser.parse_args()

    # Override dry-run if execute is specified
    if args.execute:
        args.dry_run = False

    print("🎯 COMPREHENSIVE BROKEN LINKS FIX")
    print("=" * 50)

    # Verify git branch
    current_branch = verify_git_branch()
    print(f"Git branch: {current_branch}")

    # Determine directories to process
    directories = []
    if args.htm_only:
        directories = ['docs/htm']
    elif args.new_only:
        directories = ['docs/new']
    else:
        directories = ['docs/htm', 'docs/new']

    print(f"Processing directories: {', '.join(directories)}")
    print(f"Mode: {'EXECUTE' if not args.dry_run else 'DRY RUN'}")

    # Initial analysis
    if not args.skip_analysis:
        print(f"\n📊 INITIAL BROKEN LINKS COUNT:")
        htm_count, new_count = run_broken_links_analysis()
        print(f"  HTM site: {htm_count} broken links")
        print(f"  NEW site: {new_count} broken links")
        print(f"  TOTAL: {htm_count + new_count} broken links")

    total_fixes_applied = 0
    total_errors = 0

    # Define fix scripts in optimal order
    fix_scripts = [
        {
            'name': 'Wrong Lineage Paths Fix',
            'script': 'PRPs/scripts/both/fix-wrong-lineage-paths.py',
            'description': 'Fix references to files in wrong lineage directories',
            'expected_impact': '1,228+ fixes'
        },
        {
            'name': 'Case Sensitivity Fix',
            'script': 'PRPs/scripts/both/fix-case-sensitivity.py',
            'description': 'Fix INDEX.htm -> index.htm case issues',
            'expected_impact': '138+ fixes'
        },
        {
            'name': 'Malformed Spaces Fix',
            'script': 'PRPs/scripts/both/fix-malformed-spaces.py',
            'description': 'Fix URLs with problematic spaces',
            'expected_impact': '10+ fixes'
        },
        {
            'name': 'Relative Paths Fix',
            'script': 'PRPs/scripts/both/fix-relative-paths.py',
            'description': 'Convert relative paths to absolute paths',
            'expected_impact': '6,577+ fixes'
        }
    ]

    # Execute fixes for each directory
    for directory in directories:
        print(f"\n🏗️  PROCESSING {directory.upper()}")
        print("=" * 30)

        for i, fix_script in enumerate(fix_scripts, 1):
            print(f"\n{i}/4: {fix_script['name']}")
            print(f"Expected impact: {fix_script['expected_impact']}")
            print(f"Description: {fix_script['description']}")

            # Prepare arguments
            script_args = ['--directory', directory]
            if args.dry_run:
                script_args.append('--dry-run')
            else:
                script_args.append('--execute')

            # Run the fix script
            start_time = time.time()
            exit_code, output = run_script(fix_script['script'], script_args)
            duration = time.time() - start_time

            if exit_code == 0:
                print(f"✅ {fix_script['name']} completed successfully ({duration:.1f}s)")
                # Try to extract number of fixes from output
                lines = output.split('\n')
                for line in lines:
                    if 'fixed' in line.lower() or 'modified' in line.lower():
                        print(f"   {line.strip()}")
            else:
                print(f"❌ {fix_script['name']} failed (exit code: {exit_code})")
                print("Error output:")
                print(output[:500] + "..." if len(output) > 500 else output)
                total_errors += 1

            # Small delay between scripts
            time.sleep(1)

    # Summary
    print(f"\n📊 COMPREHENSIVE FIX SUMMARY")
    print("=" * 40)
    print(f"Directories processed: {len(directories)}")
    print(f"Fix scripts executed: {len(fix_scripts) * len(directories)}")
    print(f"Errors encountered: {total_errors}")

    if not args.dry_run:
        print(f"\n🔍 POST-FIX ANALYSIS:")
        print("Recommend running the broken link checker again to measure improvement:")
        print("  python3 PRPs/scripts/both/find-broken-links.py --site=htm --timeout=3")
        print("  python3 PRPs/scripts/both/find-broken-links.py --site=new --timeout=3")

        if total_errors == 0:
            print(f"\n🎉 All fixes completed successfully!")
            print("Consider committing changes:")
            print("  git add .")
            print("  git commit -m 'Apply comprehensive broken link fixes'")
        else:
            print(f"\n⚠️  {total_errors} scripts had errors. Review output above.")

    else:
        print(f"\n💡 To execute all fixes, run:")
        print(f"   python3 {__file__} --execute")
        if args.htm_only or args.new_only:
            print(f"   (Currently limited to {directories[0]})")

if __name__ == "__main__":
    main()