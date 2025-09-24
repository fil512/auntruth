# Broken Links Fix - remove-word-artifacts.py

## Background
This is part of the systematic broken links fix plan for AuntieRuth.com genealogy website. You are working on item 006 of 6 total fixes.

**Current Status (2025-09-23 19:50):**
- Total broken links across both sites: 84,844 (much higher than initially estimated)
- Breakdown: docs/htm (14,242), docs/new (70,601)
- Latest CSV reports:
  - docs/htm: `/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_htm_20250923_195045.csv`
  - docs/new: `/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_new_20250923_195146.csv`

## Task Description
Remove Microsoft Word temporary file references

**Estimated fixes**: 50 broken links
**Priority**: 6

## Implementation Requirements

### Step 1: Create the Script
Create the script `PRPs/scripts/remove-word-artifacts.py` based on the requirements below.
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

### Step 6: Git Commit Changes
After user validation, commit all changes to git:
- Add all modified files to git staging
- Create a descriptive commit message summarizing the fixes applied
- Commit the changes to preserve the work

### Step 7: Report Results
Provide a summary of:
- Number of files modified in docs/htm
- Number of files modified in docs/new
- Total number of fixes applied across both directories
- Any issues encountered
- Representative test URLs provided to user (in localhost format)

## Script-Specific Requirements

**For remove-word-artifacts.py:**

### Word Artifact Cleanup (remove-word-artifacts.py)
- Remove Microsoft Word temporary file references
- Target patterns:
  - `Walter_files/*.mso`
  - `JohnII_files/*.xml`
  - Various `.gif` files in Word temp directories
- Clean up `_files/` directory references
- Focus on removing broken links to non-existent Word temporary files

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