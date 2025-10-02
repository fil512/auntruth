# Page Generation System - Developer Guide

## Quick Start

Generate all pages locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Extract data (if needed - already done for all lineages)
python3 PRPs/scripts/both/extract_person_data.py --lineage Hagborg-Hansson --input-dir docs/new/htm/L1 --output-dir data/people/Hagborg-Hansson

# Generate pages for a single lineage
python3 PRPs/scripts/both/generate_pages.py --lineage Hagborg-Hansson --input-dir data/people/Hagborg-Hansson --output-dir docs/new/htm/L1

# Validate generated pages
python3 PRPs/scripts/both/validate_all_lineages.py
```

## System Architecture

The page generation system follows a three-layer architecture:

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Structured Data (JSON)                   │
│  - Person records extracted from existing HTML      │
│  - Version controlled, diffable                     │
│  - Single source of truth                           │
│  - Location: data/people/{lineage}/{person_id}.json│
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2: Modern Templates (Jinja2)                 │
│  - Semantic HTML5 with Phase 4 design system        │
│  - No legacy markup patterns                        │
│  - Reusable components and macros                   │
│  - Location: templates/                             │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 3: Generated Pages (HTML)                    │
│  - Pre-rendered at build time                       │
│  - No runtime DOM transformation needed             │
│  - Deployed to docs/new/htm/L{0-9}/                │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
auntruth/
├── data/
│   └── people/                          # Structured JSON data
│       ├── Hagborg-Hansson/            # 404 people
│       ├── Lentz/                      # 77 people
│       ├── Ward/                       # 123 people
│       ├── Stebbe/                     # 153 people
│       ├── Nelson/                     # 308 people
│       ├── Selch-Weiss/                # 384 people
│       ├── Phoenix-Rogerson/           # 388 people
│       ├── Pringle-Hambley/            # 409 people
│       ├── Lathrop-Lothropp/           # 686 people
│       └── Other/                      # 72 people
│                                       # Total: 3,004 JSON files
├── templates/
│   ├── base.html                       # Root template
│   ├── person.html                     # Main person page
│   ├── components/
│   │   ├── person-header.html          # Person name & lineage
│   │   ├── essential-info.html         # Birth/death data
│   │   ├── family-section.html         # Relationships
│   │   ├── biographical-section.html   # Occupation, notes
│   │   ├── research-section.html       # Sources
│   │   └── photos-section.html         # Photo galleries
│   └── macros/
│       ├── person-link.html            # Consistent links
│       ├── section-card.html           # Disclosure sections
│       └── date-display.html           # Date formatting
├── PRPs/scripts/both/
│   ├── extract_person_data.py          # HTML → JSON
│   ├── generate_pages.py               # JSON + templates → HTML
│   ├── validate_json_data.py           # Schema compliance
│   ├── validate_extraction.py          # HTML → JSON validation
│   ├── validate_generation.py          # JSON → HTML validation
│   └── validate_all_lineages.py        # Multi-lineage validation
└── docs/new/htm/
    ├── L0/ ... L9/                     # Generated HTML (3,004+ pages)
    └── L1-generated-test/              # Test output directory
```

## Lineage Mapping

| Directory | Lineage Name | Files | Status |
|-----------|--------------|-------|--------|
| L0/ | Other | 72 | ✅ |
| L1/ | Hagborg-Hansson | 404 | ✅ |
| L2/ | Nelson | 308 | ✅ |
| L3/ | Pringle-Hambley | 409 | ✅ |
| L4/ | Lathrop-Lothropp | 686 | ✅ |
| L5/ | Ward | 123 | ✅ |
| L6/ | Selch-Weiss | 384 | ✅ |
| L7/ | Stebbe | 153 | ✅ |
| L8/ | Lentz | 77 | ✅ |
| L9/ | Phoenix-Rogerson | 388 | ✅ |

## Adding a New Person

1. Create JSON file: `data/people/{lineage}/{person_id}.json`
2. Follow schema: `PLAN/data-schema.md`
3. Commit to git
4. CI automatically generates page

Example JSON:

```json
{
  "id": "XF999",
  "name": "John Doe",
  "lineage": "Hagborg-Hansson",
  "birthDate": "1950-01-01",
  "birthLocation": "Stockholm, Sweden",
  "father": {
    "id": "XF998",
    "name": "Parent Doe",
    "url": "/auntruth/new/htm/L1/XF998.htm"
  },
  "mother": null,
  "spouses": [],
  "children": [],
  "metadata": {
    "extractionDate": "2025-10-02T12:00:00Z",
    "originalHtmlPath": "docs/new/htm/L1/XF999.htm"
  }
}
```

## Modifying Templates

1. Edit template in `templates/`
2. Test locally: `python3 PRPs/scripts/both/generate_pages.py --lineage Hagborg-Hansson --input-dir data/people/Hagborg-Hansson --output-dir docs/new/htm/L1-test`
3. Validate changes
4. Commit to git
5. CI regenerates all pages automatically

