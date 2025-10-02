# PRP: Phase 2C - Achieve 100% Validation Match Rate

## Current Status

After Phase 2B, we have:
- **326/404 perfect matches (80.7%)**
- **78 files with validation warnings**
- **119 total missing data instances**

**Goal**: Achieve **404/404 (100%) perfect validation matches**

## Root Cause Analysis

### The 78 Remaining Validation Failures Break Down Into:

1. **Non-Schema Fields** - 68 instances
   - Language(1/2/3): 42 instances
   - Cause of Death: 9 instances
   - Genetics: 7 instances
   - Waiting?: 6 instances
   - Other custom fields: 4 instances

2. **Website/Email Links Not Extracted** - 4 instances
   - Links in `<a>` tags not being extracted from WebSite/EMail fields
   - Known Phase 1 issue flagged but not fixed

3. **Children Without Links** - 10 instances (names in field column)
   - Actually FIXED in Phase 2B (children ARE in JSON)
   - Validator may be comparing text formatting differently

4. **Navigation Links** - 40 instances
   - "Home |" and "Hagborg-Hansson" header links
   - Expected difference (modern navigation vs legacy)

5. **Notes Field** - 3 instances
   - Very long text fields
   - Possible text comparison or encoding issue

6. **Marriage Date** - 1 instance
   - Known validator false positive (data IS in JSON)

## Phase 2C Strategy

To achieve 100% perfect matches, we must fix ALL categories.

### Part 1: Extend Schema for Non-Standard Fields

**Objective**: Add fields that exist in HTML but not in our schema

**New Schema Fields**:
```json
{
  "languages": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Languages spoken (Language(1), Language(2), etc.)"
  },
  "causeOfDeath": {
    "type": ["string", "null"],
    "description": "Medical cause of death"
  },
  "genetics": {
    "type": ["string", "null"],
    "description": "DNA/Genetic testing information"
  },
  "waitingStatus": {
    "type": ["boolean", "string", "null"],
    "description": "Genealogy software waiting status"
  }
}
```

**Actions**:
1. Update `PLAN/data-schema.md` with new fields
2. Enhance `extract_person_data.py`:
   ```python
   def extract_languages(self, table) -> List[str]:
       """Extract Language(1), Language(2), Language(3) fields."""
       languages = []
       for i in range(1, 4):
           lang = self.extract_table_row_value(table, f'Language({i})')
           if lang:
               languages.append(lang)
       return languages

   # Add to parse_person_html():
   person['languages'] = self.extract_languages(person_table)
   person['causeOfDeath'] = self.extract_table_row_value(person_table, 'Cause of Death')
   person['genetics'] = self.extract_table_row_value(person_table, 'Genetics')
   person['waitingStatus'] = self.extract_table_row_value(person_table, 'Waiting?')
   ```

3. Update templates to render new fields
4. Re-extract all 404 files
5. Re-generate all 404 files

**Expected Impact**: Fixes 68/119 issues (57%)

---

### Part 2: Fix Website/Email Link Extraction

**Objective**: Extract href from `<a>` tags in WebSite and EMail fields

**Root Cause**: Current code does `get_text()` which returns link text, not href

**Current Code** (lines 90-104):
```python
def extract_table_row_value(self, table, label: str) -> Optional[str]:
    """Extract plain text value from table row by label."""
    # ...
    text = value_cell.get_text().strip()  # ❌ Gets link text, not URL
    return self.normalize_value(text)
```

**Fix Required**:
```python
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

                # Special handling for WebSite and EMail fields with links
                if label in ['WebSite', 'EMail']:
                    link = value_cell.find('a')
                    if link and link.get('href'):
                        href = link.get('href', '')
                        # For email, strip "mailto:" prefix
                        if label == 'EMail' and href.startswith('mailto:'):
                            return self.normalize_value(href[7:])
                        return self.normalize_value(href)

                # Default: get text content
                text = value_cell.get_text().strip()
                return self.normalize_value(text)
    return None
```

**Actions**:
1. Update `extract_table_row_value()` method
2. Re-extract affected files (XF189, XF191, XF193, XF640, and any others)
3. Validate extraction

