# Broken Links Fix - Parent PRP

## Current Status
**Latest Scan Results (2025-09-23 19:50):**
- Sites checked: 2
- Total broken links: 84,844 (much higher than initial estimate of 12,280)
- Breakdown by site:
  - docs/htm: 14,242 broken links
  - docs/new: 70,601 broken links
- CSV reports generated:
  - 📄 `/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_htm_20250923_195045.csv`
  - 📄 `/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_new_20250923_195146.csv`

## Step 1: Background
- Current broken links analysis shows 84,844 total broken links across both sites (significantly higher than initially estimated)
- Previous fixes have been completed (items 001-003) but major issues remain
- The majority of broken links (70,601) are in the modernized site (docs/new)

## Step 2: Find next work item
- Find the FIRST INCOMPLETE item from the table in PRPs/tracking/broken-links-fix.csv
- Process only this single item through all steps before moving to the next

## Step 3: Create a new prompt from the template
- Create a PRP in PRPs/generated-prompts/{{ITEM_NUMBER}}-broken-links-fix.md from the prompt template PRPs/templates/broken-links-fix.md, populating the placeholders in that prompt from the row in the csv we are working on.

## Step 4: Update tracking IN PROGRESS
- Mark that item as IN PROGRESS in PRPs/tracking/broken-links-fix.csv

## Step 5: Execute the PRP in subcontext
- Launch a general-purpose agent with the Task tool
- Agent task: "Execute the PRP document PRPs/generated-prompts/{{ITEM_NUMBER}}-broken-links-fix.md"
- **CRITICAL**: Ensure the agent processes BOTH docs/htm AND docs/new directories
- Wait for the agent to complete and return its final report
- Store the final report in PRPs/reports/{{ITEM_NUMBER}}-broken-links-fix-report.md

## Step 6: Validation URLs
- Provide test URLs in localhost format: http://localhost:8000/auntruth/htm/... and http://localhost:8000/auntruth/new/htm/...
- Include representative URLs from BOTH original (docs/htm) and modernized (docs/new) sites
- Wait for user validation before marking complete

## Step 7: Update tracking to COMPLETE
- Mark that item as COMPLETE in PRPs/tracking/broken-links-fix.csv

## Step 8: Repeat for remaining items
- Return to Step 2 and repeat all steps for the next INCOMPLETE item
- Continue until no INCOMPLETE items remain in the tracking file

## Step 9: Create final summary report
- Once all items are COMPLETE, create PRPs/reports/broken-links-fix-summary-report.md
- Include:
  - Overview of all processed items
  - Key outcomes from each individual report
  - Any patterns or issues encountered across items
  - Overall success metrics and recommendations
  - Total number of broken links fixed across all scripts