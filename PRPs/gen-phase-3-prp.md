# PRP: Page Generation Phase 3 - CI/CD Pipeline & Full Rollout

## Prerequisites - READ THESE FILES FIRST

**CRITICAL**: Before starting this phase, read the following files to understand the complete context:

1. `Read(PLAN/page-generation-overview.md)` - Overall architecture and strategy
2. `Read(PLAN/ci-pipeline-spec.md)` - Complete CI/CD specification you must implement
3. `Read(PLAN/data-schema.md)` - Data schema for all lineages
4. `Read(PLAN/template-structure.md)` - Template architecture
5. `Read(CLAUDE.md)` - Project conventions
6. `Read(PRPs/gen-phase-1-prp.md)` - Understand Phase 1 extraction process
7. `Read(PRPs/gen-phase-2-prp.md)` - Understand Phase 2 templates and generation

## Phase 3 Overview

**Objective**: Automate page generation in GitLab CI and expand to all lineages.

**Scope**: All 10 lineages (~2,985 people total)

**Duration**: 1 week

**Output**:
- GitLab CI pipeline (`.gitlab-ci.yml`)
- All lineages extracted to JSON
- All pages generated via CI
- Complete deployment to production
- Documentation and runbooks

## Phase 3 Tasks

### Task 1: Expand Data Extraction to All Lineages (Days 1-2)

**Objective**: Extract all remaining lineages to JSON.

**Lineages to Extract**:

Based on `docs/new/htm/` directory structure, identify all lineages:

```bash
# List all lineage directories
ls -d docs/new/htm/L*/

# Expected output:
# L1/ - Hagborg-Hansson (already done in Phase 1)
# L2/ - Anderson?
# L3/ - ...
# etc.
```

**Actions**:

1. **Document all lineages**:
   ```bash
   # Create lineage mapping
   vim PLAN/lineage-mapping.md
   ```

   Example content:
   ```markdown
   # Lineage Directory Mapping

   | Directory | Lineage Name | Person Count |
   |-----------|--------------|--------------|
   | L1/ | Hagborg-Hansson | 123 |
   | L2/ | Anderson | 89 |
   | L3/ | ... | ... |
   ```

2. **Extract each lineage**:
   ```bash
   # For each lineage Lx/
   for lineage_dir in docs/new/htm/L*/; do
       lineage_num=$(basename $lineage_dir)
       lineage_name="..." # Determine from first person page

       python3 PRPs/scripts/both/extract_person_data.py \
           --lineage $lineage_name \
           --input-dir $lineage_dir \
           --output-dir data/people/$lineage_name \
           --verbose
   done
   ```

3. **Validate all extractions**:
   ```bash
   python3 PRPs/scripts/both/validate_json_data.py \
       --input-dir data/people \
       --report data/extraction-report-all-lineages.md
   ```

**Success Criteria**:
- All lineages extracted to JSON
- All JSON files pass validation
- Extraction report shows 100% success rate
- Total ~2,985 JSON files created

### Task 2: Generate All Pages Locally (Day 2)

**Objective**: Test full generation before CI automation.

**Actions**:

1. **Enhance generation script** to support multiple lineages:

   ```bash
   python3 PRPs/scripts/both/generate_pages.py \
       --all-lineages \
       --input-dir data/people \
       --output-dir docs/new/htm \
       --verbose
   ```

2. **Monitor generation**:
   - Track progress (e.g., "Generated 500/2985 pages")
   - Note any errors or warnings
   - Measure performance (pages per second)

3. **Validate all generated pages**:
   ```bash
   python3 PRPs/scripts/both/validate_generated_pages.py \
       --input-dir docs/new/htm \
       --json-dir data/people \
       --report PLAN/validation-report-all-pages.md
   ```

**Success Criteria**:
- All 2,985 pages generate without errors
- Generation completes in < 5 minutes
- All pages pass validation
- No data loss detected

### Task 3: Create GitLab CI Pipeline (Days 3-4)

**Objective**: Implement automated CI/CD pipeline.

**File**: `.gitlab-ci.yml`

**Actions**:

1. **Create GitLab CI configuration**:

