#!/usr/bin/env python3
"""
Analyze Broken Links - Pattern Detection Script

This script comprehensively analyzes broken link CSV reports to identify patterns
that can be fixed systematically with targeted scripts.
"""

import csv
import argparse
from collections import Counter, defaultdict
from urllib.parse import urlparse
from pathlib import Path
import re
import os

def analyze_patterns(csv_file: str):
    """Analyze all patterns in the broken links CSV file."""
    print(f"\n=== ANALYZING {csv_file} ===")

    data = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    print(f"Total broken links: {len(data)}")

    # Pattern 1: Missing file analysis
    missing_files = Counter()
    source_file_patterns = Counter()
    broken_url_patterns = Counter()
    original_link_patterns = Counter()
    issue_types = Counter()

    # Pattern 2: Directory structure issues
    path_issues = defaultdict(list)

    # Pattern 3: Case sensitivity issues
    case_issues = []

    # Pattern 4: Relative vs absolute path issues
    relative_path_issues = []

    for row in data:
        broken_url = row['Broken_URL']
        source_file = row['Source_File']
        original_link = row['Original_Link_Text']
        issue_type = row['Issue_Type']

        # Count issue types
        issue_types[issue_type] += 1

        # Extract URL components
        parsed = urlparse(broken_url)
        path = parsed.path

        # Analyze missing files
        filename = path.split('/')[-1]
        missing_files[filename] += 1

        # Analyze source file patterns
        source_dir = '/'.join(source_file.split('/')[:-1]) if '/' in source_file else 'root'
        source_file_patterns[source_dir] += 1

        # Analyze broken URL patterns
        broken_path = '/'.join(path.split('/')[:-1])
        broken_url_patterns[broken_path] += 1

        # Analyze original link patterns
        original_link_patterns[original_link] += 1

        # Check for case sensitivity issues
        if 'INDEX' in filename or filename.endswith('.HTM'):
            case_issues.append(row)

        # Check for relative path issues
        if original_link.startswith('../') or not original_link.startswith('/'):
            relative_path_issues.append(row)

        # Directory structure analysis
        if '/L' in path:
            lineage_match = re.search(r'/L(\d+)/', path)
            if lineage_match:
                lineage = lineage_match.group(1)
                path_issues[f'L{lineage}'].append(row)

    # Report findings
    print("\n📊 ISSUE TYPE DISTRIBUTION:")
    for issue_type, count in issue_types.most_common():
        print(f"  {issue_type}: {count}")

    print("\n📁 TOP MISSING FILES (showing top 20):")
    for filename, count in missing_files.most_common(20):
        print(f"  {filename}: {count} references")

    print("\n📂 SOURCE FILE DIRECTORIES (showing top 15):")
    for dir_pattern, count in source_file_patterns.most_common(15):
        print(f"  {dir_pattern}: {count} broken links")

    print("\n🔗 BROKEN URL PATH PATTERNS (showing top 15):")
    for url_pattern, count in broken_url_patterns.most_common(15):
        print(f"  {url_pattern}: {count} broken links")

    print("\n⚠️  CASE SENSITIVITY ISSUES:")
    if case_issues:
        case_files = Counter()
        for issue in case_issues:
            filename = issue['Broken_URL'].split('/')[-1]
            case_files[filename] += 1

        for filename, count in case_files.most_common(10):
            print(f"  {filename}: {count} references")
    else:
        print("  No obvious case sensitivity issues found")

    print("\n🔄 RELATIVE PATH ISSUES:")
    if relative_path_issues:
        rel_patterns = Counter()
        for issue in relative_path_issues:
            rel_patterns[issue['Original_Link_Text']] += 1

        print(f"  Total relative path issues: {len(relative_path_issues)}")
        for pattern, count in rel_patterns.most_common(10):
            print(f"    {pattern}: {count} times")
    else:
        print("  No relative path issues found")

    print("\n📍 LINEAGE DIRECTORY ISSUES:")
    for lineage, issues in sorted(path_issues.items()):
        if len(issues) > 5:  # Only show significant patterns
            print(f"  {lineage}: {len(issues)} broken links")
            # Show most common files in this lineage
            lineage_files = Counter()
            for issue in issues:
                filename = issue['Broken_URL'].split('/')[-1]
                lineage_files[filename] += 1
            for filename, count in lineage_files.most_common(3):
                print(f"    {filename}: {count} times")

    # Specific pattern analysis
    print("\n🎯 SPECIFIC FIXABLE PATTERNS:")

    # Pattern: XF533.htm in L1 directory
    xf533_pattern = [row for row in data if 'XF533.htm' in row['Broken_URL']]
    if xf533_pattern:
        print(f"  XF533.htm missing in L1: {len(xf533_pattern)} references")

    # Pattern: INDEX files with wrong case
    index_case_pattern = [row for row in data if '/INDEX' in row['Broken_URL'] and row['Broken_URL'].endswith('.htm')]
    if index_case_pattern:
        print(f"  INDEX.htm case issues: {len(index_case_pattern)} references")

    # Pattern: Missing index files in /auntruth/
    index_missing_pattern = [row for row in data if row['Broken_URL'].endswith('index.htm') and '/auntruth/index' in row['Broken_URL']]
    if index_missing_pattern:
        print(f"  Missing index files in /auntruth/: {len(index_missing_pattern)} references")

    # Pattern: L0/EVERYONE.htm and L0/IMAGES.htm references
    everyone_pattern = [row for row in data if 'L0/EVERYONE.htm' in row['Original_Link_Text']]
    images_pattern = [row for row in data if 'L0/IMAGES.htm' in row['Original_Link_Text']]
    if everyone_pattern:
        print(f"  L0/EVERYONE.htm references: {len(everyone_pattern)}")
    if images_pattern:
        print(f"  L0/IMAGES.htm references: {len(images_pattern)}")

    # Pattern: Space-containing URLs (malformed)
    space_pattern = [row for row in data if ' ' in row['Broken_URL']]
    if space_pattern:
        print(f"  URLs with spaces (malformed): {len(space_pattern)}")
        for issue in space_pattern[:5]:  # Show examples
            print(f"    {issue['Original_Link_Text']} -> {issue['Broken_URL']}")

    return {
        'total_issues': len(data),
        'case_issues': case_issues,
        'relative_path_issues': relative_path_issues,
        'missing_files': missing_files,
        'path_issues': path_issues,
        'xf533_issues': xf533_pattern,
        'space_issues': space_pattern,
        'everyone_issues': everyone_pattern,
        'images_issues': images_pattern
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze broken links patterns')
    parser.add_argument('--htm-report', help='Path to HTM broken links CSV')
    parser.add_argument('--new-report', help='Path to NEW broken links CSV')
    parser.add_argument('--reports-dir', default='PRPs/scripts/reports',
                       help='Directory containing reports (will find latest)')

    args = parser.parse_args()

    # Find latest reports if not specified
    reports_dir = Path(args.reports_dir)

    if args.htm_report:
        htm_report = args.htm_report
    else:
        htm_reports = list(reports_dir.glob('broken_links_htm_*.csv'))
        htm_report = str(sorted(htm_reports)[-1]) if htm_reports else None

    if args.new_report:
        new_report = args.new_report
    else:
        new_reports = list(reports_dir.glob('broken_links_new_*.csv'))
        new_report = str(sorted(new_reports)[-1]) if new_reports else None

    print("🔍 BROKEN LINKS PATTERN ANALYSIS")
    print("=" * 50)

    htm_analysis = None
    new_analysis = None

    if htm_report and os.path.exists(htm_report):
        htm_analysis = analyze_patterns(htm_report)
    else:
        print("⚠️  No HTM report found")

    if new_report and os.path.exists(new_report):
        new_analysis = analyze_patterns(new_report)
    else:
        print("⚠️  No NEW report found")

    # Combined analysis
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDED FIX PRIORITIES:")
    print("=" * 50)

    total_issues = 0
    if htm_analysis:
        total_issues += htm_analysis['total_issues']
    if new_analysis:
        total_issues += new_analysis['total_issues']

    print(f"Total broken links across both sites: {total_issues}")

    # High-impact fixes
    print("\n🔥 HIGH IMPACT FIXES:")
    if htm_analysis and htm_analysis.get('xf533_issues'):
        print(f"1. Fix XF533.htm missing file: {len(htm_analysis['xf533_issues'])} links")

    if new_analysis and new_analysis.get('everyone_issues'):
        print(f"2. Fix L0/EVERYONE.htm references: {len(new_analysis['everyone_issues'])} links")

    if new_analysis and new_analysis.get('images_issues'):
        print(f"3. Fix L0/IMAGES.htm references: {len(new_analysis['images_issues'])} links")

    # Medium-impact fixes
    print("\n⚡ MEDIUM IMPACT FIXES:")
    case_total = 0
    if htm_analysis:
        case_total += len(htm_analysis.get('case_issues', []))
    if new_analysis:
        case_total += len(new_analysis.get('case_issues', []))

    if case_total > 0:
        print(f"1. Fix case sensitivity issues: {case_total} links")

    space_total = 0
    if htm_analysis:
        space_total += len(htm_analysis.get('space_issues', []))
    if new_analysis:
        space_total += len(new_analysis.get('space_issues', []))

    if space_total > 0:
        print(f"2. Fix malformed URLs with spaces: {space_total} links")

    rel_total = 0
    if htm_analysis:
        rel_total += len(htm_analysis.get('relative_path_issues', []))
    if new_analysis:
        rel_total += len(new_analysis.get('relative_path_issues', []))

    if rel_total > 0:
        print(f"3. Fix relative path issues: {rel_total} links")

if __name__ == "__main__":
    main()