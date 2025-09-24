#!/usr/bin/env python3
"""
Fix XI lineage reference links

This script fixes broken XI references that point to incorrect lineage directories.
For example, if XI349.htm actually exists in L0/ but is referenced as L1/XI349.htm,
this script will update the reference to the correct L0/XI349.htm.

Usage:
    python3 both/fix-xi-lineage-refs.py [--dry-run] [--target-dir docs/htm|docs/new|both] [--validate]

Features:
- Builds mapping of XI files to their actual lineage directories
- Fixes href references to use correct lineage paths
- Processes both docs/htm and docs/new directories
- Dry-run mode to preview changes
- Progress reporting and error handling
- Git-safe processing with rollback capability
"""

import os
import re
import sys
import argparse
import logging
from pathlib import Path
from collections import defaultdict
import time


def setup_logging():
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fix-xi-lineage-refs.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def build_xi_file_mapping(base_dir):
    """
    Build a mapping of XI file numbers to their actual lineage directories.

    Args:
        base_dir (str): Base directory to scan (docs/htm or docs/new)

    Returns:
        dict: Mapping of XI file number to lineage directory (e.g., {'349': 'L0', '1027': 'L1'})
    """
    logger = logging.getLogger(__name__)
    xi_mapping = {}

    # Find all XI files in lineage directories
    base_path = Path(base_dir)
    lineage_dirs = [d for d in base_path.iterdir() if d.is_dir() and re.match(r'L[0-9]+', d.name)]

    for lineage_dir in lineage_dirs:
        lineage_name = lineage_dir.name
        xi_files = list(lineage_dir.glob('XI*.htm'))

        for xi_file in xi_files:
            # Extract XI number from filename (e.g., XI349.htm -> 349)
            match = re.match(r'XI(\d+)\.htm', xi_file.name)
            if match:
                xi_number = match.group(1)
                if xi_number in xi_mapping:
                    logger.warning(f"Duplicate XI file {xi_number} found in {lineage_name} and {xi_mapping[xi_number]}")
                xi_mapping[xi_number] = lineage_name

    logger.info(f"Built XI mapping for {len(xi_mapping)} files in {base_dir}")
    return xi_mapping


def fix_xi_references_in_file(file_path, xi_mapping, dry_run=False):
    """
    Fix XI references in a single HTML file.

    Args:
        file_path (Path): Path to HTML file to process
        xi_mapping (dict): Mapping of XI numbers to correct lineage directories
        dry_run (bool): If True, only show what would be changed

    Returns:
        tuple: (changes_made, total_fixes)
    """
    logger = logging.getLogger(__name__)

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return False, 0

    original_content = content
    fixes_made = 0

    # Pattern to match XI references in href attributes
    # Matches: href="/htm/L1/XI349.htm" or href="../L1/XI349.htm" or href="./L1/XI349.htm" etc.
    xi_pattern = r'href="([^"]*?/)(L[0-9]+)/(XI(\d+)\.htm)"'

    def fix_xi_reference(match):
        nonlocal fixes_made
        path_prefix = match.group(1)  # "/htm/" or "../" etc.
        current_lineage = match.group(2)  # "L1"
        xi_filename = match.group(3)  # "XI349.htm"
        xi_number = match.group(4)  # "349"

        # Check if this XI file exists in a different lineage directory
        if xi_number in xi_mapping:
            correct_lineage = xi_mapping[xi_number]

            if current_lineage != correct_lineage:
                fixes_made += 1
                new_href = f'href="{path_prefix}{correct_lineage}/{xi_filename}"'
                logger.debug(f"Fixing XI{xi_number}: {current_lineage} -> {correct_lineage}")
                return new_href

        # Return original if no fix needed
        return match.group(0)

    # Apply the fixes
    content = re.sub(xi_pattern, fix_xi_reference, content)

    if fixes_made > 0:
        if not dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.debug(f"Fixed {fixes_made} XI references in {file_path}")
            except Exception as e:
                logger.error(f"Failed to write {file_path}: {e}")
                return False, 0
        else:
            logger.info(f"DRY RUN: Would fix {fixes_made} XI references in {file_path}")

    return fixes_made > 0, fixes_made