Use the complete specification from `Read(PLAN/ci-pipeline-spec.md)`.

Key stages:
- `validate` - Validate JSON data and templates
- `generate` - Generate all HTML pages
- `test` - Run validation tests
- `deploy` - Deploy to production (manual approval)

2. **Create requirements file**:

   ```bash
   # requirements.txt
   cat > requirements.txt <<EOF
   jinja2>=3.1.0
   pyyaml>=6.0
   jsonschema>=4.0
   beautifulsoup4>=4.12.0
   lxml>=4.9.0
   html5lib>=1.1
   EOF
   ```

3. **Test pipeline locally** (if possible):

   ```bash
   # Simulate CI environment
   docker run -it --rm \
       -v $(pwd):/workspace \
       -w /workspace \
       python:3.11 \
       bash -c "pip install -r requirements.txt && python3 PRPs/scripts/both/generate_pages.py --all-lineages"
   ```

**Success Criteria**:
- `.gitlab-ci.yml` created with all stages
- `requirements.txt` lists all dependencies
- Pipeline configuration is syntactically valid
- Local testing succeeds

### Task 4: Set Up CI Environment Variables (Day 4)

**Objective**: Configure GitLab CI/CD settings.

**Environment Variables to Set** (in GitLab UI):

Navigate to: Repository Settings → CI/CD → Variables

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `DEPLOY_HOST` | `auntieruth.com` | ✓ | ✗ |
| `DEPLOY_USER` | `deployer` | ✓ | ✗ |
| `DEPLOY_PATH` | `/var/www/auntruth/new/htm` | ✓ | ✗ |
| `SSH_PRIVATE_KEY` | (SSH key content) | ✓ | ✓ |

**SSH Key Setup**:

```bash
# Generate SSH key for CI deployment (if needed)
ssh-keygen -t ed25519 -C "gitlab-ci@auntruth" -f ci_deploy_key

# Add public key to server
ssh-copy-id -i ci_deploy_key.pub deployer@auntieruth.com

# Add private key to GitLab CI variables
cat ci_deploy_key  # Copy this to GitLab
```

**Success Criteria**:
- All environment variables configured
- SSH key allows passwordless deployment
- Variables are protected and masked appropriately

### Task 5: Test CI Pipeline (Day 5)

**Objective**: Run first CI pipeline and fix any issues.

**Actions**:

1. **Commit CI configuration**:
   ```bash
   git add .gitlab-ci.yml requirements.txt
   git commit -m "Add GitLab CI/CD pipeline for automated page generation"
   git push origin main
   ```

2. **Monitor pipeline** in GitLab UI:
   - Watch each stage execute
   - Check logs for errors
   - Note execution times

3. **Debug failures**:
   - If validation fails: Fix JSON/templates
   - If generation fails: Fix generation script
   - If tests fail: Fix validation logic

4. **Iterate until green**:
   - Fix issues
   - Commit fixes
   - Re-run pipeline
   - Repeat until all stages pass

**Success Criteria**:
- Pipeline runs successfully end-to-end
- All stages pass (validate, generate, test)
- Generated pages match local generation
- Pipeline completes in < 10 minutes

### Task 6: Incremental Rollout to Production (Days 5-6)

**Objective**: Deploy generated pages to production in phases.

**Rollout Strategy**:

1. **Phase 6a: Deploy Hagborg-Hansson (already tested)**
   ```bash
   # Manual deployment first time
   rsync -avz docs/new/htm/L1/ user@server:/var/www/auntruth/new/htm/L1/
   ```

   - Test live site
   - Monitor for issues
   - Get user approval

2. **Phase 6b: Deploy 2-3 more lineages**
   - Choose smallest lineages first
   - Deploy via CI (manual trigger)
   - Test each lineage
   - Monitor error logs

3. **Phase 6c: Deploy remaining lineages**
   - Deploy all remaining lineages
   - Full site testing
   - Monitor performance

**Validation After Each Deploy**:

```bash
# Run link checker
python3 PRPs/scripts/both/check_links.py \
    --url https://auntieruth.com/auntruth/new/htm/

# Check for 404s in server logs
ssh user@server "grep '404' /var/log/nginx/access.log | grep '/auntruth/new/htm/'"
```

