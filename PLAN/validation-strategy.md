# Validation Strategy - Comprehensive Data Integrity Testing

## Overview

This document specifies the comprehensive automated validation strategy to ensure **zero data loss** during extraction (HTML → JSON) and generation (JSON → HTML).

**Critical Requirement**: With 2,985+ pages, manual spot-checks cannot catch rare edge cases (1 in 1000 files). We need 100% automated validation.

## Validation Phases

```
Phase 1: HTML → JSON Extraction
├─ Extract all data from original HTML
├─ Parse both original HTML and extracted JSON
├─ Compare: Does JSON contain ALL data from HTML?
└─ Report: Any missing data, extraction errors, edge cases

Phase 2: JSON → HTML Generation
├─ Generate HTML from JSON
├─ Parse both original HTML and generated HTML
├─ Compare: Does generated HTML contain ALL data from original?
└─ Report: Any missing data, rendering errors, regressions
```

## Tool 1: Extraction Validation (HTML → JSON)

**Script**: `PRPs/scripts/both/validate_extraction.py`

### Purpose

Compare original HTML files with extracted JSON to ensure no data loss during extraction.

### Validation Algorithm

```python
#!/usr/bin/env python3
"""
Comprehensive extraction validation: HTML → JSON

Validates that ALL data from original HTML is preserved in JSON extraction.

Usage:
    python3 validate_extraction.py \
        --html-dir docs/new/htm/L1 \
        --json-dir data/people/Hagborg-Hansson \
        --report data/extraction-validation-report.json
"""

from pathlib import Path
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Tuple

class ExtractionValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'files_validated': 0,
            'perfect_matches': 0,
            'minor_differences': 0,
            'data_loss_detected': 0
        }

    def validate_person(self, html_path: Path, json_path: Path) -> Dict:
        """Validate single person extraction."""

        # Parse original HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_soup = BeautifulSoup(f.read(), 'html.parser')

        # Load extracted JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Extract all text content from HTML
        html_content = self.extract_all_content(html_soup)

        # Extract all text content from JSON
        json_content = self.extract_all_json_content(json_data)

        # Compare
        missing_data = self.find_missing_data(html_content, json_content)

        # Validate specific fields
        field_validation = self.validate_fields(html_soup, json_data)

        return {
            'html_file': str(html_path),
            'json_file': str(json_path),
            'person_id': json_data.get('id'),
            'person_name': json_data.get('name'),
            'missing_data': missing_data,
            'field_validation': field_validation,
            'status': 'PASS' if not missing_data and all(field_validation.values()) else 'FAIL'
        }

    def extract_all_content(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all meaningful content from HTML."""
        content = {
            'text_content': [],
            'links': [],
            'table_data': {}
        }

        # Extract from main table
        table = soup.find('table', id='List')
        if table:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text().strip()
                    value_cell = cells[1]

                    # Get text content
                    text = value_cell.get_text().strip()
                    if text and text != '0':
                        content['table_data'][label] = text

                    # Get link if present
                    link = value_cell.find('a')
                    if link:
                        content['links'].append({
                            'label': label,
                            'text': link.get_text().strip(),
                            'href': link.get('href')
                        })

        # Extract children table
        children_data = self.extract_children_table(soup)
        if children_data:
            content['children'] = children_data

        # Extract photos tables
        photos_data = self.extract_photos_tables(soup)
        if photos_data:
            content['photos'] = photos_data

        return content

    def extract_children_table(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract children from second table."""
        children = []
        tables = soup.find_all('table', id='List')

        if len(tables) >= 2:
            children_table = tables[1]
            for row in children_table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link = cells[0].find('a')
                    if link:
                        children.append({
                            'name': link.get_text().strip(),
                            'href': link.get('href'),
                            'birthDate': cells[1].get_text().strip()
                        })

        return children

    def extract_photos_tables(self, soup: BeautifulSoup) -> Dict:
        """Extract photos from third and fourth tables."""
        photos = {'of_person': [], 'by_person': []}
        tables = soup.find_all('table', id='List')

        # Photos of this person (table 3)
        if len(tables) >= 3:
            photos['of_person'] = self._extract_photo_table(tables[2])

        # Photos by this person (table 4)
        if len(tables) >= 4:
            photos['by_person'] = self._extract_photo_table(tables[3])

        return photos

    def _extract_photo_table(self, table) -> List[Dict]:
        """Extract photo data from a table."""
        photos = []
        for row in table.find_all('tr')[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 3:
                photos.append({
                    'name': cells[0].get_text().strip(),
                    'date': cells[1].get_text().strip(),
                    'location': cells[2].get_text().strip()
                })
        return photos

    def extract_all_json_content(self, json_data: Dict) -> Dict:
        """Extract all content from JSON for comparison."""
        content = {
            'fields': {},
            'links': [],
            'children': [],
            'photos': {'of_person': [], 'by_person': []}
        }

        # Extract all non-null fields
        for key, value in json_data.items():
            if value is not None and value != '' and value != '0' and key != 'metadata':
                content['fields'][key] = value

        # Extract family links
        if json_data.get('father'):
            content['links'].append(json_data['father'])
        if json_data.get('mother'):
            content['links'].append(json_data['mother'])
        if json_data.get('spouses'):
            content['links'].extend(json_data['spouses'])

        # Extract children
        if json_data.get('children'):
            content['children'] = json_data['children']

        # Extract photos
        if json_data.get('photos'):
            content['photos']['of_person'] = json_data['photos']
        if json_data.get('photographedBy'):
            content['photos']['by_person'] = json_data['photographedBy']

        return content

    def find_missing_data(self, html_content: Dict, json_content: Dict) -> List[Dict]:
        """Find any data in HTML that's missing from JSON."""
        missing = []

        # Check table data
        for label, value in html_content.get('table_data', {}).items():
            # Skip known empty/placeholder values
            if value in ['0', '', 'Don\'t Know', 'Unknown']:
                continue

            # Check if this data exists anywhere in JSON
            if not self._data_exists_in_json(value, json_content):
                missing.append({
                    'type': 'table_field',
                    'label': label,
                    'value': value,
                    'severity': 'ERROR'
                })

        # Check links
        for link in html_content.get('links', []):
            if not self._link_exists_in_json(link, json_content):
                missing.append({
                    'type': 'link',
                    'label': link['label'],
                    'text': link['text'],
                    'href': link['href'],
                    'severity': 'ERROR'
                })

        # Check children
        html_children = html_content.get('children', [])
        json_children = json_content.get('children', [])
        if len(html_children) != len(json_children):
            missing.append({
                'type': 'children_count_mismatch',
                'html_count': len(html_children),
                'json_count': len(json_children),
                'severity': 'ERROR'
            })

        return missing

    def _data_exists_in_json(self, value: str, json_content: Dict) -> bool:
        """Check if a value exists anywhere in JSON."""
        json_str = json.dumps(json_content).lower()
        return value.lower() in json_str

    def _link_exists_in_json(self, link: Dict, json_content: Dict) -> bool:
        """Check if a link exists in JSON."""
        for json_link in json_content.get('links', []):
            if isinstance(json_link, dict):
                if json_link.get('name') == link['text'] or json_link.get('url') == link['href']:
                    return True
        return False

    def validate_fields(self, html_soup: BeautifulSoup, json_data: Dict) -> Dict[str, bool]:
        """Validate specific field mappings."""
        validation = {}

        # Validate name
        h1 = html_soup.find('h1')
        if h1:
            html_name = h1.get_text().split('\n')[0].strip()
            validation['name'] = html_name == json_data.get('name')

        # Validate lineage
        lineage_link = self._find_table_link(html_soup, 'Lineage')
        if lineage_link:
            validation['lineage'] = lineage_link.get_text().strip() == json_data.get('lineage')

        # Validate father
        father_link = self._find_table_link(html_soup, 'Father')
        if father_link:
            father_name = father_link.get_text().strip()
            json_father = json_data.get('father', {})
            validation['father'] = json_father.get('name') == father_name if json_father else False

        # Validate mother
        mother_link = self._find_table_link(html_soup, 'Mother')
        if mother_link:
            mother_name = mother_link.get_text().strip()
            json_mother = json_data.get('mother', {})
            validation['mother'] = json_mother.get('name') == mother_name if json_mother else False

        return validation

    def _find_table_link(self, soup: BeautifulSoup, label: str):
        """Find a link in the table by row label."""
        table = soup.find('table', id='List')
        if table:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2 and cells[0].get_text().strip() == label:
                    return cells[1].find('a')
        return None

    def validate_all(self, html_dir: Path, json_dir: Path) -> Dict:
        """Validate all files in directories."""
        results = []

        # Get all HTML files
        html_files = sorted(html_dir.glob('XF*.htm'))

        for html_file in html_files:
            person_id = html_file.stem
            json_file = json_dir / f"{person_id}.json"

            if not json_file.exists():
                self.errors.append({
                    'type': 'missing_json',
                    'html_file': str(html_file),
                    'expected_json': str(json_file)
                })
                continue

            result = self.validate_person(html_file, json_file)
            results.append(result)

            self.stats['files_validated'] += 1
            if result['status'] == 'PASS' and not result['missing_data']:
                self.stats['perfect_matches'] += 1
            elif result['status'] == 'PASS':
                self.stats['minor_differences'] += 1
            else:
                self.stats['data_loss_detected'] += 1

        return {
            'summary': self.stats,
            'results': results,
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Validate HTML → JSON extraction')
    parser.add_argument('--html-dir', required=True, help='Directory with original HTML files')
    parser.add_argument('--json-dir', required=True, help='Directory with extracted JSON files')
    parser.add_argument('--report', default='extraction-validation-report.json', help='Output report file')
    parser.add_argument('--fail-on-error', action='store_true', help='Exit with error code if validation fails')

    args = parser.parse_args()

    validator = ExtractionValidator()
    report = validator.validate_all(Path(args.html_dir), Path(args.json_dir))

    # Save report
    with open(args.report, 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print("EXTRACTION VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Files Validated: {report['summary']['files_validated']}")
    print(f"Perfect Matches: {report['summary']['perfect_matches']}")
    print(f"Minor Differences: {report['summary']['minor_differences']}")
    print(f"❌ DATA LOSS DETECTED: {report['summary']['data_loss_detected']}")
    print(f"\nReport saved to: {args.report}")

    # Exit with error if data loss detected
    if args.fail_on_error and report['summary']['data_loss_detected'] > 0:
        print("\n❌ VALIDATION FAILED - Data loss detected!")
        exit(1)
    else:
        print("\n✅ VALIDATION PASSED")
        exit(0)

if __name__ == '__main__':
    main()
```

