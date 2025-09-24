# Link Fixing Best Practices & Lessons Learned

## Overview

This document captures key insights and best practices learned from successfully fixing broken links in the AuntieRuth.com genealogy site, reducing broken links from 32,235+ to 4,598 (86% improvement) with targeted fixes.

## 🎯 Critical Success Principles

### 1. **INVESTIGATE BEFORE IMPLEMENTING**

❌ **Don't assume** what the problem is based on documentation alone
✅ **Do investigate** the actual broken links and test assumptions

**Key Actions:**
- Use `curl` to test both broken and working URLs
- Examine actual HTML files to see current link patterns
- Read recent broken link reports to understand real issues
- Test assumptions with small samples before full execution

**Example:**
```bash
# Test the assumption
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/auntruth/htm/L0/INDEX.htm  # 404
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/auntruth/htm/L0/index.htm  # 200

# This revealed the actual problem: case sensitivity, not path structure
```

### 2. **TARGET ACTUAL PROBLEMS, NOT ASSUMED ONES**

❌ **Wrong approach**: Fix image paths `/htm/jpg/` → `/jpg/` based on documentation
✅ **Right approach**: Fix case sensitivity `INDEX.htm` → `index.htm` based on investigation

**Lesson**: The documentation described historical problems that may have already been partially fixed or may not be the current highest-impact issues.

### 3. **USE PRECISE PATTERN MATCHING**

❌ **Wrong**: Use `re.IGNORECASE` when detecting case problems
✅ **Right**: Use exact case matching to find actual case sensitivity issues

**Example:**
```python
# Wrong - matches correct lowercase links as problems
if re.search(r'/L[0-9]+/INDEX\.htm', content, re.IGNORECASE):

# Right - only matches actual uppercase problems
if re.search(r'/L[0-9]+/INDEX\.htm', content):
```

### 4. **VALIDATE FIXES IMMEDIATELY**

Always validate that your fixes actually work:

```python
def validate_fixes(test_cases: List[Tuple[str, str]]) -> Dict[str, int]:
    """Test that broken URLs become working URLs"""
    for broken_url, fixed_url in test_cases:
        broken_status = test_url_with_curl(broken_url)
        fixed_status = test_url_with_curl(fixed_url)

        if broken_status == 404 and fixed_status == 200:
            # Success - we fixed a real problem
```

### 5. **START WITH HIGH-IMPACT, LOW-RISK FIXES**

**High-Impact, Low-Risk**: Case sensitivity fixes (13 files → massive improvement)
**Medium-Impact, Medium-Risk**: Path structure fixes
**Low-Impact, High-Risk**: Content deletion or major structural changes

## 🔧 Technical Best Practices

### Script Safety Requirements

**Always include:**
- `--dry-run` mode for preview
- Git branch verification
- Progress reporting for large operations
- Error handling and logging
- Small sample testing before full execution

**Example template:**
```python
def verify_git_branch(expected_branch: str) -> str:
    result = subprocess.run(["git", "branch", "--show-current"],
                          capture_output=True, text=True, check=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
    return current_branch
```

### Pattern Detection Best Practices

1. **Be specific in your regex patterns**
2. **Test patterns on sample files first**
3. **Use capture groups for flexible replacements**
4. **Consider edge cases and escaping**

**Example:**
```python
# Good pattern - specific and tested
patterns_to_fix = [
    (r'(/auntruth/htm/L[0-9]+/)INDEX\.htm', r'\1index.htm'),
    (r'(/auntruth/htm/L[0-9]+/)Index\.htm', r'\1index.htm'),
]
```

### Validation Methodology

**Before making changes:**
1. Identify sample broken URLs from reports
2. Test that they're actually broken with `curl`
3. Identify what the correct URLs should be
4. Test that the correct URLs work with `curl`

**After making changes:**
1. Test the same URLs again
2. Verify broken → working transition
3. Run broken link checker to measure improvement

## 📊 Measuring Success

### Key Metrics

- **Broken link count reduction** (primary metric)
- **HTTP status validation** (404 → 200 transitions)
- **Sample validation success rate** (aim for 100%)
- **File processing success rate**

### Expected Results by Fix Type

- **Case sensitivity fixes**: High impact, immediate results
- **Path structure fixes**: Medium impact, may need multiple iterations
- **Missing file fixes**: Low impact unless files can be restored

