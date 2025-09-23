# Broken Links Fix - fix-backslash-paths.py

## Background
This is part of the systematic broken links fix plan for AuntieRuth.com genealogy website. You are working on item 002 of 6 total fixes.

## Task Description
Convert backslash paths to forward slashes

**Estimated fixes**: 500 broken links
**Priority**: 2

## Implementation Requirements

### Step 1: Create the Script
Create the script `PRPs/scripts/fix-backslash-paths.py` based on the requirements below.
**CRITICAL**: Place script in appropriate subdirectory:
- `PRPs/scripts/both/` if it works with both docs/htm and docs/new
- `PRPs/scripts/htm/` if it only works with docs/htm
- `PRPs/scripts/new/` if it only works with docs/new

### Step 2: Test the Script (Dry Run)
Run the script in dry-run mode on BOTH directories to show what changes would be made without actually modifying files.
- Test on docs/htm directory
- Test on docs/new directory

### Step 3: Apply the Script
Run the script to apply the changes to the website files in BOTH directories.
- Process docs/htm directory completely
- Process docs/new directory completely
- Verify zero remaining references in both directories

### Step 4: Select Test URLs
Select 5-10 representative URLs from the most affected files to test the changes.
**CRITICAL**: Provide URLs in localhost format for both sites:
- Original site: http://localhost:8000/auntruth/htm/L2/FILENAME.htm
- Modernized site: http://localhost:8000/auntruth/new/htm/L2/FILENAME.htm
Include representative URLs from BOTH original (docs/htm) and modernized (docs/new) sites.

### Step 5: MANDATORY User Validation
**CRITICAL**: You must WAIT for user validation before proceeding. The user must test the provided URLs and confirm no functionality is broken.

### Step 6: Report Results
Provide a summary of:
- Number of files modified in docs/htm
- Number of files modified in docs/new
- Total number of fixes applied across both directories
- Any issues encountered
- Representative test URLs provided to user (in localhost format)

## Script-Specific Requirements

**For fix-backslash-paths.py:**

### Backslash Path Fixes (fix-backslash-paths.py)
- Convert backslash paths to forward slashes
- Fix patterns like `./L0\XF0.htm` → `./L0/XF0.htm`
- Handle double htm paths: `/htm/htm/` → `/htm/`
- Focus on modernized site (`docs/new/`) with more backslash issues

## Success Criteria
- Script executes without errors
- Fixes are applied correctly
- User validates that representative URLs still work
- No functionality is broken
- Changes are ready for git commit

## IMPORTANT NOTES
- **CRITICAL**: Process BOTH docs/htm AND docs/new directories completely
- NEVER proceed without user validation
- Select diverse test URLs from different affected areas of BOTH sites
- Provide URLs in localhost format (http://localhost:8000/auntruth/htm/... and http://localhost:8000/auntruth/new/htm/...)
- Provide clear before/after examples where helpful
- If any issues are found during user testing, investigate and fix before proceeding
- Verify zero remaining references in both directories before completion