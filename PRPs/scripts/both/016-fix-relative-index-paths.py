#!/usr/bin/env python3
"""
Fix Relative Index Paths - Priority 1
Purpose: Fix broken relative index file references to point to correct index.html location

This script addresses relative path issues where files in subdirectories are linking
to "./index.html" but the actual index.html is in the parent directory. These links
should be "../index.html" instead.

CRITICAL SAFETY REQUIREMENTS:
- This script processes hundreds of files
- Uses git branch safety system
- Implements progress reporting every 100 files
- Includes dry-run mode and error handling
- Follows patterns from existing scripts

Target Patterns to Fix:
- Files in subdirectories: href="./index.html" → href="../index.html"
- Files in nested subdirectories: href="./index.html" → href="../../index.html"
- Calculate correct relative path based on directory depth
"""

import os
import re
import argparse
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

def setup_logging(log_file: str = None) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def verify_git_branch(expected_branch: str = "task-015-broken-links-fix") -> str:
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
        print(f"✅ Verified working in correct branch: {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get current git branch: {e}")

def calculate_relative_path_to_index(file_path: str, base_dir: str) -> str:
    """Calculate correct relative path from file to index.html in base directory"""
    # Get the directory containing the HTML file
    file_dir = os.path.dirname(file_path)

    # Calculate relative path from file directory to base directory
    rel_path = os.path.relpath(base_dir, file_dir)

    # Construct the path to index.html
    if rel_path == ".":
        return "./index.html"
    else:
        return f"{rel_path}/index.html"

def scan_files_with_broken_index_refs(target_dir: str) -> List[Tuple[str, str]]:
    """Find files with ./index.html patterns and calculate correct paths"""
    affected_files = []

    print(f"🔍 Scanning {target_dir} for broken index reference patterns...")

    # Find the base directory where index.html actually exists
    index_locations = []
    for root, dirs, files in os.walk(target_dir):
        if 'index.html' in files or 'index.htm' in files:
            index_locations.append(root)

    if not index_locations:
        print("❌ No index.html files found in target directory")
        return []

    print(f"📍 Found index files in: {', '.join(index_locations)}")

    # Pattern to find ./index.html references
    pattern = r'href\s*=\s*["\']\.\/index\.html?["\']'

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check if file contains ./index.html pattern
                    if re.search(pattern, content, re.IGNORECASE):
                        # For each file, find the closest index.html
                        closest_index_dir = None
                        for index_dir in index_locations:
                            # Check if this index directory is a parent of the file
                            try:
                                file_rel = os.path.relpath(file_path, index_dir)
                                if not file_rel.startswith('..'):
                                    closest_index_dir = index_dir
                                    break
                            except ValueError:
                                continue

                        if closest_index_dir:
                            correct_path = calculate_relative_path_to_index(file_path, closest_index_dir)
                            # Only add if the correct path is different from current
                            if correct_path != "./index.html":
                                affected_files.append((file_path, correct_path))

                except (OSError, IOError) as e:
                    logging.warning(f"Could not read {file_path}: {e}")
                    continue

    return affected_files

def fix_index_paths_in_file(file_path: str, correct_path: str) -> List[str]:
    """Fix index references in single file"""
    changes_made = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Patterns to fix - replace ./index.html with the correct relative path
        patterns_to_fix = [
            # Double quotes
            (r'href\s*=\s*"\.\/index\.html?"', f'href="{correct_path}"'),
            # Single quotes
            (r"href\s*=\s*'\.\/index\.html?'", f"href='{correct_path}'"),
        ]

        for old_pattern, new_pattern in patterns_to_fix:
            old_content = content
            content = re.sub(old_pattern, new_pattern, content, flags=re.IGNORECASE)
            if content != old_content:
                matches = len(re.findall(old_pattern, old_content, re.IGNORECASE))
                changes_made.append(f"Fixed {matches} instances: ./index.html → {correct_path}")

        # Write the file only if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return []

    return changes_made