## Data Schema

All person records follow the schema in `PLAN/data-schema.md`.

### Required Fields
- `id` - Person identifier (XF### format)
- `name` - Full name
- `lineage` - Lineage name

### Core Genealogy Fields
- Family: `father`, `mother`, `spouses[]`, `children[]`
- Vital: `birthDate`, `birthLocation`, `deathDate`, `deathLocation`, `deceased`
- Biography: `occupation`, `address`, `notes`
- Contact: `email`, `phone`, `website`

### Phase 2C Enhanced Fields
- `languages[]` - Languages spoken
- `causeOfDeath` - Medical cause of death
- `genetics` - DNA/genetic testing
- `waitingStatus` - Genealogy software status

### Photos & Media
- `photos[]` - Pictures of this person
- `photographedBy[]` - Pictures taken by this person

## Running the CI Pipeline

### Local Testing

Test the pipeline locally before pushing:

```bash
# Validate JSON
python3 PRPs/scripts/both/validate_all_lineages.py

# Generate all pages
for lineage_dir in data/people/*/; do
    lineage_name=$(basename "$lineage_dir")
    case "$lineage_name" in
        "Other") output_dir="L0" ;;
        "Hagborg-Hansson") output_dir="L1" ;;
        "Nelson") output_dir="L2" ;;
        "Pringle-Hambley") output_dir="L3" ;;
        "Lathrop-Lothropp") output_dir="L4" ;;
        "Ward") output_dir="L5" ;;
        "Selch-Weiss") output_dir="L6" ;;
        "Stebbe") output_dir="L7" ;;
        "Lentz") output_dir="L8" ;;
        "Phoenix-Rogerson") output_dir="L9" ;;
    esac
    python3 PRPs/scripts/both/generate_pages.py \
        --lineage "$lineage_name" \
        --input-dir "$lineage_dir" \
        --output-dir "docs/new/htm/$output_dir"
done

# Preview locally
python3 PRPs/server/server.py
# Visit: http://localhost:8000/auntruth/new/htm/L1/XF100.htm
```

### GitLab CI

Push to git to trigger CI:

```bash
git add .
git commit -m "Update person data or templates"
git push origin main

# Pipeline runs automatically:
# 1. validate-json → validate-templates
# 2. generate-all-lineages
# 3. test-html-validity, test-data-integrity
# 4. deploy-production (manual trigger required)
```

## Troubleshooting

### Pages Not Updating

- Check CI pipeline status in GitLab
- Verify JSON data is valid: `python3 PRPs/scripts/both/validate_json_data.py --input-dir data/people/{lineage}`
- Clear browser cache

### Template Errors

Validate Jinja2 syntax:

```python
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('person.html')
```

Check template inheritance and component imports.

### Generation Failures

Run generation with verbose logging:

```bash
python3 PRPs/scripts/both/generate_pages.py --lineage Hagborg-Hansson --input-dir data/people/Hagborg-Hansson --output-dir test-output --verbose
```

Check for:
- Missing required fields in JSON
- Invalid JSON syntax
- Template rendering errors
- File permission issues

### Performance Issues

- Full generation: ~5 minutes for 3,004 pages
- CI pipeline: ~10 minutes total
- If slower, check:
  - Network/disk I/O
  - Python version (use 3.11+)
  - Template caching enabled

## Best Practices

### Data Management

- **Always validate** JSON before committing
- **Never edit** generated HTML files directly
- **Use git** for all data changes (backups, history, rollback)
- **Test locally** before pushing to CI

### Template Development

- **Semantic HTML5** - Use proper tags (`<section>`, `<article>`, etc.)
- **Mobile-first** - Design for small screens, enhance for large
- **Graceful degradation** - Handle null/missing data elegantly
- **No inline styles** - Use CSS classes from Phase 4 design system

### CI/CD

- **Run validation** locally before pushing
- **Review CI logs** if pipeline fails
- **Test on sample** before full regeneration
- **Monitor artifacts** - Check generated output quality

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Total pipeline time | < 10 min | ~10 min |
| Page generation | < 5 min | ~3-4 min |
| Validation tests | < 3 min | ~2 min |
| Pages per second | > 10 | ~12-15 |

## Documentation

- **Architecture**: `PLAN/page-generation-overview.md`
- **Data Schema**: `PLAN/data-schema.md`
- **Templates**: `PLAN/template-structure.md`
- **CI Pipeline**: `PLAN/ci-pipeline-spec.md`
- **Lineage Mapping**: `PLAN/lineage-mapping.md`
- **Operations**: `docs/RUNBOOK.md`

## Support

For questions or issues:

1. Check this guide and related documentation
2. Review CI pipeline logs in GitLab
3. Test locally with verbose logging
4. Check git history for recent changes
5. Report issues with full error messages and context

---

**Last Updated**: Phase 3 Complete (October 2025)

**Status**: Production-ready, CI/CD automated, 3,004 pages across 10 lineages
