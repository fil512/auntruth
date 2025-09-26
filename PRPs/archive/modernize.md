# GitHub Pages Modernization Plan for AuntieRuth.com

## Overview
This genealogy database was created with very old software (circa 2002-2005) and needs modernization to work properly on GitHub Pages. The site contains approximately 11,000 HTML files with family history, photos, and genealogical data.

## Current Setup
- Main content located in `/docs/htm/`
- GitHub Pages serves from `/docs/` at `https://fil512.github.io/auntruth/`
- Multiple lineage sections (L0-L9) containing family trees and photos
- Large image collection in `/jpg/` directory

## Critical Issues to Fix

### 1. Broken Absolute Path Links
**Problem:** The site uses various incompatible path formats:
- Windows-style paths: `\auntruth\htm\`
- Absolute paths: `/AuntRuth/`
- Mixed case sensitivity issues

**Solution:**
- Replace all `\auntruth\htm\` with relative paths (`./` or `../`)
- Convert `/AuntRuth/` references to work from `/auntruth/` base
- Ensure all paths use forward slashes for web compatibility

### 2. Remove Server-Side Dependencies
**Problem:** Site contains references to server-side scripts that won't work on GitHub Pages:
- CGI counter script: `/cgi-bin/counter.pl`
- Java applets for sound playback (`.au` files)

**Solution:**
- Remove all counter image tags
- Replace or remove Java applet sound players
- Consider modern alternatives if functionality is needed

### 3. Fix Missing Resources
**Problem:** Several resources have incorrect paths:
- Background image: `../jpg/backruth.jpg` (incorrect relative path)
- CSS files: `/AuntRuth/css/htm.css` and `/AuntRuth/css/main.css`
- Missing CSS files cause styling issues

**Solution:**
- Correct relative paths to jpg directory
- Update CSS references to use proper relative paths
- Create missing CSS files or remove references

## Recommended Changes

### 1. Create Modern Index Page
- Replace current `index.html` with cleaner version
- Remove Microsoft Word-specific XML and Office-specific styling
- Create proper navigation structure
- Add mobile-responsive design

### 2. Update All Internal Links
- Systematically update all internal navigation links
- Ensure case-sensitive compatibility (GitHub Pages is case-sensitive)
- Fix cross-lineage references between L0-L9 sections

### 3. Modernize HTML Structure
**Remove obsolete code:**
- VML (Vector Markup Language) references
- Microsoft Office-specific XML islands
- Deprecated HTML attributes (bgcolor, align, etc.)

**Add modern standards:**
- UTF-8 charset declarations
- Proper DOCTYPE declarations
- Semantic HTML5 elements where appropriate

### 4. Handle Large Files
**Problem:** Some index files exceed 400KB, causing slow loading
- L0/index.htm: 458KB
- L1/index.htm: >100K tokens

**Solution:**
- Consider pagination for large indexes
- Implement lazy loading for images
- Split large pages into smaller sections

## Optional Enhancements

### 1. Add Responsive Design
- Create mobile-friendly CSS
- Implement responsive tables for genealogy data
- Ensure images scale appropriately

### 2. Improve Navigation
- Add breadcrumb navigation
- Create site search functionality
- Add a sitemap for better navigation

### 3. Error Handling
- Create custom 404.html page
- Add redirects for common broken links
- Implement JavaScript fallbacks

### 4. Modern Features
- Add print-friendly stylesheets
- Implement image lightbox for photos
- Add social sharing capabilities
- Consider adding JSON-LD structured data for genealogy

## Implementation Priority

### Phase 1: Critical Fixes (Required for basic functionality)
1. Fix all path issues (absolute to relative)
2. Remove server-side dependencies
3. Correct resource paths
4. Create functional main index

### Phase 2: Compatibility Improvements
1. Update internal links throughout site
2. Fix case sensitivity issues
3. Remove obsolete HTML/XML code
4. Add UTF-8 encoding

### Phase 3: Enhancements (Optional)
1. Add responsive design
2. Improve navigation structure
3. Optimize large files
4. Add modern features

## Technical Notes

### File Statistics
- Total HTML files: ~11,069
- Image files: 500+ JPGs
- Lineage sections: 10 (L0-L9)
- Years of data: 2002-2005

### Compatibility Considerations
- GitHub Pages serves static files only
- Case-sensitive file system
- No server-side processing
- HTTPS only (may affect mixed content)

## Testing Checklist
- [ ] Main index loads correctly
- [ ] All lineage sections accessible
- [ ] Internal navigation works
- [ ] Images display properly
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Cross-browser compatibility
- [ ] Performance acceptable

## Automation Opportunities
Given the large number of files (11,000+), **mandatory scripting approach**:

### Script Reuse Policy
- **All subagents MUST read PRPs/scripts/README.md first**
- Reuse existing scripts when possible
- Document new scripts thoroughly in PRPs/scripts/README.md
- Test all scripts in dry-run mode first
- **Never proceed with >100 file changes without script-based approach**

### Required Automation Tasks
- Batch path replacements (Python scripts in PRPs/scripts/)
- Link validation (automated verification)
- HTML modernization (mass processing with backups)
- Image optimization (if needed)

### Safety Requirements
- Full backup creation before any mass operation
- Dry-run testing mandatory for >100 files
- Progress reporting and error logging
- Rollback capability verification

## Git Workflow Requirements
This repository is git-managed, so use git branches instead of file backups:
1. **Feature branches required** - Create branch for each major change
2. **No file backups needed** - Git provides full version control
3. **Test in branches** - Verify changes work before merging
4. **User review required** - Get approval before merging to main
5. **Incremental commits** - Commit changes frequently during large operations

---

*Generated: 2025-09-22*
*Repository: https://github.com/fil512/auntruth*