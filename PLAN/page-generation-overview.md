# Page Generation System - Overview

## Executive Summary

Transform the AuntieRuth.com genealogy site from runtime-transformed legacy HTML to modern, pre-generated pages built from structured data and templates. This eliminates CSS cascade wars, DOM manipulation overhead, and design inconsistencies.

## Current State Problems

1. **Legacy HTML Structure**: 2,985+ person pages use 2005-era HTML patterns (`<center>`, `<font color>`, `table#List`)
2. **Runtime Transformation**: Phase 3 JavaScript transforms old HTML → modern UI (fragile, slow)
3. **CSS Specificity Wars**: Modern design system fights legacy styles
4. **Inconsistent Design**: No single source of truth for page layout
5. **Hard to Update**: Changing design requires updating 11k+ static files

## Solution Architecture

### Three-Layer Approach

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Structured Data (JSON)                   │
│  - Person records extracted from existing HTML      │
│  - Version controlled, diffable                     │
│  - Single source of truth                           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2: Modern Templates (Jinja2)                 │
│  - Semantic HTML5 with Phase 4 design system        │
│  - No legacy markup patterns                        │
│  - Reusable components                              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Layer 3: Generated Pages (HTML)                    │
│  - Pre-rendered at build time                       │
│  - No runtime DOM transformation needed             │
│  - Deployed to docs/new/htm/                        │
└─────────────────────────────────────────────────────┘
```

## Migration Strategy

### Incremental Rollout (Recommended)

**Phase 1: Single Lineage Proof-of-Concept**
- Target: Hagborg-Hansson lineage (~100 people)
- Extract data from existing HTML
- Create JSON schema
- Validate extraction accuracy

**Phase 2: Template Development & Testing**
- Build modern Jinja2 templates
- Generate pages for test lineage
- Compare with original pages
- Iterate until perfect

**Phase 3: CI/CD Pipeline & Full Deployment**
- Automate generation in GitLab CI
- Expand to all 10 lineages
- Add validation tests
- Deploy to production

## File Organization

```
auntruth/
├── data/
│   └── people/
│       └── {lineage}/
│           └── {person_id}.json          # Extracted structured data
├── templates/
│   ├── person.html                       # Main person page template
│   ├── thumbnail.html                    # Photo gallery template
│   ├── lineage-index.html               # Lineage navigation template
│   ├── components/
│   │   ├── person-header.html           # Reusable header component
│   │   ├── family-section.html          # Family relationships
│   │   └── data-table.html              # Data display table
│   └── base.html                        # Base layout (navigation, footer)
├── PRPs/scripts/both/
│   ├── extract_person_data.py           # HTML → JSON extraction
│   ├── generate_pages.py                # JSON + templates → HTML
│   └── validate_generated_pages.py      # Quality assurance
└── docs/new/htm/
    └── L*/                               # Generated HTML output
        ├── XF*.htm                       # Person pages (generated)
        ├── THF*.htm                      # Thumbnail pages (generated)
        └── index.htm                     # Lineage index (generated)
```

## Technology Stack

- **Python 3.11+** - Generation scripts
- **Jinja2** - Template engine
- **JSON** - Data format
- **GitLab CI** - Automated builds
- **Git** - Version control for data and templates

## Key Benefits

✅ **Clean Separation of Concerns**: Data ≠ Presentation ≠ Output
✅ **Single Source of Truth**: Templates define all pages
✅ **Easy Global Changes**: Update template, regenerate all pages
✅ **Version Control Data**: JSON is diffable, trackable
✅ **No Runtime Overhead**: Pages are pre-rendered
✅ **Consistent Design**: Phase 4 design system baked in
✅ **Automated Testing**: CI validates all pages before deploy
✅ **Future-Proof**: Easy to add new fields, change design

## Success Criteria

1. **Data Accuracy**: 100% of original data preserved in JSON
2. **Visual Parity**: Generated pages match or exceed original quality
3. **Performance**: Page generation completes in < 5 minutes for all 2,985 pages
4. **Maintainability**: Non-technical users can update data via JSON
5. **CI Integration**: Automated builds pass all validation tests

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Data loss during extraction | Validate against original HTML, keep backups |
| Template bugs affect all pages | Test on single lineage first, gradual rollout |
| CI pipeline failures | Local generation works as fallback |
| Breaking existing URLs | Maintain exact same file paths and names |
| Missing edge cases | Comprehensive validation script catches issues |

## Timeline Estimate

- **Phase 1 (Data Extraction)**: 1 week
- **Phase 2 (Templates & Generation)**: 2 weeks
- **Phase 3 (CI/CD & Full Rollout)**: 1 week
- **Total**: 4 weeks for complete migration

## Dependencies

- Access to existing HTML pages in `docs/new/htm/`
- GitLab repository with CI/CD enabled
- Phase 4 design system CSS files (`modern-design-system.css`)
- Existing Phase 3 JavaScript components (can be integrated into templates)
