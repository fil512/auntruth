# Modernize Genealogy Site Task: fix-absolute-paths

## Task Overview
**Item:** 001
**Task:** fix-absolute-paths
**Description:** Replace Windows-style and absolute paths with relative paths

## Background Context
This is part of modernizing a genealogy website (AuntieRuth.com) for GitHub Pages. The site contains ~11,000 HTML files with family history data from 2002-2005 that need to be updated for modern web standards and GitHub Pages compatibility.

## Current Issue
Replace Windows-style and absolute paths with relative paths

## Target Directory
Work in: `docs/htm`

## Search Pattern
Look for: `\\auntruth\\htm\\`

## Tool Selection Guide
- **For <10 files**: Use Edit/MultiEdit tools
- **For 10-100 files**: Use MultiEdit with batching
- **For >100 files**: Use Python script with proper safeguards
- **For >1000 files**: Mandatory dry-run and phased execution

## Your Task
1. **Analyze the scope**: Search for all instances of the pattern `\\auntruth\\htm\\` in `docs/htm`
2. **Determine scale**: Count affected files to select appropriate tool/method
3. **Plan the changes**: Create a strategy for fixing these instances
4. **Implement fixes**: Use appropriate tool based on file count
5. **Verify results**: Ensure changes work correctly and don't break functionality
6. **Report findings**: Document what was changed and any issues encountered

## Batch Processing Approach (For >100 files)
When modifying many files, create a Python script with these components:

```python
#!/usr/bin/env python3
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

def create_backup_dir():
    """Create timestamped backup directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/modernize_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

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

    # Create backup and process files
    backup_dir = create_backup_dir()
    processed = 0

    for file_path in affected_files:
        # Create backup
        rel_path = os.path.relpath(file_path, target_dir)
        backup_path = os.path.join(backup_dir, rel_path)
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(file_path, backup_path)

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
    print(f"Backup created at: {backup_dir}")
    return affected_files, backup_dir
```

## Safety Requirements for Mass Changes
1. **Pre-execution Safety**
   - Create timestamped backup directory before starting
   - Run in test mode first (dry-run showing first 10 files that would be changed)
   - Generate change report before executing
   - Test on sample subset first (e.g., 5 files) if >100 files affected

2. **During Execution**
   - Progress reporting every 100 files
   - Error logging for any files that fail to process
   - Immediate backup of each file before modification
   - Transaction logging for rollback capability

3. **Post-execution Verification**
   - Sample verification: Test 5-10 modified files manually
   - Automated validation: Check for broken links, valid HTML
   - Diff report: Generate summary of all changes made
   - Rollback testing: Verify backup restoration works

## Execution Phases for Large-Scale Changes

### Phase 1: Analysis & Planning
- Count affected files using Grep tool
- Identify edge cases and special patterns
- Create test plan for verification
- Choose appropriate tool based on file count

### Phase 2: Test Run (if >100 files)
- Process 5 sample files manually or with script in dry-run mode
- Verify changes work correctly
- Check for unexpected side effects
- Adjust approach if needed

### Phase 3: Full Execution
- Run with progress tracking
- Log all changes and any errors
- Create rollback point (backup directory)
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
- All instances of `\\auntruth\\htm\\` are properly addressed
- No broken links or missing resources
- Changes are compatible with GitHub Pages static hosting
- HTML remains valid and functional
- Backup created and rollback capability verified

## Report Format
At the end, provide:
1. **Files Modified**: List of all files changed (or count if >50)
2. **Changes Made**: Summary of what was fixed
3. **Tool Used**: Edit/MultiEdit/Python script based on scale
4. **Issues Found**: Any problems encountered
5. **Verification**: How you tested the changes
6. **Backup Location**: Path to backup directory (if created)
7. **Rollback Instructions**: How to undo changes if needed
8. **Recommendations**: Any follow-up actions needed