- never chmod python scripts. just execute them as an argument to python3

## Chrome DevTools MCP Setup (WSL)

**For browser automation in Claude Code via chrome-devtools MCP on WSL**

### Prerequisites
- Node.js 20+ (chrome-devtools-mcp requires Node 20.19.0 LTS or newer)
- Claude Code running in WSL

### Setup Instructions

1. **Install Chrome for Linux in WSL:**
   ```bash
   npx -y @puppeteer/browsers install chrome@stable --path ~/chrome
   ```
   This installs Chrome for Testing (Linux-compatible) in `~/chrome`. Note the installation path.

2. **Configure MCP in `~/.claude.json`:**

   Update the `mcpServers` section in your `~/.claude.json` file:
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

   **Replace:**
   - `YOUR_USERNAME` with your WSL username
   - `VERSION` with the installed Chrome version (e.g., `141.0.7390.78`)

   **Flags explained:**
   - `--executablePath`: Points to the Linux Chrome binary (required for WSL)
   - `--no-sandbox` and `--disable-setuid-sandbox`: Required for Chrome to run in WSL

3. **Restart Claude Code:**

   Exit Claude Code completely and restart it to reload the MCP configuration.

4. **Verify Setup:**

   In Claude Code, type `/mcp` to see the chrome-devtools status. You should see:
   ```
   Reconnected to chrome-devtools.
   ```

5. **Test:**

   Ask Claude to use chrome-devtools tools, e.g.:
   - "Navigate to localhost:8000 and take a screenshot"
   - "List the open Chrome pages"

### Important Notes

- **Do NOT manually launch Chrome** - The MCP server launches its own Chrome instance
- **WSL-specific**: This setup uses Chrome for Linux, not Windows Chrome
- The Chrome instance runs in **headless mode** by default (no visible window)
- Chrome for Linux is installed via Puppeteer's `@puppeteer/browsers` package

### Troubleshooting

**"Target closed" error:**
- Make sure you're using Node 20+ (`node --version`)
- Verify the `--executablePath` points to the correct Chrome binary
- Ensure Claude Code was completely restarted after config changes
- Kill any manually-launched Chrome instances: `pkill -9 chrome`

**Network errors (e.g., ERR_NAME_NOT_RESOLVED):**
- Headless Chrome in WSL may have DNS resolution issues
- Use `localhost` URLs instead of external URLs when possible
- For external sites, you may need to configure DNS in WSL

### Reference
- GitHub Issue: https://github.com/ChromeDevTools/chrome-devtools-mcp/issues/405
- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp

## CRITICAL: NO BACKUP FILES EVER
**NEVER CREATE BACKUP FILES (.backup, .bak, .orig, etc.) WHEN USING GIT**
- We are in a git repository - git IS our backup system
- Creating .backup files is redundant, wasteful, and creates clutter
- Any script that creates backup files must be immediately fixed
- If you need to preserve state, commit to git first, then make changes
- If a script fails, use `git checkout` to revert changes
- REMOVE any existing backup files immediately upon discovery

## CRITICAL: CSS BEST PRACTICES
**NEVER USE !important IN CSS**
- CSS specificity should be managed through proper selector hierarchy, not !important
- Using !important creates maintenance nightmares and specificity wars
- It breaks the CSS cascade and makes debugging extremely difficult
- If styles aren't applying, fix the root cause (selector specificity, load order, inheritance)
- Valid alternatives to !important:
  - Increase selector specificity (e.g., `body table#List` instead of `table`)
  - Adjust CSS file load order in HTML
  - Use more specific selectors (IDs, multiple classes, descendant selectors)
  - Refactor conflicting styles at their source
- The ONLY acceptable use of !important is in utility classes specifically designed to override everything (and even then, reconsider)
- If you encounter !important in existing code, remove it and fix the underlying specificity issue

## Python Script Guidelines

