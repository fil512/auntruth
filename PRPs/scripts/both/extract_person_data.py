#!/usr/bin/env python3
"""
Extract person data from HTML pages to JSON format.

This script parses legacy HTML person pages and extracts structured data
into JSON files following the schema defined in PLAN/data-schema.md.

Usage:
    # Extract single person
    python3 extract_person_data.py \
        --input docs/new/htm/L1/XF100.htm \
        --output data/people/Hagborg-Hansson/XF100.json

    # Extract entire lineage
    python3 extract_person_data.py \
        --lineage Hagborg-Hansson \
        --input-dir docs/new/htm/L1 \
        --output-dir data/people/Hagborg-Hansson

    # Dry run (validate without writing)
    python3 extract_person_data.py \
        --lineage Hagborg-Hansson \
        --input-dir docs/new/htm/L1 \
        --output-dir data/people/Hagborg-Hansson \
        --dry-run
"""

from pathlib import Path
from bs4 import BeautifulSoup
import json
import re
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any


class PersonDataExtractor:
    """Extracts person data from HTML to JSON."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.stats = {
            'files_processed': 0,
            'files_success': 0,
            'files_failed': 0,
            'errors': []
        }

    def log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(message)

    def extract_person_id(self, html_path: Path) -> str:
        """Extract XF### from filename."""
        return html_path.stem  # e.g., XF100

    def extract_id_from_url(self, url: Optional[str]) -> Optional[str]:
        """Extract XF### from URL like '/auntruth/new/htm/L1/XF100.htm'."""
        if not url:
            return None
        match = re.search(r'(XF\d+)\.htm', url)
        if match:
            return match.group(1)
        return None

    def normalize_value(self, value: Optional[str]) -> Optional[str]:
        """Convert empty/zero values to None."""
        if not value:
            return None
        value = value.strip()
        if value in ['', '0']:
            return None
        return value

    def extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract person name from h1."""
        h1 = soup.find('h1')
        if h1:
            # "Johanna Hakanson\n<br>\nAuntieRuth.com"
            text = h1.get_text()
            # Get first line before <br>
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            # Return first line that's not "AuntieRuth.com"
            for line in lines:
                if line != 'AuntieRuth.com':
                    return line
        return None

    def extract_table_row_value(self, table, label: str) -> Optional[str]:
        """Extract plain text value from table row by label."""
        if not table:
            return None

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                row_label = cells[0].get_text().strip()
                if row_label == label:
                    value_cell = cells[1]
                    # Get text, ignoring links
                    text = value_cell.get_text().strip()
                    return self.normalize_value(text)
        return None

    def extract_table_row_link(self, table, label: str) -> Optional[Dict]:
        """Extract link data from table row by label."""
        if not table:
            return None

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                row_label = cells[0].get_text().strip()
                if row_label == label:
                    value_cell = cells[1]
                    link = value_cell.find('a')
                    if link:
                        href = link.get('href', '')
                        return {
                            'id': self.extract_id_from_url(href),
                            'name': link.get_text().strip(),
                            'url': href
                        }
        return None

    def extract_spouses(self, table) -> List[Dict]:
        """Extract all spouse entries (up to 4)."""
        spouses = []
        for i in range(1, 5):  # Spouse(1) through Spouse(4)
            spouse = self.extract_table_row_link(table, f'Spouse({i})')
            if spouse and spouse['id']:
                # Get corresponding marriage date
                marriage_date = self.extract_table_row_value(table, f'Marriage Date({i})')
                spouse['marriageDate'] = marriage_date
                spouses.append(spouse)
        return spouses

    def extract_phone_numbers(self, table) -> Optional[str]:
        """Combine all phone number fields into single value."""
        phone_fields = ['Telephone', 'Home Phone', 'Cell']
        phones = []
        for field in phone_fields:
            value = self.extract_table_row_value(table, field)
            if value:
                phones.append(value)

        if phones:
            return ', '.join(phones)
        return None

    def extract_children(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract children from second table#List."""
        tables = soup.find_all('table', id='List')

        if len(tables) < 2:
            return []

        children_table = tables[1]
        children = []

        # Skip header row (index 0)
        for row in children_table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                # First cell has child name link
                link = cells[0].find('a')
                if link:
                    href = link.get('href', '')
                    birth_date = cells[1].get_text().strip()

                    child = {
                        'id': self.extract_id_from_url(href),
                        'name': link.get_text().strip(),
                        'url': href,
                        'birthDate': self.normalize_value(birth_date)
                    }
                    children.append(child)

        return children

    def extract_photos(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract 'Photos of this Person' from third table#List."""
        tables = soup.find_all('table', id='List')

        if len(tables) < 3:
            return []

        photos_table = tables[2]
        photos = []

        # Skip header row (index 0)
        for row in photos_table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 3:
                name = cells[0].get_text().strip()
                date = cells[1].get_text().strip()
                location = cells[2].get_text().strip()

                # Look for link in name cell
                link = cells[0].find('a')
                url = link.get('href', '') if link else ''

                photo = {
                    'name': name,
                    'date': self.normalize_value(date),
                    'location': self.normalize_value(location),
                    'url': url
                }
                photos.append(photo)

        return photos

    def extract_photographed_by(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract 'Photos Photographed by this Person' from fourth table#List."""
        tables = soup.find_all('table', id='List')

        if len(tables) < 4:
            return []

        photos_table = tables[3]
        photos = []

        # Skip header row (index 0)
        for row in photos_table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 3:
                name = cells[0].get_text().strip()
                date = cells[1].get_text().strip()
                location = cells[2].get_text().strip()

                # Look for link in name cell
                link = cells[0].find('a')
                url = link.get('href', '') if link else ''

                photo = {
                    'name': name,
                    'date': self.normalize_value(date),
                    'location': self.normalize_value(location),
                    'url': url
                }
                photos.append(photo)

        return photos

    def extract_last_updated(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract last updated date from footer."""
        # Find: "WebPage Last Updated Monday, December 19, 2005 18:52:51 GMT/CUT"
        footer = soup.find('b', string=re.compile('WebPage Last Updated'))
        if footer:
            text = footer.get_text()
            match = re.search(r'WebPage Last Updated (.+)', text)
            if match:
                date_str = match.group(1).strip()
                try:
                    # Try to parse and convert to ISO format
                    # Format: "Monday, December 19, 2005 18:52:51 GMT/CUT"
                    # Remove day name and timezone
                    date_str = re.sub(r'^[A-Za-z]+,\s+', '', date_str)
                    date_str = re.sub(r'\s+GMT/CUT$', '', date_str)

                    # Parse: "December 19, 2005 18:52:51"
                    dt = datetime.strptime(date_str, '%B %d, %Y %H:%M:%S')
                    return dt.isoformat() + 'Z'
                except:
                    # If parsing fails, return original string
                    return date_str
        return None

    def parse_person_html(self, html_path: Path) -> Dict:
        """Parse a single HTML file and extract person data."""
        self.log(f"Parsing {html_path.name}...")

        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Get first table (person data)
        tables = soup.find_all('table', id='List')
        if not tables:
            raise ValueError(f"No table#List found in {html_path}")

        person_table = tables[0]

        # Extract all fields
        person_id = self.extract_person_id(html_path)
        name = self.extract_name(soup)
        lineage_link = self.extract_table_row_link(person_table, 'Lineage')
        lineage = lineage_link['name'] if lineage_link else None

        # Build person record
        person = {
            'id': person_id,
            'name': name,
            'lineage': lineage,
            'birthDate': self.extract_table_row_value(person_table, 'BirthDate'),
            'birthLocation': self.extract_table_row_value(person_table, 'Birth Location'),
            'deathDate': self.extract_table_row_value(person_table, 'Death Date'),
            'deathLocation': None,  # Not in current HTML
            'deceased': self.extract_table_row_value(person_table, 'Deceased?'),
            'father': self.extract_table_row_link(person_table, 'Father'),
            'mother': self.extract_table_row_link(person_table, 'Mother'),
            'spouses': self.extract_spouses(person_table),
            'children': self.extract_children(soup),
            'occupation': self.extract_table_row_value(person_table, 'Occupation'),
            'address': self.extract_table_row_value(person_table, 'Address'),
            'email': self.extract_table_row_value(person_table, 'EMail'),
            'phone': self.extract_phone_numbers(person_table),
            'website': self.extract_table_row_value(person_table, 'WebSite'),
            'source': self.extract_table_row_value(person_table, 'Source'),
            'notes': self.extract_table_row_value(person_table, 'Notes'),
            'photos': self.extract_photos(soup),
            'photographedBy': self.extract_photographed_by(soup),
            'metadata': {
                'lastUpdated': self.extract_last_updated(soup),
                'originalHtmlPath': str(html_path),
                'extractionDate': datetime.utcnow().isoformat() + 'Z'
            }
        }

        return person

    def extract_single_file(self, html_path: Path, output_path: Path, dry_run=False):
        """Extract data from single HTML file to JSON."""
        try:
            person = self.parse_person_html(html_path)

            if dry_run:
                self.log(f"  Would write to: {output_path}")
                self.log(f"  Person: {person['name']} (ID: {person['id']})")
            else:
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Write JSON
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(person, f, indent=2, ensure_ascii=False)

                self.log(f"  ✓ Wrote {output_path.name}")

            self.stats['files_success'] += 1
            return person

        except Exception as e:
            self.stats['files_failed'] += 1
            error = {
                'file': str(html_path),
                'error': str(e)
            }
            self.stats['errors'].append(error)
            print(f"  ✗ Error processing {html_path.name}: {e}")
            return None

    def extract_lineage(self, input_dir: Path, output_dir: Path, lineage: str, dry_run=False):
        """Extract all person files from a lineage directory."""
        # Find all XF*.htm files
        html_files = sorted(input_dir.glob('XF*.htm'))

        if not html_files:
            print(f"No XF*.htm files found in {input_dir}")
            return

        print(f"\n{'='*60}")
        print(f"Extracting {lineage} lineage")
        print(f"Input: {input_dir}")
        print(f"Output: {output_dir}")
        print(f"Files found: {len(html_files)}")
        print(f"Dry run: {dry_run}")
        print(f"{'='*60}\n")

        for i, html_file in enumerate(html_files, 1):
            self.stats['files_processed'] += 1

            # Progress reporting every 10 files
            if i % 10 == 0:
                print(f"Progress: {i}/{len(html_files)} files...")

            person_id = html_file.stem
            output_file = output_dir / f"{person_id}.json"

            self.extract_single_file(html_file, output_file, dry_run)

        # Print summary
        print(f"\n{'='*60}")
        print("EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Success: {self.stats['files_success']}")
        print(f"Failed: {self.stats['files_failed']}")

        if self.stats['errors']:
            print(f"\nErrors encountered:")
            for error in self.stats['errors']:
                print(f"  - {error['file']}: {error['error']}")
        else:
            print(f"\n✓ All files processed successfully!")


def main():
    parser = argparse.ArgumentParser(
        description='Extract person data from HTML to JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Mode 1: Single file
    parser.add_argument('--input', type=str, help='Input HTML file')
    parser.add_argument('--output', type=str, help='Output JSON file')

    # Mode 2: Entire lineage
    parser.add_argument('--lineage', type=str, help='Lineage name (e.g., Hagborg-Hansson)')
    parser.add_argument('--input-dir', type=str, help='Input directory with HTML files')
    parser.add_argument('--output-dir', type=str, help='Output directory for JSON files')

    # Options
    parser.add_argument('--dry-run', action='store_true', help='Test run without writing files')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    extractor = PersonDataExtractor(verbose=args.verbose)

    if args.input and args.output:
        # Single file mode
        html_path = Path(args.input)
        output_path = Path(args.output)

        if not html_path.exists():
            print(f"Error: Input file not found: {html_path}")
            return 1

        print(f"Extracting single file: {html_path}")
        extractor.extract_single_file(html_path, output_path, args.dry_run)

    elif args.lineage and args.input_dir and args.output_dir:
        # Lineage mode
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)

        if not input_dir.exists():
            print(f"Error: Input directory not found: {input_dir}")
            return 1

        extractor.extract_lineage(input_dir, output_dir, args.lineage, args.dry_run)

    else:
        parser.print_help()
        return 1

    return 0 if extractor.stats['files_failed'] == 0 else 1


if __name__ == '__main__':
    exit(main())
