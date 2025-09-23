#!/usr/bin/env python3
"""
Task 014: Add Mobile-Responsive CSS
Purpose: Fix CSS path references in ~10,198 HTML files and modernize for mobile devices
Author: Claude Code
Date: 2025-09-22

This script fixes /auntruth/css/htm.css references to use proper relative paths
for GitHub Pages static hosting while preserving the mobile-responsive CSS updates.
"""

import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def verify_git_branch(expected_branch):
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get current git branch: {e}")

def calculate_relative_css_path(file_path):
    """Calculate the correct relative path to css/htm.css from given file"""
    # Convert to Path object and make relative to docs/
    path = Path(file_path)

    # Find how many levels deep we are from docs/
    docs_index = None
    for i, part in enumerate(path.parts):
        if part == 'docs':
            docs_index = i
            break

    if docs_index is None:
        raise ValueError(f"File {file_path} is not under docs/ directory")

    # Get the parts after docs/
    relative_parts = path.parts[docs_index + 1:]

    # Count directory levels (excluding the filename)
    dir_levels = len(relative_parts) - 1

    # Create relative path with appropriate number of ../
    if dir_levels == 0:
        return "css/htm.css"
    else:
        return "../" * dir_levels + "css/htm.css"

def find_css_references(target_dir):
    """Find all HTML files with CSS references"""
    css_files = []
    pattern = re.compile(r'/auntruth/css/htm\.css')

    print(f"Scanning for CSS references in {target_dir}...")

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if pattern.search(content):
                            css_files.append(file_path)
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

    return css_files

def process_file(file_path, dry_run=True):
    """Process a single file to fix CSS references"""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Calculate correct relative path
        relative_path = calculate_relative_css_path(file_path)

        # Replace the absolute path with relative path
        old_pattern = r'/auntruth/css/htm\.css'
        new_content = re.sub(old_pattern, relative_path, content)

        # Check if changes were made
        if content != new_content:
            if not dry_run:
                # Write the modified content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            return True, relative_path

        return False, None

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, None