### Before Writing New Scripts
1. **ALWAYS read docs/README.md first** to understand the file naming conventions and directory structure
2. **ALWAYS read PRPs/scripts/README.md first** to check if an existing script can be reused
3. Check the organized subdirectories:
   - `PRPs/scripts/htm/` - scripts for docs/htm directory
   - `PRPs/scripts/new/` - scripts for docs/new directory
   - `PRPs/scripts/both/` - scripts that work with either directory

### When Writing New Python Scripts
- Place scripts in the appropriate subdirectory based on their target:
  - **htm/** - if script works only with docs/htm
  - **new/** - if script works only with docs/new
  - **both/** - if script can work with either directory or has options for both
- Follow the safety protocols and templates documented in PRPs/scripts/README.md
- Update PRPs/scripts/README.md with documentation for any new script
- Never run the link checker yourself. Always ask me to do it.

## Phase 3 Advanced Features - COMPLETED

**Phase 3 Advanced Features have been fully implemented** (December 2024) and are ready for integration into the live site. The components exist but are not yet active on web pages.

### Components Implemented

#### 1. Relationship Navigator Component (`docs/new/js/components/relationship-navigator.js`)
- **Size:** 27.0KB
- **Features:**
  - Complete relationship graph processing 2,985+ people across 10 lineages
  - BFS path-finding algorithm with up to 6 degrees of separation
  - Human-readable relationship descriptions (parent, grandparent, first cousin, etc.)
  - Mobile-responsive sidebar UI with smooth animations
  - Cross-component integration with search and family tree
- **Performance:** < 100ms for typical relationship queries
- **Status:** ✅ Complete with full validation testing

#### 2. Timeline Visualization Component (`docs/new/js/components/timeline.js`)
- **Size:** 25.0KB
- **Features:**
  - Robust date parsing handles all genealogy formats (100% test success rate)
  - D3.js timeline visualization with zoom/pan capabilities
  - Historical context integration with Canadian/Swedish/global events
  - Multi-dimensional filtering by lineage, date range, event types
  - Mobile touch optimization and responsive controls
- **Performance:** < 500ms initial load for typical date ranges
- **Status:** ✅ Complete with comprehensive date format testing

#### 3. Modern URL Router (`docs/new/js/utils/url-router.js`)
- **Size:** 20.5KB
- **Features:**
  - History API client-side router with pattern matching
  - Legacy URL compatibility (96.2% test success rate)
  - SEO optimization with dynamic meta tags and structured data
  - Person slug generation for modern URLs (`/person/walter-arnold-hagborg-123`)
  - 404 handling with intelligent suggestions
- **Performance:** < 50ms client-side navigation
- **Status:** ✅ Complete with extensive URL pattern testing

#### 4. Phase 3 Integration Layer (`docs/new/js/phase3-integration.js`)
- **Size:** 15.5KB
- **Features:**
  - Event-driven architecture coordinates all components
  - Phase 2 compatibility works alongside existing features
  - Lazy component loading for optimal performance
  - Keyboard shortcuts (Ctrl+R for relationships, Ctrl+T for timeline)
- **Status:** ✅ Complete with cross-component communication

#### 5. Comprehensive CSS (`docs/new/css/phase3-components.css`)
- **Features:**
  - Mobile-first responsive design
  - Accessibility compliance (WCAG 2.1)
  - Dark mode preparation
  - Print stylesheet optimization
- **Status:** ✅ Complete with mobile responsiveness

### Integration Status

**Components are BUILT but NOT INTEGRATED into web pages yet.**

To activate Phase 3 features on any HTML page:

1. **Add the data attribute:**
   ```html
   <body data-phase3-enabled>
   ```

2. **Include the integration script:**
   ```html
   <script type="module" src="docs/new/js/phase3-integration.js"></script>
   ```

3. **Include the CSS:**
   ```html
   <link rel="stylesheet" href="docs/new/css/phase3-components.css">
   ```

### Validation Results

- **✅ Relationship Graph Testing:** Graph built for 775 people, all path-finding tests passed
- **✅ Date Parsing Testing:** 36/36 test cases passed (100% success rate)
- **✅ URL Routing Testing:** 25/26 tests passed (96.2% success rate)
- **✅ Integration Testing:** All architecture compliance checks passed
- **✅ Performance:** All metrics met (< 100ms relationships, < 500ms timeline, < 50ms routing)

### User Experience Features

- **Relationship Navigator:** Fixed sidebar showing family context with immediate family
- **Timeline Exploration:** Interactive chronological view with historical events
- **Modern URLs:** Clean, SEO-friendly URLs with legacy compatibility
- **Keyboard Shortcuts:** Ctrl+R (relationships), Ctrl+T (timeline)
- **Mobile Responsive:** Touch-friendly across all screen sizes
- **Accessibility:** WCAG 2.1 compliant with screen reader support

### Next Steps for Live Integration

1. **Choose target pages** for Phase 3 activation (recommend starting with main index pages)
2. **Add integration code** to selected HTML files
3. **Test on staging** before production deployment
4. **Monitor performance** and user feedback
5. **Complete relationship finder modal** implementation (optional enhancement)
- You can curl the contents of the docs folder at the endpoint localhost:8000/auntruth/. You never need to run a server; this server is always running. If you need to see the server code, it is in PRPs/server

## Claude Code Skill: Genealogy Data Updates

**A specialized Claude Code skill is available for safely updating genealogy data.**

### Using the Genealogy Update Skill

When you need to update genealogy data (birth/death dates, marriages, children, contact info), invoke the skill:

```
/skill update-genealogy
```

The skill provides:
- **Safe updates** with automatic validation
- **Bidirectional consistency** for relationships (spouse/parent/child)
- **Automated workflow** integration with GitHub Actions
- **Complete documentation** in `.claude/skills/update-genealogy/`

**Key Features:**
- Updates 3,004 people across 10 lineages
- Validates schema compliance before commit
- Auto-regenerates HTML pages via GitHub Actions
- Maintains relationship integrity across all affected records

See `.claude/skills/update-genealogy/SKILL.md` for complete documentation.

## Page Generation System - PRODUCTION (Phase 3 Complete)

**Phase 3 of the page generation system is now COMPLETE and IN PRODUCTION** (October 2025). The system auto-generates all 11,516 genealogy pages from structured JSON data using Jinja2 templates.

### System Overview

**Pages are now auto-generated from data + templates via GitHub Actions CI/CD.**

```
JSON Data (3,004 files) + Jinja2 Templates → Generated HTML (11,516 pages)
         ↓                                           ↓
   Git Commit                                GitHub Actions Pipeline
         ↓                                           ↓
   Validation                                  Auto-deployment
```

### Key Statistics

- **📁 10 Lineages**: All family lineages extracted and automated
- **👥 3,004 People**: JSON records for entire genealogy database
- **📄 11,516 Total Pages**: Fully modernized and auto-generated
  - 3,004 person pages (XF*.htm)
  - 2,762 photo detail pages (XI*.htm)
  - 4,276 photo gallery pages (TH*.htm)
  - 1,474 other pages (indices, lineage pages, etc.)
- **✅ 99.3% Extraction Success**: 21 files failed due to missing source data (incomplete HTML)
- **✅ 98.7% Validation Success**: 38 files with schema issues (missing names in source)
- **🚀 Automated CI/CD**: GitHub Actions with validation, generation, testing, deployment
- **⏱️ 2-3 Min Generation**: All person pages regenerated in single CI run

### Directory Structure

```
data/people/                    # Source JSON data (DO NOT manually edit HTML!)
  ├── Hagborg-Hansson/         # 404 people
  ├── Nelson/                  # 308 people
  ├── Pringle-Hambley/         # 409 people
  ├── Lathrop-Lothropp/        # 686 people (largest)
  ├── Ward/                    # 123 people
  ├── Selch-Weiss/             # 384 people
  ├── Stebbe/                  # 153 people
  ├── Lentz/                   # 77 people (smallest)
  ├── Phoenix-Rogerson/        # 388 people
  └── Other/                   # 72 people (unclassified)

templates/                      # Jinja2 templates
  ├── base.html                # Root template with Phase 3/4 integration
  ├── person.html              # Main person page template
  ├── components/              # Reusable components (header, family, etc.)
  └── macros/                  # Template macros (links, dates, cards)

docs/new/htm/                  # AUTO-GENERATED HTML (DO NOT EDIT MANUALLY!)
  ├── L0-L9/                   # Person pages by lineage (3,004 pages)
  │   ├── L0/  (Other - 72 people)
  │   ├── L1/  (Hagborg-Hansson - 404 people)
  │   ├── L2/  (Nelson - 308 people)
  │   ├── L3/  (Pringle-Hambley - 409 people)
  │   ├── L4/  (Lathrop-Lothropp - 686 people)
  │   ├── L5/  (Ward - 123 people)
  │   ├── L6/  (Selch-Weiss - 384 people)
  │   ├── L7/  (Stebbe - 153 people)
  │   ├── L8/  (Lentz - 77 people)
  │   └── L9/  (Phoenix-Rogerson - 388 people)
  ├── XI*.htm                  # Photo detail pages (2,762 pages)
  ├── TH*.htm                  # Photo gallery pages (4,276 pages)
  └── Other indices and pages  # Lineage indices, search, etc.
```

### ⚠️ CRITICAL: Never Manually Edit Generated HTML

**DO NOT manually edit files in `docs/new/htm/L*/` - they are auto-generated and will be overwritten!**

- ❌ **WRONG**: Edit `docs/new/htm/L1/XF100.htm` directly
- ✅ **CORRECT**: Edit `data/people/Hagborg-Hansson/XF100.json` and commit (CI regenerates page)
- ✅ **CORRECT**: Edit `templates/person.html` to change design (CI regenerates ALL pages)

### Making Changes

#### To Update a Person's Information

1. Edit JSON file: `data/people/{lineage}/{person_id}.json`
2. Validate locally: `python3 PRPs/scripts/both/validate_json_data.py --input data/people/{lineage}/{person_id}.json`
3. Commit to git: `git add . && git commit -m "Update person data" && git push`
4. GitHub Actions automatically validates, regenerates ALL pages, and deploys

**Better yet**: Use the Claude Code skill `/skill update-genealogy` for guided updates with automatic validation!

#### To Change Page Design/Layout

1. Edit template: `templates/person.html` (or components/macros)
2. Test locally: `python3 PRPs/scripts/both/generate_pages.py --lineage Hagborg-Hansson --input-dir data/people/Hagborg-Hansson --output-dir test-output`
3. Commit to git: `git add . && git commit -m "Update page design" && git push`
4. GitHub Actions automatically regenerates ALL 3,004 person pages with new design

#### To Add a New Person

1. Create JSON file: `data/people/{lineage}/XF{number}.json`
2. Follow schema from `PLAN/data-schema.md`
3. Validate and commit (CI generates page automatically)

### Scripts

**Extraction (HTML → JSON)**:
- `PRPs/scripts/both/extract_person_data.py` - Extract structured data from HTML
- `PRPs/scripts/both/validate_extraction.py` - Validate HTML → JSON accuracy

**Generation (JSON → HTML)**:
- `PRPs/scripts/both/generate_pages.py` - Generate pages from JSON + templates
- `PRPs/scripts/both/validate_generation.py` - Validate JSON → HTML accuracy

**Validation**:
- `PRPs/scripts/both/validate_json_data.py` - Validate JSON schema compliance
- `PRPs/scripts/both/validate_all_lineages.py` - Validate all 10 lineages

### GitHub Actions CI/CD Pipeline

**Configured in `.github/workflows/build-and-deploy.yml`** with automated deployment:

**Build Job:**
1. **Checkout** - Pull latest code from repository
2. **Setup** - Configure Node.js 18 and Python 3.11
3. **Regenerate HTML** - Auto-generate all 3,004 person pages from JSON
4. **Auto-commit** - Commit regenerated HTML back to repo (with [skip ci])
5. **Build Assets** - Create data chunks and search indices
6. **Optimize** - Optimize assets for production
7. **Test & Validate** - Run tests and validate data integrity
8. **Upload** - Prepare artifacts for deployment

**Deploy Job:**
- **Deploy to GitHub Pages** - Automatic deployment on main branch
- **Live URL**: https://fil512.github.io/auntruth/

**Key Features**:
- Triggers automatically on every push to main
- Regenerates person pages from JSON data
- Auto-commits changes (marked with [skip ci] to avoid loops)
- Full deployment in 3-5 minutes from push to live site

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Generate pages for one lineage
python3 PRPs/scripts/both/generate_pages.py \
    --lineage Hagborg-Hansson \
    --input-dir data/people/Hagborg-Hansson \
    --output-dir docs/new/htm/L1

# Validate all lineages
python3 PRPs/scripts/both/validate_all_lineages.py

# Preview locally (server always running)
# Visit: http://localhost:8000/auntruth/new/htm/L1/XF100.htm
```

