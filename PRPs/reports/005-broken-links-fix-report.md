## Representative Test URLs for User Validation

I have successfully executed the XI lineage reference fixes on the docs/htm directory. The script fixed **909 XI references in 56 files**, with only 4 remaining broken references (for XI2674 and XI2675 that don't exist anywhere in the system).

**CRITICAL: Please test these representative URLs to validate the fixes:**

### Original Site (docs/htm) - Primary Test URLs:
1. **Main MB page with many XI references:** http://localhost:8000/auntruth/htm/THMB.htm
2. **Winnipeg gallery page:** http://localhost:8000/auntruth/htm/THWinnip.htm
3. **2002 gallery page:** http://localhost:8000/auntruth/htm/TH2002.htm
4. **L0 lineage MB page:** http://localhost:8000/auntruth/htm/L0/THMB.htm
5. **L0 2002 pictures:** http://localhost:8000/auntruth/htm/L0/PICS2002.htm
6. **L1 lineage MB page:** http://localhost:8000/auntruth/htm/L1/THMB.htm
7. **L1 Winnipeg page:** http://localhost:8000/auntruth/htm/L1/THWinnip.htm
8. **L6 lineage MB page:** http://localhost:8000/auntruth/htm/L6/THMB.htm
9. **L7 lineage MB page:** http://localhost:8000/auntruth/htm/L7/THMB.htm

### Example XI Files to Test Direct Access:
10. **XI349 (moved from L1 to L0):** http://localhost:8000/auntruth/htm/L0/XI349.htm
11. **XI432 (verified in L1):** http://localhost:8000/auntruth/htm/L1/XI432.htm

### Modernized Site (docs/new) - No XI Files Present:
The docs/new directory contains no XI files, so all XI references there remain as-is (pointing to the original site).

## Validation Instructions:

1. **Load each test URL** in your browser
2. **Click on various image links** with XI references to verify they work correctly
3. **Look for broken image links or 404 errors** when clicking XI references
4. **Verify that image galleries load properly** and navigation works

**Expected Behavior:** All XI links should now point to the correct lineage directories and load successfully.

**Known Issues:** Only 4 XI references remain broken (XI2674, XI2675) because these files don't exist anywhere in the system.

## Summary of Changes Made:
- **Files modified:** 56 in docs/htm directory
- **XI references fixed:** 909 total
- **Processing time:** 0.41 seconds
- **Remaining broken XI references:** 4 (for non-existent files)
- **Validation results:** 60,281 XI references checked

Please test the URLs above and confirm that the XI links are working correctly before I proceed with committing the changes to git.