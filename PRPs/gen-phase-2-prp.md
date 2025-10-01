# PRP: Page Generation Phase 2 - Template Development & Page Generation

## Prerequisites - READ THESE FILES FIRST

**CRITICAL**: Before starting this phase, read the following files to understand the complete context:

1. `Read(PLAN/page-generation-overview.md)` - Overall architecture and strategy
2. `Read(PLAN/data-schema.md)` - JSON schema you'll be rendering
3. `Read(PLAN/template-structure.md)` - Template architecture you must follow
4. `Read(PLAN/validation-strategy.md)` - Comprehensive validation strategy (CRITICAL for data integrity)
5. `Read(CLAUDE.md)` - Project conventions (including CSS best practices)
6. `Read(docs/new/css/modern-design-system.css)` - Phase 4 design tokens to use
7. `Read(docs/new/css/modern-overrides.css)` - Modern styling patterns
8. `Read(PRPs/gen-phase-1-prp.md)` - Understand Phase 1 outputs you'll be working with

## Phase 2 Overview

**Objective**: Build modern Jinja2 templates and generate HTML pages for Hagborg-Hansson lineage.

**Scope**: Hagborg-Hansson lineage only (~100 people from Phase 1)

**Duration**: 2 weeks

**Output**:
- Complete template system in `templates/`
- Page generation script: `PRPs/scripts/both/generate_pages.py`
- **Generation validation script: `PRPs/scripts/both/validate_generation.py`** (CRITICAL)
- Generated HTML pages in `docs/new/htm/L1-generated-test/` (test output)
- **Generation validation report: `generation-validation-report.json`** showing ZERO data loss
- Visual comparison report: `PLAN/phase2-comparison-report.md`

## Phase 2 Tasks

### Task 1: Set Up Template Infrastructure (Day 1)

**Objective**: Create template directory structure and base template.

**Actions**:

1. **Create directory structure**:
   ```bash
   mkdir -p templates/{components,macros}
   ```

2. **Install dependencies**:
   ```bash
   pip install jinja2 pyyaml
   ```

3. **Create base template** (`templates/base.html`):

Per `PLAN/template-structure.md`, create the foundational template that all pages extend. This template must:

- Include Phase 4 design system CSS (modern-design-system.css, modern-overrides.css)
- Include Phase 3 integration (phase3-components.css, phase3-integration.js)
- Include Phase 2 navigation (navigation.css, navigation.js, search.js)
- Provide `{% block content %}` for page-specific content
- Include consistent header/footer
- Support `data-phase3-enabled` attribute

**Reference**: See `PLAN/template-structure.md` for complete base template code.

**Success Criteria**:
- Base template exists and is syntactically valid
- All CSS/JS references use correct paths
- Template can be extended by child templates

### Task 2: Create Reusable Macros (Days 2-3)

**Objective**: Build macros for common UI patterns.

**Macros to Create**:

#### 1. Person Link Macro (`templates/macros/person-link.html`)

```html
{% macro person_link(person_obj) %}
    {% if person_obj and person_obj.url %}
        <a href="{{ person_obj.url }}" class="person-link">
            <strong>{{ person_obj.name }}</strong>
        </a>
    {% elif person_obj and person_obj.name %}
        <strong>{{ person_obj.name }}</strong>
    {% else %}
        <em class="text-tertiary">Unknown</em>
    {% endif %}
{% endmacro %}
```

#### 2. Section Card Macro (`templates/macros/section-card.html`)

```html
{% macro section_card(title, icon, open=false) %}
<section class="disclosure-section {% if open %}open{% endif %}">
    <button class="disclosure-section-toggle"
            aria-expanded="{{ 'true' if open else 'false' }}"
            aria-label="Toggle {{ title }}">
        <span class="disclosure-icon">{{ icon }}</span>
        <span class="disclosure-title">{{ title }}</span>
        <span class="disclosure-toggle">{{ '▼' if open else '▶' }}</span>
    </button>
    <div class="disclosure-content" style="display: {{ 'block' if open else 'none' }}">
        {{ caller() }}
    </div>
</section>
{% endmacro %}
```

#### 3. Date Display Macro (`templates/macros/date-display.html`)

```html
{% macro date_display(date_str) %}
    {% if date_str and date_str != '0' and date_str != 'Unknown' %}
        {{ date_str }}
    {% else %}
        <em class="text-tertiary">Unknown</em>
    {% endif %}
{% endmacro %}
```

**Success Criteria**:
- All macros are syntactically valid Jinja2
- Macros handle null/missing data gracefully
- Macros use Phase 4 design system CSS classes

### Task 3: Create Component Templates (Days 3-5)

**Objective**: Build reusable components for person page sections.

**Components to Create**:

#### 1. Person Header (`templates/components/person-header.html`)

Displays person name, lineage badge, and vital dates.

