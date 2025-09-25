# Phase 4 Broken Links Problem Resolution Plan (PRP)

**Date**: 2024-09-24
**Status**: Ready for Execution
**Priority**: CRITICAL - 1,513 fixable broken links identified

## Problem Summary

Current broken link analysis from live reports shows **1,835 total broken references** across HTM and NEW sites:
- **HTM site**: 71 broken references (45 unique URLs)
- **NEW site**: 1,764 broken references (1,687 unique URLs)

**Critical Discovery**: 82.5% of these issues (1,513 broken links) are systematic and fixable through 4 targeted scripts.

## Investigation & Analysis

### Current State Analysis ✅
Based on actual reports from broken link checker run 2024-09-24:
- `PRPs/scripts/reports/broken_links_htm_20250924_234659.csv`
- `PRPs/scripts/reports/broken_links_new_20250924_234802.csv`

### Pattern Analysis Results

1. **🔥 CRITICAL: Relative Path Conversion** - 1,486 broken links (80.9% of all issues)
   - Pattern: `/L0/XI1029.htm` should be `/auntruth/new/htm/L0/XI1029.htm`
   - Source: Primarily `docs/htm/L1/oldim.htm` (1,459 links from this single file)
   - Impact: **Single highest-impact fix possible**

2. **Image Case Sensitivity** - 22 broken links (1.2% of issues)
   - Pattern: `index_files/image###.jpg` likely exist as `image###.JPG`
   - Source: `docs/htm/L1/lastcall/index.htm`

3. **Windows Backslash Paths** - 3 broken links (0.2% of issues)
   - Pattern: `\AuntRuth\index#.htm` should be `/auntruth/index#.htm`

4. **Malformed JPG Spaces** - 2 broken links (0.1% of issues)
   - Pattern: `/auntruth/jpg/ .jpg` (space before filename)
   - Already partially addressed in previous phases

## Solution Approach

### Phase 4.1: High-Impact Relative Path Fix (PRIORITY 1)
**Script**: `PRPs/scripts/both/phase4-fix-relative-new-paths.py`
- **Target**: 1,486 broken links (80.9% of all issues)
- **Pattern**: Convert `/L#/filename.htm` to `/auntruth/new/htm/L#/filename.htm`
- **Primary Target**: `docs/htm/L1/oldim.htm` and similar files
- **Expected Impact**: Massive improvement - single fix addresses majority of problems

### Phase 4.2: Image Case Sensitivity Fix (PRIORITY 2)
**Script**: `PRPs/scripts/both/phase4-fix-image-case.py`
- **Target**: 22 broken links in HTM site
- **Pattern**: Check for case mismatches between link references and actual files
- **Actions**: Either rename files to match links or update links to match files

### Phase 4.3: Windows Path Cleanup (PRIORITY 3)
**Script**: `PRPs/scripts/both/phase4-fix-backslash-paths.py`
- **Target**: 3 broken links with Windows-style paths
- **Pattern**: Replace `\AuntRuth\` with `/auntruth/`
- **Safety**: Simple text replacement with validation

### Phase 4.4: Final Cleanup (PRIORITY 4)
**Script**: `PRPs/scripts/both/phase4-fix-malformed-spaces.py`
- **Target**: 2 remaining malformed JPG paths
- **Pattern**: Remove spaces in `/auntruth/jpg/ .jpg` patterns

## Execution Plan

### Prerequisites ✅
- [x] Current broken link analysis completed
- [x] Pattern analysis validates systematic issues
- [x] All patterns confirmed fixable through automation
- [x] Safety protocols defined per @PRPs/fix-link-tips.md

### Step 1: Execute High-Impact Fix
```bash
# Create the critical relative path conversion script
# Test pattern (dry run)
python3 PRPs/scripts/both/phase4-fix-relative-new-paths.py --dry-run --limit=10

# If validation passes, execute full fix
python3 PRPs/scripts/both/phase4-fix-relative-new-paths.py

# Expected result: ~1,486 broken links → working links
```

### Step 2: Execute Image Case Fix
```bash
# Check and fix image case sensitivity issues
python3 PRPs/scripts/both/phase4-fix-image-case.py --dry-run

