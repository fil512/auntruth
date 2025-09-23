#!/usr/bin/env python3
"""
Search Index Generator for AuntieRuth.com Genealogy Site
Parses all HTML files to extract person data and generate searchable JSON index

This script processes ~11,070 HTML files to extract:
- Person names and identifiers
- Birth/death dates and locations
- Lineage affiliations
- Family relationships
- Page URLs for direct linking

Output: docs/new/js/data.json
"""

import os
import re
import json
import argparse
from pathlib import Path
from html.parser import HTMLParser
from typing import Dict, List, Optional, Set
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PersonData:
    """Data structure for a person's genealogy information"""
    id: str
    name: str
    filename: str
    url: str
    lineage: str
    lineageName: str
    birthDate: str = ""
    birthLocation: str = ""
    deathDate: str = ""
    deathLocation: str = ""
    spouse: str = ""
    spouse2: str = ""
    spouse3: str = ""
    spouse4: str = ""
    father: str = ""
    mother: str = ""
    occupation: str = ""
    address: str = ""
    notes: str = ""
    children: List[str] = None
    deceased: str = ""
    genetics: str = ""
    source: str = ""
    waiting: str = ""

    def __post_init__(self):
        if self.children is None:
            self.children = []

class SimpleHTMLParser(HTMLParser):
    """Simple HTML parser to extract data from genealogy pages"""

    def __init__(self):
        super().__init__()
        self.reset()
        self.current_table = None
        self.current_row = []
        self.current_cell = ""
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.in_title = False
        self.in_h1 = False
        self.title_text = ""
        self.h1_text = ""
        self.tables = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            attr_dict = dict(attrs)
            if attr_dict.get('id') == 'List':
                self.in_table = True
                self.current_table = []
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag == 'td' and self.in_row:
            self.in_cell = True
            self.current_cell = ""
        elif tag == 'title':
            self.in_title = True
            self.title_text = ""
        elif tag == 'h1':
            self.in_h1 = True
            self.h1_text = ""
        elif tag == 'a':
            attr_dict = dict(attrs)
            href = attr_dict.get('href', '')
            self.links.append(href)

    def handle_endtag(self, tag):
        if tag == 'table' and self.in_table:
            self.in_table = False
            if self.current_table:
                self.tables.append(self.current_table)
        elif tag == 'tr' and self.in_row:
            self.in_row = False
            if self.current_row:
                self.current_table.append(self.current_row)
        elif tag == 'td' and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
        elif tag == 'title':
            self.in_title = False
        elif tag == 'h1':
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data
        elif self.in_title:
            self.title_text += data
        elif self.in_h1:
            self.h1_text += data

@dataclass
class LineageData:
    """Data structure for lineage information"""
    number: str
    name: str
    path: str
    peopleCount: int
    description: str = ""

