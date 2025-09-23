# Broken Links Fix - Parent PRP

## Step 1: Background
- Read PRPs/fix-links.md to understand the background of our goal.

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
- Wait for the agent to complete and return its final report
- Store the final report in PRPs/reports/{{ITEM_NUMBER}}-broken-links-fix-report.md

## Step 6: Update tracking to COMPLETE
- Mark that item as COMPLETE in PRPs/tracking/broken-links-fix.csv

## Step 7: Repeat for remaining items
- Return to Step 2 and repeat all steps for the next INCOMPLETE item
- Continue until no INCOMPLETE items remain in the tracking file

## Step 8: Create final summary report
- Once all items are COMPLETE, create PRPs/reports/broken-links-fix-summary-report.md
- Include:
  - Overview of all processed items
  - Key outcomes from each individual report
  - Any patterns or issues encountered across items
  - Overall success metrics and recommendations
  - Total number of broken links fixed across all scripts