**Expected Impact**: Fixes 4/119 issues (3%)

---

### Part 3: Fix Children Extraction Edge Cases

**Objective**: Ensure ALL children table rows are extracted correctly

**Current Issue**: Some children without links may have text formatting differences

**Investigation Needed**:
1. Check XF589, XF590 (Wendy Grant, June Grant)
2. Check XF736 (David/Bruce/Brian Rothwell)
3. Verify children ARE in JSON with correct names/dates

**Possible Issues**:
- Extra whitespace in names
- Birth date formatting differences
- Children table may have different HTML structure

**Actions**:
1. Manually inspect these 5 HTML files
2. Check corresponding JSON files
3. Verify children extraction logic handles all variations
4. Fix any edge cases found

**Expected Impact**: Fixes 10/119 issues (8%) IF there's an actual extraction issue

---

### Part 4: Fix Notes Field Long Text Handling

**Objective**: Ensure very long Notes fields are extracted completely

**Files Affected**: XF197, XF2705, (1 more)

**Investigation**:
```python
# Check current extraction
def extract_table_row_value(self, table, label: str):
    # Does this handle multi-line text correctly?
    # Does it preserve HTML entities?
    # Is there a length limit?
```

**Actions**:
1. Read XF197.htm and XF2705.htm Notes fields
2. Compare to JSON notes values
3. Check for:
   - Text truncation
   - HTML entity decoding issues
   - Newline/formatting preservation
4. Fix if needed

**Expected Impact**: Fixes 3/119 issues (2.5%)

---

### Part 5: Fix Navigation Links Issue

**Objective**: Stop validator from flagging expected navigation differences

**Current Issue**: Validator detects "Home |" and "Hagborg-Hansson" links missing

**Root Cause**: These are header/footer links, not data content
- Original HTML: Has legacy navigation
- Generated HTML: Has modern Phase 4 navigation
- This is a DESIGN IMPROVEMENT, not data loss

**Solution Option A: Update Validator to Skip Navigation Links**
```python
def extract_all_links(soup, original=True):
    """Extract links, optionally skipping navigation links."""
    links = []
    for link in soup.find_all('a'):
        text = link.get_text().strip()

        # Skip navigation links (these change with modern design)
        if text in ['Home |', 'Home', 'Hagborg-Hansson', 'AuntieRuth.com']:
            continue

        # ... rest of extraction
```

**Solution Option B: Add Navigation Links to Generated Pages**
Could add these to templates, but they're redundant with modern nav.

**Recommendation**: Option A (update validator)

**Expected Impact**: Fixes 40/119 issues (34%)

---

### Part 6: Fix Marriage Date Validator False Positive

**Objective**: Fix validator checking wrong location for marriage dates

**Current Issue**: XF2560 has marriage date in spouse object, validator checks table_data

**Fix**: Update `validate_generation.py`
```python
# Don't flag marriage dates as missing - they're in spouse objects
if 'Marriage Date' in field_name:
    # Check if this marriage date exists in any spouse object
    spouse_num = extract_number_from_field(field_name)  # e.g., "Marriage Date(1)" -> 1
    if spouse_num and len(json_data.get('spouses', [])) >= spouse_num:
        spouse = json_data['spouses'][spouse_num - 1]
        if spouse.get('marriageDate') == expected_value:
            continue  # Not actually missing
```

**Expected Impact**: Fixes 1/119 issues (0.8%)

---

## Phase 2C Task Breakdown

### Task 1: Schema Extension (Day 1 - Morning)

**Deliverable**: Extended schema with 4 new fields

1. Update `PLAN/data-schema.md`
2. Document new fields with examples
3. Update validation schema

**Success Criteria**:
- Schema includes: languages[], causeOfDeath, genetics, waitingStatus
- Documentation complete

---

### Task 2: Enhanced Extraction Script (Day 1 - Afternoon)

**Deliverable**: `extract_person_data.py` with all fixes

