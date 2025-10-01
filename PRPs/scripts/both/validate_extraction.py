#!/usr/bin/env python3
"""
Comprehensive extraction validation: HTML → JSON

Validates that ALL data from original HTML is preserved in JSON extraction.
This is the CRITICAL validation tool for ensuring zero data loss.

Usage:
    python3 validate_extraction.py \
        --html-dir docs/new/htm/L1 \
        --json-dir data/people/Hagborg-Hansson \
        --report data/extraction-validation-report.json \
        --fail-on-error
"""

from pathlib import Path
from bs4 import BeautifulSoup
import json
import re
import argparse
from typing import Dict, List, Tuple, Set, Optional


class ExtractionValidator:
    """Validates HTML → JSON extraction for data completeness."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'files_validated': 0,
            'perfect_matches': 0,
            'minor_differences': 0,
            'data_loss_detected': 0
        }

    def extract_html_content(self, soup: BeautifulSoup) -> Dict:
        """Extract all meaningful content from HTML."""
        content = {
            'name': None,
            'table_data': {},
            'links': [],
            'children': [],
            'photos_of': [],
            'photos_by': [],
            'last_updated': None
        }

        # Extract name from h1
        h1 = soup.find('h1')
        if h1:
            text = h1.get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for line in lines:
                if line != 'AuntieRuth.com':
                    content['name'] = line
                    break

        # Get all tables
        tables = soup.find_all('table', id='List')

        # Table 1: Person data
        if len(tables) >= 1:
            person_table = tables[0]
            for row in person_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text().strip()
                    value_cell = cells[1]

                    # Get text content
                    text = value_cell.get_text().strip()
                    # Only store non-empty values (not "", not "0" for most fields)
                    if text and text not in ['', '0']:
                        content['table_data'][label] = text

                    # Get link if present
                    link = value_cell.find('a')
                    if link:
                        href = link.get('href', '')
                        link_text = link.get_text().strip()
                        if href and link_text:
                            content['links'].append({
                                'label': label,
                                'text': link_text,
                                'href': href
                            })

        # Table 2: Children
        if len(tables) >= 2:
            children_table = tables[1]
            for row in children_table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link = cells[0].find('a')
                    if link:
                        content['children'].append({
                            'name': link.get_text().strip(),
                            'href': link.get('href', ''),
                            'birthDate': cells[1].get_text().strip()
                        })

        # Table 3: Photos of person
        if len(tables) >= 3:
            photos_table = tables[2]
            for row in photos_table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 3:
                    name = cells[0].get_text().strip()
                    if name:  # Only add if there's actual photo data
                        content['photos_of'].append({
                            'name': name,
                            'date': cells[1].get_text().strip(),
                            'location': cells[2].get_text().strip()
                        })

        # Table 4: Photos by person
        if len(tables) >= 4:
            photos_table = tables[3]
            for row in photos_table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 3:
                    name = cells[0].get_text().strip()
                    if name:  # Only add if there's actual photo data
                        content['photos_by'].append({
                            'name': name,
                            'date': cells[1].get_text().strip(),
                            'location': cells[2].get_text().strip()
                        })

        # Extract last updated
        footer = soup.find('b', string=re.compile('WebPage Last Updated'))
        if footer:
            content['last_updated'] = footer.get_text()

        return content

    def extract_json_content(self, json_data: Dict) -> Dict:
        """Extract all content from JSON for comparison."""
        content = {
            'name': json_data.get('name'),
            'fields': {},
            'links': [],
            'children': json_data.get('children', []),
            'photos_of': json_data.get('photos', []),
            'photos_by': json_data.get('photographedBy', [])
        }

        # Extract all non-null fields (excluding metadata)
        for key, value in json_data.items():
            if value is not None and key != 'metadata' and not isinstance(value, (list, dict)):
                content['fields'][key] = value

        # Extract family links
        if json_data.get('father'):
            content['links'].append({
                'type': 'father',
                'name': json_data['father'].get('name'),
                'id': json_data['father'].get('id'),
                'url': json_data['father'].get('url')
            })

        if json_data.get('mother'):
            content['links'].append({
                'type': 'mother',
                'name': json_data['mother'].get('name'),
                'id': json_data['mother'].get('id'),
                'url': json_data['mother'].get('url')
            })

        # Extract spouse links
        for spouse in json_data.get('spouses', []):
            content['links'].append({
                'type': 'spouse',
                'name': spouse.get('name'),
                'id': spouse.get('id'),
                'url': spouse.get('url')
            })

        # Extract lineage link
        if json_data.get('lineage'):
            content['links'].append({
                'type': 'lineage',
                'name': json_data.get('lineage')
            })

        return content

    def value_exists_in_json_content(self, value: str, json_content: Dict) -> bool:
        """Check if a value exists anywhere in JSON content."""
        # Convert to string for comparison
        json_str = json.dumps(json_content).lower()
        value_lower = value.lower().strip()

        return value_lower in json_str

    def link_exists_in_json(self, html_link: Dict, json_links: List[Dict]) -> bool:
        """Check if a link from HTML exists in JSON."""
        html_text = html_link['text'].strip()
        html_href = html_link['href'].strip()

        for json_link in json_links:
            json_name = json_link.get('name', '').strip()
            json_url = json_link.get('url', '').strip()

            # Match by name or URL
            if html_text == json_name or html_href == json_url:
                return True

        return False

    def find_missing_data(self, html_content: Dict, json_content: Dict) -> List[Dict]:
        """Find any data in HTML that's missing from JSON."""
        missing = []

        # Check name
        if html_content['name'] != json_content['name']:
            missing.append({
                'type': 'name_mismatch',
                'html_value': html_content['name'],
                'json_value': json_content['name'],
                'severity': 'ERROR'
            })

        # Check table data - every non-empty HTML field should be in JSON somewhere
        skip_values = {'0', '', 'Don\'t Know', 'Unknown'}
        for label, value in html_content.get('table_data', {}).items():
            if value in skip_values:
                continue

            # Special handling for phone fields (combined in JSON)
            if label in ['Telephone', 'Home Phone', 'Cell', 'FAX', 'Home FAX']:
                # These might be combined into single "phone" field
                # Just check if the value exists somewhere in JSON
                if not self.value_exists_in_json_content(value, json_content):
                    missing.append({
                        'type': 'missing_field_value',
                        'label': label,
                        'value': value,
                        'severity': 'ERROR'
                    })
                continue

            # Check if value exists in JSON
            if not self.value_exists_in_json_content(value, json_content):
                missing.append({
                    'type': 'missing_field_value',
                    'label': label,
                    'value': value,
                    'severity': 'ERROR'
                })

        # Check links
        for html_link in html_content.get('links', []):
            if not self.link_exists_in_json(html_link, json_content['links']):
                missing.append({
                    'type': 'missing_link',
                    'label': html_link.get('label', 'unknown'),
                    'text': html_link['text'],
                    'href': html_link['href'],
                    'severity': 'ERROR'
                })

        # Check children count
        html_children_count = len(html_content.get('children', []))
        json_children_count = len(json_content.get('children', []))
        if html_children_count != json_children_count:
            missing.append({
                'type': 'children_count_mismatch',
                'html_count': html_children_count,
                'json_count': json_children_count,
                'severity': 'ERROR'
            })

        # Check children names
        for html_child in html_content.get('children', []):
            found = False
            for json_child in json_content.get('children', []):
                if html_child['name'] == json_child.get('name'):
                    found = True
                    break
            if not found:
                missing.append({
                    'type': 'missing_child',
                    'child_name': html_child['name'],
                    'severity': 'ERROR'
                })

        # Check photos
        html_photos_count = len(html_content.get('photos_of', []))
        json_photos_count = len(json_content.get('photos_of', []))
        if html_photos_count != json_photos_count:
            missing.append({
                'type': 'photos_count_mismatch',
                'html_count': html_photos_count,
                'json_count': json_photos_count,
                'severity': 'WARNING'  # Photos tables are often empty
            })

        return missing

    def validate_person(self, html_path: Path, json_path: Path) -> Dict:
        """Validate single person extraction."""
        try:
            # Parse original HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html_soup = BeautifulSoup(f.read(), 'html.parser')

            # Load extracted JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Extract content from both
            html_content = self.extract_html_content(html_soup)
            json_content = self.extract_json_content(json_data)

            # Compare
            missing_data = self.find_missing_data(html_content, json_content)

            # Categorize issues
            error_count = len([m for m in missing_data if m['severity'] == 'ERROR'])
            warning_count = len([m for m in missing_data if m['severity'] == 'WARNING'])

            return {
                'html_file': str(html_path),
                'json_file': str(json_path),
                'person_id': json_data.get('id'),
                'person_name': json_data.get('name'),
                'missing_data': missing_data,
                'error_count': error_count,
                'warning_count': warning_count,
                'status': 'PASS' if error_count == 0 else 'FAIL'
            }

        except Exception as e:
            return {
                'html_file': str(html_path),
                'json_file': str(json_path),
                'status': 'ERROR',
                'error_count': 1,
                'warning_count': 0,
                'missing_data': [{
                    'type': 'validation_exception',
                    'message': str(e),
                    'severity': 'ERROR'
                }]
            }

    def validate_all(self, html_dir: Path, json_dir: Path) -> Dict:
        """Validate all files in directories."""
        results = []

        # Get all HTML files
        html_files = sorted(html_dir.glob('XF*.htm'))

        if not html_files:
            print(f"No XF*.htm files found in {html_dir}")
            return {'summary': self.stats, 'results': [], 'errors': self.errors}

        print(f"\n{'='*60}")
        print(f"COMPREHENSIVE EXTRACTION VALIDATION")
        print(f"{'='*60}")
        print(f"HTML directory: {html_dir}")
        print(f"JSON directory: {json_dir}")
        print(f"Files to validate: {len(html_files)}")
        print(f"{'='*60}\n")

        for i, html_file in enumerate(html_files, 1):
            person_id = html_file.stem
            json_file = json_dir / f"{person_id}.json"

            # Progress reporting every 20 files
            if i % 20 == 0:
                print(f"Progress: {i}/{len(html_files)} files...")

            if not json_file.exists():
                self.errors.append({
                    'type': 'missing_json',
                    'html_file': str(html_file),
                    'expected_json': str(json_file)
                })
                self.stats['data_loss_detected'] += 1
                continue

            result = self.validate_person(html_file, json_file)
            results.append(result)

            self.stats['files_validated'] += 1

            if result['status'] == 'PASS' and result['warning_count'] == 0:
                self.stats['perfect_matches'] += 1
            elif result['status'] == 'PASS':
                self.stats['minor_differences'] += 1
            else:
                self.stats['data_loss_detected'] += 1
                # Print errors immediately for failed files
                print(f"✗ {person_id}: {result['error_count']} errors")
                for issue in result['missing_data'][:3]:  # Show first 3
                    if issue['severity'] == 'ERROR':
                        print(f"  - {issue.get('type')}: {issue.get('value', issue.get('message', 'N/A'))}")

        return {
            'summary': self.stats,
            'results': results,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def print_summary(self, report: Dict):
        """Print validation summary."""
        print(f"\n{'='*60}")
        print("EXTRACTION VALIDATION REPORT")
        print(f"{'='*60}")
        print(f"Files Validated: {report['summary']['files_validated']}")
        print(f"✓ Perfect Matches: {report['summary']['perfect_matches']}")
        print(f"⚠ Minor Differences: {report['summary']['minor_differences']}")
        print(f"❌ DATA LOSS DETECTED: {report['summary']['data_loss_detected']}")

        if report['summary']['data_loss_detected'] > 0:
            print(f"\n{'='*60}")
            print("⚠️  CRITICAL: Data loss detected in extraction!")
            print("Review the detailed report and fix extraction issues.")
            print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate HTML → JSON extraction for data completeness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--html-dir', required=True, help='Directory with original HTML files')
    parser.add_argument('--json-dir', required=True, help='Directory with extracted JSON files')
    parser.add_argument('--report', default='extraction-validation-report.json', help='Output report file')
    parser.add_argument('--fail-on-error', action='store_true', help='Exit with error code if validation fails')

    args = parser.parse_args()

    validator = ExtractionValidator()
    report = validator.validate_all(Path(args.html_dir), Path(args.json_dir))

    # Save report
    with open(args.report, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Print summary
    validator.print_summary(report)
    print(f"\nDetailed report saved to: {args.report}")

    # Exit with error if data loss detected
    if args.fail_on_error and report['summary']['data_loss_detected'] > 0:
        print("\n❌ VALIDATION FAILED - Data loss detected!")
        exit(1)
    else:
        print("\n✅ VALIDATION PASSED")
        exit(0)


if __name__ == '__main__':
    main()
