# Broken Links Fix - {{script_name}}

## Background
This is part of the systematic broken links fix plan for AuntieRuth.com genealogy website. You are working on item {{item_number}} of 6 total fixes.

## Task Description
{{description}}

**Estimated fixes**: {{estimated_fixes}} broken links
**Priority**: {{priority}}

## Implementation Requirements

### Step 1: Create the Script
Create the script `PRPs/scripts/{{script_name}}` based on the requirements below.

### Step 2: Test the Script (Dry Run)
Run the script in dry-run mode to show what changes would be made without actually modifying files.

### Step 3: Apply the Script
Run the script to apply the changes to the website files.

### Step 4: Select Test URLs
Select 3-5 representative URLs from the most affected files to test the changes. Provide these URLs to the user for validation.

### Step 5: MANDATORY User Validation
**CRITICAL**: You must WAIT for user validation before proceeding. The user must test the provided URLs and confirm no functionality is broken.

### Step 6: Report Results
Provide a summary of:
- Number of files modified
- Number of fixes applied
- Any issues encountered
- Representative test URLs provided to user

## Script-Specific Requirements

**For {{script_name}}:**

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
- NEVER proceed without user validation
- Select diverse test URLs from different affected areas
- Provide clear before/after examples where helpful
- If any issues are found during user testing, investigate and fix before proceeding