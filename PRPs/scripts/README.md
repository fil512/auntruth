# PRPs Scripts Documentation

## Overview
This directory contains scripts for handling mass file operations during the genealogy site modernization project. All scripts are designed with safety protocols for handling thousands of files.

## Directory Organization
Scripts are organized into subdirectories based on which documentation they target:

- **`htm/`** - Scripts that work exclusively with `docs/htm` directory
- **`new/`** - Scripts that work exclusively with `docs/new` directory
- **`both/`** - Scripts that can work with either directory or provide options for both

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

## HTM Directory Scripts (`htm/`)
These scripts work exclusively with the `docs/htm` directory:

### htm/001-fix-path-format.py
**Purpose:** Task 001 - Fix absolute paths and path format issues
**Usage:** `python3 htm/001-fix-path-format.py`
**Features:**
- Replaces \auntruth\htm\ with relative paths
- Converts /AuntRuth/ absolute paths to relative paths
- Converts Windows backslashes to Unix forward slashes
- Fixes case sensitivity issues (l0-l9 to L0-L9)
- Progress reporting and error handling

### htm/002-complete-auntruuth-fix.py
**Purpose:** Task 002 - Complete /AuntRuth/ path fixing
**Usage:** `python3 htm/002-complete-auntruuth-fix.py`
**Features:**
- Handles remaining /AuntRuth/ patterns
- Fixes /AuntRuth/index.htm -> /index.htm
- Progress reporting every 100 files
- Error logging and recovery

### htm/002-final-auntruuth-cleanup.py
**Purpose:** Task 002 - Final cleanup for remaining /AuntRuth/ references
**Usage:** `python3 htm/002-final-auntruuth-cleanup.py`
**Features:**
- Handles .HTM files (uppercase)
- Fixes CSS references that were missed
- Final cleanup for all /AuntRuth/ patterns

