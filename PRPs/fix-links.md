# Broken Links Fix Plan

## Analysis Summary

Based on analysis of the broken links reports from 2025-09-23, we have identified systematic issues affecting thousands of links across both the original (`docs/htm/`) and modernized (`docs/new/`) sites.

## Major Issues by Frequency

### 1. Missing XF0.htm - 6,270+ broken links
- **Issue**: XF0.htm doesn't exist in L0 directory but is referenced everywhere as a placeholder for "empty person" slots
- **Impact**: 6,270+ broken links across both sites
- **Fix Strategy**: Remove the anchor tags while preserving any content inside (better UX than creating a placeholder page that says "nothing here")

### 2. CGI Counter References - 797 broken links
- **Issue**: Old CGI counter references using backslashes and obsolete paths
  - `\cgi-bin\counter.pl?AuntRuth` (741 instances)
  - `\AuntRuth\cgi-bin\counter.pl` (56 instances)
- **Impact**: These counters are obsolete technology from the 1990s
- **Fix Strategy**: Remove all CGI counter references entirely

### 3. Path Format Issues - 500+ broken links
- **Issues**:
  - Backslash paths: `./L0\XF0.htm` instead of `./L0/XF0.htm` (198+ instances)
  - Double htm paths: `/auntruth/htm/htm/L0/XI1029.htm`
  - Wrong base paths: `/auntruth/AuntRuth/` instead of `/auntruth/htm/`
- **Fix Strategy**: Batch replace backslashes with forward slashes, fix double paths

### 4. Missing Index Files - All lineages
- **Issue**: L0/index.htm through L9/index.htm don't exist
- **Impact**: Navigation broken for lineage directories
- **Fix Strategy**: Create index.htm files for each lineage directory

### 5. Missing XI Files in Wrong Lineage
- **Examples**:
  - XI2627.htm referenced in L1 but exists as XF2627.htm in L4
  - XI2674.htm, XI2675.htm have similar issues
- **Pattern**: Files exist but in different lineage directories or as XF instead of XI
- **Fix Strategy**: Update references to point to correct lineage directories

### 6. Missing XF533.htm - 114 references
- **Issue**: File is referenced but doesn't exist anywhere
- **Fix Strategy**: Investigate if renamed or create placeholder

### 7. Microsoft Word Artifacts
- **Issue**: Links to temporary Word files
  - `Walter_files/*.mso`
  - `JohnII_files/*.xml`
  - Various `.gif` files in Word temp directories
- **Fix Strategy**: Remove all Microsoft Word temporary file references

## Batch Fix Scripts Required

### Priority 1 - Path Issues
1. **fix-backslash-paths.py**
   - Convert all backslash paths to forward slashes
   - Fix patterns like `./L0\XF0.htm` → `./L0/XF0.htm`
   - Estimated fixes: 500+ links

2. **fix-double-htm-paths.py**
   - Fix `/htm/htm/` double path issues
   - Convert to single `/htm/` path
   - Estimated fixes: 100+ links

### Priority 2 - Obsolete Technology
3. **remove-cgi-counters.py**
   - Remove all CGI counter references
   - Clean up `\cgi-bin\counter.pl` references
   - Estimated fixes: 797 links

### Priority 3 - Handle Missing References
4. **remove-xf0-links.py**
   - Remove anchor tags pointing to XF0.htm
   - Preserve any content inside the tags (usually empty for spouse slots)
   - Estimated fixes: 6,270+ links

5. **create-missing-indexes.py**
   - Create index.htm for each lineage (L0-L9) if missing
   - Handle XF533.htm references (investigate or remove)

### Priority 4 - Lineage References
6. **fix-xi-lineage-refs.py**
   - Update XI references to correct lineage directories
   - Map XI2627.htm → L4/XF2627.htm
   - Handle similar misplaced references

### Priority 5 - Cleanup
7. **remove-word-artifacts.py**
   - Remove all Microsoft Word temporary file references
   - Clean up `_files/` directory references

## Implementation Order

1. **Remove XF0.htm links** (remove anchor tags, preserve content)
2. **Fix path format issues** (backslashes, double paths)
3. **Remove obsolete technology** (CGI counters)
4. **Create missing index files** (L0-L9 index.htm)
5. **Update lineage references** (XI to correct directories)
6. **Clean up artifacts** (Word temporary files)

## Expected Results

- **Total broken links to fix**: ~8,000+
- **Automated fixes possible**: ~7,500
- **Manual investigation needed**: ~500

## Files Most Affected

### Original Site (docs/htm/)
- L2 directory files (heavy XF0.htm references)
- L6 directory files (CGI counter references)
- Various TH*.htm files (image and XI references)

### Modernized Site (docs/new/)
- Similar patterns but with additional backslash path issues
- More instances of `./L*\*.htm` patterns

## Success Metrics

After implementing all fixes:
1. XF0.htm anchor tags removed, content preserved (6,270 fixes)
2. No CGI counter references remain (797 fixes)
3. All paths use forward slashes (500+ fixes)
4. Lineage index pages exist and work
5. XI references point to correct locations

## Notes

- The XI2627.htm issue discovered earlier is part of a larger pattern where XI files are referenced in the wrong lineage directory
- XF0.htm appears to be a placeholder for "empty" person slots in family trees (empty spouse slots) - better to remove the links than create a frustrating "nothing here" page
- CGI counters are obsolete and can be safely removed
- Many issues stem from the original Microsoft Word HTML generation