# PRP: Phase 2B - Improve Phase 1 Data Extraction

## Prerequisites - READ THESE FILES FIRST

**CRITICAL**: Before starting this phase, read the following files to understand the complete context:

1. `Read(data/phase2-generation-report.md)` - Phase 2 results and identified issues
2. `Read(data/extraction-report-phase1.md)` - Phase 1 extraction results
3. `Read(generation-validation-report.json)` - Detailed validation findings
4. `Read(PLAN/data-schema.md)` - JSON schema specification
5. `Read(PRPs/gen-phase-1-prp.md)` - Original Phase 1 implementation

## Phase 2B Overview

**Objective**: Fix Phase 1 extraction issues identified during Phase 2 validation to achieve 100% data completeness.

**Scope**: Hagborg-Hansson lineage (~80 files with missing data)

**Duration**: 1-2 days

**Output**:
- Enhanced extraction script: `PRPs/scripts/both/extract_person_data.py` (updated)
- Re-extracted JSON files: `data/people/Hagborg-Hansson/*.json` (80 files updated)
- Re-generated HTML files: `docs/new/htm/L1-generated-test/*.htm` (80 files updated)
- Updated validation report: `data/phase2b-validation-report.json`
- Summary report: `data/phase2b-extraction-fixes.md`

## Issues to Fix

From Phase 2 validation, 80 files have missing data traced to Phase 1 extraction:

### Issue 1: Missing Children (~20-30 files)

**Problem**: Some children in the children table are not being extracted.

**Example**: XF1231 (Bruce Reagan)
- HTML has: Jason Reagan (born 04/19/1988)
- JSON missing: This 4th child
- Root cause: Child extraction logic may have row limit or skip logic

**Fix Required**:
```python
# In extract_person_data.py, enhance extract_children() function
def extract_children(soup):
    """Extract ALL children from children table, no limits."""
    children = []

    # Find children section
    children_header = None
    for h2 in soup.find_all('h2'):
        if 'Children' in h2.get_text():
            children_header = h2
            break

    if not children_header:
        return children

    # Find next table after children header
    current = children_header.find_next_sibling()
    while current:
        if current.name == 'table':
            # Process ALL rows (not just first N)
            rows = current.find_all('tr')
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if len(cells) >= 2:
                    child = extract_child_from_row(cells)
                    if child:
                        children.append(child)
            break
        current = current.find_next_sibling()

    return children
```

### Issue 2: Missing Field Values (~30-40 files)

**Problem**: Certain field values like "Yes" (deceased), "Cancer" (cause of death) are being skipped.

**Examples**:
- XF165: Missing "Yes" in deceased field
- XF167: Missing "Cancer" in cause of death

**Root Cause**: Value normalization is too aggressive - treating valid short values as empty.

**Fix Required**:
```python
def normalize_value(value):
    """Convert empty/zero values to None, but preserve valid short values."""
    if not value:
        return None

    # Strip whitespace
    value = value.strip()

    # Only convert these specific empty indicators to None
    if value in ['0', '', 'Don\'t Know', 'Unknown']:
        return None

    # Preserve everything else, including "Yes", "No", single words
    return value
```

### Issue 3: Missing Navigation Links (~10 files)

**Problem**: Some "Home |" links and other navigation elements are missing.

**Example**: XF1272 missing "Home |" link in header

**Root Cause**: Link extraction is only from table cells, missing header/footer links.

**Fix Required**:
```python
# Already fixed in validate_generation.py - apply same fix to extraction
def extract_all_links(soup):
    """Extract ALL links from page, not just table cells."""
    links = []

    # Get all <a> tags
    for link in soup.find_all('a'):
        href = link.get('href')
        text = link.get_text().strip()

        if href and text:
            links.append({
                'text': text,
                'href': href,
                'context': get_link_context(link)  # header, table, footer
            })

    return links
```

## Phase 2B Tasks

### Task 1: Analyze Validation Failures (Day 1 - Morning)

**Objective**: Understand exactly which files and fields are affected.

**Actions**:

