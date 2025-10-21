# AuntieRuth.com - Genealogy Website

Family history website spanning 16th Century Denmark to 2025 Canada, with 3,004 family members across 10 lineages and 11,516 fully modernized pages.

## Project Overview

This repository contains the modernized genealogy website for AuntieRuth.com, featuring:

- **3,004 Family Members** across 10 family lineages
- **11,516 Pages** with auto-generated content from structured JSON data
  - 3,004 person pages (XF*.htm)
  - 2,762 photo detail pages (XI*.htm)
  - 4,276 photo gallery pages (TH*.htm)
  - 1,474 other pages (indices, lineage pages, etc.)
- **Phase 3 Advanced Features** including relationship navigator, timeline visualization, and modern URL routing
- **Full CI/CD Pipeline** with GitHub Actions for automated page generation and deployment
- **Claude Code Skill** for safe genealogy data updates with validation
- **16th-21st Century Coverage** from Denmark to Canada

## Quick Start

### Local Development

The site runs on a local server at `http://localhost:8000/auntruth/`:

```bash
# Server is always running (see PRPs/server for details)
# Visit the site:
# http://localhost:8000/auntruth/new/  (modern version)
# http://localhost:8000/auntruth/htm/  (legacy version)
```

### Working with Claude Code

This project is optimized for development with Claude Code (Anthropic's CLI). Key files:

- **CLAUDE.md** - Project instructions and guidelines for Claude Code
- **PRPs/** - Project Requirements and Plans directory
- **PLAN/** - Architecture and system design documentation

## Chrome DevTools MCP Setup (WSL Users)

**For browser automation in Claude Code on WSL**

### Prerequisites
- Node.js 20+ (`node --version` to check)
- Claude Code running in WSL

### Quick Setup

1. **Install Chrome for Linux:**
   ```bash
   npx -y @puppeteer/browsers install chrome@stable --path ~/chrome
   ```

2. **Configure MCP in `~/.claude.json`:**
   ```json
   "mcpServers": {
     "chrome-devtools": {
       "type": "stdio",
       "command": "npx",
       "args": [
         "chrome-devtools-mcp@latest",
         "--executablePath",
         "/home/YOUR_USERNAME/chrome/chrome/linux-VERSION/chrome-linux64/chrome",
         "--no-sandbox",
         "--disable-setuid-sandbox"
       ],
       "env": {}
     }
   }
   ```
   Replace `YOUR_USERNAME` and `VERSION` with your values.

3. **Restart Claude Code** and test with `/mcp`

See **CLAUDE.md** for complete setup instructions and troubleshooting.

## Project Structure

```
auntruth/
├── CLAUDE.md              # Claude Code project instructions
├── README.md              # This file
├── data/people/           # JSON data for 3,004 people (10 lineages)
├── templates/             # Jinja2 templates for page generation
├── docs/
│   ├── new/htm/          # Auto-generated modern HTML (DO NOT EDIT)
│   ├── htm/              # Legacy HTML files
│   ├── new/js/           # JavaScript components (Phase 3 features)
│   └── new/css/          # Stylesheets
├── PRPs/
│   ├── scripts/          # Python scripts for data processing
│   └── server/           # Local development server
└── PLAN/                 # Architecture documentation
```

## Page Generation System

**⚠️ NEVER manually edit files in `docs/new/htm/L*/` - they are auto-generated!**

### Making Changes

**To update a person's information:**

**Option 1: Use Claude Code Skill (Recommended)**
```
/skill update-genealogy
```
Provides guided updates with automatic validation and bidirectional relationship consistency.

**Option 2: Manual Update**
1. Edit JSON file: `data/people/{lineage}/{person_id}.json`
2. Validate: `python3 PRPs/scripts/both/validate_json_data.py --input ...`
3. Commit to git - GitHub Actions regenerates ALL pages automatically

**To change page design:**
1. Edit template: `templates/person.html` (or other templates)
2. Test locally: `python3 PRPs/scripts/both/generate_pages.py ...`
3. Commit to git - GitHub Actions regenerates ALL pages automatically

See `CLAUDE.md` for detailed instructions.

## Key Scripts

**Page Generation:**
```bash
# Generate pages for one lineage
python3 PRPs/scripts/both/generate_pages.py \
    --lineage Hagborg-Hansson \
    --input-dir data/people/Hagborg-Hansson \
    --output-dir docs/new/htm/L1

# Validate all lineages
python3 PRPs/scripts/both/validate_all_lineages.py
```

**Data Extraction:**
```bash
# Extract JSON from HTML
python3 PRPs/scripts/both/extract_person_data.py ...
```

See `PRPs/scripts/README.md` for complete script documentation.

## Lineages

| Directory | Lineage Name | People | Files |
|-----------|--------------|--------|-------|
| L0/ | Other | 72 | ✅ |
| L1/ | Hagborg-Hansson | 404 | ✅ |
| L2/ | Nelson | 308 | ✅ |
| L3/ | Pringle-Hambley | 409 | ✅ |
| L4/ | Lathrop-Lothropp | 686 | ✅ |
| L5/ | Ward | 123 | ✅ |
| L6/ | Selch-Weiss | 384 | ✅ |
| L7/ | Stebbe | 153 | ✅ |
| L8/ | Lentz | 77 | ✅ |
| L9/ | Phoenix-Rogerson | 388 | ✅ |

## Documentation

- **CLAUDE.md** - Development guidelines and setup instructions
- **docs/GENERATION-SYSTEM.md** - Complete page generation documentation
- **docs/RUNBOOK.md** - Emergency procedures and troubleshooting
- **PLAN/** - System architecture and design documents
- **PRPs/scripts/README.md** - Script documentation

## CI/CD Pipeline

Automated via GitHub Actions (`.github/workflows/build-and-deploy.yml`):

**Build Job:**
1. **Setup** - Node.js 18 + Python 3.11
2. **Regenerate HTML** - Auto-generate all 3,004 person pages from JSON
3. **Auto-commit** - Commit regenerated HTML back to repo ([skip ci])
4. **Build Assets** - Create data chunks and search indices
5. **Test & Validate** - HTML5 compliance and data integrity
6. **Upload** - Prepare artifacts for deployment

**Deploy Job:**
- **Deploy to GitHub Pages** - Automatic deployment on main branch
- **Live URL**: https://fil512.github.io/auntruth/

**Deployment time**: 3-5 minutes from push to live site.

## Recent Enhancements (October 2025)

### Photo Pages Modernization
- **2,762 Photo Detail Pages (XI*.htm)** - Complete redesign with high-res display, zoom, metadata preservation
- **4,276 Photo Gallery Pages (TH*.htm)** - Location/theme galleries with responsive grids and lazy loading
- **Template Integration** - All photo pages now use Jinja2 templates for consistency
- **Mobile Optimization** - Touch-friendly image viewing and responsive layouts
- **SEO & Accessibility** - Proper meta tags, alt text, ARIA labels, structured data

### Claude Code Skill
- **Genealogy Update Skill** - Safe data updates with automatic validation
- **Bidirectional Consistency** - Maintains relationship integrity across all records
- **GitHub Actions Integration** - Auto-regenerates pages after updates
- **Complete Documentation** - Workflow guides in `.claude/skills/update-genealogy/`

### CI/CD Migration
- **GitHub Actions** - Migrated from GitLab to GitHub Actions
- **Auto-regeneration** - Person pages automatically regenerated on every data commit
- **Auto-commit** - Regenerated HTML committed back to repo with [skip ci]
- **GitHub Pages** - Automatic deployment to https://fil512.github.io/auntruth/

### Bug Fixes & Improvements
- **Search Functionality** - Fixed search modal visibility and window sizing
- **Person Pages** - Restored portrait photos, fixed disclosure widgets, corrected URL paths
- **Navigation** - Fixed URL routing without navigation regression
- **Home Page** - Prevented search modal from auto-opening on page load
- **Photo Links** - Separated gallery links, fixed missing photo detail pages

## Phase 3 Features (Available but Not Activated)

Advanced features ready for integration:
- **Relationship Navigator** - BFS path-finding, 6 degrees of separation
- **Timeline Visualization** - D3.js with historical context
- **Modern URL Router** - SEO-friendly URLs with legacy compatibility
- **Mobile-first Design** - WCAG 2.1 compliant

See `CLAUDE.md` for activation instructions.

## Development Guidelines

**From CLAUDE.md:**
- ❌ Never create backup files (`.backup`, `.bak`) - use git instead
- ❌ Never use `!important` in CSS - fix specificity issues properly
- ❌ Never manually edit generated HTML in `docs/new/htm/L*/`
- ✅ Always read `docs/README.md` and `PRPs/scripts/README.md` before writing scripts
- ✅ Execute Python scripts with `python3 script.py` (never chmod)

## Emergency Procedures

**If generated pages have issues:**
```bash
# Immediate rollback
git revert HEAD
git commit -m "Emergency rollback"
git push origin main
# CI auto-deploys previous version
```

See `docs/RUNBOOK.md` for complete emergency procedures.

## Statistics

- **Pages:** 11,516 total (all auto-generated)
  - 3,004 person pages (XF*.htm)
  - 2,762 photo detail pages (XI*.htm)
  - 4,276 photo gallery pages (TH*.htm)
  - 1,474 other pages (indices, lineage pages, etc.)
- **People:** 3,004 family members
- **Lineages:** 10 family lines
- **Time Span:** 16th Century Denmark → 2025 Canada
- **Extraction Success:** 99.3% (3,004/3,025 files)
- **Validation Success:** 98.7% (2,966/3,004 files)
- **CI/CD Platform:** GitHub Actions with auto-deployment
- **Generation Time:** 2-3 minutes for person pages, 3-5 minutes total deployment

## License

Family genealogy data compiled and maintained over many years. This modernized version preserves historical integrity while enhancing accessibility.

---

**Last Updated:** October 2025
**Status:** Phase 3 Complete and In Production
