# Lineage Directory Mapping

## Overview

This document maps the lineage directories (L0-L9) to their lineage names and provides statistics about each lineage.

## Lineage Mapping Table

| Directory | Lineage Name | Person Count | Status | Notes |
|-----------|--------------|--------------|--------|-------|
| L0/ | (Other) | 82 | ⏳ Pending | Empty lineage name - unclassified people |
| L1/ | Hagborg-Hansson | 405 | ✅ Complete | Phase 1 & 2 complete, 99.3% validation |
| L2/ | Nelson | 309 | ⏳ Pending | |
| L3/ | Pringle-Hambley | 409 | ⏳ Pending | |
| L4/ | Lathrop-Lothropp | 686 | ⏳ Pending | Largest lineage |
| L5/ | Ward | 123 | ⏳ Pending | |
| L6/ | Selch-Weiss | 387 | ⏳ Pending | |
| L7/ | Stebbe | 156 | ⏳ Pending | |
| L8/ | Lentz | 77 | ⏳ Pending | Smallest lineage |
| L9/ | Phoenix-Rogerson | 391 | ⏳ Pending | |
| **TOTAL** | **10 lineages** | **3,025** | | |

## Extraction Order

Based on complexity and size, recommended extraction order for Phase 3:

1. **L8 (Lentz)** - 77 files - Smallest, good for testing
2. **L5 (Ward)** - 123 files - Small, validate process
3. **L7 (Stebbe)** - 156 files - Medium-small
4. **L2 (Nelson)** - 309 files - Medium
5. **L6 (Selch-Weiss)** - 387 files - Medium-large
6. **L9 (Phoenix-Rogerson)** - 391 files - Medium-large
7. **L3 (Pringle-Hambley)** - 409 files - Large
8. **L4 (Lathrop-Lothropp)** - 686 files - Largest (save for last to validate entire process)
9. **L0 (Other)** - 82 files - Special case with empty lineage names

## Notes

### L0 Special Case
- L0 has people with empty lineage names (empty `<strong>` tags in Lineage field)
- These appear to be unclassified or cross-lineage individuals
- Extraction script may need special handling for empty lineage names
- Suggested lineage name for data consistency: "Other" or "Unclassified"

### L1 (Hagborg-Hansson) - Reference Implementation
- **404/405 files extracted** (1 file missing/corrupted in source)
- **99.3% validation match rate** (401/404 files)
- **100% data preservation confirmed**
- All extraction scripts, templates, and validation tools tested and working
- This is the reference implementation for all other lineages

## Validation Summary

Once all lineages are extracted and generated:

| Metric | Target | Notes |
|--------|--------|-------|
| Total Pages | ~3,025 | All person pages across 10 lineages |
| JSON Files | ~3,020 | (allowing for missing/corrupted source files) |
| Generated HTML | ~3,020 | All pages with Phase 4 design system |
| Validation Match Rate | ≥99% | Based on L1 achievement of 99.3% |
| Data Preservation | 100% | Zero data loss required |
| Generation Time | < 5 min | Performance target for all pages |

## Phase 3 Timeline Estimate

- **Days 1-2**: Extract L2-L9 lineages (8 lineages, ~2,620 people)
- **Day 2**: Validate all extractions
- **Day 3**: Generate all pages and validate
- **Days 3-4**: Create GitLab CI/CD pipeline
- **Days 5-7**: Testing, deployment, documentation

**Total**: 1 week for complete Phase 3 rollout