### htm/003-remove-cgi-counters.py
**Purpose:** Task 003 - Remove CGI counter script references
**Usage:** `python3 htm/003-remove-cgi-counters.py [--dry-run] [--target-dir docs/htm]`
**Features:**
- Removes all /cgi-bin/counter.pl references from HTML files
- GitHub Pages compatibility (CGI scripts don't work in static hosting)
- Processed 1,517 files with regex pattern matching
- Progress reporting every 100 files
- Dry-run mode with sample preview
- Test mode for sample file verification

### htm/004-modernize-java-applets.py
**Purpose:** Task 004 - Modernize Java applet sound players to HTML5 audio
**Usage:** `python3 htm/004-modernize-java-applets.py [--dry-run] [--target-dir docs/htm]`
**Features:**
- Replaces Java applet sound players with HTML5 audio elements
- Converts `<APPLET CODE='hcslsond.class'>` to `<audio controls>` tags
- Preserves all .au audio files in their original location
- Modern browser compatibility without Java dependencies
- GitHub Pages compatible (no Java applet support needed)
- Processed 12 files with specific Java applet patterns
- Progress reporting and error handling
- Dry-run mode with sample preview

### htm/011-add-doctype.py
**Purpose:** Task 011 - Add DOCTYPE declarations to HTML files for modern web standards
**Usage:** `python3 htm/011-add-doctype.py [--dry-run] [--test-mode] [--execute] [--yes] [--validate]`
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

### htm/012-validate-case-sensitivity.py
**Purpose:** Task 012 - Validate case sensitivity and path resolution issues
**Usage:** `python3 htm/012-validate-case-sensitivity.py [--target-dir docs/htm] [--detailed]`
**Features:**
- Scans all 11,361 HTML files for internal links (404,678 total links found)
- Validates link resolution and case sensitivity for GitHub Pages
- **CRITICAL FINDING**: Discovered 398,380 broken links (not just case issues!)
- Identifies remaining Windows paths (\AuntRuth\), missing CSS files, incorrect absolute paths
- Shows this is not just case sensitivity but fundamental path resolution problems
- Provides detailed reporting with sample issues and validation summary
- **Status**: Task 012 requires major fixes beyond case sensitivity

### htm/014-add-mobile-css.py
**Purpose:** Task 014 - Add mobile-responsive CSS and fix CSS path references
**Usage:** `python3 htm/014-add-mobile-css.py [--dry-run] [--test-mode] [--execute] [--yes] [--validate]`
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

### htm/fix-audio-absolute-paths.py
**Purpose:** Fix audio file absolute paths in HTML files
**Usage:** `python3 htm/fix-audio-absolute-paths.py`
**Features:**
- Modernizes CSS with mobile-responsive design patterns
- Fixes ~10,183 HTML files with broken `/auntruth/css/htm.css` absolute paths
- Calculates correct relative CSS paths for each file's directory depth
- GitHub Pages compatible relative path references
- Adds comprehensive mobile breakpoints (768px, 480px)
- Touch-friendly interface improvements for mobile devices
- Responsive table layouts and image scaling
- Phased execution with checkpoint commits every 500 files
- Progress reporting every 100 files
- Comprehensive error logging and recovery
- Dry-run mode with detailed preview of changes
- Test mode for processing 5 sample files first
- Auto-confirmation mode for non-interactive environments
- Post-execution validation of changes
- Handles massive scale (>10,000 files) with full safety protocols
- Mobile-first CSS with desktop fallbacks
- Improved typography and spacing for mobile readability

### htm/fix-audio-paths.py
**Purpose:** Fix audio file path references in HTML files
**Usage:** `python3 htm/fix-audio-paths.py`

### htm/fix-backslash-paths.py
**Purpose:** Convert Windows backslash paths to forward slashes
**Usage:** `python3 htm/fix-backslash-paths.py`

### htm/fix-github-pages-paths.py
**Purpose:** General GitHub Pages path compatibility fixes
**Usage:** `python3 htm/fix-github-pages-paths.py`

### htm/fix-xi-lineage-refs.py
**Purpose:** Fix Xi lineage reference links
**Usage:** `python3 htm/fix-xi-lineage-refs.py`

### htm/remove-cgi-counters.py
**Purpose:** Remove CGI counter references (duplicate of 003)
**Usage:** `python3 htm/remove-cgi-counters.py`

### htm/remove-word-artifacts.py
**Purpose:** Remove Microsoft Word HTML artifacts
**Usage:** `python3 htm/remove-word-artifacts.py`

### htm/remove-xf0-links.py
**Purpose:** Remove invalid xf0 link references
**Usage:** `python3 htm/remove-xf0-links.py`

### htm/test-fix-paths.py
**Purpose:** Testing script for path fixes
**Usage:** `python3 htm/test-fix-paths.py`

### htm/update-audio-to-mp3.py
**Purpose:** Update audio references from .au to .mp3 format
**Usage:** `python3 htm/update-audio-to-mp3.py`

## NEW Directory Scripts (`new/`)
These scripts work exclusively with the `docs/new` directory:

### new/fix_carousel_navigation.py
**Purpose:** Fix carousel navigation functionality
**Usage:** `python3 new/fix_carousel_navigation.py`

### new/fix_gallery_json.py
**Purpose:** Fix gallery JSON data structures
**Usage:** `python3 new/fix_gallery_json.py`

### new/fix_missing_carousel_css.py
**Purpose:** Add missing CSS for carousel components
**Usage:** `python3 new/fix_missing_carousel_css.py`

### new/fix_onclick_syntax.py
**Purpose:** Fix onclick JavaScript syntax issues
**Usage:** `python3 new/fix_onclick_syntax.py`

### new/fix_thumbnails.py
**Purpose:** Fix thumbnail image references and paths
**Usage:** `python3 new/fix_thumbnails.py`

### new/generate_search_index.py
**Purpose:** Generate search index for site content
**Usage:** `python3 new/generate_search_index.py`
**Output:** `docs/new/js/data.json`

### new/modernize_image_pages.py
**Purpose:** Modernize image gallery pages
**Usage:** `python3 new/modernize_image_pages.py`

### new/update_carousel_css.py
**Purpose:** Update carousel CSS styling
**Usage:** `python3 new/update_carousel_css.py`

### new/update_navigation.py
**Purpose:** Update navigation system and injection
**Usage:** `python3 new/update_navigation.py`

## Multi-Directory Scripts (`both/`)
These scripts can work with either directory or provide options for both:

### both/normalize-file-extensions.py
**Purpose:** Normalize all file extensions to lowercase across the entire site
**Usage:** `python3 both/normalize-file-extensions.py [--target-dir docs] [--dry-run] [--files-only] [--refs-only] [--limit N]`
**Features:**
- Renames files with uppercase extensions (.HTM→.htm, .JPG→.jpg, etc.)
- Updates all internal references in HTML/CSS/JS files to use lowercase extensions
- Handles file collisions by keeping newer files and deleting older duplicates
- Comprehensive collision reporting saved to PRPs/scripts/reports/
- Supports all common web file extensions (HTM, HTML, JPG, JPEG, PNG, CSS, JS, etc.)
- Safe processing with git-based rollback capability
- Progress reporting every 100 files for large operations
- Dry-run mode for testing before execution
- Can process files-only, references-only, or both
- Collision resolution strategy: keep newer file, delete older file
- Generated collision reports include timestamps, file sizes, and decisions made
- Processed 135 JPG files and 1,711+ extension references successfully

### both/007-modernize-index-references.py
**Purpose:** Task 007 - Fix broken index.htm references for GitHub Pages
**Usage:** `python3 both/007-modernize-index-references.py [--dry-run] [--execute] [--test-mode] [--validate]`
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

### both/010-convert-to-utf8.py
**Purpose:** Task 010 - Convert Windows-1252 encoded files to UTF-8
**Usage:** `python3 both/010-convert-to-utf8.py [dry-run|execute|validate]`
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

### both/012-fix-all-home-links.py
**Purpose:** Fix all home page link references
**Usage:** `python3 both/012-fix-all-home-links.py`

### both/012-fix-home-links-correct.py
**Purpose:** Correct home page link fixes
**Usage:** `python3 both/012-fix-home-links-correct.py`

### both/analyze-remaining-links.py
**Purpose:** Analyze remaining broken links
**Usage:** `python3 both/analyze-remaining-links.py`

### both/check-image-case.py
**Purpose:** Check image file case sensitivity issues
**Usage:** `python3 both/check-image-case.py`

### both/comprehensive_html_cleanup.py
**Purpose:** Comprehensive HTML structure cleanup
**Usage:** `python3 both/comprehensive_html_cleanup.py`

### both/convert-au-to-mp3.py
**Purpose:** Convert .au audio files to .mp3 format
**Usage:** `python3 both/convert-au-to-mp3.py`

### both/find-broken-links.py
**Purpose:** Find all broken links in the site
**Usage:** `python3 both/find-broken-links.py [--site=htm|new|both] [--timeout=5]`
**Features:**
- Finds all broken links in the AuntieRuth.com genealogy site
- Ensures each URL is only checked once and provides progress feedback
- Can target htm, new, or both directories

### both/fix_duplicate_scripts.py
**Purpose:** Remove duplicate script references
**Usage:** `python3 both/fix_duplicate_scripts.py`

### both/fix_missing_css.py
**Purpose:** Add missing CSS file references
**Usage:** `python3 both/fix_missing_css.py`

### both/fix_navigation_injection.py
**Purpose:** Fix navigation injection system
**Usage:** `python3 both/fix_navigation_injection.py`

### both/fix_nested_main_tags.py
**Purpose:** Fix nested main tag issues
**Usage:** `python3 both/fix_nested_main_tags.py`

### both/linkchecker.py
**Purpose:** Comprehensive link validation tool
**Usage:** `python3 both/linkchecker.py`

### both/quick-linkcheck.py
**Purpose:** Quick link validation check
**Usage:** `python3 both/quick-linkcheck.py`

### both/remove_duplicates.py
**Purpose:** Remove duplicate content and files
**Usage:** `python3 both/remove_duplicates.py`

### both/validate_navigation.py
**Purpose:** Validate navigation system functionality
**Usage:** `python3 both/validate_navigation.py`

### both/analyze-broken-links.py
**Purpose:** Comprehensive pattern analysis of broken link reports
**Usage:** `python3 both/analyze-broken-links.py [--htm-report path] [--new-report path]`
**Features:**
- Analyzes broken link CSV reports to identify systematic patterns
- Discovers fixable patterns: wrong lineage paths (XF533.htm in L1→L9), case sensitivity, malformed URLs
- Provides priority recommendations based on impact analysis
- Found 7,953+ potential fixes across both sites through pattern detection

### both/fix-wrong-lineage-paths.py
**Purpose:** Fix references to files in wrong lineage directories
**Usage:** `python3 both/fix-wrong-lineage-paths.py --directory docs [--execute] [--validate]`
**Features:**
- Fixes XF533.htm references (L1→L9): 1,228+ fixes
- Fixes IMAGES.htm references (L0→L2): 49+ fixes
- Fixes EVERYONE.htm references (various→L0): 8+ fixes
- Curl validation of fixes before/after
- High impact, low risk systematic corrections

### both/fix-case-sensitivity.py
**Purpose:** Fix case sensitivity issues in HTML file references
**Usage:** `python3 both/fix-case-sensitivity.py --directory docs [--execute] [--validate]`
**Features:**
- Fixes INDEX.htm → index.htm case issues: 138+ fixes
- Handles INDEX6.htm, INDEX9.htm patterns
- GitHub Pages case-sensitive hosting compatibility
- Curl validation testing for broken→working URL transitions

### both/fix-malformed-spaces.py
**Purpose:** Fix malformed URLs containing space characters
**Usage:** `python3 both/fix-malformed-spaces.py --directory docs [--execute] [--validate]`
**Features:**
- Fixes URLs like "/auntruth/jpg/ .jpg" and "/auntruth/jpg/ sn206.jpg"
- Removes problematic spaces causing connection failures: 10+ fixes
- Converts malformed URLs to proper format for web servers

### both/fix-relative-paths.py
**Purpose:** Convert relative paths to absolute paths for proper resolution
**Usage:** `python3 both/fix-relative-paths.py --directory docs [--execute] [--limit N]`
**Features:**
- Largest impact potential: 6,577+ fixes for relative path issues
- Converts "L1/XF178.htm" → "/auntruth/new/L1/XF178.htm"
- Fixes "../htm/file.htm" and "../jpg/file.jpg" patterns
- Context-aware absolute path generation based on site structure
- Handles massive scale with sample testing options

### both/fix-broken-links-comprehensive.py
**Purpose:** Master script coordinating all broken link fixes in optimal order
**Usage:** `python3 both/fix-broken-links-comprehensive.py [--execute] [--htm-only] [--new-only]`
**Features:**
- Orchestrates all fix scripts in strategic order: lineage→case→spaces→relative
- Total potential impact: 7,953+ broken link fixes across both sites
- Pre/post analysis with broken link counting
- Coordinated execution with progress tracking and error reporting
- Safety protocols with dry-run testing of all component scripts

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
1. Copy an existing task script (e.g., htm/001-fix-path-format.py) as template
2. Modify for specific task requirements
3. Test on 5 sample files first
4. Run dry-run to verify scope
5. Execute with full safety protocols
6. Place in appropriate subdirectory (htm/, new/, or both/)
7. Update this README with new script documentation

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
See `htm/001-fix-path-format.py` for the standard template that includes:
- Argument parsing with required safety flags
- Git branch verification
- Progress reporting and error handling
- Dry-run and sample testing capabilities
- Rollback instructions generation

### Task-Specific Templates
- **htm/001-fix-path-format.py**: Comprehensive path format fixes
- **htm/002-complete-auntruuth-fix.py**: Specific pattern replacements
- **htm/002-final-auntruuth-cleanup.py**: Final cleanup operations

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