1. **Parse validation report**:
   ```bash
   cat generation-validation-report.json | python3 -c "
   import json, sys
   data = json.load(sys.stdin)
   fails = [r for r in data['results'] if r['status'] == 'FAIL']

   # Categorize issues
   missing_children = []
   missing_fields = []
   missing_links = []

   for fail in fails:
       for issue in fail['missing_data']:
           if issue['type'] == 'missing_link' and 'Child' in issue.get('text', ''):
               missing_children.append(fail['person_id'])
           elif issue['type'] == 'missing_field_value':
               missing_fields.append((fail['person_id'], issue['field'], issue['value']))
           elif issue['type'] == 'missing_link':
               missing_links.append((fail['person_id'], issue['text']))

   print(f'Missing children: {len(missing_children)} files')
   print(f'Missing fields: {len(missing_fields)} instances')
   print(f'Missing links: {len(missing_links)} instances')
   "
   ```

2. **Sample affected files**:
   ```bash
   # Spot check 3 files from each category
   # XF1231 - missing child
   # XF165 - missing field value
   # XF1272 - missing link

   # Compare HTML, JSON, and validation report for each
   ```

3. **Document root causes** in `data/phase2b-analysis.md`

**Success Criteria**:
- Clear understanding of each issue type
- Root cause identified for each category
- Sample files validated manually

### Task 2: Enhance Extraction Script (Day 1 - Afternoon)

**Objective**: Fix extraction bugs in `extract_person_data.py`.

**Actions**:

1. **Backup current script**:
   ```bash
   cp PRPs/scripts/both/extract_person_data.py PRPs/scripts/both/extract_person_data.py.phase1
   ```

2. **Fix child extraction**:
   - Remove any row limits or early termination
   - Process ALL <tr> elements in children table
   - Handle edge cases (children with no birth dates, etc.)

3. **Fix value normalization**:
   - Update `normalize_value()` to preserve short valid values
   - Only convert specific empty indicators: "0", "", "Don't Know", "Unknown"
   - Keep "Yes", "No", disease names, etc.

4. **Fix link extraction**:
   - Extract links from entire page, not just tables
   - Preserve header/footer navigation
   - Include lineage links, home links, etc.

5. **Add extraction logging**:
   ```python
   import logging

   logging.basicConfig(
       filename='data/extraction-phase2b.log',
       level=logging.DEBUG,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )

   # Log every extracted field
   logger.debug(f"Extracting {person_id}: found {len(children)} children")
   ```

**Success Criteria**:
- Script handles all identified edge cases
- Comprehensive logging for debugging
- Code follows same structure as Phase 1

### Task 3: Re-Extract Affected Files (Day 1 - Evening)

**Objective**: Re-run extraction on the 80 affected files.

**Actions**:

1. **Create affected files list**:
   ```bash
   # Extract person IDs from validation report
   cat generation-validation-report.json | python3 -c "
   import json, sys
   data = json.load(sys.stdin)
   fails = [r['person_id'] for r in data['results'] if r['status'] == 'FAIL']

   with open('data/affected-files-phase2b.txt', 'w') as f:
       for pid in fails:
           f.write(f'{pid}\n')
   "

   echo "Total files to re-extract: $(wc -l < data/affected-files-phase2b.txt)"
   ```

2. **Re-extract only affected files**:
   ```bash
   # Create targeted re-extraction script
   python3 PRPs/scripts/both/extract_person_data.py \
       --file-list data/affected-files-phase2b.txt \
       --input-dir docs/new/htm/L1 \
       --output-dir data/people/Hagborg-Hansson \
       --overwrite \
       --verbose
   ```

3. **Verify improvements**:
   ```bash
   # Compare old vs new JSON for sample files
   diff data/people/Hagborg-Hansson/XF1231.json.backup \
        data/people/Hagborg-Hansson/XF1231.json
   ```

**Success Criteria**:
- 80 JSON files re-extracted
- Extracted data includes previously missing fields
- No new data loss introduced

### Task 4: Re-Generate and Re-Validate (Day 2 - Morning)

**Objective**: Re-generate HTML and validate 100% data completeness.

**Actions**:

1. **Re-generate affected pages**:
   ```bash
   # Re-generate only the 80 affected pages
   python3 PRPs/scripts/both/generate_pages.py \
       --file-list data/affected-files-phase2b.txt \
       --input-dir data/people/Hagborg-Hansson \
       --output-dir docs/new/htm/L1-generated-test \
       --overwrite \
       --verbose
   ```

