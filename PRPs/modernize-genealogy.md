### Step 1: Background
- Read PLAN/modernize.md to understand the background of our goal.

### Step 2: Find next work item
- Find the FIRST INCOMPLETE item from the table in PRPs/tracking/modernize-genealogy.csv
- Process only this single item through all steps before moving to the next
- Each item will be completed in its own git branch

### Step 3: Create a new prompt from the template
- Create a PRP in PRPs/generated-prompts/{{ITEM_NUMBER}}-modernize-genealogy.md from the prompt template PRPs/templates/modernize-genealogy.md, populating the placeholders in that prompt from the row in the csv we are working on.

### Step 4: Create git branch and update tracking
- Create feature branch: `git checkout -b task-{{ITEM_NUMBER}}-{{task_name}}`
- Mark that item as IN PROGRESS in PRPs/tracking/modernize-genealogy.csv
- Commit the tracking update: `git add PRPs/tracking/modernize-genealogy.csv && git commit -m "Start task {{ITEM_NUMBER}}: {{task_name}}"`

### Step 5: Execute the PRP in subcontext
- Launch a general-purpose agent with the Task tool
- Agent task: "Execute the PRP document PRPs/generated-prompts/{{ITEM_NUMBER}}-modernize-genealogy.md. IMPORTANT: You MUST read PRPs/scripts/README.md first to check for existing scripts before creating new ones. Work in the current git branch and commit your changes."
- Wait for the agent to complete and return its final report
- Store the final report in PRPs/reports/{{ITEM_NUMBER}}-modernize-genealogy-report.md
- Agent should commit all changes to the feature branch

### Step 6: Review and merge branch
- Review the agent's work in the feature branch
- Test the changes to ensure they work correctly
- **WAIT FOR USER CONFIRMATION** before proceeding
- Once approved by user, merge the branch: `git checkout main && git merge task-{{ITEM_NUMBER}}-{{task_name}}`
- Mark that item as COMPLETE in PRPs/tracking/modernize-genealogy.csv
- Commit the tracking update to main branch
- Delete the feature branch: `git branch -d task-{{ITEM_NUMBER}}-{{task_name}}`

### Step 7: Repeat for remaining items
- Return to Step 2 and repeat all steps for the next INCOMPLETE item
- Each item gets its own feature branch and user review cycle
- Continue until no INCOMPLETE items remain in the tracking file

### Step 8: Create final summary report
- Once all items are COMPLETE, create final branch: `git checkout -b final-summary-report`
- Create PRPs/reports/modernize-genealogy-summary-report.md
- Include:
  - Overview of all processed items
  - Key outcomes from each individual report
  - Any patterns or issues encountered across items
  - Overall success metrics and recommendations
- Commit the summary report
- **WAIT FOR USER CONFIRMATION** before merging to main