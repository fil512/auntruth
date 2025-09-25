# Fix Remaining Links - Phase 5 Plan

## Prerequisites

**REQUIRED READING** before implementing any Phase 5 fixes:
1. **📚 Read `docs/README.md`** - Understanding file naming conventions and directory structure is essential for proper target identification
2. **📚 Read `PRPs/fix-link-tips.md`** - Critical lessons learned and investigation methodologies from previous phases

These documents provide the foundation for correctly identifying missing vs. misnamed files and proper investigation techniques.

## Executive Summary

After Phase 4's spectacular success (80.4% reduction in broken links), we have 359 remaining broken links that require targeted resolution. Through detailed analysis, we've categorized these into fixable issues vs. genuinely missing content.

**Current Status**: 359 broken links remaining (down from 1,835)
- HTM site: 71 broken references (45 unique URLs)
- NEW site: 288 broken references (218 unique URLs)

## Critical Data Sources

**Complete Broken Links Analysis - Sept 25, 2024:**
- 📄 `/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_htm_20250925_001222.csv`
- 📄 `/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_new_20250925_001324.csv`

These CSV files contain the complete, detailed analysis of all remaining broken links including:
- Exact broken URLs
- HTTP status codes
- Source files containing the broken links
- Original link text
- Issue type classification
- Suggested fix recommendations

**IMPORTANT**: All Phase 5 scripts must reference these CSV files as the authoritative source of broken links to fix. Do not rely on manual searches or assumptions.

## Key Discovery from Investigation

**Media Hunt Results**: Your instinct to hunt for missing media first was absolutely correct! We discovered:

✅ **Found**: F208.jpg and F404.jpg exist with lowercase names (f208.jpg, f404.jpg)
✅ **Found**: All 23 JPG files exist in docs/htm/L1/lastcall/index_files/
✅ **Found**: WMZ files (image001.wmz, image003.wmz, image004.wmz) exist
❌ **Missing**: AVI files (hag1938.avi, etc.) confirmed genuinely missing
❌ **Missing**: Birthday.pps PowerPoint file confirmed missing

**XI vs XF Investigation**: XI2674.htm and XI2675.htm are genuinely missing photo detail pages (not typos for XF files). The sequence shows XI2673 exists → XI2674,XI2675 missing → XI2676 exists. These represent photos that were never fully processed.

## Categorized Resolution Strategy

### Category 1: Case Sensitivity Fixes (~40 links - HIGH SUCCESS RATE)

**HTML File Case Issues**:
- `hh1.htm` → `HH1.htm` (file exists as uppercase)
- `pringcem.htm` → `PRINGCEM.htm` (file exists as uppercase)
- `lathbook.htm` → `LATHBOOK.htm` (file exists as uppercase)

**Image File Case Issues**:
- `F208.jpg` → `f208.jpg` (exists with lowercase)
- `F404.jpg` → `f404.jpg` (exists with lowercase)

**Expected Result**: ~40 links FIXED (not removed)

### Category 2: Path Correction Fixes (~50 links)

**index_files Path Issues**:
- 23 images referenced as `index_files/image*.jpg` need correct relative paths
- All files exist in `docs/htm/L1/lastcall/index_files/`

**NEW Site Relative Path Issues**:
- References like `XF179.htm` need `/auntruth/new/htm/L#/` prefix
- Only apply where target files actually exist

**Expected Result**: ~50 links FIXED

### Category 3: Target Investigation and Resolution (~270 links)

**CRITICAL APPROACH**: Before removing any link, use systematic investigation to find the correct target:

#### Investigation Strategy (per `docs/README.md` file conventions):

1. **Check File Naming Variations**:
   - `XF123.htm` vs `XI123.htm` (Person vs Image detail pages)
   - Case sensitivity: `INDEX.htm` vs `index.htm`
   - Directory variations: `/L1/file.htm` vs `/htm/L1/file.htm`

2. **Use File System Search**:
   ```bash
   find docs/ -iname "filename.htm"  # Case-insensitive search
   find docs/ -name "*123*"          # Partial number matching
   ```

3. **Check Sequential Numbers**:
   - If `XF1234.htm` is missing, check if `XF1233.htm` or `XF1235.htm` exist
   - Gap analysis: Some numbers may be missing due to deleted/never-created entries

4. **Directory Structure Analysis**:
   - Person files: `XF###.htm` should be in appropriate lineage directory (`L0/`, `L1/`, etc.)
   - Image files: `XI###.htm` may be cross-referenced from multiple lineages
   - Thumbnail files: `THF###.htm` should match corresponding `XF###.htm` numbers

#### Resolution Outcomes:

