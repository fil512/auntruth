#!/usr/bin/env python3
"""
Cleanup Missing Media Files - Priority 3
Removes/replaces references to missing media files (.pps, .avi, .wmz, etc.)

Based on analysis of broken link reports showing missing media file references.
Pattern Source: Analysis of remaining broken links for missing media
Target: ~500+ missing media references
"""

import argparse
import os
import re
import logging
from pathlib import Path
from datetime import datetime
import subprocess

def setup_logging_and_args():
    """Setup logging and parse command line arguments"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    parser = argparse.ArgumentParser(description="Cleanup missing media file references")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--target-dir", default="docs", help="Target directory to process (default: docs)")
    parser.add_argument("--limit", type=int, help="Limit number of files processed (for testing)")
    parser.add_argument("--branch-name", default="task-015-broken-links-fix", help="Git branch name")
    parser.add_argument("--remove-missing", action="store_true", help="Remove links to missing media files")

    return parser.parse_args()

def scan_files_with_media_references(target_dir):
    """Find HTML files with references to media files"""
    logging.info(f"Scanning for files with media references in {target_dir}")

    affected_files = []
    html_files = []

    # Find all HTML files
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))

    logging.info(f"Scanning {len(html_files)} HTML files for media file references")

    # Patterns to detect media file references
    media_patterns = [
        r'\.(pps|avi|wmz|wmf|asf|mov|mp4|mpg|mpeg|wav|mp3|wma)"',    # Common media extensions in href/src
        r'\.(PPS|AVI|WMZ|WMF|ASF|MOV|MP4|MPG|MPEG|WAV|MP3|WMA)"',   # Uppercase versions
    ]

    combined_pattern = re.compile('|'.join(media_patterns), re.IGNORECASE)

    for i, file_path in enumerate(html_files):
        if i % 1000 == 0:
            logging.info(f"  Progress: {i}/{len(html_files)} files scanned...")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if combined_pattern.search(content):
                    affected_files.append(file_path)
        except Exception as e:
            logging.warning(f"Error reading {file_path}: {e}")
            continue

    logging.info(f"Found {len(affected_files)} files with media references")
    return affected_files

def analyze_media_references_in_file(file_path):
    """Analyze media references in a single file"""
    media_refs = {
        'existing': [],
        'missing': [],
        'patterns': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find all media references
        media_pattern = re.compile(r'(href|src)="([^"]*\.(pps|avi|wmz|wmf|asf|mov|mp4|mpg|mpeg|wav|mp3|wma))"', re.IGNORECASE)
        matches = media_pattern.findall(content)

        for attr, url, ext in matches:
            media_refs['patterns'].append(f'{attr}="{url}"')

            # Try to determine if file exists (basic check)
            # For relative paths, check relative to the HTML file
            if not url.startswith('http'):
                html_dir = os.path.dirname(file_path)
                if url.startswith('/'):
                    # Absolute path from root
                    check_path = os.path.join('/home/ken/wip/fam/auntruth/docs', url.lstrip('/'))
                else:
                    # Relative path
                    check_path = os.path.join(html_dir, url)

                if os.path.exists(check_path):
                    media_refs['existing'].append(url)
                else:
                    media_refs['missing'].append(url)
            else:
                # External URLs - assume they might be missing
                media_refs['missing'].append(url)

    except Exception as e:
        logging.error(f"Error analyzing {file_path}: {e}")

    return media_refs

def cleanup_media_references_in_file(file_path, remove_missing=False):
    """Clean up media references in single file"""
    changes_made = []
    removals_logged = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        if remove_missing:
            # Pattern to find and remove entire links with missing media
            media_link_patterns = [
                # Remove entire <a href="...media_file">...</a> tags
                r'<a[^>]*href="[^"]*\.(pps|avi|wmz|wmf|asf|mov|mp4|mpg|mpeg|wav|mp3|wma)"[^>]*>.*?</a>',
                # Remove img/source tags with missing media
                r'<(img|source)[^>]*src="[^"]*\.(pps|avi|wmz|wmf|asf|mov|mp4|mpg|mpeg|wav|mp3|wma)"[^>]*/?>\s*',
                # Remove object/embed tags with missing media
                r'<(object|embed)[^>]*[^>]*\.(pps|avi|wmz|wmf|asf|mov|mp4|mpg|mpeg|wav|mp3|wma)"[^>]*>.*?</\1>',
            ]

            for pattern in media_link_patterns:
                old_content_before = content
                # Find matches before removing to log them
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
                if content != old_content_before:
                    changes_made.append(f"Removed {len(matches)} media links")
                    removals_logged.extend([f"Removed: {match}" for match in matches[:3]])  # Log first 3
        else:
            # Conservative approach: just comment out broken media references
            media_reference_patterns = [
                # Comment out href attributes to missing media
                (r'href="([^"]*\.(pps|avi|wmz|wmf|asf|mov|mp4|mpg|mpeg|wav|mp3|wma))"', r'data-broken-href="\1" href="#missing-media"'),
                # Comment out src attributes to missing media
                (r'src="([^"]*\.(pps|avi|wmz|wmf|asf|mov|mp4|mpg|mpeg|wav|mp3|wma))"', r'data-broken-src="\1" src=""'),
            ]

            for old_pattern, replacement in media_reference_patterns:
                old_content_before = content
                content = re.sub(old_pattern, replacement, content, flags=re.IGNORECASE)
                if content != old_content_before:
                    changes_made.append(f"Disabled media reference: {old_pattern}")

        # Clean up any resulting empty or malformed tags
        cleanup_patterns = [
            (r'<a[^>]*href="#missing-media"[^>]*>\s*</a>', ''),  # Remove empty links
            (r'<img[^>]*src=""\s*/>', ''),  # Remove empty img tags
        ]

        for old_pattern, replacement in cleanup_patterns:
            old_content_before = content
            content = re.sub(old_pattern, replacement, content)
            if content != old_content_before:
                changes_made.append("Cleaned up empty tags")

        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)

            return changes_made, removals_logged

        return [], []

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return [], []

def generate_media_cleanup_report(processed_files, all_removals):
    """Generate report of cleaned media references"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"PRPs/scripts/reports/media_cleanup_{timestamp}.csv"

    try:
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w') as f:
            f.write("File,Media_References_Found,Action_Taken,Sample_Removed\n")

            for file_path in processed_files:
                media_refs = analyze_media_references_in_file(file_path)
                total_refs = len(media_refs['patterns'])
                missing_refs = len(media_refs['missing'])

                if total_refs > 0:
                    sample_removed = '; '.join(media_refs['missing'][:2])  # First 2 missing refs
                    f.write(f'"{file_path}",{total_refs},"Found {missing_refs} missing media refs","{sample_removed}"\n')

        logging.info(f"Media cleanup report saved: {report_file}")
        return report_file
    except Exception as e:
        logging.warning(f"Could not save media cleanup report: {e}")
        return None