**Requirements**:
- Use `.person-header` and `.card` classes
- Display lineage as badge using `.lineage-badge`
- Show birth/death dates if available
- Follow Phase 4 design system

#### 2. Essential Info Section (`templates/components/essential-info.html`)

Displays birth/death information.

**Fields to show** (if not null):
- Birth Date
- Birth Location
- Death Date
- Death Location
- Deceased status

**Layout**: Use data list `<dl>`, `<dt>`, `<dd>` elements

#### 3. Family Section (`templates/components/family-section.html`)

Displays family relationships.

**Sections**:
- Parents (father, mother) - Use `person_link` macro
- Spouses (list all) - Show marriage dates if available
- Children link to children table (handled in main template)

**Reference**: See `PLAN/template-structure.md` for complete component code.

#### 4. Biographical Section (`templates/components/biographical-section.html`)

**Fields to show** (if not null):
- Occupation
- Address
- Email
- Phone
- Website
- Notes

#### 5. Research Section (`templates/components/research-section.html`)

**Fields to show**:
- Source attribution

#### 6. Photos Section (`templates/components/photos-section.html`)

Display photo table if `person.photos` array is not empty.

**Success Criteria**:
- All components handle missing data gracefully
- Components use semantic HTML5
- Components integrate with Phase 4 design system
- No hardcoded data (all from JSON)

### Task 4: Create Main Person Template (Day 5-6)

**Objective**: Build the primary person page template.

**Template**: `templates/person.html`

This template:
- Extends `base.html`
- Uses all components created above
- Conditionally renders sections based on data availability
- Includes children table
- Includes photo sections

**Key Requirements**:

1. **Title block**: `{{ person.name }} | AuntieRuth.com`
2. **Conditional sections**: Only show sections if data exists
3. **Disclosure sections**: Use `section_card` macro for INFO, FAMILY, BIO, RESEARCH
4. **Children table**: Separate `<section>` with data table
5. **Photos**: Two separate sections (photos of person, photos by person)

**Reference**: See `PLAN/template-structure.md` for complete template code.

**Success Criteria**:
- Template extends base correctly
- All components imported and used
- Conditional rendering works
- Generated HTML is semantic and valid

### Task 5: Create Page Generation Script (Days 6-8)

**Objective**: Build script to generate HTML from JSON + templates.

**Script**: `PRPs/scripts/both/generate_pages.py`

**Script Requirements**:

```python
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
        --output-dir docs/new/htm/L1

    # Dry run (validate without writing)
    python3 generate_pages.py \
        --lineage Hagborg-Hansson \
        --dry-run
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import sys

def setup_jinja_env():
    """Configure Jinja2 environment."""
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env

def generate_person_page(person_json_path, output_html_path, env):
    """Generate a single person page."""
    # Load person data
    with open(person_json_path, 'r', encoding='utf-8') as f:
        person = json.load(f)

    # Load template
    template = env.get_template('person.html')

    # Render HTML
    html = template.render(person=person)

    # Write output
    output_path = Path(output_html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated: {output_path}")

def generate_lineage(lineage_name, input_dir, output_dir, dry_run=False):
    """Generate all pages for a lineage."""
    env = setup_jinja_env()
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    json_files = sorted(input_path.glob('*.json'))

    print(f"Generating {len(json_files)} pages for {lineage_name}...")

    for json_file in json_files:
        person_id = json_file.stem  # e.g., XF100
        output_file = output_path / f"{person_id}.htm"

        if dry_run:
            print(f"Would generate: {output_file}")
        else:
            generate_person_page(json_file, output_file, env)

    print(f"✓ Generation complete: {len(json_files)} pages")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML pages from JSON data')
    parser.add_argument('--lineage', help='Lineage name')
    parser.add_argument('--input-dir', help='Input directory with JSON files')
    parser.add_argument('--output-dir', help='Output directory for HTML files')
    parser.add_argument('--dry-run', action='store_true', help='Validate without writing')

    args = parser.parse_args()

    if args.lineage:
        generate_lineage(args.lineage, args.input_dir, args.output_dir, args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)
```

**Success Criteria**:
- Script generates valid HTML from JSON
- All person pages can be generated
- Dry-run mode works for testing
- Error handling for missing/invalid JSON

### Task 6: Generate Test Pages (Day 8-9)

**Objective**: Generate Hagborg-Hansson lineage pages.

**Actions**:

1. **Create test output directory**:
   ```bash
   mkdir -p docs/new/htm/L1-generated-test
   ```

2. **Generate all pages**:
   ```bash
   python3 PRPs/scripts/both/generate_pages.py \
       --lineage Hagborg-Hansson \
       --input-dir data/people/Hagborg-Hansson \
       --output-dir docs/new/htm/L1-generated-test \
       --verbose
   ```