### Documentation

- **Developer Guide**: `docs/GENERATION-SYSTEM.md` - Complete development documentation
- **Operations Runbook**: `docs/RUNBOOK.md` - Emergency procedures, troubleshooting, monitoring
- **Architecture**: `PLAN/page-generation-overview.md` - System design and strategy
- **Data Schema**: `PLAN/data-schema.md` - JSON schema specification
- **Templates**: `PLAN/template-structure.md` - Template architecture
- **CI Pipeline**: `PLAN/ci-pipeline-spec.md` - Complete pipeline specification
- **Lineage Mapping**: `PLAN/lineage-mapping.md` - Directory → lineage mapping

### Emergency Procedures

**If generated pages have issues:**

```bash
# Immediate rollback (< 5 minutes)
git revert HEAD
git commit -m "Emergency rollback"
git push origin main
# CI auto-deploys previous version

# Or manual rollback
ssh deployer@auntieruth.com
rsync -avz /var/www/auntruth/backups/latest/ /var/www/auntruth/new/htm/
```

**See `docs/RUNBOOK.md` for complete emergency procedures.**

### Photo Pages Modernization (October 2025)

**All photo-related pages have been modernized and integrated into the template system.**

**Photo Detail Pages (XI*.htm) - 2,762 pages:**
- Complete redesign with modern responsive layout
- High-resolution image display with zoom capabilities
- Metadata preservation (date, location, people, photographer)
- Cross-linking to related people and galleries
- Mobile-optimized image viewing

