#!/usr/bin/env python3
"""
Task 011: Add DOCTYPE declarations to HTML files

This script adds proper DOCTYPE declarations to HTML files for GitHub Pages compatibility.
Processes ~11,000 HTML files in the genealogy site with safety protocols.

Author: Claude Code
Date: 2025-09-22
Task: 011-add-doctype
"""

import os
import re
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

def verify_git_branch(expected_branch):
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
        return current_branch
    except Exception as e:
        raise ValueError(f"Failed to verify git branch: {e}")

def find_html_files(target_dir):
    """Find all HTML files recursively"""
    html_files = []

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                html_files.append(file_path)

    return sorted(html_files)

def needs_doctype(file_path):
    """Check if file needs DOCTYPE declaration"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if file already has DOCTYPE
        if '<!DOCTYPE' in content.upper():
            return False, content

        # Check if file starts with <html> (needs DOCTYPE)
        content_stripped = content.strip()
        if content_stripped.upper().startswith('<HTML'):
            return True, content

        return False, content

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, None

def add_doctype_declaration(content):
    """Add DOCTYPE declaration to HTML content"""
    # Standard HTML5 DOCTYPE
    doctype = '<!DOCTYPE html>\n'

    # Find the <html> tag and add DOCTYPE before it
    # Handle various cases: <html>, <HTML>, with attributes, etc.
    html_pattern = r'(<html[^>]*>)'

    # Check if content starts with HTML tag
    content_stripped = content.strip()
    if re.match(r'<html', content_stripped, re.IGNORECASE):
        # Add DOCTYPE at the beginning
        new_content = doctype + content
        return new_content
    else:
        # Look for HTML tag in the content
        match = re.search(html_pattern, content, re.IGNORECASE)
        if match:
            # Insert DOCTYPE before the HTML tag
            pos = match.start()
            new_content = content[:pos] + doctype + content[pos:]
            return new_content

    # If no HTML tag found, add DOCTYPE at the beginning anyway
    return doctype + content

def process_files_batch(html_files, dry_run=True, test_mode=False, commit_interval=500):
    """Process files with safety measures"""

    if test_mode:
        print("TEST MODE - Processing only first 5 files")
        html_files = html_files[:5]

    # Filter files that need DOCTYPE
    files_to_process = []

    print("Analyzing files for DOCTYPE requirements...")
    for i, file_path in enumerate(html_files):
        if i % 1000 == 0:
            print(f"Analyzed {i}/{len(html_files)} files...")

        needs_change, content = needs_doctype(file_path)
        if needs_change and content is not None:
            files_to_process.append((file_path, content))

    print(f"\nFound {len(files_to_process)} files that need DOCTYPE declarations")

    if dry_run:
        print("\nDRY RUN - Files that would be changed:")
        for i, (file_path, _) in enumerate(files_to_process):
            if i < 10:  # Show first 10
                print(f"  {file_path}")
            elif i == 10:
                print(f"  ... and {len(files_to_process) - 10} more files")
                break
        return files_to_process

    if not files_to_process:
        print("No files need DOCTYPE declarations")
        return files_to_process

    # Process files
    processed = 0
    errors = []

    for i, (file_path, original_content) in enumerate(files_to_process):
        try:
            # Add DOCTYPE declaration
            new_content = add_doctype_declaration(original_content)

            # Write the modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            processed += 1

            # Progress reporting
            if processed % 100 == 0:
                print(f"Processed {processed}/{len(files_to_process)} files...")

            # Commit at intervals for large batches
            if not test_mode and processed % commit_interval == 0:
                try:
                    subprocess.run(["git", "add", "."], check=True)
                    commit_msg = f"Task 011: Add DOCTYPE declarations - checkpoint {processed}/{len(files_to_process)} files"
                    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                    print(f"Checkpoint commit at {processed} files")
                except subprocess.CalledProcessError as e:
                    print(f"Warning: Checkpoint commit failed: {e}")

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            print(error_msg)
            errors.append(error_msg)
            continue

    print(f"\nCompleted processing:")
    print(f"- Successfully processed: {processed} files")
    print(f"- Errors encountered: {len(errors)} files")

    if errors:
        print("\nErrors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    return files_to_process

def validate_changes(sample_files, original_contents):
    """Validate that changes were applied correctly"""
    print("\nValidating sample of changed files...")

    validation_errors = []
    sample_size = min(5, len(sample_files))

    for i in range(sample_size):
        file_path, original_content = sample_files[i], original_contents[i]

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                new_content = f.read()

            # Check if DOCTYPE was added
            if '<!DOCTYPE html>' not in new_content:
                validation_errors.append(f"DOCTYPE not found in {file_path}")

            # Check if original content is preserved (minus DOCTYPE)
            content_without_doctype = new_content.replace('<!DOCTYPE html>\n', '')
            if content_without_doctype.strip() != original_content.strip():
                validation_errors.append(f"Content changed unexpectedly in {file_path}")

        except Exception as e:
            validation_errors.append(f"Failed to validate {file_path}: {e}")

    if validation_errors:
        print("Validation errors found:")
        for error in validation_errors:
            print(f"  {error}")
        return False
    else:
        print(f"Validation successful for {sample_size} sample files")
        return True

def main():
    parser = argparse.ArgumentParser(description='Add DOCTYPE declarations to HTML files')
    parser.add_argument('--target-dir', default='/home/ken/wip/fam/auntruth/docs/htm',
                       help='Directory to process')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--test-mode', action='store_true',
                       help='Process only first 5 files for testing')
    parser.add_argument('--execute', action='store_true',
                       help='Actually execute the changes (required for non-dry-run)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate changes after execution')
    parser.add_argument('--branch-name', default='task-011-add-doctype',
                       help='Expected git branch name')
    parser.add_argument('--yes', action='store_true',
                       help='Skip confirmation prompt for batch processing')

    args = parser.parse_args()

    print("=" * 60)
    print("Task 011: Add DOCTYPE Declarations")
    print("=" * 60)
    print(f"Target directory: {args.target_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'TEST MODE' if args.test_mode else 'EXECUTE'}")
    print(f"Expected branch: {args.branch_name}")
    print(f"Timestamp: {datetime.now()}")
    print()

    # Verify git branch
    try:
        current_branch = verify_git_branch(args.branch_name)
        print(f"✓ Working in correct branch: {current_branch}")
    except ValueError as e:
        print(f"✗ Git branch error: {e}")
        return 1

    # Verify target directory
    if not os.path.exists(args.target_dir):
        print(f"✗ Target directory does not exist: {args.target_dir}")
        return 1

    print(f"✓ Target directory exists: {args.target_dir}")

    # Find all HTML files
    print("\nScanning for HTML files...")
    html_files = find_html_files(args.target_dir)
    print(f"Found {len(html_files)} HTML files")

    if not html_files:
        print("No HTML files found")
        return 0

    # Process files
    if args.dry_run:
        files_processed = process_files_batch(html_files, dry_run=True)
    elif args.test_mode:
        print("\n" + "="*40)
        print("RUNNING IN TEST MODE (5 files only)")
        print("="*40)

        original_contents = []
        for file_path in html_files[:5]:
            _, content = needs_doctype(file_path)
            original_contents.append(content)

        files_processed = process_files_batch(html_files, dry_run=False, test_mode=True)

        if args.validate and files_processed:
            validate_changes([(f[0], f[1]) for f in files_processed], original_contents)

    elif args.execute:
        print("\n" + "="*40)
        print("EXECUTING FULL PROCESSING")
        print("="*40)

        if not args.yes:
            try:
                response = input(f"About to process {len(html_files)} files. Continue? (yes/no): ")
                if response.lower() != 'yes':
                    print("Aborted by user")
                    return 0
            except EOFError:
                print("Running in non-interactive mode. Use --yes flag to proceed automatically.")
                return 1
        else:
            print(f"Auto-confirmed: Processing {len(html_files)} files...")

        files_processed = process_files_batch(html_files, dry_run=False, test_mode=False)

        # Final commit
        if files_processed:
            try:
                subprocess.run(["git", "add", "."], check=True)
                commit_msg = f"Task 011: Add DOCTYPE declarations - completed {len(files_processed)} files"
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                print("Final commit completed")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Final commit failed: {e}")

        if args.validate and files_processed:
            # Sample validation on a few files
            sample_files = files_processed[:5]
            original_contents = [f[1] for f in sample_files]
            validate_changes([(f[0], f[1]) for f in sample_files], original_contents)

    else:
        print("\nNo action specified. Use --dry-run, --test-mode, or --execute")
        return 1

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Branch: {args.branch_name}")
    print(f"Total HTML files found: {len(html_files)}")

    if hasattr(files_processed, '__len__'):
        print(f"Files that needed DOCTYPE: {len(files_processed)}")

    if args.dry_run:
        print("Mode: DRY RUN - no changes made")
    elif args.test_mode:
        print("Mode: TEST MODE - processed 5 files only")
    elif args.execute:
        print("Mode: EXECUTE - all changes committed")

    print("\nRollback instructions (if needed):")
    print(f"  git log --oneline  # Find commit hash")
    print(f"  git reset --hard <previous-commit-hash>")
    print(f"  # Or to revert to main branch:")
    print(f"  git checkout main")
    print(f"  git branch -D {args.branch_name}")

    return 0

if __name__ == '__main__':
    sys.exit(main())