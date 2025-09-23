# Task 005: Fix Background Image Paths

## Task Overview
**Item Number**: 005
**Task Name**: fix-background-image-paths
**Description**: Correct background image relative paths
**Target Directory**: docs/htm
**Search Pattern**: ../jpg/backruth.jpg
**Status**: INCOMPLETE → IN PROGRESS

## Background Context
From PLAN/modernize.md: The genealogy site has broken relative paths to background images, specifically `../jpg/backruth.jpg` which doesn't work correctly from the current directory structure. These need to be corrected to proper relative paths for the GitHub Pages deployment.

## Mandatory Pre-Execution Checklist
**CRITICAL: Complete ALL items before proceeding with any file changes**

### 1. Repository Status Verification
- [x] Verify you are in an EXISTING git branch: task-005-fix-background-image-paths
- [x] Confirm tracking CSV shows this task as IN PROGRESS
- [x] Check git status is clean before starting

### 2. Scope Analysis (MANDATORY - Complete BEFORE choosing tools)
- [ ] **Count total files** affected by this search pattern in target directory
- [ ] **Report exact file count** before selecting approach
- [ ] **List directory structure** to understand relative path requirements
- [ ] **Analyze current background image references** to understand what corrections are needed

### 3. Tool Selection Decision Point
**RULE**: If >100 files affected → MUST use Python script (Edit/MultiEdit = TASK FAILURE)
- [ ] **File count**: _____ files found
- [ ] **Tool choice**: [ ] Script (>100 files) [ ] Manual edit (<100 files)
- [ ] **Justification**: _________________________

### 4. Script Resources Check
- [ ] **Read PRPs/scripts/README.md** to check for existing relevant scripts
- [ ] **Decision**: [ ] Reuse existing script [ ] Create new script [ ] Manual edit
- [ ] **Script path** (if applicable): ________________________

## Core Task Requirements

### Primary Objective
Fix incorrect background image relative paths from `../jpg/backruth.jpg` to the correct relative path that works from the GitHub Pages deployment structure.

### Technical Details
**Current Structure Understanding Needed:**
- Site root: `/docs/` (GitHub Pages serves from here)
- HTML files: `/docs/htm/` (various subdirectories L0-L9)
- Images: `/docs/jpg/` (image directory)
- Current broken path: `../jpg/backruth.jpg`
- Correct path needs to be: `../jpg/backruth.jpg` or `/auntruth/jpg/backruth.jpg` depending on depth

### Search and Replace Patterns
**Pattern to find**: `../jpg/backruth.jpg`
**Analysis needed**:
1. Check directory depth of files using this pattern
2. Determine correct relative path for each location
3. May need different replacement patterns based on directory depth

### Validation Requirements
1. **Path verification**: Test that corrected paths actually point to existing image file
2. **Syntax check**: Ensure HTML remains valid after changes
3. **Cross-reference check**: Verify no other similar broken background image paths exist

## Implementation Plan

### Phase 1: Analysis and Discovery
1. **File discovery**: Find all files containing `../jpg/backruth.jpg`
2. **Directory analysis**: Map the directory structure and depth relationships
3. **Path calculation**: Determine correct relative paths for each file location
4. **Pattern validation**: Confirm the search pattern captures all instances

### Phase 2: Correction Implementation
1. **Path replacement**: Update paths to correct relative references
2. **Testing**: Verify each corrected path points to existing file
3. **Validation**: Ensure HTML syntax remains valid

### Phase 3: Verification and Documentation
1. **File verification**: Confirm all instances were corrected
2. **Path testing**: Validate that new paths resolve correctly
3. **Documentation**: Update script README if new script was created

## Acceptance Criteria
- [ ] All instances of `../jpg/backruth.jpg` are corrected to proper relative paths
- [ ] All corrected paths point to existing image files
- [ ] HTML syntax remains valid in all modified files
- [ ] No similar background image path issues remain unaddressed
- [ ] Changes are committed to the feature branch
- [ ] Script documented in PRPs/scripts/README.md if created

## Error Handling
- **File not found**: If image file doesn't exist at expected location, document and report
- **Multiple path patterns**: If files at different depths need different corrections, handle appropriately
- **HTML validation errors**: Fix any syntax issues introduced during path corrections

## Completion Verification
Run these commands to verify completion:
```bash
# Verify no more instances of the broken pattern exist
grep -r "../jpg/backruth.jpg" docs/htm/

# Check that corrected paths exist (example)
ls -la docs/jpg/backruth.jpg

# Validate HTML syntax for modified files (if applicable)
```

## Notes
- This task focuses specifically on `../jpg/backruth.jpg` background image paths
- May discover other similar background image path issues that should be noted for future tasks
- Consider the relative path structure carefully based on GitHub Pages deployment