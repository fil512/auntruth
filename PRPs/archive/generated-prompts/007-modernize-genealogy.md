# Modernize Genealogy Site Task: create-modern-index

## ⚠️ CRITICAL WARNING ⚠️
This repository contains ~11,000 HTML files in nested directories.
**DO NOT start editing files until you have:**
1. Searched ALL subdirectories recursively
2. Counted the EXACT number of affected files
3. Selected the appropriate tool for that scale

**Starting edits without complete analysis = TASK FAILURE**

## Task Overview
**Item:** 007
**Task:** create-modern-index
**Description:** Replace main index.html with cleaner version

## Background Context
This is part of modernizing a genealogy website (AuntieRuth.com) for GitHub Pages. The site contains ~11,000 HTML files with family history data from 2002-2005 that need to be updated for modern web standards and GitHub Pages compatibility.

## Current Issue
Replace main index.html with cleaner version

## Target Directory
Work in: `docs`

## Search Pattern
Look for: `index.html`

## MANDATORY SCOPE ANALYSIS (DO NOT SKIP)

### STOP! Complete this analysis before proceeding:
1. **Search ALL subdirectories recursively** - Use Grep with count mode: `index.html` in `docs`
2. **Document the exact count** of files affected
3. **Document the total occurrences** across all files
4. **List all affected directories** to understand the scope
5. **ONLY THEN** proceed to tool selection

⚠️ **WARNING**: Starting file edits before completing scope analysis will result in task failure.

### Required Analysis Commands
```bash
# Count files containing the pattern
grep -r "index.html" docs --include="*.htm" --include="*.html" -l | wc -l

# Count total occurrences
grep -r "index.html" docs --include="*.htm" --include="*.html" -c

# List affected files for verification
grep -r "index.html" docs --include="*.htm" --include="*.html" -l
```

## Tool Selection Guide (MANDATORY CHECK)

### FIRST: Check Existing Scripts
**ALWAYS READ** `PRPs/scripts/README.md` first to check for existing scripts that can handle this task.

### Tool Selection Decision Gate

**After scope analysis, select your approach:**

| File Count | Required Approach | Why |
|------------|------------------|-----|
| 1-9 files | Edit/MultiEdit directly | Small enough for manual handling |
| 10-99 files | MultiEdit with validation | Medium scale needs careful batching |
| 100-999 files | Python script (MANDATORY) | Too many for manual, needs automation |
| 1000+ files | Phased Python script with checkpoints | Massive scale needs incremental approach |

⚠️ **CRITICAL**: If you have >100 files and start using Edit/MultiEdit, you are doing it WRONG!

