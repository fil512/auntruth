# Broken Links Analysis & Script Recommendations

Based on analysis of 32,235+ broken links, I've identified key patterns and recommend these categorized fix scripts:

## Major Patterns Identified

### 1. **Image Path Resolution Issues** (~40% of problems)
- **Problem**: Links to `/auntruth/htm/jpg/image.jpg` (404) when actual files are at `/auntruth/jpg/image.jpg` (200 OK)
- **Root Cause**: HTML files incorrectly assume images are in subdirectories under `/htm/`
- **Scale**: Affects thousands of image references

### 2. **Missing AuntRuth Directory** (~25% of problems)
- **Problem**: Links to `/AuntRuth/` return 404
- **Affected Files**: References across L1, L3, L6 lineage directories
- **Root Cause**: Directory structure mismatch or missing directory

### 3. **Index File Path Issues** (~20% of problems)
- **Problem**: Relative links `../index.html` and `../index.htm` broken
- **Root Cause**: Incorrect relative path calculations from various directory depths

### 4. **Directory Case Sensitivity** (~10% of problems)
- **Problem**: Links to `/l4/` when directories are `/L4/`
- **Root Cause**: Inconsistent case in HTML references

### 5. **Double Directory Paths** (~5% of problems)
- **Problem**: URLs like `/auntruth/htm/htm/L0/file.htm`
- **Root Cause**: Path concatenation errors creating duplicate directories

## Recommended Fix Scripts

### Priority 1: High-Impact Scripts

#### `both/015-fix-image-path-resolution.py`
**Purpose**: Fix image path resolution (affects ~40% of broken links)
```bash
# Usage: python3 both/015-fix-image-path-resolution.py [--dry-run] [--target-dir docs]
```
**Features**:
- Replace `/auntruth/htm/jpg/` with `/auntruth/jpg/` in HTML files
- Replace `/htm/jpg/` with `/jpg/` in relative contexts
- Update CSS background-image references
- Handle both single quotes and double quotes
- Estimated fix: ~12,000+ broken image links

#### `both/016-fix-relative-index-paths.py`
**Purpose**: Fix broken relative index file references
```bash
# Usage: python3 both/016-fix-relative-index-paths.py [--dry-run]
```
**Features**:
- Calculate correct relative paths to index files from each directory level
- Fix `../index.html` → `../../index.html` where needed
- Handle both `.htm` and `.html` extensions
- Verify target files exist before updating references
- Estimated fix: ~6,000+ index link issues

### Priority 2: Structural Scripts

#### `both/017-create-missing-auntruth-directory.py`
**Purpose**: Address missing /AuntRuth/ directory structure
```bash
# Usage: python3 both/017-create-missing-auntruth-directory.py [--dry-run]
```
**Features**:
- Analyze what /AuntRuth/ should contain by examining broken links
- Create appropriate directory structure or redirects
- Update references to point to correct locations
- Estimated fix: ~8,000+ AuntRuth directory links

#### `both/018-fix-directory-case-sensitivity.py`
**Purpose**: Fix case sensitivity issues in directory references
```bash
# Usage: python3 both/018-fix-directory-case-sensitivity.py [--dry-run]
```
**Features**:
- Replace `/l4/` with `/L4/`, `/l1/` with `/L1/`, etc.
- Verify actual directory case and update accordingly
- Handle both absolute and relative paths
- Estimated fix: ~3,000+ case sensitivity issues

### Priority 3: Cleanup Scripts

#### `both/019-remove-duplicate-directory-paths.py`
**Purpose**: Fix double directory path issues
```bash
# Usage: python3 both/019-remove-duplicate-directory-paths.py [--dry-run]
```
**Features**:
- Replace `/auntruth/htm/htm/` with `/auntruth/htm/`
- Fix path concatenation errors
- Clean up malformed URLs
- Estimated fix: ~1,500+ duplicate path issues

#### `both/020-cleanup-missing-media-files.py`
**Purpose**: Handle missing media files (.pps, .avi, .wmz)
```bash
# Usage: python3 both/020-cleanup-missing-media-files.py [--dry-run]
```
**Features**:
- Remove links to missing PowerPoint files (.pps)
- Replace missing video files (.avi) with placeholders
- Handle missing Word image files (.wmz)
- Log removed references for manual review
- Estimated fix: ~500+ missing media references

## Implementation Order

1. **Start with** `015-fix-image-path-resolution.py` (highest impact)
2. **Follow with** `016-fix-relative-index-paths.py`
3. **Then address** structural issues with remaining scripts
4. **Run** `both/find-broken-links.py` after each script to measure progress

## Expected Results

- **Phase 1** (image + index fixes): ~75% reduction in broken links
- **Phase 2** (structural fixes): ~20% additional reduction
- **Phase 3** (cleanup): ~5% additional reduction
- **Final result**: <1% broken links remaining (mostly missing external files)

Each script should follow the safety protocols in PRPs/scripts/README.md with dry-run mode, progress reporting, and git branching.