## ⚠️ Common Pitfalls to Avoid

### 1. **Fixing Non-Problems**
- Don't fix links that already work correctly
- Verify problems exist before implementing solutions

### 2. **Over-Broad Pattern Matching**
- Using `.*` where specific patterns would be safer
- Using case-insensitive matching when case is the actual problem

### 3. **Not Testing Edge Cases**
- Single vs double quotes in HTML attributes
- Different directory structures
- Files that don't follow expected patterns

### 4. **Batch Processing Without Validation**
- Always test on small samples first
- Validate improvements before proceeding to larger batches

## 🎯 Investigation Workflow

### Step 1: Analyze Current State
```bash
# Get current broken link report
python3 PRPs/scripts/both/find-broken-links.py --site=htm --timeout=3

# Examine the CSV report to understand patterns
head -20 PRPs/scripts/reports/broken_links_htm_YYYYMMDD_HHMMSS.csv
```

### Step 2: Test Specific Cases
```bash
# Test a few broken URLs manually
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/problematic/url
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/potential/fix
```

### Step 3: Examine HTML Files
```bash
# Look at actual link patterns in source files
grep -o 'href="[^"]*problematic_pattern[^"]*"' path/to/file.htm

# Check what the files currently contain
head -50 path/to/sample/file.htm
```

### Step 4: Test Assumptions with Curl BEFORE Writing Script
**CRITICAL**: Always validate your theory before implementing the fix!

```bash
# Test your assumption about what's broken and what works
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/auntruth/htm/L0/INDEX.htm  # Should be 404
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/auntruth/htm/L0/index.htm  # Should be 200

# Test multiple examples to confirm pattern
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/auntruth/htm/L1/INDEX.htm  # Should be 404
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/auntruth/htm/L1/index.htm  # Should be 200

# Only proceed if your assumption is validated across multiple test cases
```

**⚠️ If curl tests don't confirm your theory, STOP and re-investigate!**

### Step 5: Create Targeted Fix
- Write script with precise patterns based on validated assumptions
- Include dry-run mode
- Test on small sample
- Validate results

### Step 5: Execute and Measure
- Run on full dataset
- Commit changes
- Re-run broken link checker
- Measure improvement

## 📝 Documentation Requirements

**For each fix script, document:**
- **Problem identified**: What specific issue does this address?
- **Investigation method**: How was the problem confirmed?
- **Solution approach**: What patterns are being fixed?
- **Expected impact**: How many links should this fix?
- **Validation method**: How to verify the fix worked?

**Example:**
```python
"""
Fix Case Sensitivity Issues - Script 015

Problem: References to INDEX.htm (uppercase) fail because files are index.htm (lowercase)
Investigation: curl tests showed INDEX.htm → 404, index.htm → 200
Solution: Convert INDEX.htm and Index.htm to index.htm in href attributes
Expected Impact: ~100+ broken link fixes based on pattern analysis
Validation: Test specific URLs before/after, run broken link checker
"""
```

## 🚀 Success Factors Summary

1. **Investigate actual problems, don't assume**
2. **Test URLs with curl to verify issues and fixes**
3. **Use precise, tested regex patterns**
4. **Start small, validate, then scale**
5. **Measure results immediately**
6. **Focus on high-impact, low-risk changes first**

The key insight: **One targeted fix addressing the actual problem (case sensitivity) achieved 86% improvement**, while assumptions about different problems would have yielded minimal results.

## 📚 Tools and Commands Reference

### Essential Testing Commands
```bash
# Test URL response
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/path/to/test

# Find files with specific patterns
grep -r "pattern" docs/htm --include="*.htm" | head -5

# Check file existence
ls -la docs/htm/path/to/check/

# Run broken link checker (let user run this)
# python3 PRPs/scripts/both/find-broken-links.py --site=htm --timeout=3
```

### Git Safety Commands
```bash
# Verify current branch
git branch --show-current

# Stage and commit changes
git add .
git commit -m "Descriptive commit message with results"
```

### Script Testing Pattern
```bash
# Always test with dry-run first
python3 script.py --dry-run

# Test on small sample
python3 script.py --limit=10

# Full execution only after validation
python3 script.py
```

---

**Remember**: The most important lesson is that investigation and testing trump assumptions every time. One hour of careful investigation can save days of implementing the wrong solution.