**Success Criteria**:
- All lineages deployed successfully
- No broken links detected
- Site performance maintained
- User approves production deployment

### Task 7: Set Up Automated Rebuilds (Day 6)

**Objective**: Configure scheduled pipeline runs.

**GitLab Scheduled Pipelines**:

Navigate to: CI/CD → Schedules → New Schedule

**Schedule Configuration**:

```
Description: Nightly full rebuild
Cron pattern: 0 2 * * *  (2 AM daily)
Target branch: main
Variables:
  REBUILD_TYPE: full
  FORCE_REGENERATE: true
```

**Scheduled Pipeline Script** (add to `.gitlab-ci.yml`):

```yaml
nightly-full-rebuild:
  stage: generate
  only:
    - schedules
  script:
    - pip install -r requirements.txt
    - python3 PRPs/scripts/both/generate_pages.py --force-all
    - python3 PRPs/scripts/both/validate_generated_pages.py --all-checks
  artifacts:
    paths:
      - docs/new/htm/
      - validation-report.html
    expire_in: 7 days
```

**Success Criteria**:
- Scheduled pipeline configured
- Nightly builds run automatically
- Artifacts preserved for review

### Task 8: Documentation & Runbooks (Day 7)

**Objective**: Document the complete system for future maintenance.

**Documents to Create**:

#### 1. Developer Guide (`docs/GENERATION-SYSTEM.md`)

```markdown
# Page Generation System - Developer Guide

## Quick Start

Generate all pages locally:

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Extract data (if needed)
python3 PRPs/scripts/both/extract_person_data.py --all-lineages

# Generate pages
python3 PRPs/scripts/both/generate_pages.py --all-lineages

# Validate
python3 PRPs/scripts/both/validate_generated_pages.py
\`\`\`

## Adding a New Person

1. Create JSON file: \`data/people/{lineage}/{person_id}.json\`
2. Follow schema: \`PLAN/data-schema.md\`
3. Commit to git
4. CI will automatically generate page

## Modifying Templates

1. Edit template in \`templates/\`
2. Test locally: \`python3 PRPs/scripts/both/generate_pages.py --dry-run\`
3. Commit changes
4. CI regenerates all pages automatically

## Troubleshooting

### Pages not updating
- Check CI pipeline status
- Verify JSON data is valid
- Clear browser cache

### Template errors
- Validate Jinja2 syntax
- Check template inheritance
- Review CI logs
\`\`\`

#### 2. Operations Runbook (`docs/RUNBOOK.md`)

```markdown
# Page Generation System - Operations Runbook

## Emergency Rollback

If generated pages have issues:

\`\`\`bash
# Immediate rollback to previous commit
git revert HEAD
git push origin main

# Or manual deployment of previous version
rsync -avz backups/latest/ user@server:/var/www/auntruth/new/htm/
\`\`\`

## Pipeline Failures

### Stage: validate
- **Symptom**: JSON schema validation fails
- **Fix**: Review and fix JSON files, re-commit
- **Command**: \`python3 PRPs/scripts/both/validate_json_data.py\`

### Stage: generate
- **Symptom**: Page generation fails
- **Fix**: Check template syntax, verify data
- **Command**: \`python3 PRPs/scripts/both/generate_pages.py --debug\`

### Stage: test
- **Symptom**: HTML validation fails
- **Fix**: Review generated HTML, fix templates
- **Command**: \`python3 PRPs/scripts/both/validate_generated_pages.py\`

### Stage: deploy
- **Symptom**: SSH connection fails
- **Fix**: Verify SSH key in GitLab CI variables
- **Test**: \`ssh deployer@auntieruth.com\`

## Monitoring

### Daily Checks
- ✓ CI pipeline status (should be green)
- ✓ Server disk space
- ✓ Error logs

### Weekly Checks
- ✓ Nightly build artifacts
- ✓ Link checker results
- ✓ Performance metrics

## Contacts

- **Repo Owner**: [User Name]
- **Server Admin**: [Admin Name]
- **On-call**: [Phone/Email]
\`\`\`

#### 3. Update CLAUDE.md

Add section documenting the page generation system:

```markdown
## Page Generation System