class GenealogyIndexGenerator:
    """Main class for generating the search index from HTML files"""

    def __init__(self, source_dir: str = 'docs/new/htm', output_file: str = 'docs/new/js/data.json'):
        self.source_dir = Path(source_dir)
        self.output_file = Path(output_file)
        self.people_data: List[PersonData] = []
        self.lineage_data: Dict[str, LineageData] = {}
        self.processed_files = 0
        self.error_files = 0
        self.duplicate_ids: Set[str] = set()

        # Lineage name mappings
        self.lineage_names = {
            '0': 'Base',
            '1': 'Hagborg-Hansson',
            '2': 'Nelson',
            '3': 'Lineage 3',
            '4': 'Lineage 4',
            '5': 'Lineage 5',
            '6': 'Lineage 6',
            '7': 'Lineage 7',
            '8': 'Lineage 8',
            '9': 'Lineage 9'
        }

    def parse_person_page(self, file_path: Path) -> Optional[PersonData]:
        """Extract person data from XF*.htm files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            parser = SimpleHTMLParser()
            parser.feed(content)

            # Extract basic file info
            filename = file_path.name
            lineage_match = re.search(r'/L(\d+)/', str(file_path))
            lineage_num = lineage_match.group(1) if lineage_match else '0'

            # Extract person ID from filename (XF123.htm -> 123)
            id_match = re.search(r'XF(\d+)\.htm', filename)
            person_id = id_match.group(1) if id_match else filename.replace('.htm', '')

            # Check for duplicates
            if person_id in self.duplicate_ids:
                logger.warning(f"Duplicate person ID found: {person_id} in {file_path}")
                person_id = f"{person_id}_{lineage_num}"
            else:
                self.duplicate_ids.add(person_id)

            # Extract name from title or h1
            name = self.extract_name(parser)

            # Extract data from the structured table
            person_data = PersonData(
                id=person_id,
                name=name,
                filename=filename,
                url=f"/auntruth/new/htm/L{lineage_num}/{filename}",
                lineage=lineage_num,
                lineageName=self.lineage_names.get(lineage_num, f"Lineage {lineage_num}")
            )

            # Parse the main data table
            self.parse_data_table(parser, person_data)

            # Parse children table if present
            self.parse_children_table(parser, person_data)

            return person_data

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            self.error_files += 1
            return None

    def extract_name(self, parser: SimpleHTMLParser) -> str:
        """Extract person name from various possible locations"""
        # Try title first
        if parser.title_text:
            title_text = parser.title_text.replace('<br>', ' ').replace('AuntieRuth.com', '').strip()
            if title_text and title_text != 'AuntieRuth.com':
                return title_text

        # Try h1 tags
        if parser.h1_text:
            h1_text = parser.h1_text.replace('AuntieRuth.com', '').strip()
            if h1_text:
                return h1_text

        return "Unknown Person"

    def parse_data_table(self, parser: SimpleHTMLParser, person_data: PersonData):
        """Parse the main genealogy data table"""
        if not parser.tables:
            logger.warning(f"No data table found for {person_data.filename}")
            return

        # Usually the first table contains the person data
        main_table = parser.tables[0]

        for row in main_table:
            if len(row) >= 2:
                label = row[0].strip().lower()
                value = row[1].strip()

                # Map table fields to person data
                if 'father' in label:
                    person_data.father = value
                elif 'mother' in label:
                    person_data.mother = value
                elif 'birthdate' in label or 'birth date' in label:
                    person_data.birthDate = value
                elif 'birth location' in label:
                    person_data.birthLocation = value
                elif 'death date' in label:
                    person_data.deathDate = value
                elif 'spouse(1)' in label or ('spouse' in label and '(' not in label):
                    person_data.spouse = value
                elif 'spouse(2)' in label:
                    person_data.spouse2 = value
                elif 'spouse(3)' in label:
                    person_data.spouse3 = value
                elif 'spouse(4)' in label:
                    person_data.spouse4 = value
                elif 'occupation' in label:
                    person_data.occupation = value
                elif 'address' in label:
                    person_data.address = value
                elif 'notes' in label:
                    person_data.notes = value
                elif 'deceased' in label:
                    person_data.deceased = value
                elif 'genetics' in label:
                    person_data.genetics = value
                elif 'source' in label:
                    person_data.source = value
                elif 'waiting' in label:
                    person_data.waiting = value

    def parse_children_table(self, parser: SimpleHTMLParser, person_data: PersonData):
        """Parse the children table if present"""
        # For now, skip children parsing as it requires more complex HTML parsing
        # This can be enhanced later if needed
        pass

    def parse_lineage_index(self, file_path: Path) -> Optional[LineageData]:
        """Extract lineage structure from index.htm files"""
        try:
            lineage_match = re.search(r'/L(\d+)/', str(file_path))
            if not lineage_match:
                return None

            lineage_num = lineage_match.group(1)

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            parser = SimpleHTMLParser()
            parser.feed(content)

            lineage_name = self.lineage_names.get(lineage_num, f"Lineage {lineage_num}")

            # Try to get better name from h1
            if parser.h1_text:
                h1_text = parser.h1_text.strip()
                if 'lineage' in h1_text.lower() and lineage_num in h1_text:
                    # Extract the lineage name part
                    parts = h1_text.split()
                    for i, part in enumerate(parts):
                        if 'lineage' in part.lower():
                            if i + 1 < len(parts):
                                lineage_name = parts[i + 1]
                            break

            # Count people in this lineage directory
            lineage_dir = file_path.parent
            xf_files = list(lineage_dir.glob('XF*.htm'))
            people_count = len(xf_files)

            return LineageData(
                number=lineage_num,
                name=lineage_name,
                path=f"/auntruth/new/htm/L{lineage_num}/",
                peopleCount=people_count,
                description=f"Family lineage {lineage_name} with {people_count} people"
            )

        except Exception as e:
            logger.error(f"Error parsing lineage index {file_path}: {e}")
            return None

    def scan_directories(self) -> List[Path]:
        """Scan all directories L0-L9 for person files"""
        person_files = []

        if not self.source_dir.exists():
            logger.error(f"Source directory does not exist: {self.source_dir}")
            return person_files

        # Scan lineage directories L0-L9
        for i in range(10):
            lineage_dir = self.source_dir / f"L{i}"
            if lineage_dir.exists():
                logger.info(f"Scanning {lineage_dir}")

                # Process lineage index
                index_file = lineage_dir / "index.htm"
                if index_file.exists():
                    lineage_data = self.parse_lineage_index(index_file)
                    if lineage_data:
                        self.lineage_data[str(i)] = lineage_data

                # Find all XF*.htm files (person pages)
                xf_files = list(lineage_dir.glob('XF*.htm'))
                person_files.extend(xf_files)

                logger.info(f"Found {len(xf_files)} person files in L{i}")
            else:
                logger.warning(f"Lineage directory L{i} not found")

        logger.info(f"Total person files found: {len(person_files)}")
        return person_files

    def generate_index(self, dry_run: bool = False) -> bool:
        """Main generation process"""
        logger.info(f"Starting index generation from {self.source_dir}")
        logger.info(f"Output file: {self.output_file}")

        if dry_run:
            logger.info("DRY RUN MODE - No files will be written")

        # Scan all directories for person files
        person_files = self.scan_directories()

        if not person_files:
            logger.error("No person files found!")
            return False

        # Process each person file
        logger.info("Processing person files...")

        for i, file_path in enumerate(person_files):
            if i % 100 == 0 and i > 0:
                logger.info(f"Processed {i}/{len(person_files)} files...")

            person_data = self.parse_person_page(file_path)
            if person_data:
                self.people_data.append(person_data)
                self.processed_files += 1

        logger.info(f"Processing complete!")
        logger.info(f"Successfully processed: {self.processed_files}")
        logger.info(f"Errors: {self.error_files}")
        logger.info(f"Total people: {len(self.people_data)}")
        logger.info(f"Total lineages: {len(self.lineage_data)}")

        if not dry_run:
            return self.write_json_output()
        else:
            logger.info("DRY RUN - Skipping file write")
            return True

    def write_json_output(self) -> bool:
        """Write the search index to JSON file"""
        try:
            # Ensure output directory exists
            self.output_file.parent.mkdir(parents=True, exist_ok=True)

            # Prepare output data
            output_data = {
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "totalPeople": len(self.people_data),
                    "totalLineages": len(self.lineage_data),
                    "processedFiles": self.processed_files,
                    "errorFiles": self.error_files,
                    "version": "1.0"
                },
                "people": [asdict(person) for person in self.people_data],
                "lineages": [asdict(lineage) for lineage in self.lineage_data.values()]
            }

            # Write JSON file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Search index written to {self.output_file}")
            logger.info(f"File size: {self.output_file.stat().st_size / 1024:.1f} KB")

            return True

        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            return False

    def validate_output(self) -> bool:
        """Validate the generated JSON file"""
        if not self.output_file.exists():
            logger.error("Output file does not exist")
            return False

        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            required_keys = ['metadata', 'people', 'lineages']
            for key in required_keys:
                if key not in data:
                    logger.error(f"Missing required key: {key}")
                    return False

            people_count = len(data['people'])
            lineages_count = len(data['lineages'])

            logger.info(f"Validation successful:")
            logger.info(f"  People: {people_count}")
            logger.info(f"  Lineages: {lineages_count}")
            logger.info(f"  File size: {self.output_file.stat().st_size / 1024:.1f} KB")

            # Check for reasonable data
            if people_count < 100:
                logger.warning(f"Low person count: {people_count} (expected thousands)")

            if lineages_count < 5:
                logger.warning(f"Low lineage count: {lineages_count} (expected ~10)")

            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate search index for AuntieRuth.com genealogy site')
    parser.add_argument('--source-dir', default='docs/new/htm',
                       help='Source directory containing HTML files (default: docs/new/htm)')
    parser.add_argument('--output-file', default='docs/new/js/data.json',
                       help='Output JSON file path (default: docs/new/js/data.json)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without writing output file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate existing output file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    generator = GenealogyIndexGenerator(args.source_dir, args.output_file)

    if args.validate:
        if generator.validate_output():
            logger.info("Validation passed!")
            return 0
        else:
            logger.error("Validation failed!")
            return 1

    try:
        success = generator.generate_index(dry_run=args.dry_run)

        if success and not args.dry_run:
            # Validate the output
            if generator.validate_output():
                logger.info("Index generation completed successfully!")
                return 0
            else:
                logger.error("Generated file failed validation!")
                return 1
        elif success:
            logger.info("Dry run completed successfully!")
            return 0
        else:
            logger.error("Index generation failed!")
            return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())