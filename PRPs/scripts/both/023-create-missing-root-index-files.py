#!/usr/bin/env python3
"""
Create Missing Root Index Files - Script 023

Problem: Links to /auntruth/index.html (500 refs) and /auntruth/new/index.htm (1506 refs) return 404
Investigation: Files exist as /auntruth/new/index.html and /auntruth/htm/index.html
Solution: Create or link the missing index files to fix thousands of broken links
Expected Impact: ~2006+ broken link fixes (1506 + 500)
Validation: Test URLs before/after, run broken link checker

Based on analysis showing:
- /auntruth/index.html (404 - 500 instances)
- /auntruth/new/index.htm (404 - 1506 instances)
- /auntruth/new/index.html (200 - exists)
- /auntruth/htm/index.html (200 - exists)
"""

import os
import subprocess
import sys
from pathlib import Path

def verify_git_branch(expected_branch: str) -> str:
    """Verify we're on the expected git branch."""
    result = subprocess.run(["git", "branch", "--show-current"],
                          capture_output=True, text=True, check=True)
    current_branch = result.stdout.strip()
    if current_branch != expected_branch:
        print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
    return current_branch

def check_existing_files():
    """Check what index files currently exist."""
    files_to_check = [
        'docs/index.html',
        'docs/index.htm',
        'docs/new/index.html',
        'docs/new/index.htm',
        'docs/htm/index.html',
        'docs/htm/index.htm'
    ]

    existing = []
    missing = []

    for file_path in files_to_check:
        if os.path.exists(file_path):
            existing.append(file_path)
        else:
            missing.append(file_path)

    return existing, missing

def create_simple_redirect_page(source_file: str, target_url: str) -> str:
    """Create a simple HTML redirect page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuntRuth.com - Genealogy Site</title>
    <meta http-equiv="refresh" content="0; url={target_url}">
    <link rel="canonical" href="{target_url}">
</head>
<body>
    <h1>AuntRuth.com Genealogy</h1>
    <p>Redirecting to <a href="{target_url}">the main site</a>...</p>
    <script>
        window.location.href = "{target_url}";
    </script>
</body>
</html>"""

def copy_file_content(source: str, target: str) -> bool:
    """Copy content from source file to target file."""
    try:
        with open(source, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error copying {source} to {target}: {e}")
        return False

def main():
    # Verify we're in the right place
    if not os.path.exists('docs/htm') or not os.path.exists('docs/new'):
        print("Error: Must run from repository root (docs/htm and docs/new should exist)")
        sys.exit(1)

    # Verify git branch
    current_branch = verify_git_branch("fix-broken-links-fix-absolute-htm-paths")

    # Parse arguments
    dry_run = '--no-dry-run' not in sys.argv

    print("🔍 Checking existing index files...")
    existing, missing = check_existing_files()

    print("✅ Existing files:")
    for file in existing:
        print(f"  {file}")

    print("❌ Missing files:")
    for file in missing:
        print(f"  {file}")

    # Identify what needs to be created
    actions = []

    # 1. Create /auntruth/index.html - redirect to the main htm/index.html
    if 'docs/index.html' in missing and 'docs/htm/index.html' in existing:
        actions.append(('redirect', 'docs/index.html', '/auntruth/htm/index.html'))

    # 2. Create /auntruth/new/index.htm - copy from new/index.html
    if 'docs/new/index.htm' in missing and 'docs/new/index.html' in existing:
        actions.append(('copy', 'docs/new/index.htm', 'docs/new/index.html'))

    # Alternative: if new/index.html doesn't exist, redirect to htm
    elif 'docs/new/index.htm' in missing:
        actions.append(('redirect', 'docs/new/index.htm', '/auntruth/htm/index.html'))

    if not actions:
        print("✅ No missing index files need to be created!")
        return

    print(f"\n📋 Planned actions:")
    for action_type, target, source in actions:
        if action_type == 'copy':
            print(f"  📄 Copy {source} → {target}")
        elif action_type == 'redirect':
            print(f"  🔗 Create redirect {target} → {source}")

    if dry_run:
        print("\n✅ Dry run complete. Use --no-dry-run to create files.")
        return

    print(f"\n🔧 Creating missing index files...")
    created_count = 0

    for action_type, target, source in actions:
        try:
            if action_type == 'copy':
                if copy_file_content(source, target):
                    print(f"✅ Copied {source} → {target}")
                    created_count += 1
                else:
                    print(f"❌ Failed to copy {source} → {target}")

            elif action_type == 'redirect':
                redirect_content = create_simple_redirect_page(target, source)
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(redirect_content)
                print(f"✅ Created redirect {target} → {source}")
                created_count += 1

        except Exception as e:
            print(f"❌ Error creating {target}: {e}")

    if created_count > 0:
        print(f"\n✅ Created {created_count} missing index files!")
        print("🔍 Re-run broken link checker to measure improvement.")

        # Test the created files
        print(f"\n🧪 Testing created files...")
        test_urls = [
            'http://localhost:8000/auntruth/index.html',
            'http://localhost:8000/auntruth/new/index.htm'
        ]

        for url in test_urls:
            try:
                import urllib.request
                response = urllib.request.urlopen(url)
                print(f"✅ {url} → {response.getcode()}")
            except Exception as e:
                print(f"❌ {url} → Error: {e}")

if __name__ == "__main__":
    main()