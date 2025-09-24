#!/usr/bin/env python3
"""
Fix Extension Case References Script
===================================

This script fixes references to files with uppercase extensions in HTML files.
It complements the normalize-file-extensions.py script by updating the content
references that the original script failed to properly update due to a regex bug.

Fixes:
- .JPG -> .jpg (broken images)
- .HTM -> .htm (broken links)
- .HTML -> .html
- .PNG -> .png
- .GIF -> .gif
- .CSS -> .css
- .JS -> .js
- .PDF -> .pdf
- .AU -> .au
- .MPG -> .mpg

Usage:
    python3 fix-extension-case-references.py [--target-dir docs] [--dry-run] [--execute]
"""

import os
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def get_extensions_to_fix() -> List[str]:
    """Return list of uppercase extensions that need to be lowercased"""
    return [
        'HTM', 'HTML', 'SHTML',
        'JPG', 'JPEG', 'PNG', 'GIF', 'BMP', 'TIFF', 'WEBP',
        'CSS', 'JS', 'JSON',
        'PDF', 'DOC', 'DOCX', 'TXT',
        'AU', 'MP3', 'WAV', 'OGG', 'MPG',
        'ZIP', 'RAR', 'TAR', 'GZ'
    ]

def create_fix_patterns() -> List[Tuple[re.Pattern, str]]:
    """
    Create regex patterns to find and fix uppercase extension references
    Returns list of (compiled_pattern, replacement_template) tuples
    """
    extensions = get_extensions_to_fix()
    patterns = []

    for ext_upper in extensions:
        ext_lower = ext_upper.lower()

        # Pattern to match file references in various HTML attributes
        # Matches: href="file.HTM", src="image.JPG", url("style.CSS"), etc.
        # Uses word boundaries and specific uppercase match (no IGNORECASE flag)
        pattern_str = rf'((?:href|src|url|content|action|value)\s*=\s*["\']?[^"\'>\s]*?)\.{ext_upper}\b(["\']?[>\s])'

        pattern = re.compile(pattern_str)
        replacement = rf'\1.{ext_lower}\2'

        patterns.append((pattern, replacement))

    return patterns

def find_html_files(target_dir: str) -> List[str]:
    """Find all HTML files in target directory"""
    html_files = []

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))

    return sorted(html_files)

def fix_extensions_in_file(file_path: str, patterns: List[Tuple[re.Pattern, str]], dry_run: bool = True) -> Dict[str, int]:
    """
    Fix extension case in a single file
    Returns dict with statistics about changes made
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        logging.warning(f"Could not read {file_path}: {e}")
        return {'error': 1, 'total_changes': 0}

    original_content = content
    total_changes = 0
    changes_by_extension = {}

    # Apply each pattern
    for pattern, replacement in patterns:
        matches = pattern.findall(content)
        if matches:
            extension = pattern.pattern.split('\\.')[-1].split('\\b')[0]  # Extract extension from pattern
            changes_count = len(matches)
            changes_by_extension[extension] = changes_count
            total_changes += changes_count

            # Apply the replacement
            content = pattern.sub(replacement, content)

    # Write changes if not in dry run mode
    if total_changes > 0 and not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Could not write {file_path}: {e}")
            return {'error': 1, 'total_changes': 0}

    result = {
        'total_changes': total_changes,
        'changes_by_extension': changes_by_extension,
        'error': 0
    }

    return result

def main():
    """Main function to fix extension case references"""
    parser = argparse.ArgumentParser(description='Fix uppercase extension references in HTML files')
    parser.add_argument('--target-dir', default='docs', help='Target directory to process (default: docs)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--execute', action='store_true', help='Execute the fixes')
    parser.add_argument('--test-file', help='Test on a single file only')

    args = parser.parse_args()

    logger = setup_logging()

    # Convert to absolute path
    target_dir = Path(args.target_dir).resolve()
    if not target_dir.exists():
        logger.error(f"Target directory {target_dir} does not exist")
        return 1

    logger.info(f"=== Fix Extension Case References ===")
    logger.info(f"Target directory: {target_dir}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create patterns
    patterns = create_fix_patterns()
    logger.info(f"Created {len(patterns)} extension fix patterns")

    # Find files to process
    if args.test_file:
        if os.path.exists(args.test_file):
            html_files = [args.test_file]
        else:
            logger.error(f"Test file {args.test_file} does not exist")
            return 1
    else:
        html_files = find_html_files(str(target_dir))

    logger.info(f"Found {len(html_files)} HTML files to process")

    if len(html_files) == 0:
        logger.info("No HTML files found. Exiting.")
        return 0

    # Process files
    if args.dry_run:
        logger.info(f"\n=== DRY RUN MODE ===")
        logger.info("Scanning for files that need extension case fixes...")
    else:
        if not args.execute:
            logger.info("\nNo action specified. Use --dry-run to preview or --execute to apply changes.")
            return 0
        logger.info(f"\n=== EXECUTING FIXES ===")

    total_files_with_changes = 0
    total_changes_made = 0
    extension_stats = {}

    for i, file_path in enumerate(html_files):
        if i % 100 == 0 and i > 0:
            logger.info(f"Progress: {i}/{len(html_files)} files processed")

        result = fix_extensions_in_file(file_path, patterns, dry_run=args.dry_run or not args.execute)

        if result['error']:
            continue

        if result['total_changes'] > 0:
            total_files_with_changes += 1
            total_changes_made += result['total_changes']

            # Aggregate extension stats
            for ext, count in result['changes_by_extension'].items():
                extension_stats[ext] = extension_stats.get(ext, 0) + count

            if args.dry_run or args.test_file:
                rel_path = os.path.relpath(file_path, target_dir)
                changes_summary = ', '.join([f"{ext}: {count}" for ext, count in result['changes_by_extension'].items()])
                logger.info(f"Would fix {rel_path}: {changes_summary}")

    # Summary
    logger.info(f"\n=== SUMMARY ===")
    logger.info(f"Files processed: {len(html_files)}")
    logger.info(f"Files needing changes: {total_files_with_changes}")
    logger.info(f"Total changes {'would be made' if args.dry_run or not args.execute else 'made'}: {total_changes_made}")

    if extension_stats:
        logger.info("Changes by extension:")
        for ext in sorted(extension_stats.keys()):
            logger.info(f"  .{ext} -> .{ext.lower()}: {extension_stats[ext]} references")

    if args.dry_run:
        logger.info(f"\nTo execute these changes, run with --execute")

    return 0

if __name__ == "__main__":
    exit(main())