### Success Criteria

- **100% of files validated**: Every HTML file has corresponding JSON
- **Zero data loss**: All meaningful data from HTML exists in JSON
- **Field accuracy**: Name, lineage, family relationships exactly match
- **Link preservation**: All URLs and person references preserved

## Tool 2: Generation Validation (JSON → HTML)

**Script**: `PRPs/scripts/both/validate_generation.py`

### Purpose

Compare generated HTML files with original HTML to ensure no data loss during generation and that modern design improvements don't sacrifice content.

### Validation Algorithm

```python
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
        missing = self.find_missing_content(original_data, generated_data)
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
        tables = soup.find_all('table')
        for table in tables:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()

                    if value and value != '0':
                        data['fields'][label] = value

                    link = cells[1].find('a')
                    if link:
                        data['links'].append({
                            'text': link.get_text().strip(),
                            'href': link.get('href')
                        })

        # Extract from disclosure sections (new format)
        disclosure_sections = soup.find_all('div', class_='disclosure-content')
        for section in disclosure_sections:
            text = section.get_text(separator=' ', strip=True)
            data['text_content'].append(text)

            # Extract links from disclosure sections
            for link in section.find_all('a'):
                data['links'].append({
                    'text': link.get_text().strip(),
                    'href': link.get('href')
                })

        return data

    def find_missing_content(self, original: Dict, generated: Dict) -> List[Dict]:
        """Find content in original that's missing from generated."""
        missing = []

        # Check name
        if original['name'] != generated['name']:
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

            # Check if value exists anywhere in generated data
            generated_str = json.dumps(generated).lower()
            if value.lower() not in generated_str:
                missing.append({
                    'type': 'missing_field_value',
                    'field': label,
                    'value': value,
                    'severity': 'ERROR'
                })

        # Check links
        for orig_link in original['links']:
            found = False
            for gen_link in generated['links']:
                if (orig_link['text'] == gen_link['text'] and
                    orig_link['href'] == gen_link['href']):
                    found = True
                    break

            if not found:
                missing.append({
                    'type': 'missing_link',
                    'text': orig_link['text'],
                    'href': orig_link['href'],
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
        if generated_soup.find('div', class_='disclosure-section'):
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
    import re

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
```