def main():
    """Main execution function"""
    args = setup_logging_and_args()

    logging.info("=" * 60)
    logging.info("Missing Media File Cleanup - Script 020")
    logging.info("=" * 60)
    logging.info(f"Target directory: {args.target_dir}")
    logging.info(f"Dry run mode: {args.dry_run}")
    logging.info(f"Remove missing media: {args.remove_missing}")
    logging.info(f"Processing limit: {args.limit or 'None'}")

    # Verify we're in the correct git branch
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                              capture_output=True, text=True)
        current_branch = result.stdout.strip()
        if current_branch != args.branch_name:
            logging.warning(f"Current branch is '{current_branch}', expected '{args.branch_name}'")
            logging.info("Continue anyway? (This should be safe)")
    except Exception as e:
        logging.warning(f"Could not check git branch: {e}")

    # Scan for affected files
    affected_files = scan_files_with_media_references(args.target_dir)

    if not affected_files:
        logging.info("No files found with media references. Nothing to do.")
        return

    # Apply limit if specified
    if args.limit:
        affected_files = affected_files[:args.limit]
        logging.info(f"Limited to first {len(affected_files)} files")

    logging.info(f"\nProcessing {len(affected_files)} files...")

    # Show dry-run preview
    if args.dry_run:
        logging.info("\n=== DRY RUN PREVIEW ===")
        sample_files = affected_files[:5]  # Show first 5 files
        for file_path in sample_files:
            try:
                media_refs = analyze_media_references_in_file(file_path)
                total_refs = len(media_refs['patterns'])
                missing_refs = len(media_refs['missing'])
                logging.info(f"  {file_path}: {total_refs} media refs ({missing_refs} missing)")

                # Show sample references
                if media_refs['missing']:
                    logging.info(f"    Missing: {', '.join(media_refs['missing'][:2])}")
            except Exception as e:
                logging.info(f"  {file_path}: Error analyzing - {e}")

        if len(affected_files) > 5:
            logging.info(f"  ... and {len(affected_files) - 5} more files")

        logging.info("\nRun without --dry-run to apply changes")
        logging.info("Add --remove-missing to remove broken media links entirely")
        return

    # Process files
    files_fixed = 0
    total_changes = 0
    all_removals = []

    for i, file_path in enumerate(affected_files):
        if i % 50 == 0:
            logging.info(f"Progress: {i}/{len(affected_files)} files processed...")

        changes, removals = cleanup_media_references_in_file(file_path, args.remove_missing)
        if changes:
            files_fixed += 1
            total_changes += len(changes)
            all_removals.extend(removals)
            logging.debug(f"Cleaned {file_path}: {', '.join(changes)}")

    # Summary
    logging.info(f"\n=== COMPLETION SUMMARY ===")
    logging.info(f"Files processed: {len(affected_files)}")
    logging.info(f"Files modified: {files_fixed}")
    logging.info(f"Total changes made: {total_changes}")
    logging.info(f"Approach: {'Removed missing media links' if args.remove_missing else 'Disabled missing media references'}")

    if files_fixed > 0:
        # Generate comprehensive report
        report_file = generate_media_cleanup_report(affected_files, all_removals)

        if report_file:
            logging.info(f"Report saved: {report_file}")

        # Show some samples of what was processed
        if all_removals:
            logging.info(f"\nSample removals:")
            for removal in all_removals[:5]:
                logging.info(f"  {removal}")

        logging.info(f"\nNext steps:")
        logging.info(f"1. Review the media cleanup report")
        logging.info(f"2. Run broken link checker to verify improvement")
        logging.info(f"3. Commit changes: git add . && git commit -m 'Script 020: Cleanup missing media references'")
    else:
        logging.info("No changes were needed - no problematic media references found")

if __name__ == "__main__":
    main()