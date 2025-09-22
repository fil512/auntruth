# Modernize Genealogy Site Task: {{task_name}}

## Task Overview
**Item:** {{item_number}}
**Task:** {{task_name}}
**Description:** {{description}}

## Background Context
This is part of modernizing a genealogy website (AuntieRuth.com) for GitHub Pages. The site contains ~11,000 HTML files with family history data from 2002-2005 that need to be updated for modern web standards and GitHub Pages compatibility.

## Current Issue
{{description}}

## Target Directory
Work in: `{{target_directory}}`

## Search Pattern
Look for: `{{search_pattern}}`

## Your Task
1. **Analyze the scope**: Search for all instances of the pattern `{{search_pattern}}` in `{{target_directory}}`
2. **Plan the changes**: Create a strategy for fixing these instances
3. **Implement fixes**: Make the necessary changes to modernize the code
4. **Verify results**: Ensure changes work correctly and don't break functionality
5. **Report findings**: Document what was changed and any issues encountered

## Specific Requirements
- Maintain backward compatibility where possible
- Ensure all paths work correctly on GitHub Pages (case-sensitive, static hosting)
- Remove any server-side dependencies (CGI, Java applets, etc.)
- Use modern web standards (UTF-8, proper DOCTYPE, etc.)
- Keep the genealogical content and structure intact

## Success Criteria
- All instances of `{{search_pattern}}` are properly addressed
- No broken links or missing resources
- Changes are compatible with GitHub Pages static hosting
- HTML remains valid and functional

## Report Format
At the end, provide:
1. **Files Modified**: List of all files changed
2. **Changes Made**: Summary of what was fixed
3. **Issues Found**: Any problems encountered
4. **Verification**: How you tested the changes
5. **Recommendations**: Any follow-up actions needed