**Pages are now auto-generated from data + templates.**

- **Data**: \`data/people/{lineage}/{person_id}.json\`
- **Templates**: \`templates/*.html\`
- **Generated Output**: \`docs/new/htm/L*/*.htm\`

### Making Changes

**Add/Edit Person Data**:
1. Edit JSON file in \`data/people/\`
2. Commit to git
3. CI auto-generates pages

**Change Page Design**:
1. Edit templates in \`templates/\`
2. Commit to git
3. CI regenerates all pages

**NEVER manually edit files in \`docs/new/htm/L*/\` - they are auto-generated.**

### Local Development

\`\`\`bash
python3 PRPs/scripts/both/generate_pages.py --lineage Hagborg-Hansson
\`\`\`

### Documentation

- Architecture: \`PLAN/page-generation-overview.md\`
- Data Schema: \`PLAN/data-schema.md\`
- Templates: \`PLAN/template-structure.md\`
- CI Pipeline: \`PLAN/ci-pipeline-spec.md\`
```

**Success Criteria**:
- Complete documentation created
- Runbooks cover all common scenarios
- CLAUDE.md updated with generation system info
- Documentation committed to git

### Task 9: Performance Optimization (Day 7)

**Objective**: Ensure generation is fast and efficient.

**Optimizations to Implement**:

1. **Parallel Generation**:

   ```python
   from multiprocessing import Pool

   def generate_batch(json_files):
       with Pool(processes=8) as pool:
           pool.map(generate_person_page, json_files)
   ```

2. **Incremental Builds**:

   ```python
   def get_changed_files():
       """Only regenerate pages if JSON or templates changed."""
       result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'],
                              capture_output=True, text=True)
       return result.stdout.split('\n')

   def should_regenerate(person_id, changed_files):
       json_file = f'data/people/*/{person_id}.json'
       return any(f.startswith('templates/') or f == json_file
                 for f in changed_files)
   ```

3. **Template Caching**:

   ```python
   from jinja2 import FileSystemBytecodeCache

   env = Environment(
       loader=FileSystemLoader('templates'),
       bytecode_cache=FileSystemBytecodeCache('/tmp/jinja_cache')
   )
   ```

**Performance Targets**:
- Full generation (2,985 pages): < 5 minutes
- Incremental build (10 changed pages): < 30 seconds
- CI pipeline total: < 10 minutes

**Success Criteria**:
- Full generation completes in target time
- Incremental builds are fast
- CI pipeline stays under 10 minutes

### Task 10: Final Production Deployment (Day 7)

**Objective**: Complete full deployment and sign-off.

**Final Deployment Checklist**:

- [ ] All 2,985 pages generated successfully
- [ ] All validation tests pass
- [ ] CI pipeline fully automated
- [ ] Nightly builds scheduled
- [ ] Documentation complete
- [ ] User approval obtained
- [ ] Production deployment complete
- [ ] Monitoring in place

**Production Deployment**:

```bash
# Final deployment via CI (manual approval)
# Trigger in GitLab UI: Pipelines → Run Pipeline → Deploy stage → Manual trigger
```

**Post-Deployment Verification**:

```bash
# Test random sampling of pages
curl -I https://auntieruth.com/auntruth/new/htm/L1/XF100.htm
# Should return: 200 OK

# Run full link check
python3 PRPs/scripts/both/check_links.py --url https://auntieruth.com/auntruth/new/htm/

# Monitor error logs for 24 hours
ssh user@server "tail -f /var/log/nginx/error.log | grep auntruth"
```

**Success Criteria**:
- All pages accessible on production
- No broken links
- No server errors
- User confirms site works correctly

## Deliverables Checklist

At the end of Phase 3, you must have:

