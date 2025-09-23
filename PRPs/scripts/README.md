# PRPs Scripts Documentation

## Overview
This directory contains scripts for handling mass file operations during the genealogy site modernization project. All scripts are designed with safety protocols for handling thousands of files.

## CRITICAL: Scope Analysis Before Tool Selection

### Why This Matters
With 11,000+ files in this repository, assuming "just a few files" is DANGEROUS.
A pattern that seems rare might appear in thousands of files across subdirectories.

### Mandatory Analysis Process
1. **Never assume** - Always count first using recursive search
2. **Search recursively** - Patterns may be in nested folders (docs/htm has many subdirectories)
3. **Use grep count mode** - Get exact numbers before deciding on tools
4. **Document findings** - Report file count before starting work
5. **Follow decision gate** - Use the tool selection table based on actual file counts

### Red Flags (Stop if you see these)
- Starting to edit files without knowing the total count
- Using Edit/MultiEdit for more than 10 files
- Not checking subdirectories with recursive search
- Assuming a pattern is rare without verification
- Skipping the mandatory scope analysis section

### Proper Scope Analysis Commands
```bash
# Count files containing pattern (most important)
grep -r "PATTERN" TARGET_DIR --include="*.htm" --include="*.html" -l | wc -l

# Count total occurrences
grep -r "PATTERN" TARGET_DIR --include="*.htm" --include="*.html" -c

# List affected files for verification
grep -r "PATTERN" TARGET_DIR --include="*.htm" --include="*.html" -l
```

## Available Scripts

### 001-fix-path-format.py
**Purpose:** Task 001 - Fix absolute paths and path format issues
**Usage:** `python3 001-fix-path-format.py`
**Features:**
- Replaces \auntruth\htm\ with relative paths
- Converts /AuntRuth/ absolute paths to relative paths
- Converts Windows backslashes to Unix forward slashes
- Fixes case sensitivity issues (l0-l9 to L0-L9)
- Progress reporting and error handling

### 002-complete-auntruuth-fix.py
**Purpose:** Task 002 - Complete /AuntRuth/ path fixing
**Usage:** `python3 002-complete-auntruuth-fix.py`
**Features:**
- Handles remaining /AuntRuth/ patterns
- Fixes /AuntRuth/index.htm -> /index.htm
- Progress reporting every 100 files
- Error logging and recovery

### 002-final-auntruuth-cleanup.py
**Purpose:** Task 002 - Final cleanup for remaining /AuntRuth/ references
**Usage:** `python3 002-final-auntruuth-cleanup.py`
**Features:**
- Handles .HTM files (uppercase)
- Fixes CSS references that were missed
- Final cleanup for all /AuntRuth/ patterns

### 003-remove-cgi-counters.py
**Purpose:** Task 003 - Remove CGI counter script references
**Usage:** `python3 003-remove-cgi-counters.py [--dry-run] [--target-dir docs/htm]`
**Features:**
- Removes all /cgi-bin/counter.pl references from HTML files
- GitHub Pages compatibility (CGI scripts don't work in static hosting)
- Processed 1,517 files with regex pattern matching
- Progress reporting every 100 files
- Dry-run mode with sample preview
- Test mode for sample file verification

### 004-modernize-java-applets.py
**Purpose:** Task 004 - Modernize Java applet sound players to HTML5 audio
**Usage:** `python3 004-modernize-java-applets.py [--dry-run] [--target-dir docs/htm]`
**Features:**
- Replaces Java applet sound players with HTML5 audio elements
- Converts `<APPLET CODE='hcslsond.class'>` to `<audio controls>` tags
- Preserves all .au audio files in their original location
- Modern browser compatibility without Java dependencies
- GitHub Pages compatible (no Java applet support needed)
- Processed 12 files with specific Java applet patterns
- Progress reporting and error handling
- Dry-run mode with sample preview

### 007-modernize-index-references.py
**Purpose:** Task 007 - Fix broken index.htm references for GitHub Pages
**Usage:** `python3 007-modernize-index-references.py [--dry-run] [--execute] [--test-mode] [--validate]`
**Features:**
- Fixes ~5,225 files with broken `\AuntRuth\index.htm` references
- Converts Windows-style absolute paths to proper relative paths
- Calculates correct relative paths for each file's location
- GitHub Pages compatible static hosting paths
- Phased execution with checkpoint commits every 500 files
- Progress reporting every 100 files
- Comprehensive error logging and recovery
- Dry-run mode with detailed preview of changes
- Test mode for processing only 5 files first
- Post-execution validation of changes
- Handles massive scale (>5000 files) with safety protocols

### 011-add-doctype.py
**Purpose:** Task 011 - Add DOCTYPE declarations to HTML files for modern web standards
**Usage:** `python3 011-add-doctype.py [--dry-run] [--test-mode] [--execute] [--yes] [--validate]`
**Features:**
- Adds HTML5 DOCTYPE declarations to ~11,000 HTML files
- GitHub Pages compatible modern web standards
- Phased execution with checkpoint commits every 500 files
- Processed 11,065 files (5 already had DOCTYPE declarations)
- Progress reporting every 100 files
- Comprehensive error logging and recovery
- Dry-run mode with detailed preview of changes
- Test mode for processing only 5 files first
- Auto-confirmation mode for non-interactive environments
- Post-execution validation of changes
- Handles massive scale (>11,000 files) with full safety protocols

### 010-convert-to-utf8.py
**Purpose:** Task 010 - Convert Windows-1252 encoded files to UTF-8
**Usage:** `python3 010-convert-to-utf8.py [dry-run|execute|validate]`
**Features:**
- Converts Windows-1252 encoded characters to proper Unicode (fixes garbled characters)
- Updates charset declarations from windows-1252 to utf-8
- Handles smart quotes, copyright symbols, and other special characters
- Fixes specific garbled text patterns (e.g., "China�" → "China"")
- GitHub Pages compatible UTF-8 encoding
- Processes 23+ files with charset issues
- Multiple execution modes (dry-run, execute, validate)
- Character-level conversion with Windows-1252 to Unicode mapping
- Progress reporting and comprehensive error handling

### fix-github-pages-paths.py
**Purpose:** General GitHub Pages path compatibility fixes
**Usage:** `python3 fix-github-pages-paths.py`
**Features:**
- GitHub Pages specific path corrections
- Case sensitivity fixes for static hosting

### test-fix-paths.py
**Purpose:** Testing script for path fixes
**Usage:** `python3 test-fix-paths.py`
**Features:**
- Test path correction logic
- Validation of changes

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
1. Copy an existing task script (e.g., 001-fix-path-format.py) as template
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
See `001-fix-path-format.py` for the standard template that includes:
- Argument parsing with required safety flags
- Git branch verification
- Progress reporting and error handling
- Dry-run and sample testing capabilities
- Rollback instructions generation

### Task-Specific Templates
- **001-fix-path-format.py**: Comprehensive path format fixes
- **002-complete-auntruuth-fix.py**: Specific pattern replacements
- **002-final-auntruuth-cleanup.py**: Final cleanup operations

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