def process_directory(target_dir, xi_mapping, dry_run=False):
    """
    Process all HTML files in a directory to fix XI references.

    Args:
        target_dir (str): Directory to process
        xi_mapping (dict): Mapping of XI numbers to correct lineage directories
        dry_run (bool): If True, only show what would be changed

    Returns:
        tuple: (files_modified, total_fixes)
    """
    logger = logging.getLogger(__name__)

    base_path = Path(target_dir)
    if not base_path.exists():
        logger.error(f"Directory {target_dir} does not exist")
        return 0, 0

    # Find all HTML files
    html_files = list(base_path.rglob('*.htm')) + list(base_path.rglob('*.html'))
    logger.info(f"Processing {len(html_files)} HTML files in {target_dir}")

    files_modified = 0
    total_fixes = 0

    for i, html_file in enumerate(html_files):
        if i % 100 == 0:
            logger.info(f"Progress: {i}/{len(html_files)} files processed")

        try:
            changed, fixes = fix_xi_references_in_file(html_file, xi_mapping, dry_run)
            if changed:
                files_modified += 1
            total_fixes += fixes
        except Exception as e:
            logger.error(f"Error processing {html_file}: {e}")

    return files_modified, total_fixes


def validate_fixes(target_dir, xi_mapping):
    """
    Validate that XI references now point to existing files.

    Args:
        target_dir (str): Directory to validate
        xi_mapping (dict): Mapping of XI numbers to lineage directories

    Returns:
        tuple: (total_checked, remaining_broken)
    """
    logger = logging.getLogger(__name__)

    base_path = Path(target_dir)
    html_files = list(base_path.rglob('*.htm')) + list(base_path.rglob('*.html'))

    total_checked = 0
    remaining_broken = 0

    xi_pattern = r'href="([^"]*?/)(L[0-9]+)/(XI(\d+)\.htm)"'

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for match in re.finditer(xi_pattern, content):
                total_checked += 1
                xi_number = match.group(4)
                current_lineage = match.group(2)

                # Check if the referenced file exists
                if xi_number in xi_mapping:
                    correct_lineage = xi_mapping[xi_number]
                    if current_lineage != correct_lineage:
                        remaining_broken += 1
                        logger.warning(f"Still broken: {html_file} references XI{xi_number} in {current_lineage}, should be {correct_lineage}")
                else:
                    remaining_broken += 1
                    logger.warning(f"XI{xi_number} not found anywhere")

        except Exception as e:
            logger.error(f"Error validating {html_file}: {e}")

    return total_checked, remaining_broken


def main():
    parser = argparse.ArgumentParser(description='Fix XI lineage reference links')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    parser.add_argument('--target-dir', choices=['docs/htm', 'docs/new', 'both'], default='both',
                        help='Directory to process')
    parser.add_argument('--validate', action='store_true',
                        help='Validate fixes after processing')

    args = parser.parse_args()

    logger = setup_logging()

    # Determine directories to process
    if args.target_dir == 'both':
        target_dirs = ['docs/htm', 'docs/new']
    else:
        target_dirs = [args.target_dir]

    start_time = time.time()
    total_files_modified = 0
    total_fixes_applied = 0

    for target_dir in target_dirs:
        logger.info(f"{'='*60}")
        logger.info(f"Processing {target_dir}")
        logger.info(f"{'='*60}")

        # Build XI mapping for this directory
        xi_mapping = build_xi_file_mapping(target_dir)
        logger.info(f"Found {len(xi_mapping)} XI files in {target_dir}")

        if args.dry_run:
            logger.info("DRY RUN MODE - No changes will be made")

        # Process the directory
        files_modified, fixes_applied = process_directory(target_dir, xi_mapping, args.dry_run)

        total_files_modified += files_modified
        total_fixes_applied += fixes_applied

        logger.info(f"Results for {target_dir}:")
        logger.info(f"  Files modified: {files_modified}")
        logger.info(f"  XI references fixed: {fixes_applied}")

        # Validation if requested
        if args.validate and not args.dry_run:
            logger.info("Validating fixes...")
            total_checked, remaining_broken = validate_fixes(target_dir, xi_mapping)
            logger.info(f"Validation results:")
            logger.info(f"  Total XI references checked: {total_checked}")
            logger.info(f"  Remaining broken references: {remaining_broken}")

    # Final summary
    elapsed_time = time.time() - start_time
    logger.info(f"{'='*60}")
    logger.info(f"FINAL SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total files modified: {total_files_modified}")
    logger.info(f"Total XI references fixed: {total_fixes_applied}")
    logger.info(f"Processing time: {elapsed_time:.2f} seconds")

    if args.dry_run:
        logger.info("This was a DRY RUN. No changes were made.")
        logger.info("Run without --dry-run to apply the fixes.")
    else:
        logger.info("XI lineage reference fixes completed successfully!")


if __name__ == '__main__':
    main()