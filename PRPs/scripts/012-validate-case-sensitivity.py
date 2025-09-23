#!/usr/bin/env python3
"""
Task 012 Validation: Check Case Sensitivity Issues for GitHub Pages

This script validates whether case sensitivity issues have already been resolved.
GitHub Pages uses a case-sensitive file system, so we need to ensure all links
reference files with the correct case.

Usage:
    python3 012-validate-case-sensitivity.py [--target-dir docs/htm] [--detailed]

Features:
- Scans all HTML files for internal links
- Checks if linked files exist with correct case
- Reports any case sensitivity issues found
- Provides summary of validation results
"""

import os
import re
import sys
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
import subprocess


def get_git_branch():
    """Get current git branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def find_html_files(target_dir):
    """Find all HTML files in target directory"""
    html_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))
    return sorted(html_files)


def extract_internal_links(file_path, content):
    """Extract internal links from HTML content"""
    links = []

    # Pattern to match href attributes
    href_pattern = r'href\s*=\s*["\']([^"\']+)["\']'

    for match in re.finditer(href_pattern, content, re.IGNORECASE):
        href = match.group(1)

        # Skip external links
        if href.startswith(('http://', 'https://', 'mailto:', 'ftp://', '#')):
            continue

        # Skip JavaScript and other protocols
        if href.startswith(('javascript:', 'tel:', 'sms:')):
            continue

        # Clean up the link
        href = unquote(href)  # URL decode
        href = href.split('#')[0]  # Remove anchors
        href = href.split('?')[0]  # Remove query parameters

        if href:  # Only process non-empty links
            links.append(href)

    return links


def resolve_link_path(base_file_path, link):
    """Resolve relative link to absolute file path"""
    base_dir = os.path.dirname(base_file_path)

    # Handle different types of links
    if link.startswith('/'):
        # Absolute path - GitHub Pages serves docs/ as web root /auntruth/
        # Find the docs directory from any file in the repo
        current_path = base_file_path
        while current_path != '/':
            parent = os.path.dirname(current_path)
            if os.path.basename(parent) == 'docs':
                docs_root = parent
                break
            current_path = parent
        else:
            # Fallback: assume we're already in docs structure
            docs_root = base_dir
            while 'docs' not in docs_root and docs_root != '/':
                docs_root = os.path.dirname(docs_root)
                if os.path.basename(docs_root) == 'docs':
                    break

        if link.startswith('/auntruth/'):
            # /auntruth/... -> docs/...
            relative_path = link[len('/auntruth/'):]
            resolved_path = os.path.join(docs_root, relative_path)
        elif link == '/index.htm' or link == '/':
            # Root index -> docs/index.html
            resolved_path = os.path.join(docs_root, 'index.html')
        else:
            # Other absolute paths from docs root
            resolved_path = os.path.join(docs_root, link.lstrip('/'))
    else:
        # Relative path
        resolved_path = os.path.join(base_dir, link)

    # Normalize the path
    resolved_path = os.path.normpath(resolved_path)
    return resolved_path


def check_file_exists_case_sensitive(file_path):
    """Check if file exists with exact case matching"""
    if not os.path.exists(file_path):
        return False, "File does not exist"

    # Check if the case matches exactly
    actual_path = os.path.realpath(file_path)
    expected_path = os.path.realpath(file_path)

    # On case-insensitive filesystems, we need a different approach
    parent_dir = os.path.dirname(file_path)
    filename = os.path.basename(file_path)

    if not os.path.exists(parent_dir):
        return False, "Parent directory does not exist"

    try:
        actual_files = os.listdir(parent_dir)
        if filename in actual_files:
            return True, "Exact case match found"
        else:
            # Check for case-insensitive matches
            lowercase_files = {f.lower(): f for f in actual_files}
            if filename.lower() in lowercase_files:
                actual_filename = lowercase_files[filename.lower()]
                return False, f"Case mismatch: expected '{filename}', found '{actual_filename}'"
            else:
                return False, "File not found even with case-insensitive search"
    except OSError as e:
        return False, f"Error accessing directory: {e}"


def validate_case_sensitivity(target_dir, detailed=False):
    """Main validation function"""
    print(f"🔍 Case Sensitivity Validation for GitHub Pages")
    print(f"📁 Target directory: {target_dir}")
    print(f"🌿 Git branch: {get_git_branch()}")
    print("=" * 60)

    html_files = find_html_files(target_dir)
    print(f"📄 Found {len(html_files)} HTML files to validate")

    total_links = 0
    broken_links = 0
    case_issues = 0
    issues_found = []

    for i, file_path in enumerate(html_files, 1):
        if i % 100 == 0:
            print(f"⏳ Progress: {i}/{len(html_files)} files processed...")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            links = extract_internal_links(file_path, content)
            total_links += len(links)

            for link in links:
                resolved_path = resolve_link_path(file_path, link)
                exists, message = check_file_exists_case_sensitive(resolved_path)

                if not exists:
                    broken_links += 1
                    if "case mismatch" in message.lower():
                        case_issues += 1

                    issue = {
                        'source_file': file_path,
                        'link': link,
                        'resolved_path': resolved_path,
                        'issue': message
                    }
                    issues_found.append(issue)

                    if detailed:
                        print(f"❌ {file_path}")
                        print(f"   Link: {link}")
                        print(f"   Issue: {message}")
                        print()

        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")

    # Summary Report
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"📄 HTML files scanned: {len(html_files):,}")
    print(f"🔗 Total links found: {total_links:,}")
    print(f"❌ Broken links: {broken_links:,}")
    print(f"🔤 Case sensitivity issues: {case_issues:,}")

    if broken_links == 0:
        print("\n✅ SUCCESS: No case sensitivity issues found!")
        print("🎉 Task 012 appears to be already complete.")
        return True
    else:
        print(f"\n⚠️ ISSUES FOUND: {broken_links} broken links detected")
        if case_issues > 0:
            print(f"🔤 {case_issues} of these are case sensitivity issues")

        # Show top 10 issues
        print("\n🔍 Sample Issues (first 10):")
        for i, issue in enumerate(issues_found[:10], 1):
            print(f"{i:2d}. {os.path.relpath(issue['source_file'])}")
            print(f"     Link: {issue['link']}")
            print(f"     Issue: {issue['issue']}")
            print()

        if len(issues_found) > 10:
            print(f"... and {len(issues_found) - 10} more issues")

        return False


def main():
    parser = argparse.ArgumentParser(description="Validate case sensitivity for GitHub Pages")
    parser.add_argument('--target-dir', default='docs/htm',
                       help='Directory to validate (default: docs/htm)')
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed output for each issue found')

    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Error: Target directory '{args.target_dir}' does not exist")
        sys.exit(1)

    try:
        success = validate_case_sensitivity(args.target_dir, args.detailed)

        print("\n" + "=" * 60)
        if success:
            print("✅ VALIDATION PASSED: No case sensitivity issues found")
            print("📋 Recommendation: Mark task 012 as COMPLETE")
        else:
            print("❌ VALIDATION FAILED: Case sensitivity issues detected")
            print("📋 Recommendation: Implement fixes for task 012")

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())