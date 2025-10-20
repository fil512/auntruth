# AuntieRuth.com - Genealogy Website

Family history website spanning 16th Century Denmark to 2003 Canada, with 2,985+ family members across 10 lineages and 11,069 pages.

## Project Overview

This repository contains the modernized genealogy website for AuntieRuth.com, featuring:

- **2,985+ Family Members** across 10 family lineages
- **11,069 Pages** with auto-generated content from structured JSON data
- **Phase 3 Advanced Features** including relationship navigator, timeline visualization, and modern URL routing
- **Full CI/CD Pipeline** with GitLab for automated page generation and deployment
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
1. Edit JSON file: `data/people/{lineage}/{person_id}.json`
2. Validate: `python3 PRPs/scripts/both/validate_json_data.py --input ...`
3. Commit to git - CI regenerates page automatically

**To change page design:**
1. Edit template: `templates/person.html`
2. Test locally: `python3 PRPs/scripts/both/generate_pages.py ...`
3. Commit to git - CI regenerates ALL pages

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

Automated via GitLab CI with 4 stages:
1. **validate** - JSON data and template syntax
2. **generate** - All 3,004 HTML pages (3-4 min)
3. **test** - HTML5 compliance and data integrity
4. **deploy** - Production deployment (manual approval)

Nightly rebuilds at 2 AM for continuous validation.

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

- **Pages:** 11,069 total (3,004 auto-generated)
- **People:** 2,985+ family members
- **Lineages:** 10 family lines
- **Time Span:** 16th Century Denmark → 2003 Canada
- **Extraction Success:** 99.3% (3,004/3,025 files)
- **Validation Success:** 98.7% (2,966/3,004 files)
- **Generation Time:** 3-4 minutes for all pages

## License

Family genealogy data compiled and maintained over many years. This modernized version preserves historical integrity while enhancing accessibility.

---

**Last Updated:** October 2025
**Status:** Phase 3 Complete and In Production
