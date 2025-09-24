- never chmod python scripts. just execute them as an argument to python3

## CRITICAL: NO BACKUP FILES EVER
**NEVER CREATE BACKUP FILES (.backup, .bak, .orig, etc.) WHEN USING GIT**
- We are in a git repository - git IS our backup system
- Creating .backup files is redundant, wasteful, and creates clutter
- Any script that creates backup files must be immediately fixed
- If you need to preserve state, commit to git first, then make changes
- If a script fails, use `git checkout` to revert changes
- REMOVE any existing backup files immediately upon discovery

## Python Script Guidelines

### Before Writing New Scripts
1. **ALWAYS read PRPs/scripts/README.md first** to check if an existing script can be reused
2. Check the organized subdirectories:
   - `PRPs/scripts/htm/` - scripts for docs/htm directory
   - `PRPs/scripts/new/` - scripts for docs/new directory
   - `PRPs/scripts/both/` - scripts that work with either directory

### When Writing New Python Scripts
- Place scripts in the appropriate subdirectory based on their target:
  - **htm/** - if script works only with docs/htm
  - **new/** - if script works only with docs/new
  - **both/** - if script can work with either directory or has options for both
- Follow the safety protocols and templates documented in PRPs/scripts/README.md
- Update PRPs/scripts/README.md with documentation for any new script
- Never run the link checker yourself. Always ask me to do it.