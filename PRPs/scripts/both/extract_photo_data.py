#!/usr/bin/env python3
"""
Extract Photo Data from XI Pages

This script extracts photo detail information from XI (photo detail) HTML pages
and creates JSON data files for regeneration with modern templates.

Usage:
    python3 extract_photo_data.py --lineage Hagborg-Hansson
    python3 extract_photo_data.py --all-lineages
"""

import re
import json
import argparse
from pathlib import Path
from bs4 import BeautifulSoup

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


def extract_photo_id_and_name(soup):
    """Extract photo ID and name from title or h1."""
    h1 = soup.find('h1')
    if h1:
        text = h1.get_text()
        # Format: "1316 Siblings(sn809)" or "2681 ()"
        lines = [l.strip() for l in text.split('\n') if l.strip() and l.strip() != 'AuntieRuth.com']
        if lines:
            match = re.match(r'(\d+)\s*(.+)', lines[0])
            if match:
                photo_id = match.group(1)
                rest = match.group(2).strip()
                # Extract name and filename
                name_match = re.match(r'([^(]*)\(([^)]*)\)', rest)
                if name_match:
                    return photo_id, name_match.group(1).strip(), name_match.group(2).strip()
                else:
                    return photo_id, rest, None
    return None, None, None


def extract_image_src(soup):
    """Extract image source from img tag."""
    # Look for <center><img src="..."></center> pattern
    img = soup.find('img', src=True)
    if img:
        return img['src']
    return None


def extract_table_data(soup):
    """Extract all data from the table."""
    data = {}
    table = soup.find('table', id='List')
    if not table:
        return data

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            label = cells[0].get_text().strip()
            value_cell = cells[1]

            # Check if value has a link
            link = value_cell.find('a')
            if link and link.get('href'):
                value = {
                    'name': link.get_text().strip(),
                    'url': link.get('href')
                }
            else:
                value = value_cell.get_text().strip()

            # Only add non-empty values
            if value and value != '':
                data[label] = value

    return data


def process_xi_file(xi_path):
    """Extract photo data from a single XI file."""
    try:
        with open(xi_path, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')

        # Extract data
        photo_id, name, filename = extract_photo_id_and_name(soup)
        image_src = extract_image_src(soup)
        table_data = extract_table_data(soup)

        photo_data = {
            'id': f"XI{photo_id}" if photo_id else xi_path.stem,
            'name': name or '',
            'filename': filename or '',
            'imageSrc': image_src,
            'date': table_data.get('Image Date'),
            'location': table_data.get('Location'),
            'city': table_data.get('City'),
            'state': table_data.get('State/Province'),
            'country': table_data.get('Country'),
            'photographer': table_data.get('Photographer'),
            'people': [],
            'nonFamily': [],
            'notes': table_data.get('Notes')
        }

        # Extract people
        for i in range(1, 10):
            person_key = f'Person({i})'
            if person_key in table_data and table_data[person_key]:
                photo_data['people'].append(table_data[person_key])

        # Extract non-family
        for i in range(1, 6):
            nonfam_key = f'NonFamily({i})'
            if nonfam_key in table_data and table_data[nonfam_key]:
                photo_data['nonFamily'].append(table_data[nonfam_key])

        return photo_data

    except Exception as e:
        print(f"Error processing {xi_path}: {e}")
        return None


def process_lineage(lineage_name, html_dir, output_dir, dry_run=False, verbose=False):
    """Process all XI files for a lineage."""
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

    # Find all XI files
    xi_files = sorted(html_path.glob('XI*.htm'))

    print(f"\nProcessing {len(xi_files)} XI files for {lineage_name} ({lineage_dir})...")

    # Create output directory
    lineage_output_dir = output_dir / lineage_name
    if not dry_run:
        lineage_output_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    skipped = 0

    for xi_path in xi_files:
        photo_data = process_xi_file(xi_path)

        if not photo_data:
            skipped += 1
            continue

        # Write JSON
        output_path = lineage_output_dir / f"{xi_path.stem}.json"

        if dry_run:
            if verbose:
                print(f"  {xi_path.name}: Would create {output_path.name}")
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(photo_data, f, indent=2, ensure_ascii=False)
            if verbose:
                print(f"  {xi_path.name}: Created {output_path.name}")

        processed += 1

    print(f"\n{'='*60}")
    print(f"{'Simulation' if dry_run else 'Extraction'} complete for {lineage_name}")
    print(f"{'='*60}")
    print(f"XI files found: {len(xi_files)}")
    print(f"Photos processed: {processed}")
    if skipped > 0:
        print(f"Skipped (errors): {skipped}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Extract photo data from XI pages')
    parser.add_argument('--lineage', help='Process specific lineage')
    parser.add_argument('--all-lineages', action='store_true', help='Process all lineages')
    parser.add_argument('--html-dir', default='docs/new/htm', help='HTML directory')
    parser.add_argument('--output-dir', default='data/photos', help='Output directory for JSON files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    html_dir = Path(args.html_dir)
    output_dir = Path(args.output_dir)

    if not html_dir.exists():
        print(f"Error: HTML directory not found: {html_dir}")
        return 1

    if args.all_lineages:
        for lineage_name in LINEAGE_MAP.values():
            process_lineage(lineage_name, html_dir, output_dir, args.dry_run, args.verbose)
    elif args.lineage:
        process_lineage(args.lineage, html_dir, output_dir, args.dry_run, args.verbose)
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
