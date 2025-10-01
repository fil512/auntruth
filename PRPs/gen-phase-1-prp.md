# PRP: Page Generation Phase 1 - Data Extraction

## Prerequisites - READ THESE FILES FIRST

**CRITICAL**: Before starting this phase, read the following files to understand the complete context:

1. `Read(PLAN/page-generation-overview.md)` - Overall architecture and strategy
2. `Read(PLAN/data-schema.md)` - JSON schema specification you must follow
3. `Read(PLAN/validation-strategy.md)` - Comprehensive validation strategy (CRITICAL for data integrity)
4. `Read(CLAUDE.md)` - Project conventions and guidelines
5. `Read(docs/README.md)` - File structure and naming conventions
6. `Read(PRPs/scripts/README.md)` - Script development guidelines

## Phase 1 Overview

**Objective**: Extract structured data from existing HTML person pages into JSON format.

**Scope**: Start with **Hagborg-Hansson lineage only** (~100 people) as proof-of-concept.

**Duration**: 1 week

**Output**:
- JSON files in `data/people/Hagborg-Hansson/*.json`
- Extraction script: `PRPs/scripts/both/extract_person_data.py`
- Schema validation script: `PRPs/scripts/both/validate_json_data.py`
- **Comprehensive validation tool: `PRPs/scripts/both/validate_extraction.py`** (CRITICAL)
- Extraction validation report: `data/extraction-validation-report.json`
- Extraction summary report: `data/extraction-report-phase1.md`

## Phase 1 Tasks

### Task 1: Analyze Existing HTML Structure (Day 1)

**Objective**: Understand the HTML patterns used in person pages.

**Actions**:
1. Read sample person pages from `docs/new/htm/L1/`:
   - `XF100.htm` (Johanna Hakanson) - Test page
   - `XF82.htm` (Matts Hakansson) - Father reference
   - `XF81.htm` (Else Hansdotter-Hakansson) - Mother reference
   - `XF101.htm` (Albert) - Spouse reference

2. Document HTML patterns found:
   - How is `table#List` structured?
   - How are links formatted? (extract person ID from href)
   - How are empty fields represented? (empty `<strong>`, "0", empty string)
   - How are multiple spouses/children handled?
   - What edge cases exist?

3. Create pattern documentation:
   ```bash
   # Document findings
   vim PLAN/html-patterns.md
   ```

**Success Criteria**:
- Understand all table row labels and their meanings
- Know how to extract person IDs from URLs
- Identify all edge cases (missing data, special characters, etc.)

### Task 2: Create Data Extraction Script (Days 2-3)

**Objective**: Build Python script to parse HTML → JSON.

**Script Location**: `PRPs/scripts/both/extract_person_data.py`

**Script Requirements**:

1. **Command-line interface**:
   ```bash
   # Extract single person
   python3 PRPs/scripts/both/extract_person_data.py \
       --input docs/new/htm/L1/XF100.htm \
       --output data/people/Hagborg-Hansson/XF100.json

   # Extract entire lineage
   python3 PRPs/scripts/both/extract_person_data.py \
       --lineage Hagborg-Hansson \
       --input-dir docs/new/htm/L1 \
       --output-dir data/people/Hagborg-Hansson

   # Dry run (validate without writing)
   python3 PRPs/scripts/both/extract_person_data.py \
       --lineage Hagborg-Hansson \
       --dry-run
   ```

