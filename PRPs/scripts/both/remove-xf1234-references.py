#!/usr/bin/env python3
"""
Remove XF1234 Placeholder References - Phase 6B.1 Script

This script removes XF1234.htm placeholder references from HTML dropdown menus.
These entries represent missing person pages that were never created.

Problem: References to XF1234.htm create broken links in dropdown menus
Solution: Remove the entire <option> entry while preserving dropdown structure

Usage:
    python3 remove-xf1234-references.py --site=htm --dry-run    # Preview HTM site
    python3 remove-xf1234-references.py --site=new --dry-run    # Preview NEW site
    python3 remove-xf1234-references.py --site=both --dry-run   # Preview both sites
    python3 remove-xf1234-references.py --site=htm             # Clean HTM site
    python3 remove-xf1234-references.py --site=new            # Clean NEW site
    python3 remove-xf1234-references.py --site=both           # Clean both sites

Features:
- Removes complete <option value="*/XF1234.htm">...</option> entries
- Preserves surrounding dropdown structure
- Dry-run mode for preview
- Progress reporting and error handling
- Git branch verification

Safety Features:
- Git branch verification
- Dry-run mode
- Progress reporting
- Error handling with detailed logging
"""

import os
import sys
import argparse
import subprocess
import logging
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

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

def get_html_files_with_xf1234(base_path: str) -> List[Path]:
    """Get list of HTML files that reference XF1234."""
    base = Path(base_path)
    html_files = []

    # Find all .htm files recursively
    for html_file in base.glob('**/*.htm'):
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'XF1234' in content:
                    html_files.append(html_file)
        except Exception as e:
            logging.warning(f"Could not read {html_file}: {e}")
            continue

    return sorted(html_files)

def remove_xf1234_entries(content: str) -> Tuple[str, int]:
    """
    Remove XF1234.htm references from HTML content.

    The pattern is:
    <option value="/auntruth/*/XF1234.htm">
        Person Name [Family]
    </option>

    Returns:
        Tuple of (modified_content, number_of_removals)
    """

    # Pattern to match the complete option entry with XF1234
    # This matches across multiple lines and captures the complete option element
    option_pattern = r'<option\s+value="[^"]*XF1234\.htm"[^>]*>.*?</option>'

    # Count matches before removal
    matches = list(re.finditer(option_pattern, content, re.IGNORECASE | re.DOTALL))
    removal_count = len(matches)

    if removal_count == 0:
        return content, 0

    # Remove all XF1234 option entries
    modified_content = re.sub(option_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)

    # Clean up any double newlines that might result
    modified_content = re.sub(r'\n\s*\n\s*\n', '\n\n', modified_content)

    return modified_content, removal_count

def process_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, str, int]:
    """
    Process a single HTML file to remove XF1234 references.

    Returns:
        Tuple of (success: bool, message: str, removals_count: int)
    """
    try:
        # Read original content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        # Remove XF1234 entries
        modified_content, removal_count = remove_xf1234_entries(original_content)

        if removal_count == 0:
            return True, f"No XF1234 references found in {file_path}", 0

        if dry_run:
            return True, f"Would remove {removal_count} XF1234 entries from {file_path}", removal_count

        # Write modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        return True, f"✅ Removed {removal_count} XF1234 entries from {file_path}", removal_count

    except Exception as e:
        return False, f"❌ Error processing {file_path}: {e}", 0

def process_site(site_dir: str, dry_run: bool = False) -> Dict[str, Any]:
    """Process all HTML files in a site directory."""
    logger = logging.getLogger(__name__)

    if not os.path.exists(site_dir):
        return {
            'success': False,
            'message': f"Directory {site_dir} does not exist",
            'files_processed': 0,
            'files_successful': 0,
            'files_failed': 0,
            'total_removals': 0
        }

    html_files = get_html_files_with_xf1234(site_dir)

    if not html_files:
        return {
            'success': True,
            'message': f"No files with XF1234 references found in {site_dir}",
            'files_processed': 0,
            'files_successful': 0,
            'files_failed': 0,
            'total_removals': 0
        }

    logger.info(f"Found {len(html_files)} files with XF1234 references in {site_dir}")

    successful = 0
    failed = 0
    total_removals = 0
    failed_files = []

    for i, html_file in enumerate(html_files, 1):
        logger.info(f"[{i}/{len(html_files)}] Processing {html_file}")

        success, message, removal_count = process_file(html_file, dry_run)
        total_removals += removal_count

        if success:
            successful += 1
            logger.info(message)
        else:
            failed += 1
            failed_files.append(str(html_file))
            logger.error(message)

    result = {
        'success': failed == 0,
        'message': f"Processed {len(html_files)} files: {successful} successful, {failed} failed, {total_removals} total removals",
        'files_processed': len(html_files),
        'files_successful': successful,
        'files_failed': failed,
        'failed_files': failed_files,
        'total_removals': total_removals
    }

    action = "Would remove" if dry_run else "Removed"
    if not dry_run:
        logger.info(f"✅ Site {site_dir} processing complete: {result['message']}")
    else:
        logger.info(f"🔍 Dry-run for {site_dir}: {action} {total_removals} XF1234 references from {len(html_files)} files")

    return result

def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(
        description='Remove XF1234.htm references from HTML dropdown menus'
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
    total_removals = 0

    for site_dir in site_dirs:
        logger.info(f"{'🔍 Dry-run for' if args.dry_run else '🧹 Cleaning'} {site_dir}")

        result = process_site(site_dir, args.dry_run)

        if not result['success']:
            overall_success = False
            logger.error(f"❌ Failed processing {site_dir}: {result['message']}")

        total_processed += result['files_processed']
        total_successful += result['files_successful']
        total_failed += result['files_failed']
        total_removals += result['total_removals']

        if result['failed_files']:
            logger.error(f"Failed files in {site_dir}:")
            for failed_file in result['failed_files']:
                logger.error(f"  - {failed_file}")

    # Final summary
    action = "Would remove" if args.dry_run else "Removed"
    logger.info(f"\n📊 Final Summary:")
    logger.info(f"  Files processed: {total_processed}")
    logger.info(f"  Files successful: {total_successful}")
    logger.info(f"  Files failed: {total_failed}")
    logger.info(f"  XF1234 entries {action.lower()}: {total_removals}")

    if args.dry_run:
        logger.info(f"\n🔍 This was a dry-run. To actually remove XF1234 references, run without --dry-run")
    elif overall_success:
        logger.info(f"\n✅ All XF1234 references cleaned successfully!")
        logger.info(f"📝 Next steps:")
        logger.info(f"  1. Review the cleaned files in your browser")
        logger.info(f"  2. Commit changes: git add . && git commit -m 'Remove XF1234.htm references - cleaned {total_removals} broken dropdown entries'")
    else:
        logger.error(f"\n❌ Some files failed processing. Review the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()