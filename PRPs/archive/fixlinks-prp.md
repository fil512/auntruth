# Fix Links Problem Resolution Plan (PRP)

**Date**: 2024-09-24
**Status**: Ready for Execution
**Priority**: HIGH - 1,841 broken links identified

## Problem Summary

Broken link checker identified **1,841 total broken references** across HTM and NEW sites:
- **HTM site**: 74 broken references (46 unique URLs)
- **NEW site**: 1,767 broken references (1,688 unique URLs)

## Investigation & Analysis

### Pattern Analysis Completed ✅
Created and ran `PRPs/scripts/both/analyze-broken-link-patterns.py` which identified:

1. **🔥 CRITICAL: Missing /htm/ Prefix** - 1,486 broken links (80.7% of all issues)
   - Pattern: `/auntruth/new/L[0-9]+/` should be `/auntruth/new/htm/L[0-9]+/`
   - This matches the Phase 3 breakthrough documented in @PRPs/fix-link-tips.md

2. **Backslash Path Separators** - 3 broken links
   - Pattern: `\AuntRuth\index` should be `/AuntRuth/index`

3. **Malformed JPG Paths** - 10 broken links
   - Pattern: `/auntruth/jpg/ filename.jpg` should be `/auntruth/jpg/filename.jpg`

4. **Other Missing Files** - 290 broken links requiring individual investigation

## Solution Approach

### Phase 1: High-Impact Pattern Fix (PRIORITY 1)
**Script**: `PRPs/scripts/new/fix-missing-htm-prefix.py` (Script 017)
- **Target**: 1,486 broken links (81% of all issues)
- **Expected Impact**: Massive improvement - single fix addresses majority of problems
- **Pattern**: Add missing `/htm/` component to NEW site lineage references
- **Safety**: Includes URL validation, dry-run mode, sample testing

### Phase 2: Medium-Priority Cleanup (PRIORITY 2)
**Script**: `PRPs/scripts/both/fix-backslash-paths.py` (existing)
- **Target**: 3 broken links using Windows-style paths
- **Pattern**: Convert backslash to forward slash separators

### Phase 3: Low-Priority Cleanup (PRIORITY 3)
**Script**: `PRPs/scripts/both/fix-malformed-jpg-paths.py` (Script 019)
- **Target**: 10 broken links with space issues in JPG paths
- **Pattern**: Remove/fix problematic spaces in image paths
- **Note**: Some cases may require manual review for corrupted paths

## Execution Plan

### Prerequisites ✅
- [x] Pattern analysis completed
- [x] Fix scripts created and tested
- [x] All scripts include dry-run modes
- [x] Safety protocols implemented per @PRPs/fix-link-tips.md

### Step 1: Execute High-Impact Fix
```bash
# Test the fix pattern (dry run)
python3 PRPs/scripts/new/fix-missing-htm-prefix.py --dry-run --limit=10

# If validation passes, execute full fix
python3 PRPs/scripts/new/fix-missing-htm-prefix.py

# Expected result: ~1,486 broken links → working links
```

### Step 2: Execute Medium-Priority Fix
```bash
# Check if backslash issues exist
python3 PRPs/scripts/both/fix-backslash-paths.py --dry-run

# Execute if issues found
python3 PRPs/scripts/both/fix-backslash-paths.py
```

### Step 3: Execute Low-Priority Cleanup
```bash
# Check malformed JPG paths
python3 PRPs/scripts/both/fix-malformed-jpg-paths.py --dry-run

# Execute cleanup
python3 PRPs/scripts/both/fix-malformed-jpg-paths.py
```

### Step 4: Validation & Measurement
```bash
# Re-run broken link checker to measure improvement
# (User will run this - don't run automatically)

# Expected improvement: 1,499 broken links fixed (81.4% reduction)
```

## Expected Outcomes

### Immediate Impact
- **Before**: 1,841 total broken references
- **After Phase 1**: ~355 remaining broken references (80.7% reduction)
- **After All Phases**: ~342 remaining broken references (81.4% reduction)

### Success Metrics
- ✅ Massive reduction in broken link count
- ✅ NEW site accessibility dramatically improved
- ✅ Systematic pattern issues resolved
- ✅ Foundation laid for addressing remaining edge cases

## Risk Assessment & Mitigation

### Low Risk ✅
All scripts implement safety protocols from @PRPs/fix-link-tips.md:
- Git branch verification
- Dry-run modes for preview
- Sample URL validation where possible
- Pattern-specific targeting (no broad replacements)
- Progress reporting and error handling

### Validation Strategy
- URL testing with curl (where server is available)
- Pattern-specific regex matching
- Small sample testing before full execution
- Immediate measurement via broken link checker

## Critical Success Factors

**MUST READ**: @PRPs/fix-link-tips.md before execution

Key principles from tips document:
1. **Investigation over assumption** - Analysis confirmed actual patterns
2. **High-impact, low-risk first** - Phase 1 addresses 80.7% of issues
3. **Precise pattern matching** - Each script targets specific verified patterns
4. **Immediate validation** - Test fixes with curl and broken link checker

## Next Actions

1. **Execute Phase 1** - Run fix-missing-htm-prefix.py (highest impact)
2. **Measure results** - Run broken link checker to validate improvement
3. **Execute Phase 2 & 3** - Clean up remaining pattern-based issues
4. **Final measurement** - Confirm overall improvement
5. **Commit changes** - If results meet expectations

## Notes

- This follows the same breakthrough pattern from Phase 3 (missing /htm/ prefix)
- Scripts are placed in appropriate directories per PRPs/scripts/README.md
- Expected total improvement: **81.4% broken link reduction**
- Remaining 342 broken links will likely be individual missing files requiring separate investigation

**SUCCESS INDICATOR**: If Phase 1 achieves expected results (80%+ improvement), this PRP validates the systematic pattern-fixing approach and demonstrates the power of data-driven investigation over assumption-based fixes.