def process_files_batch(target_dir, dry_run=True, test_mode=False):
    """Process files with safety measures and progress reporting"""

    # Find all files with CSS references
    affected_files = find_css_references(target_dir)
    total_files = len(affected_files)

    print(f"Found {total_files} files with CSS references to fix")

    if total_files == 0:
        print("No files found with CSS references. Nothing to do.")
        return []

    if dry_run:
        print(f"\nDRY RUN - Preview of changes for first 10 files:")
        for i, file_path in enumerate(affected_files[:10]):
            relative_path = calculate_relative_css_path(file_path)
            print(f"  {file_path}")
            print(f"    /auntruth/css/htm.css -> {relative_path}")

        if total_files > 10:
            print(f"  ... and {total_files - 10} more files")

        return affected_files

    if test_mode:
        print(f"\nTEST MODE - Processing first 5 files only:")
        affected_files = affected_files[:5]
        total_files = len(affected_files)

    # Process files with progress reporting
    processed = 0
    modified = 0
    errors = []

    print(f"\nProcessing {total_files} files...")

    for i, file_path in enumerate(affected_files):
        success, relative_path = process_file(file_path, dry_run=False)

        if success:
            processed += 1
            modified += 1
            if modified % 100 == 0:
                print(f"  Processed {processed}/{total_files} files... (Modified: {modified})")
        else:
            processed += 1
            if relative_path is None:
                errors.append(file_path)

        # Checkpoint commits every 500 files for large operations
        if not test_mode and modified > 0 and modified % 500 == 0:
            try:
                print(f"\n  Creating checkpoint commit at {modified} files...")
                subprocess.run(["git", "add", "."], check=True)
                commit_msg = f"Task 014 checkpoint: Fixed CSS paths in {modified} files\n\n🤖 Generated with Claude Code"
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                print(f"  Checkpoint commit created successfully")
            except subprocess.CalledProcessError as e:
                print(f"  Warning: Checkpoint commit failed: {e}")

    print(f"\nCompleted processing:")
    print(f"  Total files processed: {processed}")
    print(f"  Files modified: {modified}")
    print(f"  Errors encountered: {len(errors)}")

    if errors:
        print(f"\nFiles with errors:")
        for error_file in errors[:10]:  # Show first 10 errors
            print(f"  {error_file}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    return affected_files

def validate_changes(target_dir, sample_size=10):
    """Validate that changes were applied correctly"""
    print(f"\nValidating changes in {target_dir}...")

    # Find a sample of files to validate
    validation_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')) and len(validation_files) < sample_size:
                validation_files.append(os.path.join(root, file))

    issues_found = 0

    for file_path in validation_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for old absolute paths
            if '/auntruth/css/htm.css' in content:
                print(f"  ISSUE: Old absolute path still found in {file_path}")
                issues_found += 1

            # Check for correct relative path
            expected_path = calculate_relative_css_path(file_path)
            if expected_path not in content:
                print(f"  ISSUE: Expected relative path '{expected_path}' not found in {file_path}")
                issues_found += 1

        except Exception as e:
            print(f"  Error validating {file_path}: {e}")
            issues_found += 1

    if issues_found == 0:
        print(f"  ✓ Validation passed - all {len(validation_files)} sample files look correct")
    else:
        print(f"  ✗ Validation found {issues_found} issues in sample files")

    return issues_found == 0

def main():
    """Main execution function"""
    # Configuration
    expected_branch = "task-014-add-mobile-css"
    target_dir = "docs/htm"

    # Parse command line arguments
    dry_run = "--dry-run" in sys.argv
    test_mode = "--test-mode" in sys.argv
    execute = "--execute" in sys.argv
    validate = "--validate" in sys.argv
    force_yes = "--yes" in sys.argv

    print("=" * 80)
    print("Task 014: Add Mobile-Responsive CSS")
    print("Fixing CSS path references for GitHub Pages compatibility")
    print("=" * 80)

    try:
        # Verify git branch
        current_branch = verify_git_branch(expected_branch)
        print(f"✓ Working in correct git branch: {current_branch}")

        # Verify target directory exists
        if not os.path.exists(target_dir):
            raise ValueError(f"Target directory {target_dir} does not exist")
        print(f"✓ Target directory exists: {target_dir}")

        # Check git status
        try:
            result = subprocess.run(["git", "status", "--porcelain"],
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print(f"⚠️  Git working directory has uncommitted changes")
                if not force_yes:
                    response = input("Continue anyway? (y/N): ")
                    if response.lower() != 'y':
                        print("Aborted by user")
                        return 1
        except subprocess.CalledProcessError:
            print("⚠️  Could not check git status")

        if dry_run:
            print("\n📋 DRY RUN MODE - No files will be modified")
            process_files_batch(target_dir, dry_run=True)

        elif test_mode:
            print("\n🧪 TEST MODE - Processing 5 sample files only")
            if not force_yes:
                response = input("Proceed with test processing? (y/N): ")
                if response.lower() != 'y':
                    print("Aborted by user")
                    return 1

            affected_files = process_files_batch(target_dir, dry_run=False, test_mode=True)

            if affected_files:
                print("\nTest processing completed. Validating results...")
                validate_changes(target_dir, sample_size=5)

        elif execute:
            print("\n🚀 EXECUTE MODE - Processing all files")
            if not force_yes:
                response = input(f"This will modify thousands of files. Are you sure? (y/N): ")
                if response.lower() != 'y':
                    print("Aborted by user")
                    return 1

            affected_files = process_files_batch(target_dir, dry_run=False, test_mode=False)

            if affected_files:
                print("\nFull processing completed. Validating results...")
                validate_changes(target_dir)

        elif validate:
            print("\n🔍 VALIDATE MODE - Checking existing changes")
            validate_changes(target_dir)

        else:
            print("\nNo action specified. Available options:")
            print("  --dry-run     Preview changes without modifying files")
            print("  --test-mode   Process 5 sample files only")
            print("  --execute     Process all files (requires confirmation)")
            print("  --validate    Validate existing changes")
            print("  --yes         Auto-confirm prompts (for automation)")
            print("\nExample: python3 014-add-mobile-css.py --dry-run")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    print(f"\n✓ Task 014 script completed successfully")
    return 0

if __name__ == "__main__":
    exit(main())