#!/usr/bin/env python3
"""
Phase 5 Script 4: Remove Confirmed Missing Content

Problem: Links to content that is confirmed genuinely missing after investigation
Investigation: These items have been verified as missing through systematic search

Confirmed Missing Content:
- XF1234.htm (22 references) - obvious sequential placeholder ID
- XI2674.htm, XI2675.htm - confirmed missing photo detail pages (verified in sequence)
- .avi video files (hag1938.avi, hag1946.avi, etc.) - confirmed genuinely missing
- Birthday.pps PowerPoint file - confirmed missing
- Missing index files (/auntruth/index*.htm)

Resolution: Remove only anchor tags, preserve all text content
Example: <a href="missing.htm">Person Name</a> → Person Name

Data Source: PRPs/scripts/reports/broken_links_*_20250925_*.csv
"""

import os
import sys
import re
import csv
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Add the project root to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def verify_git_branch(expected_branch: str = None) -> str:
    """Verify and return current git branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True,
                              cwd=Path(__file__).parent.parent.parent)
        current_branch = result.stdout.strip()
        if expected_branch and current_branch != expected_branch:
            print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking git branch: {e}")
        return "unknown"

def load_broken_links_from_csv(csv_file: str) -> List[Dict]:
    """Load broken links from CSV file"""
    broken_links = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                broken_links.append(row)
    except Exception as e:
        print(f"❌ Error reading CSV file {csv_file}: {e}")
    return broken_links

def is_confirmed_missing(original_link: str) -> Tuple[bool, str]:
    """
    Check if this link is confirmed missing content that should be removed.
    Returns: (is_confirmed_missing, reason)
    """

    filename = os.path.basename(original_link).lower()

    # Confirmed placeholder links
    if 'xf1234.htm' in filename:
        return True, 'XF1234.htm - confirmed placeholder ID'

    # Confirmed missing photo detail pages
    if filename in ['xi2674.htm', 'xi2675.htm']:
        return True, f'{filename.upper()} - confirmed missing photo detail page'

    # Confirmed missing media files
    if filename.endswith('.avi'):
        return True, f'{filename} - confirmed missing video file'

    if 'birthday.pps' in filename:
        return True, 'Birthday.pps - confirmed missing PowerPoint file'

    # Missing index files at root level
    if '/auntruth/index' in original_link and original_link.endswith('.htm'):
        index_filename = os.path.basename(original_link)
        if re.match(r'index\d*\.htm', index_filename):
            return True, f'{index_filename} - confirmed missing index file'

    return False, 'Not confirmed missing'

def remove_link_preserve_content(file_path: str, original_link: str) -> Tuple[bool, str]:
    """
    Remove broken link but preserve content text.
    Returns: (success, details)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Escape special regex characters in the link
        escaped_link = re.escape(original_link)

        # Pattern to match <a href="broken_link">text</a> and replace with just text
        patterns = [
            # Case 1: <a href="link">text</a>
            rf'<a\s+href=["\']?{escaped_link}["\']?[^>]*>(.*?)</a>',
            # Case 2: <A href="link">text</A> (uppercase)
            rf'<A\s+href=["\']?{escaped_link}["\']?[^>]*>(.*?)</A>',
            # Case 3: href first, then other attributes
            rf'<a\s+[^>]*href=["\']?{escaped_link}["\']?[^>]*>(.*?)</a>',
            rf'<A\s+[^>]*href=["\']?{escaped_link}["\']?[^>]*>(.*?)</A>',
        ]

        removals_made = []

        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, content, flags=re.IGNORECASE | re.DOTALL)

            if matches:
                # Replace the link with just the content
                new_content = re.sub(pattern, r'\1', content, flags=re.IGNORECASE | re.DOTALL)
                if new_content != content:
                    content = new_content
                    removals_made.append(f"Pattern {i+1}: {len(matches)} instances")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, '; '.join(removals_made)
        else:
            return False, 'No matching link patterns found'

    except Exception as e:
        return False, f'Error: {str(e)}'

def determine_site_directory(source_file: str, broken_url: str) -> str:
    """Determine if this is HTM or NEW site based on URL and source file"""
    if '/new/' in broken_url:
        return 'new'
    elif source_file.startswith('htm/'):
        return 'new'  # NEW site files have htm/ prefix
    else:
        return 'htm'  # HTM site files have no prefix

