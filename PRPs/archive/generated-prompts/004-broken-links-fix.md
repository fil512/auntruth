# Broken Links Fix - create-missing-indexes.py

## Background
This is part of the systematic broken links fix plan for AuntieRuth.com genealogy website. You are working on item 004 of 6 total fixes.

**Current Status (2025-09-23 19:50):**
- Total broken links across both sites: 84,844 (much higher than initially estimated)
- Breakdown: docs/htm (14,242), docs/new (70,601)
- Latest CSV reports:
  - docs/htm: `/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_htm_20250923_195045.csv`
  - docs/new: `/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_new_20250923_195146.csv`

## Task Description
Create missing L0-L9 index.htm files

**Estimated fixes**: 10 broken links
**Priority**: 4

## Implementation Requirements

### Step 1: Create the Script
Create the script `PRPs/scripts/create-missing-indexes.py` based on the requirements below.
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

**For create-missing-indexes.py:**

### XF0.htm Link Removal (remove-xf0-links.py)
- Remove anchor tags pointing to XF0.htm
- Preserve any content inside the anchor tags
- Pattern: `<a href="*/XF0.htm">content</a>` → `content`
- Focus on L2 directory files (heavy XF0 references)

### Backslash Path Fixes (fix-backslash-paths.py)
- Convert backslash paths to forward slashes
- Fix patterns like `./L0\XF0.htm` → `./L0/XF0.htm`
- Handle double htm paths: `/htm/htm/` → `/htm/`
- Focus on modernized site (`docs/new/`) with more backslash issues

### CGI Counter Removal (remove-cgi-counters.py)
- Remove obsolete CGI counter references
- Target patterns:
  - `\cgi-bin\counter.pl?AuntRuth` (741 instances)
  - `\AuntRuth\cgi-bin\counter.pl` (56 instances)
- Focus on L6 directory files (heavy counter references)

### Missing Index Creation (create-missing-indexes.py)
- Create index.htm files for lineages L0-L9 if missing
- Basic navigation structure pointing to main lineage files
- Investigate XF533.htm references and handle appropriately

### XI Lineage Reference Fixes (fix-xi-lineage-refs.py)
- Update XI references to correct lineage directories
- Key mappings:
  - XI2627.htm in L1 → L4/XF2627.htm
  - Similar misplaced XI references
- Check both original and modernized sites

### Word Artifact Cleanup (remove-word-artifacts.py)
- Remove Microsoft Word temporary file references
- Target patterns:
  - `Walter_files/*.mso`
  - `JohnII_files/*.xml`
  - Various `.gif` files in Word temp directories
- Clean up `_files/` directory references

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