#!/usr/bin/env python3
"""
Normalize File Extensions Script

This script normalizes all file extensions to lowercase in docs/htm and docs/new directories:
1. Renames files with uppercase extensions (e.g., .HTM -> .htm, .JPG -> .jpg)
2. Updates all references inside files to use lowercase extensions

Common extensions handled: .HTM, .HTML, .JPG, .JPEG, .PNG, .GIF, .CSS, .JS, .PDF, .AU, .MP3
"""

import os
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
import shutil
from datetime import datetime

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

def get_file_extensions_to_normalize() -> List[str]:
    """Return list of file extensions that should be normalized to lowercase"""
    return [
        '.HTM', '.HTML', '.SHTML',
        '.JPG', '.JPEG', '.PNG', '.GIF', '.BMP', '.TIFF', '.WEBP',
        '.CSS', '.JS', '.JSON',
        '.PDF', '.DOC', '.DOCX', '.TXT',
        '.AU', '.MP3', '.WAV', '.OGG',
        '.ZIP', '.RAR', '.TAR', '.GZ'
    ]

def scan_files_needing_rename(target_dir: str) -> Tuple[Dict[str, str], List[Dict]]:
    """
    Scan directory for files with uppercase extensions that need renaming
    Returns tuple of (rename_map, collisions_list)

    rename_map: dict mapping old_path -> new_path (only files without collisions)
    collisions_list: list of collision info dicts for logging
    """
    extensions_to_fix = get_file_extensions_to_normalize()
    rename_map = {}
    collisions = []

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_obj = Path(file_path)

            if file_obj.suffix.upper() in extensions_to_fix:
                new_name = file_obj.stem + file_obj.suffix.lower()
                new_path = os.path.join(root, new_name)

                if file_path != new_path:  # Only if change is needed
                    if os.path.exists(new_path):
                        # Collision detected - need to decide which file to keep
                        collision = handle_collision(file_path, new_path)
                        collisions.append(collision)

                        # If we decided to keep the uppercase file, add to rename map
                        if collision['action'] == 'rename_uppercase':
                            rename_map[file_path] = new_path
                    else:
                        # No collision, safe to rename
                        rename_map[file_path] = new_path

    return rename_map, collisions

def handle_collision(uppercase_file: str, lowercase_file: str) -> Dict:
    """
    Handle collision between uppercase and lowercase versions of same file.
    Returns collision info dict with decision.

    Strategy: Keep the newer file (by modification time)
    """
    try:
        uppercase_stat = os.stat(uppercase_file)
        lowercase_stat = os.stat(lowercase_file)

        uppercase_time = uppercase_stat.st_mtime
        lowercase_time = lowercase_stat.st_mtime
        uppercase_size = uppercase_stat.st_size
        lowercase_size = lowercase_stat.st_size

        # Decision: keep newer file
        if uppercase_time > lowercase_time:
            # Uppercase is newer - rename it and delete lowercase
            action = 'rename_uppercase'
            keep_file = uppercase_file
            delete_file = lowercase_file
            reason = f"uppercase newer ({datetime.fromtimestamp(uppercase_time)} vs {datetime.fromtimestamp(lowercase_time)})"
        else:
            # Lowercase is newer - keep it, delete uppercase
            action = 'keep_lowercase'
            keep_file = lowercase_file
            delete_file = uppercase_file
            reason = f"lowercase newer ({datetime.fromtimestamp(lowercase_time)} vs {datetime.fromtimestamp(uppercase_time)})"

        collision_info = {
            'uppercase_file': uppercase_file,
            'lowercase_file': lowercase_file,
            'action': action,
            'keep_file': keep_file,
            'delete_file': delete_file,
            'reason': reason,
            'uppercase_time': datetime.fromtimestamp(uppercase_time).isoformat(),
            'lowercase_time': datetime.fromtimestamp(lowercase_time).isoformat(),
            'uppercase_size': uppercase_size,
            'lowercase_size': lowercase_size,
            'size_diff': uppercase_size - lowercase_size
        }

        return collision_info

    except Exception as e:
        # Fallback: keep lowercase if we can't determine
        return {
            'uppercase_file': uppercase_file,
            'lowercase_file': lowercase_file,
            'action': 'keep_lowercase',
            'keep_file': lowercase_file,
            'delete_file': uppercase_file,
            'reason': f"error comparing files: {e}",
            'error': str(e)
        }

def scan_text_files_for_references(target_dir: str) -> List[str]:
    """
    Find all text files that might contain references to update
    """
    text_files = []
    text_extensions = {'.htm', '.html', '.css', '.js', '.json', '.txt', '.md'}

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_obj = Path(file_path)

            if file_obj.suffix.lower() in text_extensions:
                text_files.append(file_path)

    return text_files