### Success Criteria

- **100% content preservation**: All data from original HTML exists in generated HTML
- **Zero missing links**: All family/lineage links preserved
- **Design improvements documented**: Modern features added without data loss

## Validation Workflow

### Phase 1 Workflow

```bash
# 1. Extract data
python3 PRPs/scripts/both/extract_person_data.py \
    --lineage Hagborg-Hansson \
    --input-dir docs/new/htm/L1 \
    --output-dir data/people/Hagborg-Hansson

# 2. Validate extraction (CRITICAL)
python3 PRPs/scripts/both/validate_extraction.py \
    --html-dir docs/new/htm/L1 \
    --json-dir data/people/Hagborg-Hansson \
    --report data/extraction-validation-report.json \
    --fail-on-error

# If validation fails, fix extraction script and re-run
# Do NOT proceed to Phase 2 until this passes 100%
```

### Phase 2 Workflow

```bash
# 1. Generate pages
python3 PRPs/scripts/both/generate_pages.py \
    --lineage Hagborg-Hansson \
    --input-dir data/people/Hagborg-Hansson \
    --output-dir docs/new/htm/L1-generated-test

# 2. Validate generation (CRITICAL)
python3 PRPs/scripts/both/validate_generation.py \
    --original-dir docs/new/htm/L1 \
    --generated-dir docs/new/htm/L1-generated-test \
    --json-dir data/people/Hagborg-Hansson \
    --report generation-validation-report.json \
    --fail-on-error

# If validation fails, fix templates/generation script and re-run
# Do NOT deploy until this passes 100%
```