### Script Requirements (For >100 files)
When creating or using scripts for mass operations:
1. **Store in PRPs/scripts/** directory
2. **Update PRPs/scripts/README.md** with script documentation
3. **Use git branches for safety** (no file backups needed)
4. **Implement dry-run mode** with sample output
5. **Progress reporting** every 100 files
6. **Error logging and recovery**
7. **Test on 5 sample files first**

## Pre-Execution Checklist (MANDATORY)

**Before making ANY file changes, confirm:**
- [ ] I have verified I'm working in the correct git branch: `task-007-create-modern-index`
- [ ] I have checked that tracking shows this task as "IN PROGRESS"
- [ ] I have searched ALL subdirectories recursively using Grep
- [ ] I have counted the TOTAL number of affected files: ___ files
- [ ] I have counted the TOTAL occurrences: ___ occurrences
- [ ] I have selected the appropriate tool based on file count from the decision gate
- [ ] If >100 files, I have created/found a Python script in PRPs/scripts/

⚠️ **DO NOT PROCEED if any checkbox is unchecked!**

## Your Task

**Note: The parent workflow has already created the git branch and updated tracking. You are working in an existing branch.**

1. **Verify setup**: Confirm you're in branch `task-007-create-modern-index` and tracking shows "IN PROGRESS"
2. **Check existing scripts**: Read PRPs/scripts/README.md to see if suitable script exists
3. **MANDATORY SCOPE ANALYSIS**: Complete the analysis section above - count ALL affected files recursively
4. **Determine scale**: Use the file count to select appropriate tool from decision gate
5. **Complete checklist**: Fill out the pre-execution checklist above
6. **Plan the changes**: Create a strategy for fixing these instances (script vs manual)
7. **Implement fixes**: Use appropriate tool based on file count and safety requirements
8. **Verify results**: Ensure changes work correctly and don't break functionality
9. **Commit changes**: Commit all changes with descriptive message
10. **Update documentation**: If new script created, update PRPs/scripts/README.md
11. **Report findings**: Document what was changed and any issues encountered

## Batch Processing Approach (For >100 files)
When modifying many files, create a Python script with these components:

```python
#!/usr/bin/env python3
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

def verify_git_branch(expected_branch):
    """Verify we're working in the correct branch"""
    import subprocess
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
    return current_branch

def process_files_batch(target_dir, pattern, replacement, dry_run=True):
    """Process files with safety measures"""
    affected_files = []

    # Find all matching files
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if pattern in content:
                        affected_files.append(file_path)

    print(f"Found {len(affected_files)} files to process")

    if dry_run:
        print("DRY RUN - showing first 10 files that would be changed:")
        for file_path in affected_files[:10]:
            print(f"  {file_path}")
        return affected_files

    # Process files (git provides backup via branches)
    processed = 0

    for file_path in affected_files:

        # Process file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content = content.replace(pattern, replacement)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        processed += 1
        if processed % 100 == 0:
            print(f"Processed {processed}/{len(affected_files)} files...")

    print(f"Completed processing {processed} files")
    print(f"Changes made in git branch - ready for commit")
    return affected_files
```

## Safety Requirements for Mass Changes
1. **Pre-execution Safety**
   - **MANDATORY**: Read PRPs/scripts/README.md for existing solutions
   - **MANDATORY**: Create git feature branch before starting
   - Run in test mode first (dry-run showing first 10 files that would be changed)
   - Generate change report before executing
   - **MANDATORY**: Test on sample subset first (e.g., 5 files) if >100 files affected
   - Verify git workflow with test commit

2. **During Execution**
   - Progress reporting every 100 files
   - Error logging for any files that fail to process
   - Commit changes incrementally (every 500 files for large operations)
   - Git provides automatic change tracking

3. **Post-execution Verification**
   - Sample verification: Test 5-10 modified files manually
   - Automated validation: Check for broken links, valid HTML
   - Git diff report: Generate summary of all changes made
   - Commit all changes with descriptive message

## Execution Phases for Large-Scale Changes

### Phase 1: Analysis & Planning
- **FIRST**: Read PRPs/scripts/README.md for existing scripts
- Count affected files using Grep tool
- Identify edge cases and special patterns
- Create test plan for verification
- Choose appropriate tool based on file count
- If creating new script, plan to update PRPs/scripts/README.md

### Phase 2: Test Run (if >100 files)
- Process 5 sample files manually or with script in dry-run mode
- Verify changes work correctly
- Check for unexpected side effects
- Adjust approach if needed

### Phase 3: Full Execution
- Run with progress tracking
- Log all changes and any errors
- Commit changes incrementally as rollback points
- Monitor for issues during execution

### Phase 4: Verification
- Spot-check results on random sample of files
- Run automated validation if possible
- Document any issues found
- Create summary report

## Specific Requirements
- Maintain backward compatibility where possible
- Ensure all paths work correctly on GitHub Pages (case-sensitive, static hosting)
- Remove any server-side dependencies (CGI, Java applets, etc.)
- Use modern web standards (UTF-8, proper DOCTYPE, etc.)
- Keep the genealogical content and structure intact

## Success Criteria
- All instances of `index.html` are properly addressed
- No broken links or missing resources
- Changes are compatible with GitHub Pages static hosting
- HTML remains valid and functional
- Git branch created and changes committed

## Report Format
At the end, provide:
1. **Branch Verification**: Confirm you worked in the correct branch and tracking was IN PROGRESS
2. **Script Check**: Confirm you read PRPs/scripts/README.md and note any existing scripts used
3. **Files Modified**: List of all files changed (or count if >50)
4. **Changes Made**: Summary of what was fixed
5. **Tool Used**: Edit/MultiEdit/Python script based on scale
6. **Issues Found**: Any problems encountered
7. **Verification**: How you tested the changes
8. **Git Branch**: Confirm branch name used
9. **Script Documentation**: If new script created, confirm PRPs/scripts/README.md updated
10. **Rollback Instructions**: Git commands to revert changes if needed
11. **Recommendations**: Any follow-up actions needed