def create_reference_patterns() -> List[tuple]:
    """
    Create regex patterns to find and fix references in text files
    Returns list of (pattern, replacement_function) tuples
    """
    extensions = get_file_extensions_to_normalize()
    patterns = []

    for ext in extensions:
        ext_lower = ext.lower()
        ext_upper = ext.upper()

        # Pattern for file references (href, src, url attributes)
        # Matches: href="file.HTM", src="image.JPG", etc.
        pattern = re.compile(
            rf'((?:href|src|url|content)\s*=\s*["\']?)([^"\'>\s]*?){re.escape(ext_upper)}(["\']?)',
            re.IGNORECASE
        )

        def make_replacement(lower_ext):
            def replacement(match):
                return match.group(1) + match.group(2) + lower_ext + match.group(3)
            return replacement

        patterns.append((pattern, make_replacement(ext_lower)))

    return patterns

def backup_file(file_path: str) -> str:
    """Create backup of file before modification"""
    backup_path = file_path + '.backup'
    shutil.copy2(file_path, backup_path)
    return backup_path

def update_references_in_file(file_path: str, patterns: List[tuple], dry_run: bool = False) -> int:
    """
    Update file extension references in a single file
    Returns number of changes made
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        logging.warning(f"Could not read {file_path}: {e}")
        return 0

    original_content = content
    changes_made = 0

    for pattern, replacement_func in patterns:
        new_content = pattern.sub(replacement_func, content)
        if new_content != content:
            changes_count = len(pattern.findall(content))
            changes_made += changes_count
            content = new_content

    if changes_made > 0 and not dry_run:
        try:
            # Create backup
            backup_file(file_path)

            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            logging.error(f"Could not update {file_path}: {e}")
            return 0

    return changes_made

def process_collisions(collisions: List[Dict], dry_run: bool = False) -> int:
    """
    Process file collisions by deleting the older file
    Returns number of files deleted
    """
    deleted_count = 0

    for collision in collisions:
        delete_file = collision['delete_file']
        action = collision['action']
        reason = collision['reason']

        if not dry_run:
            try:
                os.remove(delete_file)
                logging.info(f"Deleted {delete_file} - {reason}")
                deleted_count += 1
            except Exception as e:
                logging.error(f"Could not delete {delete_file}: {e}")
                collision['deletion_error'] = str(e)
        else:
            logging.info(f"Would delete {delete_file} - {reason}")
            deleted_count += 1

    return deleted_count

def save_collision_report(collisions: List[Dict], target_dirs: List[str]) -> str:
    """
    Save collision report to PRPs/scripts/reports directory
    Returns path to report file
    """
    # Create reports directory if it doesn't exist
    reports_dir = "PRPs/scripts/reports"
    os.makedirs(reports_dir, exist_ok=True)

    # Generate report filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(reports_dir, f"file_collision_report_{timestamp}.csv")

    # Write CSV report
    import csv
    with open(report_file, 'w', newline='', encoding='utf-8') as f:
        if collisions:
            writer = csv.DictWriter(f, fieldnames=collisions[0].keys())
            writer.writeheader()
            writer.writerows(collisions)
        else:
            # Empty report
            f.write("# No file collisions detected\n")
            f.write(f"# Scanned directories: {', '.join(target_dirs)}\n")
            f.write(f"# Scan time: {datetime.now().isoformat()}\n")

    return report_file

def rename_files(rename_map: Dict[str, str], dry_run: bool = False) -> int:
    """
    Rename files according to rename_map
    Returns number of files renamed
    """
    renamed_count = 0

    for old_path, new_path in rename_map.items():
        if os.path.exists(new_path):
            logging.warning(f"Target file already exists, skipping: {new_path}")
            continue

        if not dry_run:
            try:
                os.rename(old_path, new_path)
                logging.info(f"Renamed: {old_path} -> {new_path}")
                renamed_count += 1
            except Exception as e:
                logging.error(f"Could not rename {old_path} to {new_path}: {e}")
        else:
            logging.info(f"Would rename: {old_path} -> {new_path}")
            renamed_count += 1

    return renamed_count

def main():
    parser = argparse.ArgumentParser(description='Normalize file extensions to lowercase')
    parser.add_argument('--target-dir', default='docs', help='Target directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--files-only', action='store_true', help='Only rename files, do not update references')
    parser.add_argument('--refs-only', action='store_true', help='Only update references, do not rename files')
    parser.add_argument('--log-file', help='Log file path')
    parser.add_argument('--limit', type=int, help='Limit number of files to process (for testing)')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_file)

    if args.dry_run:
        logger.info("=== DRY RUN MODE - No changes will be made ===")

    # Determine target directories
    target_dirs = []

    # If target_dir is exactly one of our special directories, use it directly
    if args.target_dir.endswith('jpg') or args.target_dir.endswith('htm') or args.target_dir.endswith('new'):
        if os.path.exists(args.target_dir):
            target_dirs.append(args.target_dir)
    else:
        # Look for subdirectories
        if os.path.exists(os.path.join(args.target_dir, 'htm')):
            target_dirs.append(os.path.join(args.target_dir, 'htm'))
        if os.path.exists(os.path.join(args.target_dir, 'new')):
            target_dirs.append(os.path.join(args.target_dir, 'new'))
        if os.path.exists(os.path.join(args.target_dir, 'jpg')):
            target_dirs.append(os.path.join(args.target_dir, 'jpg'))

    if not target_dirs:
        logger.error(f"No valid target directories found in {args.target_dir}")
        return

    logger.info(f"Processing directories: {target_dirs}")

    total_files_renamed = 0
    total_references_updated = 0
    total_files_with_ref_changes = 0
    total_collisions_processed = 0
    all_collisions = []

    # Phase 1: Rename files (if not refs-only)
    if not args.refs_only:
        logger.info("=== Phase 1: Scanning for files to rename ===")
        all_rename_map = {}

        for target_dir in target_dirs:
            rename_map, collisions = scan_files_needing_rename(target_dir)
            all_rename_map.update(rename_map)
            all_collisions.extend(collisions)

        logger.info(f"Found {len(all_rename_map)} files that need renaming")
        logger.info(f"Found {len(all_collisions)} file collisions to resolve")

        # Save collision report
        if all_collisions:
            report_file = save_collision_report(all_collisions, target_dirs)
            logger.info(f"Collision report saved to: {report_file}")

        if args.limit:
            limited_rename_map = dict(list(all_rename_map.items())[:args.limit])
            all_rename_map = limited_rename_map
            # Also limit collisions for testing
            limited_collisions = all_collisions[:args.limit] if all_collisions else []
            all_collisions = limited_collisions
            logger.info(f"Limited to {len(all_rename_map)} renames and {len(all_collisions)} collisions for testing")

        # Process collisions first (delete older files)
        if all_collisions:
            logger.info("=== Phase 1a: Processing file collisions ===")
            if args.dry_run:
                logger.info("Collisions that would be resolved:")
                for collision in all_collisions[:5]:
                    logger.info(f"  Keep: {collision['keep_file']}")
                    logger.info(f"  Delete: {collision['delete_file']} - {collision['reason']}")
                if len(all_collisions) > 5:
                    logger.info(f"  ... and {len(all_collisions) - 5} more collisions")

            total_collisions_processed = process_collisions(all_collisions, args.dry_run)
            logger.info(f"Collisions processed: {total_collisions_processed}")

        # Then rename the remaining files
        if all_rename_map:
            logger.info("=== Phase 1b: Renaming files ===")
            if args.dry_run:
                logger.info("Files that would be renamed:")
                for old_path, new_path in list(all_rename_map.items())[:10]:
                    logger.info(f"  {old_path} -> {new_path}")
                if len(all_rename_map) > 10:
                    logger.info(f"  ... and {len(all_rename_map) - 10} more files")

            total_files_renamed = rename_files(all_rename_map, args.dry_run)
            logger.info(f"Files renamed: {total_files_renamed}")

    # Phase 2: Update references (if not files-only)
    if not args.files_only:
        logger.info("=== Phase 2: Updating references in text files ===")

        # Create reference patterns
        patterns = create_reference_patterns()

        # Find all text files to process
        all_text_files = []
        for target_dir in target_dirs:
            text_files = scan_text_files_for_references(target_dir)
            all_text_files.extend(text_files)

        logger.info(f"Found {len(all_text_files)} text files to scan for references")

        if args.limit:
            all_text_files = all_text_files[:args.limit]
            logger.info(f"Limited to {len(all_text_files)} files for testing")

        # Process each text file
        for i, file_path in enumerate(all_text_files):
            if i % 100 == 0:
                logger.info(f"Processing references: {i}/{len(all_text_files)} files")

            changes = update_references_in_file(file_path, patterns, args.dry_run)
            if changes > 0:
                total_references_updated += changes
                total_files_with_ref_changes += 1
                if args.dry_run:
                    logger.info(f"Would update {changes} references in {file_path}")

        logger.info(f"Files with reference changes: {total_files_with_ref_changes}")
        logger.info(f"Total references updated: {total_references_updated}")

    # Summary
    logger.info("=== SUMMARY ===")
    if not args.refs_only:
        logger.info(f"File collisions processed: {total_collisions_processed}")
        logger.info(f"Files renamed: {total_files_renamed}")
    if not args.files_only:
        logger.info(f"Files with reference updates: {total_files_with_ref_changes}")
        logger.info(f"Total references updated: {total_references_updated}")

    if args.dry_run:
        logger.info("This was a dry run - no actual changes were made")
        logger.info("Run without --dry-run to apply changes")
    else:
        if all_collisions:
            logger.info(f"Collision report available at: {report_file}")

if __name__ == "__main__":
    main()