2. **Core Functionality**:
   ```python
   #!/usr/bin/env python3
   """
   Extract person data from HTML pages to JSON.

   Usage:
       python3 extract_person_data.py --lineage Hagborg-Hansson
   """

   from pathlib import Path
   from bs4 import BeautifulSoup
   import json
   import re
   from datetime import datetime

   def parse_person_html(html_path):
       """Parse a single HTML file and extract person data."""
       with open(html_path, 'r', encoding='utf-8') as f:
           soup = BeautifulSoup(f.read(), 'html.parser')

       person = {
           'id': extract_person_id(html_path),
           'name': extract_name(soup),
           'lineage': extract_lineage(soup),
           # ... extract all fields per schema
       }

       return person

   def extract_person_id(html_path):
       """Extract XF### from filename."""
       return Path(html_path).stem  # e.g., XF100

   def extract_name(soup):
       """Extract person name from h1."""
       h1 = soup.find('h1')
       if h1:
           # "Johanna Hakanson\n<br>\nAuntieRuth.com"
           text = h1.get_text()
           # Get first line before <br>
           return text.split('\n')[0].strip()
       return None

   def extract_table_data(soup):
       """Extract data from table#List."""
       table = soup.find('table', id='List')
       if not table:
           return {}

       data = {}
       rows = table.find_all('tr')

       for row in rows:
           cells = row.find_all('td')
           if len(cells) >= 2:
               label = cells[0].get_text().strip()
               value_cell = cells[1]

               # Extract link if present
               link = value_cell.find('a')
               if link:
                   data[label] = {
                       'name': link.get_text().strip(),
                       'url': link.get('href'),
                       'id': extract_id_from_url(link.get('href'))
                   }
               else:
                   # Plain text value
                   value = value_cell.get_text().strip()
                   data[label] = normalize_value(value)

       return data

   def extract_id_from_url(url):
       """Extract XF### from URL like '/auntruth/new/htm/L1/XF100.htm'."""
       if url:
           match = re.search(r'(XF\d+)\.htm', url)
           if match:
               return match.group(1)
       return None

   def normalize_value(value):
       """Convert empty/zero values to None."""
       if not value or value == '0' or value == '':
           return None
       return value

   def map_to_schema(raw_data, html_path):
       """Map extracted data to official JSON schema."""
       # Map table labels to schema fields
       person = {
           'id': raw_data.get('id'),
           'name': raw_data.get('name'),
           'lineage': raw_data.get('Lineage', {}).get('name'),
           'birthDate': raw_data.get('BirthDate'),
           'birthLocation': raw_data.get('Birth Location'),
           'deathDate': raw_data.get('Death Date'),
           'deathLocation': None,  # Not in current HTML
           'deceased': raw_data.get('Deceased?'),
           'father': raw_data.get('Father'),
           'mother': raw_data.get('Mother'),
           'spouses': collect_spouses(raw_data),
           'children': extract_children(raw_data.get('soup')),
           'occupation': raw_data.get('Occupation'),
           'address': raw_data.get('Address'),
           'email': raw_data.get('EMail'),
           'phone': collect_phones(raw_data),
           'website': raw_data.get('WebSite'),
           'source': raw_data.get('Source'),
           'notes': raw_data.get('Notes'),
           'photos': extract_photos(raw_data.get('soup')),
           'photographedBy': extract_photographed_by(raw_data.get('soup')),
           'metadata': {
               'lastUpdated': extract_last_updated(raw_data.get('soup')),
               'originalHtmlPath': str(html_path),
               'extractionDate': datetime.utcnow().isoformat() + 'Z'
           }
       }

       return person

   # ... implement all helper functions
   ```

3. **Data Validation**:
   - Validate against JSON schema from `PLAN/data-schema.md`
   - Report any extraction warnings/errors
   - Log statistics (fields populated, missing data, etc.)

