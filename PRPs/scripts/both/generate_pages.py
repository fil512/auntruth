#!/usr/bin/env python3
"""
Generate HTML pages from JSON data and Jinja2 templates.

Usage:
    # Generate single page
    python3 generate_pages.py \
        --input data/people/Hagborg-Hansson/XF100.json \
        --output docs/new/htm/L1/XF100.htm

    # Generate all pages for lineage
    python3 generate_pages.py \
        --lineage Hagborg-Hansson \
        --input-dir data/people/Hagborg-Hansson \
        --output-dir docs/new/htm/L1-generated-test

    # Dry run (validate without writing)
    python3 generate_pages.py \
        --lineage Hagborg-Hansson \
        --dry-run
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import sys
import argparse


def setup_jinja_env():
    """Configure Jinja2 environment."""
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env


def generate_person_page(person_json_path, output_html_path, env, dry_run=False):
    """Generate a single person page."""
    # Load person data
    with open(person_json_path, 'r', encoding='utf-8') as f:
        person = json.load(f)

    # Load template
    template = env.get_template('person.html')

    # Render HTML
    html = template.render(person=person)

    if dry_run:
        print(f"Would generate: {output_html_path}")
        return

    # Write output
    output_path = Path(output_html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated: {output_path}")


def generate_lineage(lineage_name, input_dir, output_dir, dry_run=False, verbose=False):
    """Generate all pages for a lineage."""
    env = setup_jinja_env()
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    json_files = sorted(input_path.glob('*.json'))

    print(f"Generating {len(json_files)} pages for {lineage_name}...")

    success_count = 0
    error_count = 0

    for json_file in json_files:
        person_id = json_file.stem  # e.g., XF100
        output_file = output_path / f"{person_id}.htm"

        try:
            generate_person_page(json_file, output_file, env, dry_run)
            success_count += 1
        except Exception as e:
            error_count += 1
            print(f"ERROR generating {json_file}: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Generation {'simulated' if dry_run else 'complete'}")
    print(f"{'='*60}")
    print(f"✓ Success: {success_count} pages")
    if error_count > 0:
        print(f"✗ Errors: {error_count} pages")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Generate HTML pages from JSON data')
    parser.add_argument('--lineage', help='Lineage name')
    parser.add_argument('--input', help='Input JSON file (single file mode)')
    parser.add_argument('--output', help='Output HTML file (single file mode)')
    parser.add_argument('--input-dir', help='Input directory with JSON files')
    parser.add_argument('--output-dir', help='Output directory for HTML files')
    parser.add_argument('--dry-run', action='store_true', help='Validate without writing')
    parser.add_argument('--verbose', action='store_true', help='Verbose error reporting')

    args = parser.parse_args()

    if args.lineage:
        # Batch mode
        if not args.input_dir or not args.output_dir:
            print("ERROR: --input-dir and --output-dir required for lineage mode", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
        generate_lineage(args.lineage, args.input_dir, args.output_dir, args.dry_run, args.verbose)
    elif args.input and args.output:
        # Single file mode
        env = setup_jinja_env()
        try:
            generate_person_page(args.input, args.output, env, args.dry_run)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
