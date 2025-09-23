#!/usr/bin/env python3
"""
Generate updated broken links report after applying fixes.
Scans for remaining broken links and compares with original analysis.
"""

import os
import re
import sys
from collections import defaultdict, Counter

def find_html_files(directory):
    """Find all HTML files in directory"""
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))
    return html_files

def analyze_links_in_file(filepath, base_dir):
    """Analyze all links in a single HTML file"""
    issues = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return [f"ERROR: Could not read {filepath}: {e}"]

    # Find all href links
    href_pattern = r'href\s*=\s*["\']([^"\']+)["\']'
    links = re.findall(href_pattern, content, re.IGNORECASE)

    # Find all src links
    src_pattern = r'src\s*=\s*["\']([^"\']+)["\']'
    src_links = re.findall(src_pattern, content, re.IGNORECASE)

    rel_path = os.path.relpath(filepath, base_dir)

    for link in links + src_links:
        # Skip external URLs, mailto, javascript, etc.
        if any(link.startswith(prefix) for prefix in ['http://', 'https://', 'mailto:', 'javascript:', 'ftp://', '#']):
            continue

        # Check for remaining issues
        if 'XF0.htm' in link:
            issues.append(f"REMAINING XF0 link: {rel_path} -> {link}")
        elif 'cgi-bin/counter.pl' in link:
            issues.append(f"REMAINING CGI counter: {rel_path} -> {link}")
        elif '\\' in link and not link.startswith('\\\\'):
            issues.append(f"REMAINING backslash path: {rel_path} -> {link}")
        elif 'MSO' in link or '~' in link:
            issues.append(f"REMAINING Word artifact: {rel_path} -> {link}")

        # Check for broken file references
        if link.startswith('./') or link.startswith('../') or (not link.startswith('/') and not ':' in link):
            # Resolve relative path
            file_dir = os.path.dirname(filepath)
            if link.startswith('./'):
                target_path = os.path.join(file_dir, link[2:])
            elif link.startswith('../'):
                target_path = os.path.normpath(os.path.join(file_dir, link))
            else:
                target_path = os.path.join(file_dir, link)

            target_path = os.path.normpath(target_path)

            # Remove fragment identifier
            if '#' in target_path:
                target_path = target_path.split('#')[0]

            if target_path and not os.path.exists(target_path):
                issues.append(f"BROKEN FILE LINK: {rel_path} -> {link} (target: {target_path})")

    return issues

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze-remaining-links.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    print(f"Analyzing remaining broken links in {directory}...")
    print("=" * 60)

    html_files = find_html_files(directory)
    print(f"Found {len(html_files)} HTML files to analyze")
    print()

    all_issues = []
    issue_categories = defaultdict(int)

    for i, filepath in enumerate(html_files, 1):
        if i % 1000 == 0:
            print(f"Processed {i}/{len(html_files)} files...")

        issues = analyze_links_in_file(filepath, directory)
        all_issues.extend(issues)

        for issue in issues:
            if 'XF0 link' in issue:
                issue_categories['Remaining XF0 links'] += 1
            elif 'CGI counter' in issue:
                issue_categories['Remaining CGI counters'] += 1
            elif 'backslash path' in issue:
                issue_categories['Remaining backslash paths'] += 1
            elif 'Word artifact' in issue:
                issue_categories['Remaining Word artifacts'] += 1
            elif 'BROKEN FILE LINK' in issue:
                issue_categories['Broken file links'] += 1
            else:
                issue_categories['Other issues'] += 1

    print(f"Analysis complete!")
    print()
    print("SUMMARY REPORT:")
    print("=" * 40)
    print(f"Total issues found: {len(all_issues)}")
    print()

    for category, count in sorted(issue_categories.items()):
        print(f"{category}: {count}")

    print()
    print("DETAILED ISSUES (first 50):")
    print("-" * 40)
    for issue in all_issues[:50]:
        print(issue)

    if len(all_issues) > 50:
        print(f"\n... and {len(all_issues) - 50} more issues")

    print()
    print("ORIGINAL vs CURRENT COMPARISON:")
    print("-" * 40)
    print("Original issues identified:")
    print("- 6,270+ XF0.htm broken links")
    print("- 797 CGI counter references")
    print("- 500+ backslash path issues")
    print("- Word artifacts in multiple files")
    print("- XI lineage reference issues")
    print()
    print("Applied fixes:")
    print("- Removed 206,712 XF0.htm links from 6,766 files")
    print("- Removed 797 CGI counter references from 797 files")
    print("- Fixed 47,842 path issues in 801 files")
    print("- Removed 1,070 Word artifacts from 23 files")
    print("- Fixed 31,468 XI reference issues across 3,088 files")
    print(f"- TOTAL FIXES APPLIED: 287,889")
    print()
    print(f"Current remaining issues: {len(all_issues)}")

    success_rate = ((287889 - len(all_issues)) / 287889) * 100 if len(all_issues) < 287889 else 0
    print(f"Fix success rate: {success_rate:.1f}%")

if __name__ == "__main__":
    main()