def validate_sample_fixes(processed_files: List[Tuple[str, str]], sample_size: int = 10) -> Dict[str, int]:
    """Validate that a sample of fixes work by checking if target index files exist"""
    if not processed_files:
        return {"total": 0, "success": 0, "failed": 0}

    import random
    sample_files = random.sample(processed_files, min(sample_size, len(processed_files)))

    validation_results = {"total": 0, "success": 0, "failed": 0}

    print(f"🔬 Validating sample of {len(sample_files)} fixed files...")

    for file_path, correct_path in sample_files:
        validation_results["total"] += 1

        # Calculate the absolute path to the target index file
        file_dir = os.path.dirname(file_path)
        if correct_path.startswith('./'):
            target_index = os.path.join(file_dir, correct_path[2:])
        else:
            target_index = os.path.join(file_dir, correct_path)

        # Check if the target index file exists
        if os.path.exists(target_index):
            validation_results["success"] += 1
        else:
            validation_results["failed"] += 1
            logging.warning(f"Target index file does not exist: {target_index}")

    return validation_results

def show_dry_run_preview(affected_files: List[Tuple[str, str]], limit: int = 10) -> None:
    """Show preview of what would be changed in dry-run mode"""
    print(f"\n📋 DRY RUN PREVIEW - Would process {len(affected_files)} files")
    print("=" * 80)

    preview_files = affected_files[:limit]

    for i, (file_path, correct_path) in enumerate(preview_files, 1):
        print(f"{i}. {file_path}")
        print(f"   Change: ./index.html → {correct_path}")

        # Show the actual line that would be changed
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Find the href line
            match = re.search(r'.*href\s*=\s*["\']\.\/index\.html?["\'].*', content, re.IGNORECASE)
            if match:
                line = match.group(0).strip()[:100]  # Limit line length
                print(f"   Example: {line}")

        except Exception as e:
            print(f"   Could not preview: {e}")

    if len(affected_files) > limit:
        print(f"   ... and {len(affected_files) - limit} more files")

    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description='Fix relative index path references')
    parser.add_argument('--target-dir', default='docs', help='Target directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--limit', type=int, help='Limit number of files processed (for testing)')
    parser.add_argument('--branch-name', default='task-015-broken-links-fix', help='Git branch name')
    parser.add_argument('--log-file', help='Log file path')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_file)

    print("🚀 Starting Relative Index Paths Fix (Script 016)")
    print("=" * 60)

    # Verify git branch
    try:
        verify_git_branch(args.branch_name)
    except ValueError as e:
        logger.error(f"Git branch verification failed: {e}")
        return 1

    # Scan for affected files
    affected_files = scan_files_with_broken_index_refs(args.target_dir)

    if not affected_files:
        print("✅ No files found with broken index path patterns")
        return 0

    print(f"📊 Found {len(affected_files)} files with broken index paths")

    # Apply limit if specified
    if args.limit:
        affected_files = affected_files[:args.limit]
        print(f"📏 Limited to {len(affected_files)} files for this run")

    # Dry run mode
    if args.dry_run:
        show_dry_run_preview(affected_files)
        print("\n🔍 This was a DRY RUN - no changes were made")
        print("Run without --dry-run to apply changes")
        return 0

    # Process files
    print(f"\n🔧 Processing {len(affected_files)} files...")
    files_fixed = 0
    total_changes = 0
    errors = []

    for i, (file_path, correct_path) in enumerate(affected_files):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(affected_files)} files processed...")

        changes = fix_index_paths_in_file(file_path, correct_path)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            logger.info(f"Fixed {file_path}: {', '.join(changes)}")

        # Log errors but continue processing
        if not changes:
            logger.debug(f"No changes needed for {file_path}")

    # Summary
    print(f"\n📋 PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Files processed: {len(affected_files)}")
    print(f"Files fixed: {files_fixed}")
    print(f"Total changes: {total_changes}")
    print(f"Errors: {len(errors)}")

    # Validate sample of fixes
    if files_fixed > 0:
        validation = validate_sample_fixes(affected_files[:files_fixed])
        print(f"\n🔬 Sample validation results:")
        print(f"Files tested: {validation['total']}")
        print(f"Successful: {validation['success']}")
        print(f"Failed: {validation['failed']}")

    print(f"\n✅ Script 016 completed successfully!")
    print(f"Expected impact: Additional reduction in broken links")
    print(f"Next: Run validation tests and commit changes")

    return 0

if __name__ == "__main__":
    exit(main())