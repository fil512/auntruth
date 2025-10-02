# Page Generation System - Operations Runbook

## Table of Contents

- [Emergency Procedures](#emergency-procedures)
- [Pipeline Failures](#pipeline-failures)
- [Monitoring](#monitoring)
- [Routine Maintenance](#routine-maintenance)
- [Deployment Procedures](#deployment-procedures)
- [Rollback Procedures](#rollback-procedures)
- [Contact Information](#contact-information)

---

## Emergency Procedures

### Immediate Rollback (< 5 minutes)

If generated pages have critical issues in production:

```bash
# 1. Revert last commit
git revert HEAD
git commit -m "Emergency rollback: reverting problematic changes"
git push origin main

# CI will auto-deploy previous version within 10 minutes
```

### Manual Rollback (if CI is down)

```bash
# 1. SSH to production server
ssh deployer@auntieruth.com

# 2. Deploy from backup
cd /var/www/auntruth/backups
rsync -avz $(ls -t | head -1)/ /var/www/auntruth/new/htm/

# 3. Verify deployment
curl -I https://auntieruth.com/auntruth/new/htm/L1/XF100.htm
# Should return: 200 OK
```

### Selective Rollback (single lineage)

```bash
# Revert specific lineage only
git checkout HEAD~1 -- docs/new/htm/L2/
git checkout HEAD~1 -- data/people/Nelson/

git commit -m "Rollback: Nelson lineage only"
git push origin main
```

---

## Pipeline Failures

### Stage: validate-json

**Symptom**: JSON schema validation fails

**Diagnosis**:
```bash
# Check which files failed
cat data/phase3-combined-validation-report.md

# Validate specific lineage
python3 PRPs/scripts/both/validate_json_data.py \
    --input-dir data/people/Hagborg-Hansson \
    --report data/validation-debug.md
```

**Fix**:
1. Review validation report for specific errors
2. Fix JSON files with schema violations
3. Common issues:
   - Missing required fields (`id`, `name`, `lineage`)
   - Invalid ID format (must be `XF\d+`)
   - Invalid field types (e.g., spouses must be array)
4. Re-validate locally: `python3 PRPs/scripts/both/validate_json_data.py --input-dir data/people/{lineage}`
5. Commit fixes and re-run pipeline

### Stage: validate-templates

**Symptom**: Template syntax validation fails

**Diagnosis**:
```bash
# Test template syntax manually
python3 << 'EOF'
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('person.html')  # Replace with failing template
print("Template is valid")
EOF
```

**Fix**:
1. Check template for Jinja2 syntax errors
2. Common issues:
   - Unclosed blocks ({% raw %}`{% if %}`{% endraw %} without {% raw %}`{% endif %}`{% endraw %})
   - Missing macro arguments
   - Invalid template inheritance
3. Verify template compiles locally
4. Commit fixes and re-run pipeline

### Stage: generate-all-lineages

**Symptom**: Page generation fails

**Diagnosis**:
```bash
# Run generation manually with verbose logging
python3 PRPs/scripts/both/generate_pages.py \
    --lineage Hagborg-Hansson \
    --input-dir data/people/Hagborg-Hansson \
    --output-dir test-output \
    --verbose
```

**Fix**:
1. Check error messages for specific failures
2. Common issues:
   - Missing JSON files for linked people
   - Template rendering errors (undefined variables)
   - File permission issues
   - Disk space exhausted
3. Fix underlying issue
4. Test locally first
5. Commit and re-run pipeline

**Timeout**:
- Pipeline has 30-minute timeout for generation
- If timing out consistently, check performance:
  ```bash
  time python3 PRPs/scripts/both/generate_pages.py --lineage Lathrop-Lothropp ...
  # Should complete in < 2 minutes for 686 files
  ```

### Stage: test-html-validity

**Symptom**: HTML validation fails

**Diagnosis**:
- Check CI logs for specific HTML errors
- Most common: malformed HTML, unclosed tags

**Fix**:
1. Review template that generates invalid HTML
2. Fix template syntax
3. Test with sample person locally
4. Commit template fixes

**Note**: This stage is `allow_failure: true` - warnings won't block pipeline

### Stage: test-data-integrity

**Symptom**: Data not rendering correctly in generated pages

**Diagnosis**:
```bash
# Check specific person's data rendering
python3 << 'EOF'
import json
from pathlib import Path
from bs4 import BeautifulSoup

person_id = "XF100"
lineage = "Hagborg-Hansson"

# Load JSON
with open(f'data/people/{lineage}/{person_id}.json') as f:
    person = json.load(f)

# Load generated HTML
with open(f'docs/new/htm/L1/{person_id}.htm') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Check if name appears
if person['name'] in soup.get_text():
    print(f"✓ {person['name']} found in HTML")
else:
    print(f"✗ {person['name']} NOT found in HTML")
EOF
```

**Fix**:
1. Verify JSON data is correct
2. Check template renders the field
3. Test locally with verbose output
4. Fix template or data as needed

### Stage: deploy-production

**Symptom**: SSH connection fails

**Diagnosis**:
```bash
# Test SSH connection manually
ssh deployer@auntieruth.com

# If fails, check:
# 1. SSH key in GitLab CI variables (Settings → CI/CD → Variables)
# 2. SSH key permissions on server
# 3. Network connectivity
```

**Fix**:
1. Verify `SSH_PRIVATE_KEY` variable is set in GitLab
2. Ensure key has proper permissions: `chmod 600 ~/.ssh/id_rsa`
3. Test key works: `ssh -i /path/to/key deployer@auntieruth.com`
4. Update GitLab CI variable if key changed
5. Re-run deploy job

**Symptom**: Rsync fails

**Diagnosis**:
```bash
# Test rsync manually
rsync -avz --dry-run docs/new/htm/ deployer@auntieruth.com:/var/www/auntruth/new/htm/
```

**Fix**:
1. Check disk space on server: `df -h /var/www`
2. Verify permissions: `ls -la /var/www/auntruth/new`
3. Ensure rsync installed on server
4. Check network bandwidth/stability

---

## Monitoring

### Daily Checks

**Automated** (should be green):
```bash
# 1. Check CI pipeline status
# GitLab UI → Pipelines → Latest should be ✓ Passed

# 2. Check for errors in server logs
ssh deployer@auntieruth.com \
    "grep ERROR /var/log/nginx/error.log | grep auntruth | tail -20"

# 3. Spot-check random pages
curl -I https://auntieruth.com/auntruth/new/htm/L1/XF100.htm
curl -I https://auntieruth.com/auntruth/new/htm/L4/XF1199.htm
# Both should return: 200 OK
```

**Manual** (weekly):
- Review nightly build artifacts in GitLab
- Check validation reports for trends
- Monitor artifact disk usage

### Weekly Checks

```bash
# 1. Review nightly build artifacts
# GitLab UI → Pipelines → Scheduled → Latest → Artifacts

# 2. Run comprehensive link check (if available)
python3 PRPs/scripts/both/linkchecker.py

# 3. Check server disk space
ssh deployer@auntieruth.com "df -h"

# 4. Review validation trends
cat data/phase3-combined-validation-report.md
# Look for: declining success rates, new error patterns
```

### Monthly Tasks

- Review and archive old CI artifacts (GitLab Settings → CI/CD → Artifacts)
- Rotate SSH deployment keys (generate new, update GitLab variable, deploy to server)
- Performance audit:
  ```bash
  # Check CI pipeline duration trends
  # Goal: < 10 minutes end-to-end
  ```
- User feedback review (check for reported issues)

### Alerts to Monitor

Set up notifications for:
- ❌ CI pipeline failures (GitLab Settings → Integrations → Email/Slack)
- ⚠️  Disk space < 20% on server
- ⚠️  Validation success rate < 95%
- ❌ Nightly build failures
- ❌ Production deployment failures

---

## Routine Maintenance

### Updating Dependencies

```bash
# 1. Check for outdated packages
pip list --outdated

# 2. Update requirements.txt
vim requirements.txt

# 3. Test locally
pip install -r requirements.txt
python3 PRPs/scripts/both/validate_all_lineages.py
python3 PRPs/scripts/both/generate_pages.py --lineage Hagborg-Hansson ...

# 4. Commit and test in CI
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

### Adding New Lineage

```bash
# 1. Create lineage directory
mkdir -p data/people/NewLineage

# 2. Extract data
python3 PRPs/scripts/both/extract_person_data.py \
    --lineage NewLineage \
    --input-dir docs/new/htm/LX \
    --output-dir data/people/NewLineage

# 3. Update .gitlab-ci.yml
# Add case in lineage mapping:
#   "NewLineage") output_subdir="LX" ;;

# 4. Update PLAN/lineage-mapping.md

# 5. Test generation locally
python3 PRPs/scripts/both/generate_pages.py \
    --lineage NewLineage \
    --input-dir data/people/NewLineage \
    --output-dir docs/new/htm/LX

# 6. Validate
python3 PRPs/scripts/both/validate_json_data.py \
    --input-dir data/people/NewLineage

# 7. Commit and push
git add .
git commit -m "Add NewLineage lineage"
git push origin main
```

### Regenerating Single Lineage

```bash
# 1. Trigger manual job in GitLab UI
# Pipelines → Run Pipeline → regenerate-all-pages

# OR run locally:
python3 PRPs/scripts/both/generate_pages.py \
    --lineage Hagborg-Hansson \
    --input-dir data/people/Hagborg-Hansson \
    --output-dir docs/new/htm/L1

# 2. Commit and push
git add docs/new/htm/L1/
git commit -m "Regenerate Hagborg-Hansson lineage"
git push origin main
```

---

## Deployment Procedures

### Standard Deployment (Automated)

1. Make changes to data or templates
2. Commit and push to main branch
3. CI pipeline runs automatically:
   - Validates JSON and templates
   - Generates all pages
   - Runs tests
4. Review CI logs
5. Manually trigger `deploy-production` job in GitLab UI
6. Verify deployment:
   ```bash
   curl -I https://auntieruth.com/auntruth/new/htm/L1/XF100.htm
   ```

### Emergency Hotfix

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-fix

# 2. Make minimal fix
vim data/people/Hagborg-Hansson/XF100.json

# 3. Test locally
python3 PRPs/scripts/both/validate_json_data.py --input data/people/Hagborg-Hansson/XF100.json
python3 PRPs/scripts/both/generate_pages.py --input data/people/Hagborg-Hansson/XF100.json --output test-output/XF100.htm

# 4. Commit and push
git add .
git commit -m "Hotfix: critical data correction for XF100"
git push origin hotfix/critical-fix

# 5. Merge to main immediately (skip MR if critical)
git checkout main
git merge hotfix/critical-fix
git push origin main

# 6. Monitor CI and trigger deploy
```

### Scheduled Deployment

Nightly rebuilds run automatically at 2 AM (configured in GitLab Schedules).

To modify schedule:
1. GitLab UI → CI/CD → Schedules
2. Edit "Nightly full rebuild"
3. Change cron pattern (default: `0 2 * * *`)

---

## Rollback Procedures

### Full Site Rollback

```bash
# Method 1: Git revert (preferred)
git revert HEAD
git commit -m "Rollback: reverting to previous stable version"
git push origin main
# Wait for CI to deploy (~10 minutes)

# Method 2: Manual deployment from backup
ssh deployer@auntieruth.com
cd /var/www/auntruth/backups
rsync -avz YYYYMMDD-HHMM/ /var/www/auntruth/new/htm/

# Method 3: Re-run previous pipeline
# GitLab UI → Pipelines → Find last good build → Retry → deploy-production
```

### Partial Rollback (Single Lineage)

```bash
# Rollback just one lineage directory
git checkout HEAD~1 -- docs/new/htm/L2/
git checkout HEAD~1 -- data/people/Nelson/
git commit -m "Rollback: Nelson lineage to previous version"
git push origin main
```

### Data-Only Rollback

```bash
# Rollback JSON data but keep templates
git checkout HEAD~1 -- data/people/
git commit -m "Rollback: data only"
git push origin main
```

---

## Contact Information

### Escalation Path

1. **Primary Contact**: Repository Owner
2. **Server Admin**: [Server Administrator Name/Email]
3. **On-Call**: [On-call contact/phone]

### External Services

- **GitLab**: https://gitlab.com/[project-path]
- **Server**: ssh deployer@auntieruth.com
- **Production Site**: https://auntieruth.com

### Documentation Links

- Developer Guide: `docs/GENERATION-SYSTEM.md`
- CI Pipeline Spec: `PLAN/ci-pipeline-spec.md`
- Data Schema: `PLAN/data-schema.md`
- Lineage Mapping: `PLAN/lineage-mapping.md`

---

## Appendix: Common Commands

### Validation

```bash
# Validate all lineages
python3 PRPs/scripts/both/validate_all_lineages.py

# Validate single lineage
python3 PRPs/scripts/both/validate_json_data.py --input-dir data/people/Hagborg-Hansson

# Validate single file
python3 PRPs/scripts/both/validate_json_data.py --input data/people/Hagborg-Hansson/XF100.json
```

### Generation

```bash
# Generate all lineages
for lineage_dir in data/people/*/; do
    lineage_name=$(basename "$lineage_dir")
    # ... (see docs/GENERATION-SYSTEM.md for full script)
done

# Generate single lineage
python3 PRPs/scripts/both/generate_pages.py \
    --lineage Hagborg-Hansson \
    --input-dir data/people/Hagborg-Hansson \
    --output-dir docs/new/htm/L1

# Generate single person
python3 PRPs/scripts/both/generate_pages.py \
    --input data/people/Hagborg-Hansson/XF100.json \
    --output docs/new/htm/L1/XF100.htm
```

### Deployment

```bash
# Deploy to production (manual)
rsync -avz --delete docs/new/htm/ deployer@auntieruth.com:/var/www/auntruth/new/htm/

# Check deployment
curl -I https://auntieruth.com/auntruth/new/htm/L1/XF100.htm
```

---

**Last Updated**: Phase 3 Complete (October 2025)

**Status**: Production operations runbook for 3,004-page automated generation system
