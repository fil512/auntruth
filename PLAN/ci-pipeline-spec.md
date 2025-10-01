# GitLab CI/CD Pipeline Specification

## Pipeline Overview

Automated page generation pipeline that builds all HTML pages from JSON data and templates on every commit.

## Pipeline Stages

```
┌─────────────┐
│  validate   │  Validate JSON data and templates
└──────┬──────┘
       ↓
┌─────────────┐
│  generate   │  Generate HTML pages from data + templates
└──────┬──────┘
       ↓
┌─────────────┐
│    test     │  Run validation tests on generated pages
└──────┬──────┘
       ↓
┌─────────────┐
│   deploy    │  Deploy to production (main branch only)
└─────────────┘
```

## GitLab CI Configuration

### `.gitlab-ci.yml`

```yaml
# Page Generation CI/CD Pipeline for AuntieRuth.com
# Generates modern HTML pages from JSON data + Jinja2 templates

stages:
  - validate
  - generate
  - test
  - deploy

# Global variables
variables:
  PYTHON_VERSION: "3.11"
  DATA_DIR: "data/people"
  TEMPLATES_DIR: "templates"
  OUTPUT_DIR: "docs/new/htm"

# Cache pip dependencies
cache:
  paths:
    - .cache/pip

# ============================================
# STAGE 1: Validate
# ============================================

validate-json:
  stage: validate
  image: python:${PYTHON_VERSION}
  script:
    - pip install jsonschema pyyaml
    - python3 PRPs/scripts/both/validate_json_data.py
    - echo "✓ Validated $(find ${DATA_DIR} -name '*.json' | wc -l) person records"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

validate-templates:
  stage: validate
  image: python:${PYTHON_VERSION}
  script:
    - pip install jinja2
    - python3 PRPs/scripts/both/validate_templates.py
    - echo "✓ Templates validated successfully"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# ============================================
# STAGE 2: Generate Pages
# ============================================

generate-person-pages:
  stage: generate
  image: python:${PYTHON_VERSION}
  needs:
    - validate-json
    - validate-templates
  script:
    - pip install jinja2 pyyaml
    - python3 PRPs/scripts/both/generate_pages.py --type person
    - echo "✓ Generated person pages"
    - echo "   Total: $(find ${OUTPUT_DIR} -name 'XF*.htm' | wc -l) files"
    - echo "   Size: $(du -sh ${OUTPUT_DIR} | cut -f1)"
  artifacts:
    paths:
      - ${OUTPUT_DIR}/
    expire_in: 1 week
    reports:
      dotenv: generation-stats.env
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

generate-thumbnail-pages:
  stage: generate
  image: python:${PYTHON_VERSION}
  needs:
    - validate-json
    - validate-templates
  script:
    - pip install jinja2 pyyaml
    - python3 PRPs/scripts/both/generate_pages.py --type thumbnail
    - echo "✓ Generated thumbnail pages"
  artifacts:
    paths:
      - ${OUTPUT_DIR}/
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

generate-index-pages:
  stage: generate
  image: python:${PYTHON_VERSION}
  needs:
    - validate-json
    - validate-templates
  script:
    - pip install jinja2 pyyaml
    - python3 PRPs/scripts/both/generate_pages.py --type index
    - echo "✓ Generated lineage index pages"
  artifacts:
    paths:
      - ${OUTPUT_DIR}/
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# ============================================
# STAGE 3: Test Generated Pages
# ============================================

test-html-validity:
  stage: test
  image: python:${PYTHON_VERSION}
  needs:
    - generate-person-pages
    - generate-thumbnail-pages
    - generate-index-pages
  script:
    - pip install html5lib lxml
    - python3 PRPs/scripts/both/validate_generated_pages.py --check html5
    - echo "✓ All pages pass HTML5 validation"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test-data-integrity:
  stage: test
  image: python:${PYTHON_VERSION}
  needs:
    - generate-person-pages
  script:
    - pip install beautifulsoup4 lxml
    - python3 PRPs/scripts/both/validate_generated_pages.py --check data-integrity
    - echo "✓ All person data correctly rendered"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test-links:
  stage: test
  image: python:${PYTHON_VERSION}
  needs:
    - generate-person-pages
    - generate-thumbnail-pages
    - generate-index-pages
  script:
    - python3 PRPs/scripts/both/validate_generated_pages.py --check links
    - echo "✓ All internal links valid"
  allow_failure: true  # Don't block on broken external links
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test-visual-regression:
  stage: test
  image: python:${PYTHON_VERSION}
  needs:
    - generate-person-pages
  script:
    - pip install pillow selenium
    - python3 PRPs/scripts/both/visual_regression_test.py
    - echo "✓ Visual regression tests passed"
  allow_failure: true  # Optional test
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  only:
    changes:
      - templates/**/*
      - docs/new/css/**/*

# ============================================
# STAGE 4: Deploy
# ============================================

deploy-production:
  stage: deploy
  image: alpine:latest
  needs:
    - test-html-validity
    - test-data-integrity
    - test-links
  before_script:
    - apk add --no-cache rsync openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan -H $DEPLOY_HOST >> ~/.ssh/known_hosts
  script:
    - rsync -avz --delete ${OUTPUT_DIR}/ ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}
    - echo "✓ Deployed to production"
  environment:
    name: production
    url: https://auntieruth.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual  # Require manual approval for production deploy
  only:
    - main

# ============================================
# Manual Jobs
# ============================================

regenerate-all:
  stage: generate
  image: python:${PYTHON_VERSION}
  script:
    - pip install jinja2 pyyaml
    - python3 PRPs/scripts/both/generate_pages.py --force-all
    - echo "✓ Force-regenerated all pages"
  artifacts:
    paths:
      - ${OUTPUT_DIR}/
    expire_in: 1 month
  when: manual
  only:
    - main

# ============================================
# Scheduled Jobs
# ============================================

nightly-full-rebuild:
  stage: generate
  image: python:${PYTHON_VERSION}
  script:
    - pip install jinja2 pyyaml
    - python3 PRPs/scripts/both/generate_pages.py --force-all
    - python3 PRPs/scripts/both/validate_generated_pages.py --all-checks
  artifacts:
    paths:
      - ${OUTPUT_DIR}/
      - validation-report.html
    expire_in: 7 days
  only:
    - schedules
```