4. **Error Handling**:
   - Gracefully handle malformed HTML
   - Report files that fail extraction
   - Continue processing on errors (don't halt entire batch)

**Success Criteria**:
- Script extracts all fields defined in schema
- Handles edge cases (missing data, special characters)
- Produces valid JSON per schema
- No data loss compared to original HTML

### Task 3: Create Validation Script (Day 3)

**Objective**: Validate extracted JSON data.

**Script Location**: `PRPs/scripts/both/validate_json_data.py`

**Validation Checks**:

1. **Schema Compliance**:
   ```python
   import jsonschema

   def validate_schema(json_file, schema):
       with open(json_file) as f:
           data = json.load(f)
       jsonschema.validate(data, schema)
   ```

2. **Data Integrity**:
   - Required fields present: `id`, `name`, `lineage`
   - ID format matches pattern: `XF\d+`
   - URLs are valid paths
   - No circular references in family relationships

3. **Completeness Check**:
   - Compare field population rate with original HTML
   - Report any fields that are always empty (might indicate extraction bug)

4. **Relationship Validation**:
   - If person A lists person B as father, does B's JSON exist?
   - Do spouse relationships exist bidirectionally?

**Success Criteria**:
- All JSON files pass schema validation
- No data integrity errors
- Validation report generated

### Task 3.5: Create Comprehensive Extraction Validation Tool (Day 3-4)

**Objective**: Build automated tool to validate 100% of extracted data against original HTML.

**CRITICAL**: This tool ensures zero data loss. Spot checks are insufficient for 2,985+ pages.

**Script Location**: `PRPs/scripts/both/validate_extraction.py`

**Implementation**:

Follow the complete specification in `PLAN/validation-strategy.md` under "Tool 1: Extraction Validation (HTML → JSON)".

The tool must:

1. **Parse both HTML and JSON**:
   - Extract all data from original HTML (tables, links, text)
   - Extract all data from JSON
   - Compare comprehensively

2. **Detect any missing data**:
   - Table fields not in JSON
   - Links not preserved
   - Children count mismatches
   - Photos not extracted

3. **Validate field mappings**:
   - Name extraction correct
   - Lineage correct
   - Family relationships correct
   - All URLs preserved

4. **Generate detailed report**:
   ```json
   {
     "summary": {
       "files_validated": 123,
       "perfect_matches": 121,
       "minor_differences": 2,
       "data_loss_detected": 0
     },
     "results": [...]
   }
   ```

5. **Exit with error code** if data loss detected:
   ```bash
   python3 PRPs/scripts/both/validate_extraction.py \
       --html-dir docs/new/htm/L1 \
       --json-dir data/people/Hagborg-Hansson \
       --report data/extraction-validation-report.json \
       --fail-on-error
   ```

**Success Criteria**:
- Tool validates 100% of files (not just samples)
- Detects any missing data automatically
- Report is clear and actionable
- CI/CD integration ready

**IMPORTANT**: Do not proceed to Task 5 or Phase 2 until this validation passes with zero data loss.

### Task 4: Extract Hagborg-Hansson Lineage (Day 4)

**Objective**: Run extraction on target lineage.

**Actions**:

1. **Identify all Hagborg-Hansson person pages**:
   ```bash
   # Find all XF*.htm files in L1/ (Hagborg-Hansson is L1)
   find docs/new/htm/L1 -name 'XF*.htm' | wc -l
   ```

2. **Create output directory**:
   ```bash
   mkdir -p data/people/Hagborg-Hansson
   ```

3. **Run extraction**:
   ```bash
   python3 PRPs/scripts/both/extract_person_data.py \
       --lineage Hagborg-Hansson \
       --input-dir docs/new/htm/L1 \
       --output-dir data/people/Hagborg-Hansson \
       --verbose
   ```

4. **Monitor output**:
   - Watch for errors/warnings
   - Check sample JSON files manually
   - Verify data accuracy against original HTML

**Success Criteria**:
- All person pages in L1/ successfully extracted
- JSON files created in `data/people/Hagborg-Hansson/`
- No extraction errors

### Task 5: Validate Extracted Data - Comprehensive Automated Validation (Day 5)

**Objective**: Ensure 100% data accuracy with zero data loss.

**Actions**:

1. **Run schema validation** (basic check):
   ```bash
   python3 PRPs/scripts/both/validate_json_data.py \
       --input-dir data/people/Hagborg-Hansson \
       --report data/schema-validation-report.md
   ```

2. **Run comprehensive extraction validation** (CRITICAL):
   ```bash
   python3 PRPs/scripts/both/validate_extraction.py \
       --html-dir docs/new/htm/L1 \
       --json-dir data/people/Hagborg-Hansson \
       --report data/extraction-validation-report.json \
       --fail-on-error
   ```

   This validates:
   - ✅ All 123 files (100% coverage, not just samples)
   - ✅ Every data field from HTML exists in JSON
   - ✅ All links preserved correctly
   - ✅ Children count matches
   - ✅ Photos extracted correctly
   - ✅ Family relationships accurate

3. **Review validation report**:
   ```bash
   # Check summary
   cat data/extraction-validation-report.json | jq '.summary'

   # Should show:
   # {
   #   "files_validated": 123,
   #   "perfect_matches": 121,
   #   "minor_differences": 2,
   #   "data_loss_detected": 0    <-- MUST BE ZERO
   # }
   ```

4. **Manual spot-checks** (optional, for confidence):
   - Pick 5 random JSON files from validation report
   - Open HTML and JSON side-by-side
   - Verify automated validation is accurate

5. **Fix extraction issues** (if any):
   - If `data_loss_detected > 0`, review detailed report
   - Identify which files/fields have issues
   - Fix extraction script to handle edge case
   - Re-run extraction
   - Re-run comprehensive validation
   - Repeat until `data_loss_detected: 0`

**CRITICAL GATE**:
- **DO NOT proceed to Task 6 or Phase 2** if validation shows data loss
- Better to delay than lose genealogy data
- All extraction issues must be resolved before proceeding

**Success Criteria**:
- ✅ 100% of JSON files pass schema validation
- ✅ **Comprehensive validation shows ZERO data loss**
- ✅ Validation report confirms all data preserved
- ✅ Optional manual spot-checks confirm automated validation accuracy

### Task 6: Create Extraction Report (Day 5)

**Objective**: Document Phase 1 results.

**Report Location**: `data/extraction-report-phase1.md`

**Report Contents**:

```markdown
# Phase 1 Data Extraction Report

## Summary

- **Lineage**: Hagborg-Hansson
- **Files Processed**: 123
- **Files Successfully Extracted**: 123
- **Files Failed**: 0
- **Extraction Date**: 2025-10-01

## Statistics

### Field Population Rates

| Field | Populated | % |
|-------|-----------|---|
| name | 123 | 100% |
| birthDate | 45 | 36.6% |
| birthLocation | 89 | 72.4% |
| father | 98 | 79.7% |
| mother | 98 | 79.7% |
| spouses | 67 | 54.5% |
| ... | ... | ... |

### Data Quality

- ✓ All JSON files valid per schema
- ✓ No circular reference errors
- ✓ All URLs valid
- ✓ No data loss detected

## Issues Found

### Edge Cases Handled

1. Multiple spouses (up to 4) - ✓ Handled
2. Missing birth dates - ✓ Null values
3. Special characters in names - ✓ Preserved
4. Empty children tables - ✓ Empty arrays

### Extraction Warnings

- 12 files had "0" in date fields (converted to null)
- 5 files had phone numbers as "0" (converted to null)
- All handled gracefully

## Sample Files

Representative samples:
- `XF100.json` - Complete record with all fields
- `XF82.json` - Minimal record (missing many fields)
- `XF101.json` - Multiple spouses example

## Next Steps

Phase 1 complete. Ready for Phase 2: Template Development.
```

**Success Criteria**:
- Report documents all extraction results
- Statistics show data quality
- Ready to proceed to Phase 2

## Deliverables Checklist

At the end of Phase 1, you must have:

- [ ] `PRPs/scripts/both/extract_person_data.py` - Working extraction script
- [ ] `PRPs/scripts/both/validate_json_data.py` - Schema validation script
- [ ] **`PRPs/scripts/both/validate_extraction.py`** - **Comprehensive validation tool (CRITICAL)**
- [ ] `data/people/Hagborg-Hansson/*.json` - All extracted person records (123 files)
- [ ] `data/extraction-validation-report.json` - Comprehensive validation report showing ZERO data loss
- [ ] `data/extraction-report-phase1.md` - Summary extraction report
- [ ] `PLAN/html-patterns.md` - HTML pattern documentation (optional but recommended)
- [ ] All JSON files pass schema validation
- [ ] **Comprehensive validation shows ZERO data loss (100% of 123 files validated)**
- [ ] Git commit with message: "Phase 1: Extract Hagborg-Hansson lineage data to JSON - Zero data loss validated"

## Testing & Validation

### Unit Tests

Create `PRPs/scripts/both/test_extract_person_data.py`:

```python
import pytest
from extract_person_data import *

def test_extract_person_id():
    assert extract_person_id('docs/new/htm/L1/XF100.htm') == 'XF100'

def test_extract_id_from_url():
    url = '/auntruth/new/htm/L1/XF100.htm'
    assert extract_id_from_url(url) == 'XF100'

def test_normalize_value():
    assert normalize_value('0') is None
    assert normalize_value('') is None
    assert normalize_value('SWE') == 'SWE'

# ... more tests
```

Run tests:
```bash
python3 -m pytest PRPs/scripts/both/test_extract_person_data.py -v
```

### Integration Test

```bash
# Extract one person
python3 PRPs/scripts/both/extract_person_data.py \
    --input docs/new/htm/L1/XF100.htm \
    --output /tmp/test-XF100.json

# Validate
python3 PRPs/scripts/both/validate_json_data.py \
    --input /tmp/test-XF100.json

# Compare with original
diff <(python3 -c "import json; print(json.dumps(json.load(open('/tmp/test-XF100.json')), indent=2))") \
     expected-XF100.json
```

## Common Issues & Solutions

### Issue: HTML parsing fails

**Solution**: Install BeautifulSoup4 and lxml:
```bash
pip install beautifulsoup4 lxml
```

### Issue: Special characters corrupted

**Solution**: Ensure UTF-8 encoding:
```python
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()
```

### Issue: Circular references

**Solution**: Track visited nodes during extraction, don't follow infinite loops.

### Issue: Extraction too slow

**Solution**: Use multiprocessing:
```python
from multiprocessing import Pool

with Pool(processes=8) as pool:
    pool.map(extract_person, html_files)
```

## Phase 1 Exit Criteria

Phase 1 is complete when:

1. ✅ All Hagborg-Hansson person pages extracted to JSON (123 files)
2. ✅ All JSON files pass schema validation
3. ✅ **Comprehensive validation tool (`validate_extraction.py`) shows ZERO data loss**
4. ✅ **Validation report confirms 100% of 123 files validated with no missing data**
5. ✅ Optional manual spot-checks confirm automated validation accuracy
6. ✅ Extraction script is documented and tested
7. ✅ Changes committed to git

**CRITICAL**: Do not proceed to Phase 2 unless comprehensive validation passes with zero data loss. Spot checks alone are insufficient for 2,985+ pages.

## Questions for User Before Starting

Before executing this phase, confirm with user:

1. Should we start with Hagborg-Hansson lineage (L1) or different lineage?
2. Are there any specific fields that are high priority to extract correctly?
3. Should we preserve the original HTML structure (like keeping `[Lineage]` in names)?
4. Any known data quality issues in the HTML we should watch for?

## Next Phase

Once Phase 1 is complete, proceed to **Phase 2: Template Development & Page Generation** (PRPs/gen-phase-2-prp.md).