# Execute if issues found and validated
python3 PRPs/scripts/both/phase4-fix-image-case.py
```

### Step 3: Execute Windows Path Cleanup
```bash
# Fix Windows backslash paths
python3 PRPs/scripts/both/phase4-fix-backslash-paths.py --dry-run

# Execute cleanup
python3 PRPs/scripts/both/phase4-fix-backslash-paths.py
```

### Step 4: Execute Final Cleanup
```bash
# Fix remaining malformed spaces
python3 PRPs/scripts/both/phase4-fix-malformed-spaces.py --dry-run

# Execute final cleanup
python3 PRPs/scripts/both/phase4-fix-malformed-spaces.py
```

### Step 5: Validation & Measurement
```bash
# Re-run broken link checker to measure improvement
# (User will run this - don't run automatically)

# Expected improvement: 1,513 broken links fixed (82.5% reduction)
```

## Expected Outcomes

### Immediate Impact
- **Before**: 1,835 total broken references
- **After Phase 4.1**: ~349 remaining broken references (80.9% reduction)
- **After All Phases**: ~322 remaining broken references (82.5% reduction)

### Success Metrics
- ✅ Massive reduction in broken link count
- ✅ NEW site accessibility dramatically improved
- ✅ Systematic pattern issues resolved
- ✅ Foundation laid for addressing remaining edge cases

## Risk Assessment & Mitigation

### Low Risk ✅
All scripts will implement safety protocols from @PRPs/fix-link-tips.md:
- Git branch verification
- Dry-run modes for preview
- Pattern-specific targeting (no broad replacements)
- Progress reporting and error handling
- Sample validation where possible

### Validation Strategy
- Pattern-specific regex matching for each fix type
- Small sample testing before full execution
- Immediate measurement via broken link checker
- URL testing with curl where server is available

## Script Implementation Requirements

### Script 1: phase4-fix-relative-new-paths.py (CRITICAL)
**Purpose**: Convert relative NEW site paths to absolute paths with /htm/ prefix
**Target Pattern**: `/L#/filename.htm` → `/auntruth/new/htm/L#/filename.htm`
**Primary Focus**: `docs/htm/L1/oldim.htm` and similar files with relative NEW site references

### Script 2: phase4-fix-image-case.py
**Purpose**: Fix image file case sensitivity issues
**Target Pattern**: Check `index_files/image###.jpg` vs actual file case
**Action**: Rename files or update references to match

### Script 3: phase4-fix-backslash-paths.py
**Purpose**: Convert Windows-style backslash paths to forward slashes
**Target Pattern**: `\AuntRuth\index#.htm` → `/auntruth/index#.htm`

### Script 4: phase4-fix-malformed-spaces.py
**Purpose**: Clean up remaining malformed JPG paths with spaces
**Target Pattern**: `/auntruth/jpg/ .jpg` → `/auntruth/jpg/corrected-filename.jpg`

## Critical Success Factors

**MUST USE**: Current broken link reports as source of truth
- `PRPs/scripts/reports/broken_links_htm_20250924_234659.csv`
- `PRPs/scripts/reports/broken_links_new_20250924_234802.csv`

Key principles:
1. **Current data over assumptions** - Base all fixes on actual current broken link patterns
2. **High-impact, low-risk first** - Phase 4.1 addresses 80.9% of issues
3. **Precise pattern matching** - Each script targets specific verified patterns
4. **Immediate validation** - Test fixes and measure improvement

## Next Actions

1. **Create Script 1** - phase4-fix-relative-new-paths.py (highest impact)
2. **Execute Phase 4.1** - Run relative path conversion fix
3. **Measure results** - Run broken link checker to validate improvement
4. **Execute remaining phases** - Clean up remaining systematic issues
5. **Final measurement** - Confirm overall improvement
6. **Commit changes** - If results meet expectations

## Notes

- This follows data-driven investigation based on actual current broken link reports
- Scripts target the real patterns found in live data, not assumptions
- Expected total improvement: **82.5% broken link reduction**
- Remaining 322 broken links will likely be individual missing files requiring separate investigation

**SUCCESS INDICATOR**: If Phase 4.1 achieves expected results (80%+ improvement), this validates the current-data-first approach and demonstrates the critical importance of using live reports over historical analysis.