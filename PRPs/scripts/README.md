# PRPs Scripts Documentation

## Overview
This directory contains scripts for handling mass file operations during the genealogy site modernization project. All scripts are designed with safety protocols for handling thousands of files.

## Available Scripts

### mass_file_processor.py
**Purpose:** Template script for processing large numbers of HTML files safely
**Usage:** `python3 mass_file_processor.py --pattern "search" --replacement "replace" --target-dir "docs/htm" [--dry-run]`
**Features:**
- Automatic backup creation with timestamps
- Dry-run mode for testing
- Progress reporting every 100 files
- Error logging and recovery
- Rollback capability

### validate_changes.py
**Purpose:** Validates HTML files after mass changes
**Usage:** `python3 validate_changes.py --target-dir "docs/htm" [--sample-size 50]`
**Features:**
- HTML validation
- Link checking
- Sample-based verification
- Change reporting

## Script Standards

### Mandatory Features for All Scripts
1. **Git Branch Safety System**
   - Create feature branch before processing (e.g., `task-001-fix-absolute-paths`)
   - Work entirely within the feature branch
   - Commit changes incrementally with descriptive messages

2. **Dry-Run Mode**
   - Always implement `--dry-run` flag
   - Show first 10 affected files in dry-run
   - Report total count of files that would be changed

3. **Progress Reporting**
   - Report progress every 100 files processed
   - Show estimated time remaining for large operations
   - Log any errors encountered

4. **Error Handling**
   - Continue processing on individual file errors
   - Log all errors with file paths
   - Provide error summary at completion

5. **Safety Protocols**
   - Test on 5 sample files before full run
   - Verify changes don't break HTML structure
   - Use git commits as rollback points

### Required Script Arguments
- `--target-dir`: Directory to process
- `--dry-run`: Test mode flag
- `--branch-name`: Git branch name (auto-generated if not provided)
- `--log-file`: Optional custom log file location

### File Processing Standards
- Support UTF-8 encoding with error handling
- Process .html and .htm files only
- Preserve file timestamps and permissions
- Handle binary files gracefully (skip with warning)

## Usage Guidelines

### Before Creating New Scripts
1. **Check this README** - See if existing script can be modified
2. **Check file count** - Use grep/find to count affected files
3. **Plan approach** - Choose appropriate tool based on scale

### Scale-Based Tool Selection
- **<10 files**: Use Edit/MultiEdit tools directly
- **10-100 files**: Use MultiEdit with batching OR existing script
- **>100 files**: **MANDATORY** - Use Python script with full safety protocol
- **>1000 files**: Phased execution with checkpoints required

### Script Creation Process
1. Copy mass_file_processor.py as template
2. Modify for specific task requirements
3. Test on 5 sample files first
4. Run dry-run to verify scope
5. Execute with full safety protocols
6. Update this README with new script documentation

## Safety Checklist

### Pre-Execution (MANDATORY for >100 files)
- [ ] Create feature branch for the task
- [ ] Run dry-run and verify output
- [ ] Test on 5 sample files manually
- [ ] Commit test changes to verify git workflow
- [ ] Check git status is clean before starting

### During Execution
- [ ] Monitor progress output
- [ ] Check for error messages
- [ ] Verify expected file counts
- [ ] Watch for unexpected behavior

### Post-Execution
- [ ] Verify sample of changed files
- [ ] Check for broken links/references
- [ ] Commit all changes with descriptive message
- [ ] Document results and issues
- [ ] Push branch for review before merging

## Git Workflow Procedures

### Standard Git Workflow
```bash
# Create feature branch
git checkout -b task-001-fix-absolute-paths

# Make changes (via script or manually)
# ... processing files ...

# Stage and commit changes
git add .
git commit -m "Fix absolute paths: Replace \auntruth\htm\ with relative paths

- Processed X files in docs/htm/
- Replaced Windows-style paths with ./
- Verified changes don't break navigation"

# Push for review
git push -u origin task-001-fix-absolute-paths
```

### Rollback Procedures
```bash
# To undo last commit (keep changes as uncommitted)
git reset HEAD~1

# To completely revert to main branch state
git checkout main
git branch -D task-001-fix-absolute-paths

# To revert specific commit (creates new commit)
git revert <commit-hash>
```

## Script Templates

### Basic Mass File Processor Template
See `mass_file_processor.py` for the standard template that includes:
- Argument parsing with required safety flags
- Backup creation and verification
- Progress reporting and error handling
- Dry-run and sample testing capabilities
- Rollback instructions generation

### Validation Script Template
See `validate_changes.py` for HTML validation and verification

## Documentation Requirements

When adding a new script:
1. **Update this README** with script name, purpose, and usage
2. **Include inline documentation** in the script itself
3. **Provide usage examples** for common scenarios
4. **Document any limitations** or special considerations
5. **List any dependencies** required

## Contact and Support

For questions about scripts or to report issues:
- Check existing script documentation first
- Review safety protocols in this README
- Test thoroughly in dry-run mode before executing

---
*Last updated: 2025-09-22*
*Project: AuntieRuth.com Genealogy Site Modernization*