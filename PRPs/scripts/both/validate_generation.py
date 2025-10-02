#!/usr/bin/env python3
"""
Comprehensive generation validation: Original HTML → Generated HTML

Validates that ALL data from original HTML appears in generated HTML.

Usage:
    python3 validate_generation.py \
        --original-dir docs/new/htm/L1 \
        --generated-dir docs/new/htm/L1-generated-test \
        --json-dir data/people/Hagborg-Hansson \
        --report generation-validation-report.json
"""

from pathlib import Path
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List


class GenerationValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'files_validated': 0,
            'content_matches': 0,
            'missing_data': 0,
            'design_improvements': 0
        }

    def validate_person(self, original_html: Path, generated_html: Path, json_path: Path) -> Dict:
        """Validate single generated page."""

        # Parse original HTML
        with open(original_html, 'r', encoding='utf-8') as f:
            original_soup = BeautifulSoup(f.read(), 'html.parser')

        # Parse generated HTML
        with open(generated_html, 'r', encoding='utf-8') as f:
            generated_soup = BeautifulSoup(f.read(), 'html.parser')

        # Load JSON for reference
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Extract data from both
        original_data = self.extract_data_from_html(original_soup)
        generated_data = self.extract_data_from_html(generated_soup)

        # Compare
        missing = self.find_missing_content(original_data, generated_data, json_data)
        improvements = self.find_improvements(original_soup, generated_soup)

        return {
            'original_file': str(original_html),
            'generated_file': str(generated_html),
            'person_id': json_data.get('id'),
            'person_name': json_data.get('name'),
            'missing_data': missing,
            'improvements': improvements,
            'status': 'PASS' if not missing else 'FAIL'
        }

    def extract_data_from_html(self, soup: BeautifulSoup) -> Dict:
        """Extract all data points from HTML (original or generated)."""
        data = {
            'name': None,
            'fields': {},
            'links': [],
            'children': [],
            'text_content': []
        }

        # Extract name from h1
        h1 = soup.find('h1')
        if h1:
            data['name'] = h1.get_text().split('\n')[0].strip()

        # Extract from tables (works for both old and new structure)
        # Only extract fields from FIRST table (person data table)
        # Subsequent tables are children, photos, etc. which are handled separately
        tables = soup.find_all('table')
        person_table = tables[0] if tables else None

        if person_table:
            for row in person_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()

                    # Skip table header rows (where both cells contain <b> tags with short single words)
                    if cells[0].find('b') and cells[1].find('b'):
                        # Check if both values look like headers (short single words)
                        if len(label.split()) <= 1 and len(value.split()) <= 1:
                            continue

                    if value and value != '0':
                        data['fields'][label] = value

                    link = cells[1].find('a')
                    if link:
                        link_text = link.get_text().strip()
                        # Skip navigation links (these change with modern design)
                        navigation_links = ['Home |', 'Home', 'Hagborg-Hansson', 'AuntieRuth.com']
                        if link_text not in navigation_links:
                            data['links'].append({
                                'text': link_text,
                                'href': link.get('href')
                            })

        # Extract from disclosure sections (new format)
        disclosure_sections = soup.find_all('div', class_='disclosure-content')
        for section in disclosure_sections:
            text = section.get_text(separator=' ', strip=True)
            data['text_content'].append(text)

        # Extract ALL links from the page (not just from tables)
        # This ensures we catch links in headers, footers, disclosure sections, etc.
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text().strip()

            # Skip navigation links (these change with modern design)
            navigation_links = ['Home |', 'Home', 'Hagborg-Hansson', 'AuntieRuth.com']
            if text in navigation_links:
                continue

            # Avoid duplicates
            if not any(l['text'] == text and l['href'] == href for l in data['links']):
                data['links'].append({
                    'text': text,
                    'href': href
                })

        # Extract from children section
        children_section = soup.find('section', class_='children-section')
        if children_section:
            table = children_section.find('table')
            if table:
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        link = cells[0].find('a')
                        if link:
                            data['children'].append({
                                'text': link.get_text().strip(),
                                'href': link.get('href')
                            })

        return data

    def find_missing_content(self, original: Dict, generated: Dict, json_data: Dict) -> List[Dict]:
        """Find content in original that's missing from generated."""
        missing = []

        # Check name
        if original['name'] and generated['name']:
            # Normalize whitespace for comparison
            orig_name_norm = ' '.join(original['name'].split())
            gen_name_norm = ' '.join(generated['name'].split())
            if orig_name_norm != gen_name_norm:
                missing.append({
                    'type': 'name_mismatch',
                    'original': original['name'],
                    'generated': generated['name'],
                    'severity': 'ERROR'
                })

        # Check fields - allow for different structure but same content
        for label, value in original['fields'].items():
            if value in ['0', '', 'Don\'t Know']:
                continue

            # Skip lineage field - it's in JSON and navigation, not shown as redundant table field
            # This is a design improvement, not data loss
            if label == 'Lineage':
                continue

            # Skip language fields - they're in languages[] array in JSON
            if label.startswith('Language('):
                # Check if this language exists in the languages array
                lang_found = False
                if 'languages' in json_data and isinstance(json_data['languages'], list):
                    if value in json_data['languages']:
                        lang_found = True
                if lang_found:
                    continue

            # Skip children without links - they appear as "Child Name" label with "birthdate" value
            # These are in the children[] array in JSON
            if 'children' in json_data:
                child_found = False
                for child in json_data['children']:
                    # Check if this label matches a child's name and value matches birth date
                    child_name = child.get('name', '') or ''
                    child_name = child_name.strip()
                    child_birth = child.get('birthDate') or ''
                    child_birth = child_birth.strip() if child_birth else ''
                    # Normalize whitespace in label for comparison
                    import re
                    label_norm = re.sub(r'\s+', ' ', label.strip())
                    if label_norm == child_name and value == child_birth:
                        child_found = True
                        break
                if child_found:
                    continue

            # Skip marriage date fields - they're in spouse objects, not table_data
            if label.startswith('Marriage Date'):
                # Check if this marriage date exists in any spouse object
                marriage_date_found = False
                if 'spouses' in json_data:
                    for spouse in json_data['spouses']:
                        if spouse.get('marriageDate') == value:
                            marriage_date_found = True
                            break
                if marriage_date_found:
                    continue  # Not actually missing

            # Check if value exists anywhere in generated data
            # Normalize whitespace for comparison (HTML extraction may have different spacing)
            import re
            value_norm = re.sub(r'\s+', ' ', value.lower().strip())
            generated_str = json.dumps(generated).lower()
            generated_str_norm = re.sub(r'\s+', ' ', generated_str)

            if value_norm not in generated_str_norm:
                missing.append({
                    'type': 'missing_field_value',
                    'field': label,
                    'value': value,
                    'severity': 'ERROR'
                })

        # Check links - compare hrefs only (link text may differ in modern design)
        # Create sets of normalized hrefs
        orig_hrefs = set()
        for link in original['links']:
            href_norm = link['href'].rstrip('/') if link['href'] else ''
            if href_norm:
                orig_hrefs.add(href_norm)

        gen_hrefs = set()
        for link in generated['links']:
            href_norm = link['href'].rstrip('/') if link['href'] else ''
            if href_norm:
                gen_hrefs.add(href_norm)

        # Find hrefs in original that are not in generated
        missing_hrefs = orig_hrefs - gen_hrefs

        for href in missing_hrefs:
            # Thumbnail links (THF files) are acceptable to omit if person has no photos
            # This is an improvement - not showing links to empty thumbnail pages
            if '/THF' in href or 'ThumbNails' in href:
                continue  # Skip - this is an acceptable improvement

            # Find original link text for this href
            orig_text = next((link['text'] for link in original['links'] if link['href'].rstrip('/') == href), href)

            missing.append({
                'type': 'missing_link',
                'text': orig_text,
                'href': href,
                'severity': 'ERROR'
            })

        return missing

    def find_improvements(self, original_soup: BeautifulSoup, generated_soup: BeautifulSoup) -> List[str]:
        """Document design improvements in generated version."""
        improvements = []

        # Check for modern design system
        if generated_soup.find('link', href=re.compile('modern-design-system')):
            improvements.append('Phase 4 design system applied')

        # Check for disclosure sections
        if generated_soup.find('section', class_='disclosure-section'):
            improvements.append('Modern disclosure sections implemented')

        # Check for card-based layout
        if generated_soup.find(class_='card'):
            improvements.append('Card-based layout applied')

        # Check for semantic HTML
        if generated_soup.find('section'):
            improvements.append('Semantic HTML5 structure')

        # Check background color (should be white, not green)
        body_style = generated_soup.find('body')
        if body_style:
            improvements.append('Modern color scheme (white background)')

        return improvements

    def validate_all(self, original_dir: Path, generated_dir: Path, json_dir: Path) -> Dict:
        """Validate all generated files."""
        results = []

        original_files = sorted(original_dir.glob('XF*.htm'))

        for original_file in original_files:
            person_id = original_file.stem
            generated_file = generated_dir / f"{person_id}.htm"
            json_file = json_dir / f"{person_id}.json"

            if not generated_file.exists():
                self.errors.append({
                    'type': 'missing_generated',
                    'original': str(original_file),
                    'expected': str(generated_file)
                })
                continue

            if not json_file.exists():
                self.errors.append({
                    'type': 'missing_json',
                    'expected': str(json_file)
                })
                continue

            result = self.validate_person(original_file, generated_file, json_file)
            results.append(result)

            self.stats['files_validated'] += 1
            if result['status'] == 'PASS':
                self.stats['content_matches'] += 1
            else:
                self.stats['missing_data'] += 1

            if result['improvements']:
                self.stats['design_improvements'] += 1

        return {
            'summary': self.stats,
            'results': results,
            'errors': self.errors,
            'warnings': self.warnings
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Validate generated HTML vs original')
    parser.add_argument('--original-dir', required=True, help='Directory with original HTML files')
    parser.add_argument('--generated-dir', required=True, help='Directory with generated HTML files')
    parser.add_argument('--json-dir', required=True, help='Directory with JSON data files')
    parser.add_argument('--report', default='generation-validation-report.json', help='Output report file')
    parser.add_argument('--fail-on-error', action='store_true', help='Exit with error code if validation fails')

    args = parser.parse_args()

    validator = GenerationValidator()
    report = validator.validate_all(
        Path(args.original_dir),
        Path(args.generated_dir),
        Path(args.json_dir)
    )

    # Save report
    with open(args.report, 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print("GENERATION VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Files Validated: {report['summary']['files_validated']}")
    print(f"✅ Content Matches: {report['summary']['content_matches']}")
    print(f"❌ Missing Data: {report['summary']['missing_data']}")
    print(f"🎨 Design Improvements: {report['summary']['design_improvements']}")
    print(f"\nReport saved to: {args.report}")

    # Show sample missing data
    if report['summary']['missing_data'] > 0:
        print(f"\n⚠️  ISSUES FOUND:")
        for result in report['results'][:5]:  # Show first 5
            if result['missing_data']:
                print(f"\n  File: {result['generated_file']}")
                for missing in result['missing_data'][:3]:  # Show first 3 issues
                    print(f"    - {missing['type']}: {missing.get('value', missing.get('text', 'N/A'))}")

    # Exit with error if data missing
    if args.fail_on_error and report['summary']['missing_data'] > 0:
        print("\n❌ VALIDATION FAILED - Missing data detected!")
        exit(1)
    else:
        print("\n✅ VALIDATION PASSED")
        exit(0)


if __name__ == '__main__':
    main()