2. **Run comprehensive validation**:
   ```bash
   python3 PRPs/scripts/both/validate_generation.py \
       --original-dir docs/new/htm/L1 \
       --generated-dir docs/new/htm/L1-generated-test \
       --json-dir data/people/Hagborg-Hansson \
       --report data/phase2b-validation-report.json \
       --fail-on-error
   ```

3. **Compare validation results**:
   ```bash
   # Phase 2: 324 perfect matches, 80 missing data
   # Phase 2B target: 404 perfect matches, 0 missing data

   cat data/phase2b-validation-report.json | python3 -c "
   import json, sys
   data = json.load(sys.stdin)
   print(f\"Perfect matches: {data['summary']['content_matches']}/404\")
   print(f\"Missing data: {data['summary']['missing_data']}/404\")

   if data['summary']['missing_data'] == 0:
       print('✅ 100% DATA COMPLETENESS ACHIEVED!')
   else:
       print('⚠️  Still have missing data - review failures')
   "
   ```

**Success Criteria**:
- 404 perfect content matches (100%)
- 0 missing data issues
- Validation report confirms zero data loss

### Task 5: Create Phase 2B Report (Day 2 - Afternoon)

**Objective**: Document extraction improvements and final results.

**Report Location**: `data/phase2b-extraction-fixes.md`

**Report Contents**:

```markdown
# Phase 2B Extraction Fixes Report

## Summary

- **Files Re-Extracted**: 80 (19.8% of total)
- **Extraction Issues Fixed**: 3 categories
- **Final Validation Results**: 404/404 perfect matches (100%)
- **Data Completeness**: ✅ Zero data loss

## Issues Fixed

### 1. Missing Children (20-30 files)
- **Root Cause**: Row limit in child extraction logic
- **Fix**: Removed limits, process ALL table rows
- **Example**: XF1231 now includes Jason Reagan (4th child)
- **Files Fixed**: [list of 20-30 file IDs]

### 2. Missing Field Values (30-40 files)
- **Root Cause**: Over-aggressive value normalization
- **Fix**: Preserve short valid values ("Yes", "No", disease names)
- **Examples**:
  - XF165: Now includes "Yes" in deceased field
  - XF167: Now includes "Cancer" in cause of death
- **Files Fixed**: [list of 30-40 file IDs]

### 3. Missing Navigation Links (10 files)
- **Root Cause**: Link extraction limited to tables only
- **Fix**: Extract all <a> tags from entire page
- **Example**: XF1272 now includes "Home |" navigation
- **Files Fixed**: [list of 10 file IDs]

## Validation Comparison

| Metric | Phase 2 | Phase 2B | Improvement |
|--------|---------|----------|-------------|
| Perfect Matches | 324 (80.2%) | 404 (100%) | +80 files |
| Missing Data | 80 (19.8%) | 0 (0%) | -80 issues |
| Data Completeness | 80.2% | 100% | +19.8% |

## Next Steps

✅ **Phase 2B Complete** - 100% data extraction accuracy achieved

**Option A: Deploy to Production**
- All data validated and complete
- Ready for production deployment

**Option B: Extend to All Lineages (Phase 2C)**
- Apply enhanced extraction to L2-L9
- Generate remaining ~2,500 pages
```

**Success Criteria**:
- Report documents all fixes clearly
- Validation results demonstrate 100% completion
- Next steps clearly defined

## Deliverables Checklist

At the end of Phase 2B, you must have:

- [ ] **Enhanced Extraction Script**
  - [ ] `extract_person_data.py` - Fixed child extraction
  - [ ] `extract_person_data.py` - Fixed value normalization
  - [ ] `extract_person_data.py` - Fixed link extraction
  - [ ] Comprehensive logging added

- [ ] **Re-Extracted Data**
  - [ ] 80 JSON files updated in `data/people/Hagborg-Hansson/`
  - [ ] Previously missing children now included
  - [ ] Previously missing field values now included
  - [ ] Previously missing links now included

- [ ] **Re-Generated Pages**
  - [ ] 80 HTML files updated in `docs/new/htm/L1-generated-test/`
  - [ ] All missing data now rendered