3. **Spot-check generated pages**:
   - Open `docs/new/htm/L1-generated-test/XF100.htm` in browser
   - Verify styling looks modern (white background, no emojis, modern cards)
   - Check Phase 3 integration loads (disclosure sections work)
   - Test Phase 2 navigation (search, breadcrumbs)

**Success Criteria**:
- All pages generate without errors
- Generated pages display correctly in browser
- Modern design system applied
- No broken links within generated pages

### Task 7: Visual Comparison & Iteration (Days 9-12)

**Objective**: Compare generated pages with originals, iterate to perfection.

**Comparison Process**:

1. **Side-by-side comparison**:
   ```bash
   # Open original
   open http://localhost:8000/auntruth/new/htm/L1/XF100.htm

   # Open generated
   open http://localhost:8000/auntruth/new/htm/L1-generated-test/XF100.htm
   ```

2. **Compare visually**:
   - ✅ Modern design (white background, cards, proper typography)
   - ✅ All data present (no missing fields)
   - ✅ Family links work
   - ✅ Disclosure sections expand/collapse
   - ✅ Navigation loads correctly
   - ✅ Search works
   - ✅ Mobile responsive

3. **Identify differences**:
   - Are any data fields missing?
   - Is styling different (better is okay, worse is not)?
   - Are there any JavaScript errors in console?

4. **Iterate on templates**:
   - Fix any issues found
   - Regenerate pages
   - Re-compare
   - Repeat until perfect

**Create comparison report**: `PLAN/phase2-comparison-report.md`

```markdown
# Phase 2: Generated Pages Comparison Report

## Test Page: XF100.htm (Johanna Hakanson)

### Visual Quality

- ✅ White background (vs old pale green)
- ✅ Modern card-based layout
- ✅ Professional text labels (INFO, FAMILY, BIO, RESEARCH) - no emojis
- ✅ Phase 4 design system fully applied
- ✅ Proper spacing and typography

### Data Accuracy

- ✅ All person data present
- ✅ Family relationships correct
- ✅ Children table matches original
- ✅ No data loss

### Functionality

- ✅ Disclosure sections expand/collapse
- ✅ Phase 3 integration loads
- ✅ Navigation appears
- ✅ Search works
- ✅ All internal links valid

### Improvements Over Original

1. Modern, professional appearance
2. Better information hierarchy
3. Responsive design (works on mobile)
4. Cleaner markup (semantic HTML5)
5. No deprecated HTML tags

### Issues Found

None - ready for production.

## Sample Pages Tested

- XF100.htm - Complete record
- XF82.htm - Minimal fields
- XF101.htm - Multiple spouses

All pass visual comparison.
```

**Success Criteria**:
- Generated pages match or exceed original quality
- All data correctly rendered
- Modern design applied consistently
- User approval of visual quality

### Task 8: Create Comprehensive Generation Validation Tool (Days 12-13)

**Objective**: Build automated tool to validate 100% of generated pages against original HTML.

**CRITICAL**: This tool ensures zero data loss during generation. Visual spot-checks are insufficient for 2,985+ pages.

**Script**: `PRPs/scripts/both/validate_generation.py`

**Implementation**:

Follow the complete specification in `PLAN/validation-strategy.md` under "Tool 2: Generation Validation (JSON → HTML)".

The tool must:

1. **Parse original HTML, generated HTML, and JSON**:
   - Extract all data from original HTML
   - Extract all data from generated HTML
   - Compare comprehensively

2. **Detect any missing content**:
   - Data fields in original not in generated
   - Links not preserved
   - Name/lineage mismatches
   - Family relationships missing

3. **Document improvements**:
   - Phase 4 design system applied
   - Modern disclosure sections
   - Semantic HTML5 structure
   - Modern color scheme

4. **Generate detailed report**:
   ```json
   {
     "summary": {
       "files_validated": 123,
       "content_matches": 123,
       "missing_data": 0,
       "design_improvements": 123
     },
     "results": [...]
   }
   ```

5. **Exit with error code** if data missing:
   ```bash
   python3 PRPs/scripts/both/validate_generation.py \
       --original-dir docs/new/htm/L1 \
       --generated-dir docs/new/htm/L1-generated-test \
       --json-dir data/people/Hagborg-Hansson \
       --report generation-validation-report.json \
       --fail-on-error
   ```

**Success Criteria**:
- Tool validates 100% of files (all 123 files)
- Detects any missing content automatically
- Report confirms zero data loss
- Documents design improvements
- CI/CD integration ready

**IMPORTANT**: Do not proceed to Task 9 (deployment) until this validation passes with zero data loss.

### Task 9: Production Deployment (Day 14)

**Objective**: Replace original pages with generated pages.

**IMPORTANT**: Only do this after user approval AND comprehensive validation passes!

**Deployment Process**:

