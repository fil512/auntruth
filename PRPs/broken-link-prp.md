# Broken Links Fix - Phase 2 PRP

## Overview
After successfully reducing broken links from 32,235+ to 4,598 (86% improvement) in Phase 1, this PRP addresses the remaining broken links with targeted, high-impact fixes.

## Current State
- **Total broken links**: 4,598
- **HTM site**: 6,728 broken links in CSV (some duplicates)
- **NEW site**: 11,385 broken links in CSV (some duplicates)
- **Last report date**: 2025-09-24

## Root Cause Analysis

### Issue 1: Missing Index Files (2,006 broken links)
**Pattern**: Links pointing to non-existent root index files
- `/auntruth/index.html` - 500 references (404)
- `/auntruth/new/index.htm` - 1,506 references (404)

**Root Cause**: These files were never created or were removed
**Impact**: 43.6% of all broken links

### Issue 2: Missing /auntruth/ Prefix (13,128+ patterns)
**Pattern**: Links use `/htm/L0/file.htm` instead of `/auntruth/htm/L0/file.htm`
- Found in 719 files across both sites
- Causes server to resolve paths incorrectly
- Shows as `/auntruth/htm/htm/L0/file.htm` in broken link reports

**Root Cause**: Relative path resolution in web server context
**Impact**: Affects hundreds of files with thousands of links

### Issue 3: Wrong Lineage Directory References (222 links)
**Pattern**: Files referenced in wrong L directory
- Example: XF533.htm exists in L9/ but 111 links point to L1/
- Similar pattern for XF1234.htm (20 instances)

**Root Cause**: Likely manual errors or file moves without updating references
**Impact**: ~5% of broken links - LOW PRIORITY (isolated cases)

## Solution Plan

### Phase 2.1: Create Missing Index Files
**Script**: `023-create-missing-root-index-files.py`
- Create `/auntruth/index.html` as redirect to `/auntruth/htm/index.html`
- Copy `/auntruth/new/index.html` to `/auntruth/new/index.htm`
- Expected fix: 2,006 broken links (~44% of remaining)

### Phase 2.2: Fix Missing /auntruth/ Prefix
**Script**: `024-fix-missing-auntruth-prefix.py`
- Add `/auntruth/` prefix to all `/htm/` paths in href/src attributes
- Process 719 files with 13,128+ patterns
- Expected fix: Most of the remaining broken links

### Phase 2.3: Manual Investigation (if needed)
- After running scripts, re-run broken link checker
- Investigate any remaining high-frequency broken links
- Consider manual fixes for isolated cases like XF533.htm

## Scripts Created

### Script 023: create-missing-root-index-files.py
- **Location**: `PRPs/scripts/both/023-create-missing-root-index-files.py`
- **Purpose**: Create missing index.html and index.htm files
- **Safety**: Creates new files only, doesn't modify existing
- **Testing**: Has dry-run mode, validates with curl

### Script 024: fix-missing-auntruth-prefix.py
- **Location**: `PRPs/scripts/both/024-fix-missing-auntruth-prefix.py`
- **Purpose**: Add /auntruth/ prefix to relative /htm/ paths
- **Safety**: Has dry-run mode, git branch verification
- **Testing**: Tests sample URLs before/after with curl

## Execution Steps

1. **MANDATORY: Read the best practices guide**
   ```bash
   # CRITICAL: Read this BEFORE doing anything else
   cat PRPs/fix-link-tips.md
   ```
   This document contains critical lessons learned and common pitfalls to avoid.
   **DO NOT SKIP THIS STEP** - it will save hours of debugging and prevent mistakes.

2. **Verify current state**
   ```bash
   # Check current branch
   git branch --show-current

   # Get fresh broken link count (user runs this)
   # python3 PRPs/scripts/both/find-broken-links.py --site=htm --timeout=3
   ```

3. **Run Script 023 - Create missing index files**
   ```bash
   # Dry run first
   python3 PRPs/scripts/both/023-create-missing-root-index-files.py

   # Execute
   python3 PRPs/scripts/both/023-create-missing-root-index-files.py --no-dry-run
   ```

4. **Run Script 024 - Fix missing /auntruth/ prefix**
   ```bash
   # Dry run first (will show many files)
   python3 PRPs/scripts/both/024-fix-missing-auntruth-prefix.py

   # Execute
   python3 PRPs/scripts/both/024-fix-missing-auntruth-prefix.py --no-dry-run
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "Phase 2: Fix missing index files and /auntruth/ prefixes

   - Created missing root index files (2,006 broken links fixed)
   - Added /auntruth/ prefix to relative paths (13,128+ patterns fixed)
   - Expected reduction: 4,598 → <500 broken links (90%+ improvement)"
   ```

6. **Measure improvement**
   ```bash
   # User runs broken link checker again
   # python3 PRPs/scripts/both/find-broken-links.py --site=htm --timeout=3
   ```

## Expected Results

### Quantitative
- **Before Phase 2**: 4,598 broken links
- **After Phase 2**: <500 broken links (estimated)
- **Total improvement**: From 32,235+ to <500 (98%+ reduction)

### Qualitative
- Site navigation significantly improved
- User experience enhanced with working links
- Maintenance easier with consistent path structure

## Validation Methods

1. **URL Testing**: Scripts test sample URLs with curl
2. **Dry Run Mode**: Preview changes before execution
3. **Broken Link Reports**: Compare before/after CSVs
4. **Git Diff Review**: Inspect changes before committing

## Risk Assessment

### Low Risk
- Creating new index files (no existing files modified)
- Adding /auntruth/ prefix (consistent, predictable change)
- All changes reversible via git

### Mitigations
- Dry-run mode for all scripts
- Git branch verification
- Small sample testing before full execution
- Ability to revert via git if issues arise

## Lessons Learned (Phase 1 & 2)

1. **Investigation beats assumptions** - Always test with curl first
2. **Pattern frequency matters** - Fix common patterns first
3. **Creating vs fixing** - Sometimes creating missing files is simpler
4. **CSV columns tell different stories** - Check both Broken_URL and Original_Link_Text
5. **Validate both success and failure** - Ensure old URLs are actually broken

## Next Steps (After Phase 2)

1. Review remaining broken links after Phase 2 execution
2. Identify any new patterns in residual broken links
3. Consider manual fixes for isolated cases
4. Document any new patterns in fix-link-tips.md
5. Plan Phase 3 if significant broken links remain

## Success Criteria

- [ ] Broken links reduced to <500 (from 4,598)
- [ ] Both scripts execute without errors
- [ ] Git commit includes all changes
- [ ] Broken link checker confirms improvement
- [ ] No new broken links introduced

---

**Status**: Ready for execution
**Last Updated**: 2025-09-24
**Author**: Claude with Ken