**Changes Required**:
1. Add `extract_languages()` method
2. Fix `extract_table_row_value()` for WebSite/EMail links
3. Add extraction for causeOfDeath, genetics, waitingStatus
4. Verify Notes field handles long text
5. Review children extraction edge cases

**Success Criteria**:
- All new fields extracted correctly
- Website/Email links extracted from `<a>` tags
- Long text preserved in Notes
- Children edge cases handled

---

### Task 3: Template Updates (Day 1 - Evening)

**Deliverable**: Templates render new fields

**Templates to Update**:
1. `templates/components/biographical-section.html`:
   - Add Cause of Death display
   - Add Genetics display
   - Add Languages display

**Success Criteria**:
- New fields display when present
- Graceful handling when fields are null
- Consistent with Phase 4 design

---

### Task 4: Re-Extract All Files (Day 2 - Morning)

**Deliverable**: 404 updated JSON files

**Command**:
```bash
python3 PRPs/scripts/both/extract_person_data.py \
    --lineage Hagborg-Hansson \
    --input-dir docs/new/htm/L1 \
    --output-dir data/people/Hagborg-Hansson \
    --verbose
```

**Validation**:
```bash
# Spot-check new fields
python3 -c "
import json
with open('data/people/Hagborg-Hansson/XF191.json') as f:
    data = json.load(f)
print(f'Languages: {data.get(\"languages\")}')
print(f'Website: {data.get(\"website\")}')
print(f'Cause of Death: {data.get(\"causeOfDeath\")}')
"
```

**Success Criteria**:
- 404/404 files extracted successfully
- New fields populated where present
- Website links extracted correctly

---

### Task 5: Re-Generate All Pages (Day 2 - Late Morning)

**Deliverable**: 404 updated HTML files

**Command**:
```bash
python3 PRPs/scripts/both/generate_pages.py \
    --lineage Hagborg-Hansson \
    --input-dir data/people/Hagborg-Hansson \
    --output-dir docs/new/htm/L1-generated-test \
    --verbose
```

**Success Criteria**:
- 404/404 pages generated
- New fields render in HTML
- No generation errors

---

### Task 6: Fix Validator Navigation Links (Day 2 - Noon)

**Deliverable**: Updated `validate_generation.py`

**Changes**:
1. Skip navigation links in comparison
2. Fix marriage date false positive check
3. Improve reporting for expected differences

**Success Criteria**:
- Validator doesn't flag navigation links
- Validator doesn't flag marriage dates in spouse objects
- Clear distinction between data loss vs design changes

---

### Task 7: Final Validation (Day 2 - Afternoon)

**Deliverable**: 100% validation pass

**Command**:
```bash
python3 PRPs/scripts/both/validate_generation.py \
    --original-dir docs/new/htm/L1 \
    --generated-dir docs/new/htm/L1-generated-test \
    --json-dir data/people/Hagborg-Hansson \
    --report data/phase2c-validation-report.json
```

**Expected Result**:
```
Files Validated: 404
✅ Content Matches: 404
❌ Missing Data: 0
🎨 Design Improvements: 404

✅✅✅ 100% VALIDATION PASSED ✅✅✅
```

**Success Criteria**:
- **404/404 perfect content matches (100%)**
- **0 missing data issues**
- All files pass validation

---

### Task 8: Phase 2C Report (Day 2 - Late Afternoon)

**Deliverable**: `data/phase2c-100-percent-report.md`

**Contents**:
1. Summary of all fixes
2. Before/after comparison (326 → 404)
3. Schema extensions documented
4. Extraction improvements listed
5. Validator improvements listed
6. 100% achievement confirmation

---

## Testing Strategy

### Unit Tests for New Extraction Features

**Test Website/Email Link Extraction**:
```python
def test_extract_website_link():
    html = '''
    <tr>
        <td>WebSite</td>
        <td><a href="http://www.example.com">www.example.com</a></td>
    </tr>
    '''
    value = extractor.extract_table_row_value(soup, 'WebSite')
    assert value == 'http://www.example.com'

def test_extract_email_link():
    html = '''
    <tr>
        <td>EMail</td>
        <td><a href="mailto:test@example.com">test@example.com</a></td>
    </tr>
    '''
    value = extractor.extract_table_row_value(soup, 'EMail')
    assert value == 'test@example.com'  # mailto: stripped
```

