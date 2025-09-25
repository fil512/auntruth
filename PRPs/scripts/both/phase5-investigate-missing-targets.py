#!/usr/bin/env python3
"""
Phase 5 Script 3: Investigate and Resolve Missing Targets

Problem: Broken links that may actually exist with different names/paths/locations
Investigation: Systematic investigation using docs/README.md naming conventions
and PRPs/fix-link-tips.md methodologies

Strategy:
1. Check File Naming Variations (XF vs XI, case sensitivity, directory variations)
2. Use File System Search (case-insensitive, partial matching)
3. Check Sequential Numbers (gaps analysis)
4. Directory Structure Analysis (lineage directories)

Resolution:
A. Target Found → Fix the Link (preserve functionality)
B. Target Genuinely Missing → Remove Link, Preserve Content

Data Source: PRPs/scripts/reports/broken_links_*_20250925_*.csv
"""

import os
import sys
import re
import csv
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

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

def test_url_with_curl(url: str) -> int:
    """Test URL and return HTTP status code"""
    try:
        result = subprocess.run([
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url
        ], capture_output=True, text=True, timeout=10)
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired):
        return 0

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

def find_file_variations(filename: str, docs_dir: str) -> List[str]:
    """Find file variations using systematic search"""
    variations = []

    # Extract base name and extension
    if '.' in filename:
        base_name, ext = filename.rsplit('.', 1)
        ext = f".{ext}"
    else:
        base_name, ext = filename, ""

    # Strategy 1: Case-insensitive search
    try:
        result = subprocess.run([
            "find", docs_dir, "-iname", filename
        ], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line and os.path.exists(line):
                    variations.append(line)
    except:
        pass

    # Strategy 2: Partial number matching for XF/XI files
    if re.match(r'^(XF|XI|THF?)\d+', base_name):
        prefix = re.match(r'^([A-Z]+)', base_name).group(1)
        number = re.search(r'(\d+)', base_name)
        if number:
            num = number.group(1)

            # Check for XF vs XI variations
            if prefix == "XF":
                xi_variant = f"XI{num}{ext}"
                try:
                    result = subprocess.run([
                        "find", docs_dir, "-name", xi_variant
                    ], capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            if line and os.path.exists(line):
                                variations.append(line)
                except:
                    pass
            elif prefix == "XI":
                xf_variant = f"XF{num}{ext}"
                try:
                    result = subprocess.run([
                        "find", docs_dir, "-name", xf_variant
                    ], capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            if line and os.path.exists(line):
                                variations.append(line)
                except:
                    pass

    # Strategy 3: Sequential number check (nearby files)
    if re.search(r'\d+', base_name):
        try:
            numbers = re.findall(r'\d+', base_name)
            if numbers:
                main_num = int(numbers[-1])  # Use last number found
                base_pattern = re.sub(r'\d+$', '', base_name)

                # Check ±5 around the number
                for offset in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
                    test_num = main_num + offset
                    if test_num > 0:
                        test_filename = f"{base_pattern}{test_num}{ext}"
                        try:
                            result = subprocess.run([
                                "find", docs_dir, "-name", test_filename
                            ], capture_output=True, text=True)
                            if result.returncode == 0:
                                for line in result.stdout.strip().split('\n'):
                                    if line and os.path.exists(line):
                                        variations.append(line)
                        except:
                            continue
        except:
            pass

    # Remove duplicates and return
    return list(set(variations))

def investigate_broken_link(broken_link: Dict, docs_dir: str) -> Tuple[str, str, Optional[str]]:
    """
    Investigate a broken link and return decision.
    Returns: (decision, reason, suggested_fix_path)

    decision: 'fix' or 'remove'
    reason: explanation of the decision
    suggested_fix_path: new path if decision is 'fix', None if 'remove'
    """

    original_link = broken_link['Original_Link_Text']
    broken_url = broken_link['Broken_URL']

    # Extract filename from the original link
    filename = os.path.basename(original_link)

    if not filename or filename == original_link:
        return 'remove', 'Invalid or empty filename', None

    # Skip already processed patterns from previous scripts
    if any(skip_pattern in filename.lower() for skip_pattern in [
        'xf1234.htm',  # Known placeholder - handle in script 4
        'xi2674.htm', 'xi2675.htm',  # Known missing images - handle in script 4
        'birthday.pps',  # Known missing file - handle in script 4
        'hag193', '.avi',  # Known missing media - handle in script 4
    ]):
        return 'remove', 'Known missing content - handle in script 4', None

    # Find file variations
    variations = find_file_variations(filename, docs_dir)

    if not variations:
        # No variations found - genuinely missing
        return 'remove', f'No file variations found for {filename}', None

    # Choose best variation
    best_variation = None

    # Prefer NEW site over HTM site if available
    new_variations = [v for v in variations if '/new/' in v]
    htm_variations = [v for v in variations if '/htm/' in v and '/new/' not in v]

    if new_variations:
        best_variation = new_variations[0]  # Take first NEW site match
    elif htm_variations:
        best_variation = htm_variations[0]  # Fall back to HTM site
    else:
        best_variation = variations[0]  # Take any match

    # Convert file path to URL path
    rel_path = os.path.relpath(best_variation, docs_dir)
    url_path = f"/auntruth/{rel_path}"

    # Test that this URL actually works
    test_url = f"http://localhost:8000{url_path}"
    status = test_url_with_curl(test_url)

    if status == 200:
        return 'fix', f'Found working alternative: {rel_path}', url_path
    else:
        return 'remove', f'Found file {rel_path} but URL returns {status}', None

def fix_broken_link_in_file(file_path: str, original_link: str, new_link: str) -> bool:
    """Fix a broken link in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Replace the href attribute
        old_pattern = f'href="{original_link}"'
        new_pattern = f'href="{new_link}"'

        new_content = content.replace(old_pattern, new_pattern)

        # Also try with single quotes
        old_pattern_single = f"href='{original_link}'"
        new_pattern_single = f"href='{new_link}'"
        new_content = new_content.replace(old_pattern_single, new_pattern_single)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

    except Exception as e:
        print(f"❌ Error fixing link in {file_path}: {e}")

    return False

def remove_broken_link_in_file(file_path: str, original_link: str) -> bool:
    """Remove broken link but preserve content text"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Pattern to match <a href="broken_link">text</a> and replace with just text
        patterns = [
            rf'<a\s+href=["\']?{re.escape(original_link)}["\']?[^>]*>(.*?)</a>',
            rf'<A\s+href=["\']?{re.escape(original_link)}["\']?[^>]*>(.*?)</A>',
        ]

        original_content = content

        for pattern in patterns:
            # Use IGNORECASE and DOTALL to catch multi-line link content
            content = re.sub(pattern, r'\1', content, flags=re.IGNORECASE | re.DOTALL)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"❌ Error removing link in {file_path}: {e}")

    return False

def main():
    parser = argparse.ArgumentParser(description="Investigate missing targets and fix or remove broken links")
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

    print("🔧 Phase 5 Script 3: Investigate and Resolve Missing Targets")
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
    print(f"   Total: {len(all_broken_links)} broken links to investigate")

    if args.limit:
        all_broken_links = all_broken_links[:args.limit]
        print(f"   Limited to: {len(all_broken_links)} links for testing")

    print()

    # Investigate each broken link
    print("🔍 Investigating broken links...")

    decisions = {'fix': [], 'remove': []}

    for i, broken_link in enumerate(all_broken_links):
        if i > 0 and i % 50 == 0:
            print(f"   Progress: {i}/{len(all_broken_links)} links investigated...")

        decision, reason, fix_path = investigate_broken_link(broken_link, args.directory)

        decisions[decision].append({
            'link': broken_link,
            'reason': reason,
            'fix_path': fix_path
        })

    print(f"\n📊 Investigation Results:")
    print(f"   Links to fix: {len(decisions['fix'])}")
    print(f"   Links to remove: {len(decisions['remove'])}")

    if args.dry_run:
        print(f"\n🔍 DRY RUN - Sample decisions:")
        print(f"\n✅ FIXES (first 10):")
        for item in decisions['fix'][:10]:
            original = item['link']['Original_Link_Text']
            filename = os.path.basename(original)
            print(f"   {filename} → {item['fix_path']} ({item['reason']})")

        print(f"\n❌ REMOVALS (first 10):")
        for item in decisions['remove'][:10]:
            original = item['link']['Original_Link_Text']
            filename = os.path.basename(original)
            print(f"   {filename}: {item['reason']}")

        print(f"\n💡 Run without --dry-run to apply changes")
        return

    # Apply fixes
    print(f"\n🔄 Applying link fixes...")
    fixed_count = 0
    removed_count = 0

    def determine_site_directory(source_file: str, broken_url: str) -> str:
        """Determine if this is HTM or NEW site based on URL and source file"""
        if '/new/' in broken_url:
            return 'new'
        elif source_file.startswith('htm/'):
            return 'new'  # NEW site files have htm/ prefix
        else:
            return 'htm'  # HTM site files have no prefix

    # Process fixes
    for item in decisions['fix']:
        broken_link = item['link']
        fix_path = item['fix_path']
        source_file = broken_link['Source_File']

        # Determine correct site directory
        site_dir = determine_site_directory(source_file, broken_link['Broken_URL'])

        if site_dir == 'new' and not source_file.startswith('new/'):
            # NEW site files in CSV are stored as htm/L1/file.htm
            source_file_path = os.path.join(args.directory, 'new', source_file)
        else:
            # HTM site files in CSV are stored as L1/file.htm
            source_file_path = os.path.join(args.directory, 'htm', source_file)

        original_link = broken_link['Original_Link_Text']

        if fix_broken_link_in_file(source_file_path, original_link, fix_path):
            fixed_count += 1
            filename = os.path.basename(original_link)
            print(f"✅ Fixed {filename} → {fix_path} in {source_file}")

    # Process removals
    for item in decisions['remove']:
        broken_link = item['link']
        source_file = broken_link['Source_File']

        # Determine correct site directory
        site_dir = determine_site_directory(source_file, broken_link['Broken_URL'])

        if site_dir == 'new' and not source_file.startswith('new/'):
            # NEW site files in CSV are stored as htm/L1/file.htm
            source_file_path = os.path.join(args.directory, 'new', source_file)
        else:
            # HTM site files in CSV are stored as L1/file.htm
            source_file_path = os.path.join(args.directory, 'htm', source_file)

        original_link = broken_link['Original_Link_Text']

        if remove_broken_link_in_file(source_file_path, original_link):
            removed_count += 1
            filename = os.path.basename(original_link)
            print(f"🗑️  Removed {filename} link (preserved content) in {source_file}")

    # Results summary
    print(f"\n📊 Processing Complete!")
    print(f"   Links fixed: {fixed_count}/{len(decisions['fix'])}")
    print(f"   Links removed: {removed_count}/{len(decisions['remove'])}")
    print(f"   Total actions: {fixed_count + removed_count}")

    if fixed_count + removed_count > 0:
        print(f"\n💾 Commit these changes:")
        print(f"   git add .")
        print(f"   git commit -m 'Phase 5-3: Investigate missing targets - {fixed_count} fixed, {removed_count} removed'")

if __name__ == "__main__":
    main()