- [ ] `.gitlab-ci.yml` - Complete CI/CD pipeline
- [ ] `requirements.txt` - Python dependencies
- [ ] `data/people/` - All lineages extracted to JSON (~2,985 files)
- [ ] `docs/new/htm/L*/` - All pages generated and deployed
- [ ] `docs/GENERATION-SYSTEM.md` - Developer guide
- [ ] `docs/RUNBOOK.md` - Operations runbook
- [ ] `CLAUDE.md` - Updated with generation system docs
- [ ] `PLAN/validation-report-all-pages.md` - Complete validation report
- [ ] CI pipeline running successfully
- [ ] Scheduled nightly builds active
- [ ] Production deployment complete
- [ ] User sign-off obtained

## Testing Checklist

### Pre-Deployment Testing

- [ ] All 2,985 pages generate locally without errors
- [ ] All generated pages pass HTML5 validation
- [ ] All internal links valid
- [ ] No data loss from original pages
- [ ] CI pipeline runs successfully
- [ ] All stages pass (validate, generate, test)

### Post-Deployment Testing

- [ ] Random sample of 50 pages loads correctly
- [ ] Navigation works across all lineages
- [ ] Search functionality works
- [ ] Phase 3 features work (disclosure, timeline, etc.)
- [ ] Mobile responsive on all pages tested
- [ ] No 404 errors in server logs
- [ ] Performance acceptable (page load < 2s)

## Monitoring & Maintenance

### Daily Monitoring

```bash
# Check CI pipeline status
gitlab-ci status

# Check for errors in logs
ssh user@server "grep ERROR /var/log/nginx/error.log | grep auntruth | tail -20"
```

### Weekly Maintenance

```bash
# Review nightly build artifacts
# Download from GitLab Artifacts

# Run full link check
python3 PRPs/scripts/both/check_links.py --comprehensive

# Update dependencies
pip list --outdated
```

### Monthly Tasks

- Review and archive old CI artifacts
- Rotate SSH deployment keys
- Performance audit
- User feedback review

## Rollback Procedures

### Immediate Rollback (< 5 minutes)

```bash
# Revert last commit
git revert HEAD
git push origin main
# CI will auto-deploy previous version
```

### Manual Rollback (if CI is down)

```bash
# Deploy from backup
rsync -avz backups/$(date -d yesterday +%Y%m%d)/ \
    deployer@auntieruth.com:/var/www/auntruth/new/htm/
```

### Selective Rollback (single lineage)

```bash
# Revert specific lineage
git checkout HEAD~1 -- docs/new/htm/L2/
git commit -m "Rollback L2 lineage"
git push origin main
```

## Phase 3 Exit Criteria

Phase 3 is complete when:

1. ✅ All 10 lineages extracted to JSON
2. ✅ All 2,985 pages generated successfully
3. ✅ CI/CD pipeline fully automated
4. ✅ All validation tests pass
5. ✅ Production deployment complete
6. ✅ Monitoring and alerting in place
7. ✅ Documentation complete
8. ✅ User sign-off obtained

## Success Metrics

### Technical Metrics

- **Generation Time**: < 5 minutes for all 2,985 pages ✓
- **CI Pipeline Time**: < 10 minutes total ✓
- **Test Pass Rate**: 100% ✓
- **Deployment Success Rate**: 100% ✓

### Business Metrics

- **Data Accuracy**: 100% of original data preserved ✓
- **Visual Quality**: Modern, professional design ✓
- **User Satisfaction**: Positive feedback ✓
- **Maintainability**: Easy to update/modify ✓

## Next Steps After Phase 3

With the generation system complete, future enhancements could include:

1. **Data Management UI** - Web interface for editing person data
2. **Multiple Template Themes** - User-selectable designs
3. **Advanced Features** - Interactive family trees, maps, timelines
4. **Analytics** - Track page views, popular lineages
5. **API** - RESTful API for genealogy data
6. **Mobile App** - Native mobile experience

## Questions for User Before Final Deployment

Before completing Phase 3:

1. Have you reviewed sample pages from all lineages?
2. Are you satisfied with the automated CI/CD pipeline?
3. Is the documentation sufficient for ongoing maintenance?
4. Are you ready for full production deployment?
5. Who will be responsible for ongoing maintenance?

---

**Congratulations! With Phase 3 complete, you have a fully automated, modern page generation system for AuntieRuth.com.**
