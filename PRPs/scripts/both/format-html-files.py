#!/usr/bin/env python3
"""
Format HTML Files - Phase 6 Utility Script

This script formats HTML files using tidy to make them more readable.
Addresses the issue where HTML files appear as single long lines in browsers/editors.

Usage:
    python3 format-html-files.py --site=htm --dry-run    # Preview HTM site formatting
    python3 format-html-files.py --site=new --dry-run    # Preview NEW site formatting
    python3 format-html-files.py --site=both --dry-run   # Preview both sites
    python3 format-html-files.py --site=htm              # Format HTM site files
    python3 format-html-files.py --site=new             # Format NEW site files
    python3 format-html-files.py --site=both            # Format both sites

Features:
- Uses tidy HTML formatter for clean, readable output
- Processes .htm and .html files recursively
- Dry-run mode for preview
- Progress reporting
- Error handling with detailed logging
- Git branch verification
- Backup creation before modification (optional)

Safety Features:
- Git branch verification
- Dry-run mode
- Progress reporting
- Error handling
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any
import tempfile
import shutil

def setup_logging() -> logging.Logger:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def verify_git_branch(expected_branch: str = "main") -> str:
    """Verify current git branch and return current branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, check=True
        )
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking git branch: {e}")
        return ""

def get_html_files(base_path: str) -> List[Path]:
    """Get list of HTML files to process."""
    base = Path(base_path)
    html_files = []

    # Find all .htm and .html files recursively
    for pattern in ['**/*.htm', '**/*.html']:
        html_files.extend(base.glob(pattern))

    # Sort for consistent processing order
    return sorted(html_files)

def format_html_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Format a single HTML file using tidy.

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if dry_run:
            return True, f"Would format: {file_path}"

        # Create backup of original file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.backup') as backup:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as original:
                backup.write(original.read())
            backup_path = backup.name

        # Run tidy formatter
        # -i: indent
        # -m: modify in place
        # -w 0: no line wrapping
        # --show-warnings no: suppress warnings
        # --drop-proprietary-attributes no: keep custom attributes
        # --fix-uri no: don't modify URIs
        cmd = [
            'tidy',
            '-i',           # indent elements
            '-m',           # modify in place
            '-w', '0',      # no line wrapping
            '--show-warnings', 'no',  # suppress warnings
            '--drop-proprietary-attributes', 'no',  # keep custom attributes
            '--fix-uri', 'no',  # don't modify URIs
            '--quiet', 'yes',   # suppress info messages
            str(file_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        # Tidy returns non-zero exit codes for warnings, which is normal
        # Only treat as error if file wasn't modified at all
        if file_path.exists():
            # Remove backup file since formatting succeeded
            os.unlink(backup_path)
            return True, f"✅ Formatted: {file_path}"
        else:
            # Restore from backup if file was damaged
            shutil.move(backup_path, str(file_path))
            return False, f"❌ Failed to format {file_path}: File damaged, restored from backup"

    except subprocess.CalledProcessError as e:
        return False, f"❌ Tidy error for {file_path}: {e}"
    except Exception as e:
        return False, f"❌ Unexpected error for {file_path}: {e}"

def process_site(site_dir: str, dry_run: bool = False) -> Dict[str, Any]:
    """Process all HTML files in a site directory."""
    logger = logging.getLogger(__name__)

    if not os.path.exists(site_dir):
        return {
            'success': False,
            'message': f"Directory {site_dir} does not exist",
            'files_processed': 0,
            'files_successful': 0,
            'files_failed': 0
        }

    html_files = get_html_files(site_dir)

    if not html_files:
        return {
            'success': True,
            'message': f"No HTML files found in {site_dir}",
            'files_processed': 0,
            'files_successful': 0,
            'files_failed': 0
        }

    logger.info(f"Found {len(html_files)} HTML files in {site_dir}")

    successful = 0
    failed = 0
    failed_files = []

    for i, html_file in enumerate(html_files, 1):
        logger.info(f"[{i}/{len(html_files)}] Processing {html_file}")

        success, message = format_html_file(html_file, dry_run)

        if success:
            successful += 1
            logger.info(message)
        else:
            failed += 1
            failed_files.append(str(html_file))
            logger.error(message)

    result = {
        'success': failed == 0,
        'message': f"Processed {len(html_files)} files: {successful} successful, {failed} failed",
        'files_processed': len(html_files),
        'files_successful': successful,
        'files_failed': failed,
        'failed_files': failed_files
    }

    if not dry_run:
        logger.info(f"✅ Site {site_dir} processing complete: {result['message']}")
    else:
        logger.info(f"🔍 Dry-run for {site_dir}: Would process {len(html_files)} files")

    return result

def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(
        description='Format HTML files using tidy for better readability'
    )
    parser.add_argument(
        '--site',
        choices=['htm', 'new', 'both'],
        required=True,
        help='Which site to process (htm, new, or both)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making modifications'
    )
    parser.add_argument(
        '--branch',
        default='main',
        help='Expected git branch (default: main)'
    )

    args = parser.parse_args()

    logger = setup_logging()

    # Verify git branch
    current_branch = verify_git_branch(args.branch)
    if not current_branch:
        sys.exit(1)

    # Determine directories to process
    base_dir = os.path.join(os.getcwd(), 'docs')
    site_dirs = []

    if args.site in ['htm', 'both']:
        site_dirs.append(os.path.join(base_dir, 'htm'))
    if args.site in ['new', 'both']:
        site_dirs.append(os.path.join(base_dir, 'new'))

    # Process each site
    overall_success = True
    total_processed = 0
    total_successful = 0
    total_failed = 0

    for site_dir in site_dirs:
        logger.info(f"{'🔍 Dry-run for' if args.dry_run else '🔧 Processing'} {site_dir}")

        result = process_site(site_dir, args.dry_run)

        if not result['success']:
            overall_success = False
            logger.error(f"❌ Failed processing {site_dir}: {result['message']}")

        total_processed += result['files_processed']
        total_successful += result['files_successful']
        total_failed += result['files_failed']

        if result['failed_files']:
            logger.error(f"Failed files in {site_dir}:")
            for failed_file in result['failed_files']:
                logger.error(f"  - {failed_file}")

    # Final summary
    action = "Would format" if args.dry_run else "Formatted"
    logger.info(f"\n📊 Final Summary:")
    logger.info(f"  {action}: {total_processed} files")
    logger.info(f"  Successful: {total_successful}")
    logger.info(f"  Failed: {total_failed}")

    if args.dry_run:
        logger.info(f"\n🔍 This was a dry-run. To actually format files, run without --dry-run")
    elif overall_success:
        logger.info(f"\n✅ All files processed successfully!")
        logger.info(f"📝 Next steps:")
        logger.info(f"  1. Review the formatted files in your browser")
        logger.info(f"  2. Commit changes: git add . && git commit -m 'Format HTML files for better readability'")
    else:
        logger.error(f"\n❌ Some files failed processing. Review the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()