**Photo Gallery Pages (TH*.htm) - 4,276 pages:**
- Location-based and theme-based galleries
- Thumbnail grids with lazy loading
- Integration with person pages and photo details
- Breadcrumb navigation and search integration
- Responsive grid layouts for all screen sizes

**Key Features:**
- All pages use Jinja2 templates for consistency
- Integrated with Phase 3 features (search, navigation)
- SEO-optimized with proper meta tags and structured data
- Accessibility improvements (alt text, ARIA labels)
- Fast loading with optimized images and lazy loading

### Phase 3 Achievements

- ✅ **All 10 lineages extracted** (3,004/3,025 files, 99.3% success)
- ✅ **Schema compliance validated** (2,966/3,004 files, 98.7% success)
- ✅ **GitHub Actions CI/CD pipeline** fully automated
- ✅ **Photo pages modernized** (2,762 detail + 4,276 gallery pages)
- ✅ **Claude Code skill created** for safe genealogy data updates
- ✅ **Comprehensive documentation** (developer guide, runbook, skills)
- ✅ **Templates created** with Phase 4 design system integration
- ✅ **Production deployment** automated to GitHub Pages

### Lineage Directory Mapping

| Directory | Lineage Name | Files | Status |
|-----------|--------------|-------|--------|
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

---

**Phase 3 Status**: ✅ **COMPLETE AND IN PRODUCTION** (October 2025)

**Key Takeaway**: Data-driven page generation system with full GitHub Actions CI/CD automation for 11,516 genealogy pages (3,004 person pages + 2,762 photo detail pages + 4,276 photo gallery pages) across 10 family lineages. Includes Claude Code skill for safe genealogy data updates.