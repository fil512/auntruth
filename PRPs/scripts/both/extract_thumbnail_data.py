#!/usr/bin/env python3
"""
Extract Thumbnail Image Data from THF Pages

This script enhances person JSON files with thumbnail image paths by:
1. Reading THF (thumbnail gallery) HTML files
2. Extracting thumbnail image sources and their XI page links
3. Matching them to existing photos in person JSON files
4. Adding 'thumbnailSrc' field to each photo

Usage:
    python3 extract_thumbnail_data.py --lineage Hagborg-Hansson
    python3 extract_thumbnail_data.py --all-lineages
    python3 extract_thumbnail_data.py --dry-run
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


def extract_person_id_from_thf(thf_content):
    """Extract person ID (XF###) from THF page title."""
    # Look for pattern like "Thumbnails for [Name] [Lineage]"
    # We need to find the corresponding XF file
    # The THF filename itself is like THF182.htm, and we need to find XF182
    return None  # Will extract from filename instead


def extract_thumbnail_images(thf_content):
    """
    Extract thumbnail image data from THF HTML content.
    Returns list of dicts with: {src, alt, link}
    """
    images = []

    # Pattern: <img src="..." ... usemap="#MapXXX"> followed by <map name="MapXXX"> with <area href="...">
    # Example:
    # <img src="/auntruth/jpg/sn200.jpg" width="50" height="50" align="NONE" usemap="#Map713" border="" alt="">
    # <map name="Map713">
    #     <area shape="RECT" coords="00,00,50,50" href="/auntruth/new/htm/L3/XI713.htm" alt="At Joyce's 10/01/1996 Brampton(713)">
    # </map>

    # Find all img+map combinations
    img_pattern = r'<img\s+src="([^"]+)"[^>]*usemap="#([^"]+)"[^>]*>'
    map_pattern = r'<map\s+name="([^"]+)"[^>]*>.*?<area[^>]*href="([^"]+)"[^>]*alt="([^"]*)"[^>]*>.*?</map>'

    img_matches = re.findall(img_pattern, thf_content, re.IGNORECASE)
    map_matches = re.findall(map_pattern, thf_content, re.IGNORECASE | re.DOTALL)

    # Create lookup dict for maps
    maps = {name: (href, alt) for name, href, alt in map_matches}

    # Match images to maps
    for src, map_name in img_matches:
        if map_name in maps:
            href, alt = maps[map_name]
            images.append({
                'src': src,
                'alt': alt,
                'link': href
            })

    return images


def get_xi_id_from_url(url):
    """Extract XI### from URL like '/auntruth/new/htm/L3/XI713.htm'."""
    match = re.search(r'/(XI\d+)\.htm', url)
    return match.group(1) if match else None


def find_person_json_for_thf(thf_path, data_dir):
    """
    Find the person JSON file corresponding to a THF file.
    THF182.htm corresponds to XF182.json
    """
    # Extract number from THF filename
    thf_filename = thf_path.name
    match = re.match(r'THF(\d+)\.htm', thf_filename)
    if not match:
        return None

    person_num = match.group(1)
    person_id = f"XF{person_num}"

    # Determine lineage from directory
    lineage_dir = thf_path.parent.name  # e.g., "L1"
    lineage_name = LINEAGE_MAP.get(lineage_dir)

    if not lineage_name:
        return None

    # Find JSON file
    json_path = data_dir / lineage_name / f"{person_id}.json"

    return json_path if json_path.exists() else None


def enhance_person_json_with_thumbnails(json_path, thumbnail_data, dry_run=False):
    """
    Add thumbnail image sources to person JSON file.
    Matches XI page URLs to find the right photo entry.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        person = json.load(f)

    if not person.get('photos'):
        return 0, 0

    # Create lookup dict: XI page URL -> thumbnail src
    xi_to_thumb = {img['link']: img['src'] for img in thumbnail_data}

    matched = 0
    updated = 0

    # Update each photo with thumbnail src
    for photo in person['photos']:
        photo_url = photo.get('url')
        if photo_url in xi_to_thumb:
            matched += 1
            if 'thumbnailSrc' not in photo or photo.get('thumbnailSrc') != xi_to_thumb[photo_url]:
                photo['thumbnailSrc'] = xi_to_thumb[photo_url]
                updated += 1

    # Write back if changed and not dry run
    if updated > 0 and not dry_run:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(person, f, indent=2, ensure_ascii=False)

    return matched, updated


def process_lineage(lineage_name, html_dir, data_dir, dry_run=False, verbose=False):
    """Process all THF files for a lineage."""
    # Find lineage directory
    lineage_dir = None
    for dir_code, name in LINEAGE_MAP.items():
        if name == lineage_name:
            lineage_dir = dir_code
            break

    if not lineage_dir:
        print(f"Error: Unknown lineage '{lineage_name}'")
        return

    thf_dir = html_dir / lineage_dir
    if not thf_dir.exists():
        print(f"Error: Directory not found: {thf_dir}")
        return

    # Find all THF files
    thf_files = sorted(thf_dir.glob('THF*.htm'))

    print(f"\nProcessing {len(thf_files)} THF files for {lineage_name} ({lineage_dir})...")

    total_processed = 0
    total_matched = 0
    total_updated = 0
    errors = 0

    for thf_path in thf_files:
        try:
            # Read THF file
            with open(thf_path, 'r', encoding='utf-8', errors='ignore') as f:
                thf_content = f.read()

            # Extract thumbnail data
            thumbnail_data = extract_thumbnail_images(thf_content)

            if not thumbnail_data:
                if verbose:
                    print(f"  {thf_path.name}: No images found")
                continue

            # Find corresponding person JSON
            json_path = find_person_json_for_thf(thf_path, data_dir)

            if not json_path:
                if verbose:
                    print(f"  {thf_path.name}: Person JSON not found")
                continue

            # Enhance JSON with thumbnail data
            matched, updated = enhance_person_json_with_thumbnails(
                json_path, thumbnail_data, dry_run
            )

            total_processed += 1
            total_matched += matched
            total_updated += updated

            if verbose or updated > 0:
                status = "(dry run) " if dry_run else ""
                print(f"  {thf_path.name} -> {json_path.name}: {status}{updated}/{matched} photos updated")

        except Exception as e:
            errors += 1
            print(f"  ERROR processing {thf_path.name}: {e}")
            if verbose:
                import traceback
                traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Extraction {'simulated' if dry_run else 'complete'} for {lineage_name}")
    print(f"{'='*60}")
    print(f"THF files processed: {total_processed}")
    print(f"Photos matched: {total_matched}")
    print(f"Photos updated: {total_updated}")
    if errors > 0:
        print(f"Errors: {errors}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Extract thumbnail data from THF pages')
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