**Test Languages Extraction**:
```python
def test_extract_multiple_languages():
    # HTML with Language(1), Language(2), Language(3)
    languages = extractor.extract_languages(soup)
    assert languages == ['English', 'French', 'Italian']
```

**Test Long Notes Field**:
```python
def test_extract_long_notes():
    # HTML with 5000+ character Notes field
    notes = extractor.extract_table_row_value(soup, 'Notes')
    assert len(notes) > 5000
    assert 'specific text from middle' in notes
```

---

## Deliverables Checklist

At the end of Phase 2C, we must have:

- [ ] **Extended Schema**
  - [ ] `PLAN/data-schema.md` updated with 4 new fields
  - [ ] All fields documented with examples

- [ ] **Enhanced Extraction Script**
  - [ ] Languages extraction implemented
  - [ ] Website/Email link extraction fixed
  - [ ] Cause of Death, Genetics, Waiting extraction added
  - [ ] Long Notes text verified working
  - [ ] All edge cases handled

- [ ] **Updated Templates**
  - [ ] Biographical section renders new fields
  - [ ] Graceful null handling
  - [ ] Phase 4 design consistency

- [ ] **Re-Extracted Data**
  - [ ] 404/404 JSON files updated
  - [ ] All new fields populated correctly
  - [ ] Website links now in JSON

- [ ] **Re-Generated Pages**
  - [ ] 404/404 HTML files updated
  - [ ] New fields render correctly

- [ ] **Improved Validator**
  - [ ] Navigation links no longer flagged
  - [ ] Marriage date false positive fixed
  - [ ] Clear reporting of expected vs unexpected differences

- [ ] **100% Validation**
  - [ ] **404/404 perfect matches achieved**
  - [ ] **0 missing data issues**
  - [ ] Validation report confirms 100%

- [ ] **Reports & Documentation**
  - [ ] `data/phase2c-validation-report.json` shows 100%
  - [ ] `data/phase2c-100-percent-report.md` complete
  - [ ] Git commit: "Phase 2C: Achieve 100% Validation - Complete Data Extraction"

---

## Risk Assessment

### Low Risk Items ✅
1. Schema extension (additive, no breaking changes)
2. Website/Email link extraction (simple code fix)
3. Template updates (cosmetic additions)

### Medium Risk Items ⚠️
1. Validator changes (could mask real issues if too aggressive)
2. Languages extraction (need to handle Language(1), (2), (3) correctly)

### Mitigation Strategies
1. Test validator changes on sample files first
2. Manually verify that navigation link filtering doesn't hide real data loss
3. Unit test all new extraction methods
4. Spot-check random sample of 20 files after re-extraction

---

## Success Criteria

Phase 2C is complete when:

1. ✅ Schema extended with 4 new fields
2. ✅ Extraction script extracts all HTML fields
3. ✅ Website/Email links extracted from `<a>` tags
4. ✅ Templates render all new fields
5. ✅ 404 JSON files re-extracted with new data
6. ✅ 404 HTML files re-generated successfully
7. ✅ Validator updated to skip navigation links
8. ✅ **Validation shows 404/404 perfect matches (100%)**
9. ✅ **Zero missing data detected**
10. ✅ Phase 2C report documents 100% achievement
11. ✅ Changes committed to git

**CRITICAL**: Do not proceed to production deployment or Phase 3 until 100% validation is achieved.

---

## Timeline Estimate

- **Day 1**: Schema + Extraction + Templates (6-8 hours)
- **Day 2**: Re-extract + Re-generate + Validate + Report (4-6 hours)
- **Total**: 1.5-2 days

---

## Next Phase

Once Phase 2C achieves 100% validation:

**Phase 3: Scale to All Lineages**
- Apply enhanced extraction to L2-L9 lineages
- Generate ~2,500 additional pages
- Full site template conversion with 100% data fidelity
