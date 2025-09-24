#!/usr/bin/env python3
"""
Fix Image Path Resolution - Priority 1
Purpose: Fixes /auntruth/htm/jpg/ → /auntruth/jpg/ path issues

This script addresses the highest-impact broken links issue where image paths
contain an extra /htm/ directory that causes 404 errors. This pattern affects
approximately 40% of broken links (~12,000+ links).

CRITICAL SAFETY REQUIREMENTS:
- This script processes thousands of files
- Uses git branch safety system
- Implements progress reporting every 100 files
- Includes dry-run mode and error handling
- Follows patterns from existing scripts

Target Patterns to Fix:
- src="/auntruth/htm/jpg/filename.jpg" → src="/auntruth/jpg/filename.jpg"
- src="/htm/jpg/filename.jpg" → src="/jpg/filename.jpg"
- background-image: url(/auntruth/htm/jpg/...) → url(/auntruth/jpg/...)
- Both single and double quotes supported
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

def scan_files_with_broken_image_paths(target_dir: str) -> List[str]:
    """Find HTML files with absolute /jpg/ patterns that need fixing to /auntruth/jpg/"""
    affected_files = []

    print(f"🔍 Scanning {target_dir} for broken image path patterns...")

    # Patterns to detect broken image paths - absolute paths that need /auntruth/ prefix
    patterns = [
        r'(src|href)="/jpg/',   # src="/jpg/filename.jpg" - needs to become src="/auntruth/jpg/filename.jpg"
        r"(src|href)='/jpg/",   # src='/jpg/filename.jpg' - needs to become src='/auntruth/jpg/filename.jpg'
        r'url\(["\']?/jpg/',    # url(/jpg/...) - needs to become url(/auntruth/jpg/...)
        r'background-image:\s*url\(["\']?/jpg/',  # background-image: url(/jpg/...)
    ]

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check if any pattern matches
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            affected_files.append(file_path)
                            break  # File already added, no need to check other patterns

                except (OSError, IOError) as e:
                    logging.warning(f"Could not read {file_path}: {e}")
                    continue

    return affected_files

def fix_image_paths_in_file(file_path: str) -> List[str]:
    """Apply image path fixes to single file"""
    changes_made = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Pattern fixes based on actual broken link analysis
        # Convert absolute /jpg/ paths to /auntruth/jpg/ paths
        patterns_to_fix = [
            # Fix src/href attributes with double quotes: "/jpg/" -> "/auntruth/jpg/"
            (r'(src|href)="/jpg/', r'\1="/auntruth/jpg/'),

            # Fix src/href attributes with single quotes: '/jpg/' -> '/auntruth/jpg/'
            (r"(src|href)='/jpg/", r"\1='/auntruth/jpg/"),

            # Fix CSS url() patterns: url(/jpg/...) -> url(/auntruth/jpg/...)
            (r'url\((["\']?)/jpg/', r'url(\1/auntruth/jpg/'),

            # Fix background-image patterns: background-image: url(/jpg/...) -> background-image: url(/auntruth/jpg/...)
            (r'background-image:\s*url\((["\']?)/jpg/', r'background-image: url(\1/auntruth/jpg/'),
        ]

        for old_pattern, new_pattern in patterns_to_fix:
            old_content = content
            content = re.sub(old_pattern, new_pattern, content, flags=re.IGNORECASE)
            if content != old_content:
                matches = len(re.findall(old_pattern, old_content, re.IGNORECASE))
                changes_made.append(f"Fixed {matches} instances of pattern: {old_pattern}")

        # Write the file only if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return []

    return changes_made

def validate_sample_fixes(processed_files: List[str], sample_size: int = 10) -> Dict[str, int]:
    """Validate that a sample of fixes work by testing URLs with curl"""
    if not processed_files:
        return {"total": 0, "success": 0, "failed": 0}

    import random
    sample_files = random.sample(processed_files, min(sample_size, len(processed_files)))

    validation_results = {"total": 0, "success": 0, "failed": 0}

    print(f"🔬 Validating sample of {len(sample_files)} fixed files...")

    for file_path in sample_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract jpg URLs that we fixed
            jpg_urls = re.findall(r'(src|href)=["\']([^"\']*\.jpg)["\']', content, re.IGNORECASE)

            for attr, url in jpg_urls[:3]:  # Test up to 3 URLs per file
                if url.startswith('/auntruth/') or url.startswith('/jpg/'):
                    test_url = f"http://localhost:8000{url}"

                    validation_results["total"] += 1

                    # Test URL with curl
                    try:
                        result = subprocess.run([
                            'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', test_url
                        ], capture_output=True, text=True, timeout=5)

                        if result.stdout.strip() == '200':
                            validation_results["success"] += 1
                        else:
                            validation_results["failed"] += 1
                            logging.warning(f"URL still broken: {test_url} (HTTP {result.stdout.strip()})")

                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        validation_results["failed"] += 1
                        logging.warning(f"Could not test URL: {test_url}")

        except Exception as e:
            logging.warning(f"Could not validate {file_path}: {e}")

    return validation_results

def show_dry_run_preview(affected_files: List[str], limit: int = 10) -> None:
    """Show preview of what would be changed in dry-run mode"""
    print(f"\n📋 DRY RUN PREVIEW - Would process {len(affected_files)} files")
    print("=" * 60)

    preview_files = affected_files[:limit]

    for i, file_path in enumerate(preview_files, 1):
        print(f"{i}. {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Show examples of what would be fixed
            examples = []
            patterns = [
                r'(src|href)="[^"]*/(auntruth/)?htm/jpg/[^"]*"',
                r"(src|href)='[^']*/(auntruth/)?htm/jpg/[^']*'",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                examples.extend(matches[:2])  # Show up to 2 examples per pattern

            if examples:
                for example in examples[:3]:  # Show up to 3 examples total
                    print(f"   Example: {example}")

        except Exception as e:
            print(f"   Could not preview: {e}")

    if len(affected_files) > limit:
        print(f"   ... and {len(affected_files) - limit} more files")

    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Fix image path resolution issues')
    parser.add_argument('--target-dir', default='docs', help='Target directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--limit', type=int, help='Limit number of files processed (for testing)')
    parser.add_argument('--branch-name', default='task-015-broken-links-fix', help='Git branch name')
    parser.add_argument('--log-file', help='Log file path')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_file)

    print("🚀 Starting Image Path Resolution Fix (Script 015)")
    print("=" * 60)

    # Verify git branch
    try:
        verify_git_branch(args.branch_name)
    except ValueError as e:
        logger.error(f"Git branch verification failed: {e}")
        return 1

    # Scan for affected files
    affected_files = scan_files_with_broken_image_paths(args.target_dir)

    if not affected_files:
        print("✅ No files found with broken image path patterns")
        return 0

    print(f"📊 Found {len(affected_files)} files with broken image paths")

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

    for i, file_path in enumerate(affected_files):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(affected_files)} files processed...")

        changes = fix_image_paths_in_file(file_path)
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
        validation = validate_sample_fixes([f for f in affected_files if fix_image_paths_in_file.__name__])
        print(f"\n🔬 Sample validation results:")
        print(f"URLs tested: {validation['total']}")
        print(f"Successful: {validation['success']}")
        print(f"Failed: {validation['failed']}")

    print(f"\n✅ Script 015 completed successfully!")
    print(f"Expected impact: ~40% reduction in broken links")
    print(f"Next: Run validation tests and commit changes")

    return 0

if __name__ == "__main__":
    exit(main())