1. **Run comprehensive validation** (CRITICAL - do this first):
   ```bash
   python3 PRPs/scripts/both/validate_generation.py \
       --original-dir docs/new/htm/L1 \
       --generated-dir docs/new/htm/L1-generated-test \
       --json-dir data/people/Hagborg-Hansson \
       --report generation-validation-report.json \
       --fail-on-error

   # Verify zero data loss
   cat generation-validation-report.json | jq '.summary.missing_data'
   # MUST output: 0
   ```

   **STOP HERE if validation fails**. Do not deploy pages with missing data.

2. **Backup originals**:
   ```bash
   # Git already has backups, but create explicit backup
   mkdir -p backups/L1-originals-$(date +%Y%m%d)
   cp -r docs/new/htm/L1/*.htm backups/L1-originals-$(date +%Y%m%d)/
   ```

2. **Deploy generated pages**:
   ```bash
   # Copy generated pages to production location
   cp docs/new/htm/L1-generated-test/*.htm docs/new/htm/L1/
   ```

3. **Test live site**:
   ```bash
   # Visit in browser
   open http://localhost:8000/auntruth/new/htm/L1/XF100.htm
   ```

4. **Git commit**:
   ```bash
   git add docs/new/htm/L1/
   git add data/people/Hagborg-Hansson/
   git add templates/
   git add PRPs/scripts/both/generate_pages.py

   git commit -m "Phase 2: Replace Hagborg-Hansson pages with generated versions - Zero data loss validated

   - Created Jinja2 template system with Phase 4 design
   - Generated 123 person pages from JSON data
   - Modern card-based layout with professional styling
   - All Phase 2/3/4 features integrated
   - Comprehensive validation: 123/123 files pass, zero data loss
   - 100% data accuracy confirmed via automated validation"
   ```

**Success Criteria**:
- Generated pages deployed to production location
- Site works correctly
- Changes committed to git
- User approves final result

## Deliverables Checklist

At the end of Phase 2, you must have:

- [ ] `templates/base.html` - Base template
- [ ] `templates/person.html` - Person page template
- [ ] `templates/components/*.html` - All component templates
- [ ] `templates/macros/*.html` - All macro templates
- [ ] `PRPs/scripts/both/generate_pages.py` - Generation script
- [ ] `PRPs/scripts/both/validate_generation.py` - Generation validation script (CRITICAL)
- [ ] `docs/new/htm/L1/*.htm` - Generated pages (deployed)
- [ ] `PLAN/phase2-comparison-report.md` - Comparison report
- [ ] `generation-validation-report.json` - Validation report showing ZERO data loss (CRITICAL)
- [ ] All generated pages pass validation (100% of files, zero data loss)
- [ ] Visual quality approved by user
- [ ] Git commit with all changes

## Testing Checklist

Test each generated page for:

- [ ] Page loads without errors
- [ ] Phase 4 design applied (white background, modern cards)
- [ ] Professional text labels (no emojis)
- [ ] All person data visible
- [ ] Family links work
- [ ] Disclosure sections expand/collapse
- [ ] Navigation appears and works
- [ ] Search functionality works
- [ ] Mobile responsive
- [ ] No console errors
- [ ] Valid HTML5

## Common Issues & Solutions

### Issue: Template syntax errors

**Solution**: Validate Jinja2 syntax:
```python
from jinja2 import Environment
env = Environment()
env.parse(open('templates/person.html').read())
```

### Issue: Missing data in generated pages

**Solution**: Add debug output in template:
```html
<!-- DEBUG: {{ person }} -->
```

### Issue: CSS not loading

**Solution**: Verify paths are correct:
```html
<!-- Should be absolute paths -->
<link rel="stylesheet" href="/auntruth/new/css/modern-design-system.css">
```

### Issue: Phase 3 integration not working

**Solution**: Ensure `data-phase3-enabled` attribute on `<body>`:
```html
<body data-phase3-enabled>
```

## Phase 2 Exit Criteria

Phase 2 is complete when:

1. ✅ All templates created and tested
2. ✅ Generation script works correctly
3. ✅ All Hagborg-Hansson pages generated
4. ✅ Generated pages match or exceed original quality
5. ✅ All validation tests pass
6. ✅ User approves visual quality
7. ✅ Pages deployed to production location
8. ✅ Changes committed to git

## Questions for User Before Deployment

Before deploying generated pages to production:

1. Please review generated test page: `http://localhost:8000/auntruth/new/htm/L1-generated-test/XF100.htm`
2. Are you satisfied with the visual design?
3. Is all data correctly displayed?
4. Are you ready to replace original pages with generated versions?

## Next Phase

Once Phase 2 is complete and user-approved, proceed to **Phase 3: CI/CD Pipeline & Full Rollout** (PRPs/gen-phase-3-prp.md).