def main():
    parser = argparse.ArgumentParser(description="Remove confirmed missing content while preserving text")
    parser.add_argument("--directory", default="/home/ken/wip/fam/auntruth/docs",
                       help="Target directory to process")
    parser.add_argument("--htm-csv",
                       default="/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_htm_20250925_001222.csv",
                       help="HTM site broken links CSV file")
    parser.add_argument("--new-csv",
                       default="/home/ken/wip/fam/auntruth/PRPs/scripts/reports/broken_links_new_20250925_001324.csv",
                       help="NEW site broken links CSV file")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be changed without making changes")
    parser.add_argument("--limit", type=int,
                       help="Limit processing to N links (for testing)")

    args = parser.parse_args()

    print("🔧 Phase 5 Script 4: Remove Confirmed Missing Content")
    print("=" * 60)

    # Verify git branch
    current_branch = verify_git_branch()
    print(f"📂 Current git branch: {current_branch}")
    print(f"📁 Target directory: {args.directory}")
    print(f"🔍 Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print()

    # Load broken links from both CSV files
    print("📄 Loading broken links from CSV files...")
    htm_links = load_broken_links_from_csv(args.htm_csv)
    new_links = load_broken_links_from_csv(args.new_csv)

    all_broken_links = htm_links + new_links
    print(f"   HTM site: {len(htm_links)} broken links")
    print(f"   NEW site: {len(new_links)} broken links")
    print(f"   Total: {len(all_broken_links)} broken links loaded")

    # Filter for confirmed missing content only
    confirmed_missing = []
    for link in all_broken_links:
        original_link = link['Original_Link_Text']
        is_missing, reason = is_confirmed_missing(original_link)
        if is_missing:
            confirmed_missing.append((link, reason))

    print(f"   Confirmed missing: {len(confirmed_missing)} links")

    if args.limit:
        confirmed_missing = confirmed_missing[:args.limit]
        print(f"   Limited to: {len(confirmed_missing)} links for testing")

    print()

    if not confirmed_missing:
        print("✅ No confirmed missing content found to remove!")
        return

    if args.dry_run:
        print(f"🔍 DRY RUN - Confirmed missing content to remove:")
        for link_data, reason in confirmed_missing:
            original_link = link_data['Original_Link_Text']
            source_file = link_data['Source_File']
            filename = os.path.basename(original_link)
            print(f"   {filename} in {source_file}: {reason}")

        print(f"\n💡 Run without --dry-run to remove {len(confirmed_missing)} confirmed missing links")
        return

    # Process confirmed missing content removals
    print(f"🔄 Removing confirmed missing content...")

    removed_count = 0
    processed_files = set()

    for link_data, reason in confirmed_missing:
        source_file = link_data['Source_File']
        original_link = link_data['Original_Link_Text']

        # Determine correct site directory and construct path
        site_dir = determine_site_directory(source_file, link_data['Broken_URL'])

        if site_dir == 'new' and not source_file.startswith('new/'):
            # NEW site files in CSV are stored as htm/L1/file.htm
            source_file_path = os.path.join(args.directory, 'new', source_file)
        else:
            # HTM site files in CSV are stored as L1/file.htm
            source_file_path = os.path.join(args.directory, 'htm', source_file)

        # Skip if file doesn't exist
        if not os.path.exists(source_file_path):
            continue

        success, details = remove_link_preserve_content(source_file_path, original_link)

        if success:
            removed_count += 1
            filename = os.path.basename(original_link)
            print(f"🗑️  Removed {filename} in {source_file}: {reason} ({details})")
            processed_files.add(source_file_path)

    # Results summary
    print(f"\n📊 Processing Complete!")
    print(f"   Confirmed missing links processed: {len(confirmed_missing)}")
    print(f"   Links successfully removed: {removed_count}")
    print(f"   Files modified: {len(processed_files)}")

    if removed_count > 0:
        print(f"\n🔧 Content Preservation Summary:")
        print(f"   - All text content preserved")
        print(f"   - Only anchor tags removed")
        print(f"   - No information loss")

        print(f"\n💾 Commit these changes:")
        print(f"   git add .")
        print(f"   git commit -m 'Phase 5-4: Remove confirmed missing content - {removed_count} links cleaned'")

    else:
        print("ℹ️  No changes made - all confirmed missing links may have been processed already")

if __name__ == "__main__":
    main()