#!/usr/bin/env python3
"""
Extract Portrait Images from Person HTML Pages

This script extracts portrait image paths from person pages (XF*.htm) and
adds them to the corresponding JSON files.

Usage:
    python3 extract_portraits.py --lineage Hagborg-Hansson
    python3 extract_portraits.py --all-lineages
"""

import re
import json
import argparse
from pathlib import Path

# Lineage mapping
LINEAGE_MAP = {
    'L0': 'Other',
    'L1': 'Hagborg-Hansson',
    'L2': 'Nelson',
    'L3': 'Pringle-Hambley',
    'L4': 'Lathrop-Lothropp',
    'L5': 'Ward',
    'L6': 'Selch-Weiss',
    'L7': 'Stebbe',
    'L8': 'Lentz',
    'L9': 'Phoenix-Rogerson'
}


def extract_portrait_from_html(html_path):
    """Extract portrait image path from HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Look for pattern: <center><img src="/auntruth/jpg/XXX.jpg"></center>
        # between the </h1> and the first <table>
        pattern = r'</h1>.*?<center>\s*<img src="([^"]+)"[^>]*>\s*</center>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if match:
            return match.group(1)

        return None
    except Exception as e:
        print(f"Error reading {html_path}: {e}")
        return None


def update_person_json_with_portrait(json_path, portrait_path):
    """Add portrait field to person JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            person = json.load(f)

        # Add portrait field
        person['portrait'] = portrait_path

        # Write back
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(person, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Error updating {json_path}: {e}")
        return False


def process_lineage(lineage_name, html_dir, data_dir, dry_run=False, verbose=False):
    """Process all person files for a lineage."""
    # Find lineage directory
    lineage_dir = None
    for dir_code, name in LINEAGE_MAP.items():
        if name == lineage_name:
            lineage_dir = dir_code
            break

    if not lineage_dir:
        print(f"Error: Unknown lineage '{lineage_name}'")
        return

    html_path = html_dir / lineage_dir
    if not html_path.exists():
        print(f"Error: Directory not found: {html_path}")
        return

    # Find all XF (person) files
    xf_files = sorted(html_path.glob('XF*.htm'))

    print(f"\nProcessing {len(xf_files)} person files for {lineage_name} ({lineage_dir})...")

    total_processed = 0
    portraits_found = 0
    portraits_added = 0

    for html_file in xf_files:
        person_id = html_file.stem  # e.g., XF178

        # Extract portrait from HTML
        portrait = extract_portrait_from_html(html_file)

        if not portrait:
            if verbose:
                print(f"  {html_file.name}: No portrait found")
            continue

        portraits_found += 1

        # Find corresponding JSON file
        json_path = data_dir / lineage_name / f"{person_id}.json"

        if not json_path.exists():
            if verbose:
                print(f"  {html_file.name}: JSON not found at {json_path}")
            continue

        # Update JSON
        if dry_run:
            print(f"  {html_file.name}: Would add portrait {portrait}")
            portraits_added += 1
        else:
            if update_person_json_with_portrait(json_path, portrait):
                print(f"  {html_file.name}: Added portrait {portrait}")
                portraits_added += 1

        total_processed += 1

    print(f"\n{'='*60}")
    print(f"{'Simulation' if dry_run else 'Extraction'} complete for {lineage_name}")
    print(f"{'='*60}")
    print(f"Person files scanned: {len(xf_files)}")
    print(f"Portraits found: {portraits_found}")
    print(f"JSON files updated: {portraits_added}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Extract portrait images from HTML person pages')
    parser.add_argument('--lineage', help='Process specific lineage (e.g., Hagborg-Hansson)')
    parser.add_argument('--all-lineages', action='store_true', help='Process all lineages')
    parser.add_argument('--html-dir', default='docs/new/htm', help='HTML directory')
    parser.add_argument('--data-dir', default='data/people', help='JSON data directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    html_dir = Path(args.html_dir)
    data_dir = Path(args.data_dir)

    if not html_dir.exists():
        print(f"Error: HTML directory not found: {html_dir}")
        return 1

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return 1

    if args.all_lineages:
        for lineage_name in LINEAGE_MAP.values():
            process_lineage(lineage_name, html_dir, data_dir, args.dry_run, args.verbose)
    elif args.lineage:
        process_lineage(args.lineage, html_dir, data_dir, args.dry_run, args.verbose)
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
