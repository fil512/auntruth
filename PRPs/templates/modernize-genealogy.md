# Modernize Genealogy Site Task: {{task_name}}

## Task Overview
**Item:** {{item_number}}
**Task:** {{task_name}}
**Description:** {{description}}

## Background Context
This is part of modernizing a genealogy website (AuntieRuth.com) for GitHub Pages. The site contains ~11,000 HTML files with family history data from 2002-2005 that need to be updated for modern web standards and GitHub Pages compatibility.

## Current Issue
{{description}}

## Target Directory
Work in: `{{target_directory}}`

## Search Pattern
Look for: `{{search_pattern}}`

## Tool Selection Guide (MANDATORY CHECK)

### FIRST: Check Existing Scripts
**ALWAYS READ** `PRPs/scripts/README.md` first to check for existing scripts that can handle this task.

### Scale-Based Tool Selection
- **For <10 files**: Use Edit/MultiEdit tools directly
- **For 10-100 files**: Use MultiEdit with batching OR existing script from PRPs/scripts/
- **For >100 files**: **MANDATORY** - Use Python script with full safety protocol
- **For >1000 files**: Phased execution with checkpoints required

### Script Requirements (For >100 files)
When creating or using scripts for mass operations:
1. **Store in PRPs/scripts/** directory
2. **Update PRPs/scripts/README.md** with script documentation
3. **Use git branches for safety** (no file backups needed)
4. **Implement dry-run mode** with sample output
5. **Progress reporting** every 100 files
6. **Error logging and recovery**
7. **Test on 5 sample files first**

## Your Task
1. **Create feature branch**: Create branch named `task-{{item_number}}-{{task_name}}`
2. **Check existing scripts**: Read PRPs/scripts/README.md to see if suitable script exists
3. **Analyze the scope**: Search for all instances of the pattern `{{search_pattern}}` in `{{target_directory}}`
4. **Determine scale**: Count affected files to select appropriate tool/method
5. **Plan the changes**: Create a strategy for fixing these instances (script vs manual)
6. **Implement fixes**: Use appropriate tool based on file count and safety requirements
7. **Verify results**: Ensure changes work correctly and don't break functionality
8. **Commit changes**: Commit all changes with descriptive message
9. **Update documentation**: If new script created, update PRPs/scripts/README.md
10. **Report findings**: Document what was changed and any issues encountered

## Batch Processing Approach (For >100 files)
When modifying many files, create a Python script with these components:

```python
#!/usr/bin/env python3
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

def create_git_branch(task_name):
    """Create feature branch for task"""
    import subprocess
    branch_name = f"task-{task_name}"
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    return branch_name

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
- All instances of `{{search_pattern}}` are properly addressed
- No broken links or missing resources
- Changes are compatible with GitHub Pages static hosting
- HTML remains valid and functional
- Git branch created and changes committed

## Report Format
At the end, provide:
1. **Script Check**: Confirm you read PRPs/scripts/README.md and note any existing scripts used
2. **Files Modified**: List of all files changed (or count if >50)
3. **Changes Made**: Summary of what was fixed
4. **Tool Used**: Edit/MultiEdit/Python script based on scale
5. **Issues Found**: Any problems encountered
6. **Verification**: How you tested the changes
7. **Git Branch**: Name of feature branch created
8. **Script Documentation**: If new script created, confirm PRPs/scripts/README.md updated
9. **Rollback Instructions**: Git commands to revert changes if needed
10. **Recommendations**: Any follow-up actions needed