**A. Target Found → Fix the Link**:
- Update link to correct path/filename/case
- Preserve full functionality

**B. Target Genuinely Missing → Remove Link, Preserve Content**:
- Replace `<a href="missing.htm">Person Name</a>` with `Person Name`
- Preserve all descriptive text and context
- Remove only the non-functional anchor tag

#### Specific Cases for Link Removal (After Investigation):

**Confirmed Placeholder Links**:
- `XF1234.htm` (22 references) - obvious sequential placeholder ID
- `XI2674.htm`, `XI2675.htm` - confirmed missing photo detail pages (verified in sequence)

**Confirmed Missing Media** (after thorough hunt):
- `.avi` video files (hag1938.avi, hag1946.avi, etc.) - confirmed genuinely missing
- `Birthday.pps` PowerPoint file - confirmed missing

**Missing Index Files**:
- `/auntruth/index1.htm`, `/auntruth/index3.htm`, etc.
- `/auntruth/new/L*/index.htm` files
- Consider creating simple redirect pages rather than removing all references

**Expected Result**: Investigation-based resolution - fix where possible, clean only when genuinely missing

## Implementation Scripts

### Script 1: Case Sensitivity Fixes (Priority 1)
```python
# PRPs/scripts/both/phase5-fix-case-sensitivity.py
# Fix both HTML and image case sensitivity issues
# Pattern: hh1.htm → HH1.htm, F208.jpg → f208.jpg
```

### Script 2: Path Correction Fixes (Priority 2)
```python
# PRPs/scripts/both/phase5-fix-path-issues.py
# Correct index_files paths and NEW site relative paths
# Only fix where target files actually exist
```

### Script 3: Investigate and Resolve Missing Targets (Priority 3)
```python
# PRPs/scripts/both/phase5-investigate-missing-targets.py
# For each broken link in CSV:
# 1. Apply file naming convention knowledge from docs/README.md
# 2. Use systematic file system searches to locate correct targets
# 3. Apply findings from PRPs/fix-link-tips.md investigation techniques
# 4. Fix link if target found, remove anchor (preserve text) if genuinely missing
```

### Script 4: Remove Confirmed Missing Content (Priority 4)
```python
# PRPs/scripts/both/phase5-remove-confirmed-missing.py
# Remove only confirmed missing content after investigation:
# - XF1234.htm placeholder references
# - Confirmed missing .avi files
# - Missing Birthday.pps reference
# - XI2674.htm, XI2675.htm (verified missing photo pages)
# Always preserve text content, remove only anchor tags
```

## Expected Final Results

### Investigation-Based Outcomes

**Phase 5A: Direct Fixes (High Success Rate)**
- **Case sensitivity**: ~40 links fixed
- **Path corrections**: ~50 links fixed
- **Target investigation discoveries**: TBD based on systematic search results

**Phase 5B: Content Preservation (After Thorough Investigation)**
- **Confirmed placeholder links**: ~22 links cleaned (anchor removed, text preserved)
- **Genuinely missing files**: Variable based on investigation findings
- **Missing media**: ~10 links cleaned (confirmed after hunt)

**Expected Investigation Results**:
- **50-70% of "missing" files may be findable** through proper naming convention analysis
- **30-50% may be genuinely missing** and require link removal with content preservation

### Final Outcome
- **Total Addressed**: 359 links (100% of remaining issues)
- **Links Fixed**: 90+ (preserve functionality where files exist)
- **Links Cleaned**: Variable based on investigation (remove anchors, preserve all text)
- **User Experience**: No more clicks to nowhere, maximum content preservation
- **Data Integrity**: All person names, descriptions, and context retained

## Key Principles

1. **Investigate First**: Use `docs/README.md` naming conventions and `PRPs/fix-link-tips.md` methodologies before any action
2. **Hunt Before Remove**: Systematically search for files using multiple strategies before assuming they're missing
3. **Fix Over Remove**: Prefer fixing broken paths over removing functional content
4. **Preserve All Content**: When removing links, always preserve text content - no information loss
5. **Never Create Placeholders**: If target doesn't exist, remove anchor but keep content - don't create dummy pages
6. **Data-Driven Investigation**: Use CSV reports and file system searches, not assumptions

## Success Metrics

**Phase 4 Achievement**: 80.4% reduction (1,835 → 359 links)
**Phase 5 Target**: Address all remaining 359 links
**Expected Final State**: ~92 working links preserved, ~267 dead links cleaned
**Total Project Impact**: 95%+ improvement in broken links resolution

This represents one of the most comprehensive broken link resolution efforts possible while maintaining content integrity and user experience.