## Environment Variables

Configure in GitLab CI/CD Settings → Variables:

| Variable | Description | Example | Protected | Masked |
|----------|-------------|---------|-----------|--------|
| `DEPLOY_HOST` | Production server hostname | `auntieruth.com` | ✓ | ✗ |
| `DEPLOY_USER` | SSH user for deployment | `deployer` | ✓ | ✗ |
| `DEPLOY_PATH` | Target directory on server | `/var/www/auntruth/new/htm` | ✓ | ✗ |
| `SSH_PRIVATE_KEY` | SSH key for deployment | `-----BEGIN...` | ✓ | ✓ |

## Pipeline Triggers

### Automatic Triggers

1. **Merge Request** - Run validation and generation on every MR
2. **Main Branch Push** - Full pipeline including tests
3. **Nightly Schedule** - Complete rebuild and validation

### Manual Triggers

1. **Production Deploy** - Manual approval required
2. **Force Regenerate All** - Rebuild all pages from scratch

## Artifacts

Generated artifacts stored for:

- **1 week**: Normal builds (MR, branch pushes)
- **1 month**: Manual regenerations
- **7 days**: Nightly builds

### Artifact Contents

```
artifacts/
├── docs/new/htm/          # Generated HTML pages
├── generation-stats.env   # Build statistics
└── validation-report.html # Test results
```

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Total pipeline time | < 10 minutes | TBD |
| Page generation | < 5 minutes | TBD |
| Validation tests | < 3 minutes | TBD |
| Pages per second | > 10 | TBD |

## Monitoring & Alerts

### Pipeline Failure Notifications

Configure in GitLab Settings → Integrations:

- **Email** - Notify on failure
- **Slack** - #genealogy-deployments channel
- **PagerDuty** - Production failures only

### Metrics to Track

1. **Build Duration Trend** - Detect performance degradation
2. **Failure Rate** - Track reliability
3. **Artifact Size** - Monitor disk usage
4. **Test Coverage** - Ensure quality

## Rollback Strategy

If deployment issues occur:

1. **Immediate**: Revert to previous commit
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Manual**: Re-run previous successful pipeline
   - GitLab UI → Pipelines → Find last green build → Retry deploy job

3. **Emergency**: Manual SSH to server
   ```bash
   ssh deployer@auntieruth.com
   cd /var/www/auntruth/new/htm
   git checkout main^1  # Previous commit
   ```

## Local Development

Developers can run generation locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Generate pages
python3 PRPs/scripts/both/generate_pages.py

# Validate output
python3 PRPs/scripts/both/validate_generated_pages.py

# Preview locally
python3 PRPs/server/server.py
# Visit: http://localhost:8000/auntruth/new/htm/L1/XF100.htm
```

## Optimization Strategies

### 1. Incremental Builds

Only regenerate pages when:
- Person JSON data changes
- Corresponding template changes
- Base template changes (requires full rebuild)

Implementation:
```python
# Check git diff to find changed files
changed_files = get_git_diff()
changed_people = [f for f in changed_files if f.startswith('data/people/')]
# Only regenerate those person pages
```

### 2. Parallel Generation

Use Python multiprocessing:
```python
from multiprocessing import Pool
with Pool(processes=8) as pool:
    pool.map(generate_person_page, person_files)
```

Target: Generate 2,985 pages in < 2 minutes

### 3. Template Compilation Caching

Jinja2 bytecode cache:
```python
from jinja2 import Environment, FileSystemLoader
env = Environment(
    loader=FileSystemLoader('templates'),
    bytecode_cache=FileSystemBytecodeCache('/tmp/jinja_cache'),
    auto_reload=False
)
```

## Security Considerations

1. **No Secrets in Artifacts** - Never include credentials in generated pages
2. **Input Sanitization** - Escape all user-provided data in templates
3. **Artifact Expiration** - Auto-delete old artifacts to save space
4. **Protected Branches** - Only main branch can deploy to production
5. **SSH Key Rotation** - Rotate `SSH_PRIVATE_KEY` every 90 days

## Future Enhancements

- **Preview Environments** - Deploy MRs to staging URLs
- **A/B Testing** - Generate multiple template variants
- **CDN Integration** - Deploy to CloudFlare/Fastly
- **Progressive Updates** - Stream updates to production
- **Analytics Integration** - Embed tracking codes during generation