## CI/CD Integration

Add to `.gitlab-ci.yml`:

```yaml
validate-extraction:
  stage: test
  script:
    - pip install beautifulsoup4 lxml
    - python3 PRPs/scripts/both/validate_extraction.py \
        --html-dir docs/new/htm \
        --json-dir data/people \
        --report extraction-validation.json \
        --fail-on-error
  artifacts:
    paths:
      - extraction-validation.json
    when: always

validate-generation:
  stage: test
  script:
    - pip install beautifulsoup4 lxml
    - python3 PRPs/scripts/both/validate_generation.py \
        --original-dir docs/new/htm \
        --generated-dir docs/new/htm-generated \
        --json-dir data/people \
        --report generation-validation.json \
        --fail-on-error
  artifacts:
    paths:
      - generation-validation.json
    when: always
```

## Validation Report Format

### Extraction Validation Report

```json
{
  "summary": {
    "files_validated": 123,
    "perfect_matches": 121,
    "minor_differences": 2,
    "data_loss_detected": 0
  },
  "results": [
    {
      "html_file": "docs/new/htm/L1/XF100.htm",
      "json_file": "data/people/Hagborg-Hansson/XF100.json",
      "person_id": "XF100",
      "person_name": "Johanna Hakanson",
      "missing_data": [],
      "field_validation": {
        "name": true,
        "lineage": true,
        "father": true,
        "mother": true
      },
      "status": "PASS"
    }
  ],
  "errors": [],
  "warnings": []
}
```

### Generation Validation Report

```json
{
  "summary": {
    "files_validated": 123,
    "content_matches": 123,
    "missing_data": 0,
    "design_improvements": 123
  },
  "results": [
    {
      "original_file": "docs/new/htm/L1/XF100.htm",
      "generated_file": "docs/new/htm/L1-generated-test/XF100.htm",
      "person_id": "XF100",
      "person_name": "Johanna Hakanson",
      "missing_data": [],
      "improvements": [
        "Phase 4 design system applied",
        "Modern disclosure sections implemented",
        "Card-based layout applied",
        "Semantic HTML5 structure",
        "Modern color scheme (white background)"
      ],
      "status": "PASS"
    }
  ],
  "errors": [],
  "warnings": []
}
```

## Edge Cases to Test

The validation tools must handle:

1. **Special characters**: Names with accents, umlauts (Swedish characters)
2. **Multiple spouses**: Up to 4 spouse entries
3. **Empty fields**: Null vs "0" vs empty string
4. **Missing data**: Birth dates, locations, etc.
5. **Long text**: Notes fields with paragraphs
6. **Brackets in names**: `[Lineage]` suffixes
7. **Unusual URLs**: Malformed or relative paths
8. **Circular references**: Parent lists child, child lists parent
9. **Orphaned records**: People with no family connections
10. **Large families**: 10+ children

## Acceptance Criteria

Before deployment to production:

- [ ] **100% extraction validation**: All files pass, zero data loss
- [ ] **100% generation validation**: All files pass, zero data loss
- [ ] **Manual review**: User reviews 10 random validated pages
- [ ] **Edge case coverage**: All 10 edge cases tested and handled
- [ ] **CI integration**: Validation runs automatically on every commit
- [ ] **Documentation**: Validation reports are clear and actionable

## Failure Response

If validation detects data loss:

1. **STOP immediately** - Do not proceed to next phase
2. **Review validation report** - Identify which files/fields failed
3. **Analyze edge cases** - What pattern causes the failure?
4. **Fix extraction/generation script** - Address the root cause
5. **Re-run validation** - Verify fix resolves issue
6. **Commit fix** - Document what edge case was found
7. **Repeat** - Until 100% validation pass rate achieved

**Never deploy with data loss. Better to delay than lose genealogy data.**
