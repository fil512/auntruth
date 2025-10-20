#!/usr/bin/env python3
"""
Generate Photo Detail HTML pages from photo JSON data and Jinja2 templates.

This script generates XI (photo detail) pages from the extracted photo data.

Usage:
    # Generate all photos for a lineage
    python3 generate_photo_pages.py \
        --lineage Hagborg-Hansson \
        --input-dir data/photos/Hagborg-Hansson \
        --output-dir docs/new/htm/L1

    # Generate all photos for all lineages
    python3 generate_photo_pages.py --all-lineages

    # Dry run (validate without writing)
    python3 generate_photo_pages.py \
        --lineage Hagborg-Hansson \
        --dry-run
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import sys
import argparse

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


def setup_jinja_env():
    """Configure Jinja2 environment."""
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env


def generate_photo_detail_page(photo_json_path, output_html_path, env, dry_run=False):
    """Generate a single photo detail page."""
    # Load photo data
    with open(photo_json_path, 'r', encoding='utf-8') as f:
        photo = json.load(f)

    # Load template
    template = env.get_template('photo-detail.html')

    # Render HTML
    html = template.render(photo=photo)

    if dry_run:
        print(f"Would generate: {output_html_path}")
        return True

    # Write output
    output_path = Path(output_html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return True


def generate_lineage(lineage_name, input_dir, output_dir, dry_run=False, verbose=False):
    """Generate all photo detail pages for a lineage."""
    env = setup_jinja_env()
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    json_files = sorted(input_path.glob('XI*.json'))

    print(f"\nGenerating photo detail pages for {lineage_name} ({len(json_files)} photos)...")

    success_count = 0
    error_count = 0

    for json_file in json_files:
        photo_id = json_file.stem  # e.g., XI1316
        output_file = output_path / f"{photo_id}.htm"

        try:
            generate_photo_detail_page(json_file, output_file, env, dry_run)
            success_count += 1
            if verbose:
                print(f"  {json_file.name}: Generated {output_file.name}")

        except Exception as e:
            error_count += 1
            print(f"ERROR generating {json_file}: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Generation {'simulated' if dry_run else 'complete'} for {lineage_name}")
    print(f"{'='*60}")
    print(f"✓ Photo detail pages: {success_count}")
    if error_count > 0:
        print(f"✗ Errors: {error_count}")
    print(f"{'='*60}\n")

    return success_count


def main():
    parser = argparse.ArgumentParser(description='Generate photo detail HTML pages from photo JSON data')
    parser.add_argument('--lineage', help='Lineage name (e.g., Hagborg-Hansson)')
    parser.add_argument('--all-lineages', action='store_true', help='Process all lineages')
    parser.add_argument('--input-dir', help='Input directory with photo JSON files')
    parser.add_argument('--output-dir', help='Output directory for HTML files')
    parser.add_argument('--photo-data-dir', default='data/photos', help='Root directory for photo data')
    parser.add_argument('--html-dir', default='docs/new/htm', help='Root directory for HTML output')
    parser.add_argument('--dry-run', action='store_true', help='Validate without writing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    photo_data_dir = Path(args.photo_data_dir)
    html_dir = Path(args.html_dir)

    if args.all_lineages:
        total_generated = 0
        for dir_code, lineage_name in LINEAGE_MAP.items():
            input_dir = photo_data_dir / lineage_name
            output_dir = html_dir / dir_code

            if not input_dir.exists():
                print(f"Skipping {lineage_name}: directory not found at {input_dir}")
                continue

            count = generate_lineage(lineage_name, input_dir, output_dir, args.dry_run, args.verbose)
            total_generated += count

        print(f"\n{'='*60}")
        print(f"TOTAL PHOTO DETAIL PAGES GENERATED: {total_generated}")
        print(f"{'='*60}\n")

    elif args.lineage:
        # Single lineage mode
        if args.input_dir and args.output_dir:
            # Use provided directories
            generate_lineage(args.lineage, args.input_dir, args.output_dir, args.dry_run, args.verbose)
        else:
            # Auto-determine directories from lineage name
            lineage_dir = None
            for dir_code, name in LINEAGE_MAP.items():
                if name == args.lineage:
                    lineage_dir = dir_code
                    break

            if not lineage_dir:
                print(f"ERROR: Unknown lineage '{args.lineage}'", file=sys.stderr)
                print(f"Valid lineages: {', '.join(LINEAGE_MAP.values())}")
                sys.exit(1)

            input_dir = photo_data_dir / args.lineage
            output_dir = html_dir / lineage_dir

            if not input_dir.exists():
                print(f"ERROR: Photo data directory not found: {input_dir}", file=sys.stderr)
                sys.exit(1)

            generate_lineage(args.lineage, input_dir, output_dir, args.dry_run, args.verbose)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