- [ ] **Validation & Reports**
  - [ ] `phase2b-validation-report.json` - Shows 100% completion
  - [ ] `phase2b-extraction-fixes.md` - Summary report
  - [ ] `phase2b-analysis.md` - Root cause analysis
  - [ ] Git commit: "Phase 2B: Fix extraction issues - Achieve 100% data completeness"

## Testing & Validation

### Unit Tests for Fixes

Create `PRPs/scripts/both/test_extraction_fixes.py`:

```python
import pytest
from extract_person_data import normalize_value, extract_children

def test_normalize_value_preserves_short_values():
    """Short valid values should be preserved, not converted to None."""
    assert normalize_value('Yes') == 'Yes'
    assert normalize_value('No') == 'No'
    assert normalize_value('Cancer') == 'Cancer'

def test_normalize_value_converts_empty():
    """Empty indicators should be converted to None."""
    assert normalize_value('0') is None
    assert normalize_value('') is None
    assert normalize_value('Don\'t Know') is None
    assert normalize_value('Unknown') is None

def test_extract_children_gets_all_rows():
    """Should extract ALL children, no row limits."""
    # Test with HTML containing 5+ children
    html = """<h2>Children</h2>
    <table>
        <tr><td>Child 1</td><td>1980</td></tr>
        <tr><td>Child 2</td><td>1982</td></tr>
        <tr><td>Child 3</td><td>1984</td></tr>
        <tr><td>Child 4</td><td>1986</td></tr>
        <tr><td>Child 5</td><td>1988</td></tr>
    </table>"""

    children = extract_children(BeautifulSoup(html, 'html.parser'))
    assert len(children) == 5  # All children extracted
```

Run tests:
```bash
python3 -m pytest PRPs/scripts/both/test_extraction_fixes.py -v
```

### Integration Test

```bash
# Test complete workflow on sample affected files
SAMPLE_FILES="XF1231 XF165 XF1272"

for file_id in $SAMPLE_FILES; do
    echo "Testing $file_id..."

    # Re-extract
    python3 PRPs/scripts/both/extract_person_data.py \
        --input docs/new/htm/L1/${file_id}.htm \
        --output /tmp/${file_id}.json

    # Validate JSON has previously missing data
    python3 -c "
import json
with open('/tmp/${file_id}.json') as f:
    data = json.load(f)
    # Check for specific fixes
    print(f'Children count: {len(data.get(\"children\", []))}')
    print(f'Deceased value: {data.get(\"deceased\")}')
    "
done
```

## Common Issues & Solutions

### Issue: Re-extraction creates duplicates

**Solution**: Use `--overwrite` flag to replace existing JSON files:
```bash
python3 extract_person_data.py ... --overwrite
```

### Issue: Some children still missing

**Solution**: Check HTML structure - may need custom parsing for edge cases:
```python
# Add special handling for non-standard children tables
if not children and 'child' in page_text.lower():
    # Try alternative extraction methods
    children = extract_children_alternative(soup)
```

### Issue: Validation still shows failures

**Solution**: Debug specific failures:
```bash
# Get detailed failure info
cat phase2b-validation-report.json | jq '.results[] | select(.status == "FAIL")'

# Debug specific file
python3 PRPs/scripts/both/debug_link_extraction.py \
    --original docs/new/htm/L1/XF1231.htm \
    --generated docs/new/htm/L1-generated-test/XF1231.htm
```

## Phase 2B Exit Criteria

Phase 2B is complete when:

1. ✅ All extraction bugs identified and fixed
2. ✅ 80 affected JSON files re-extracted successfully
3. ✅ 80 affected HTML files re-generated successfully
4. ✅ **Validation shows 404/404 perfect matches (100%)**
5. ✅ **Zero missing data detected**
6. ✅ Comprehensive testing passed
7. ✅ Changes committed to git
8. ✅ Phase 2B report complete

**CRITICAL**: Do not proceed to Phase 2C or production deployment until 100% data completeness is achieved.

## Next Phase

Once Phase 2B is complete with 100% data completeness, proceed to:

**Phase 2C: Scale to All Lineages** (PRPs/gen-phase-2c.md)
- Apply enhanced extraction to L2-L9 lineages
- Generate ~2,500 additional pages
- Full site template conversion
