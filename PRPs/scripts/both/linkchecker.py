#!/usr/bin/env python3
"""
Comprehensive Link Checker for AuntieRuth.com

This script validates all internal links on both:
- http://localhost:8000/auntruth/htm/ (original site)
- http://localhost:8000/auntruth/new/ (modernized site)

Uses curl to check HTTP status codes and identifies broken links.

Usage: python3 linkchecker.py [--dry-run] [--site=htm|new|both]
"""

import os
import sys
import argparse
import re
import subprocess
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import defaultdict

def run_curl(url, timeout=10):
    """Run curl to check if URL is accessible."""
    try:
        result = subprocess.run([
            'curl', '-s', '-I', '--max-time', str(timeout), url
        ], capture_output=True, text=True, timeout=timeout+5)

        if result.returncode == 0:
            # Parse HTTP status from first line
            first_line = result.stdout.split('\n')[0]
            if 'HTTP/' in first_line:
                status_code = first_line.split()[1]
                return int(status_code)
        return 0  # Connection failed
    except (subprocess.TimeoutExpired, ValueError, IndexError):
        return 0

def extract_links_from_file(file_path):
    """Extract all internal links from an HTML file."""
    links = set()

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find all href and src attributes that reference internal links
        patterns = [
            r'href=["\']([^"\']*)["\']',      # href links
            r'src=["\']([^"\']*)["\']',       # image sources
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                link = match.group(1)

                # Only process internal links (starting with / or relative)
                if link.startswith('/auntruth/') or (
                    not link.startswith(('http://', 'https://', 'mailto:', '#', 'javascript:'))
                    and link
                ):
                    links.add(link)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return links

def normalize_link(link, base_site):
    """Convert relative links to absolute URLs for testing."""
    if link.startswith('/auntruth/'):
        return f"http://localhost:8000{link}"
    elif link.startswith('/'):
        return f"http://localhost:8000/auntruth/{base_site}{link}"
    elif link.startswith('../'):
        # Handle relative paths like ../../jpg/image.jpg
        if base_site == 'htm':
            return f"http://localhost:8000/auntruth/{link.replace('../', '')}"
        else:
            return f"http://localhost:8000/auntruth/{link.replace('../', '')}"
    else:
        # Relative path without leading slash
        return f"http://localhost:8000/auntruth/{base_site}/{link}"

def check_links_in_directory(directory, base_site, dry_run=False):
    """Check all links in HTML files within a directory."""
    print(f"\n=== Checking links in {directory} ===")

    broken_links = defaultdict(list)
    total_files = 0
    total_links = 0
    broken_count = 0

    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files to check")

    if dry_run:
        print("DRY RUN MODE - Will not actually check URLs")
        return broken_links, 0, 0, 0

    for i, html_file in enumerate(html_files):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(html_files)} files checked...")

        total_files += 1
        links = extract_links_from_file(html_file)

        for link in links:
            total_links += 1

            # Convert to absolute URL for testing
            abs_url = normalize_link(link, base_site)

            # Skip certain file types that might not be accessible via HTTP
            if any(abs_url.lower().endswith(ext) for ext in ['.mp3', '.wav', '.au']):
                continue

            # Check if URL is accessible
            status_code = run_curl(abs_url)

            if status_code != 200:
                broken_count += 1
                rel_path = os.path.relpath(html_file, directory)
                broken_links[abs_url].append({
                    'file': rel_path,
                    'original_link': link,
                    'status': status_code
                })

    print(f"Checked {total_files} files with {total_links} total links")
    return broken_links, total_files, total_links, broken_count

def generate_report(broken_links, site_name, output_file=None):
    """Generate a detailed report of broken links."""
    report_lines = []
    report_lines.append(f"\n=== BROKEN LINKS REPORT: {site_name.upper()} ===")
    report_lines.append(f"Total broken URLs: {len(broken_links)}")

    if not broken_links:
        report_lines.append("🎉 No broken links found!")
        report = "\n".join(report_lines)
        print(report)
        return report

    # Group by status code
    by_status = defaultdict(list)
    for url, instances in broken_links.items():
        status = instances[0]['status']  # All instances should have same status
        by_status[status].append((url, instances))

    for status_code in sorted(by_status.keys()):
        urls = by_status[status_code]
        report_lines.append(f"\n--- Status {status_code} ({len(urls)} URLs) ---")

        for url, instances in urls:
            report_lines.append(f"\n❌ {url}")
            report_lines.append(f"   Referenced in {len(instances)} file(s):")

            for instance in instances[:5]:  # Limit to first 5 instances
                report_lines.append(f"     • {instance['file']} (link: {instance['original_link']})")

            if len(instances) > 5:
                report_lines.append(f"     ... and {len(instances) - 5} more files")

    # Suggestions for common issues
    report_lines.append(f"\n=== COMMON ISSUES & FIXES ===")

    for status_code in by_status.keys():
        if status_code == 404:
            report_lines.append("• 404 errors: File not found. Check if:")
            report_lines.append("  - File was renamed or moved")
            report_lines.append("  - Wrong lineage directory (L0 vs L1 vs L2, etc.)")
            report_lines.append("  - Case sensitivity issues (.HTM vs .htm)")
        elif status_code == 0:
            report_lines.append("• Connection failed: Check if:")
            report_lines.append("  - Local server is running on localhost:8000")
            report_lines.append("  - Path format is correct")

    report = "\n".join(report_lines)
    print(report)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")

    return report

def main():
    parser = argparse.ArgumentParser(description="Check all links in AuntieRuth.com")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be checked without actually checking URLs")
    parser.add_argument("--site", choices=['htm', 'new', 'both'], default='both',
                       help="Which site to check (default: both)")
    parser.add_argument("--output", type=str,
                       help="Save report to file")
    parser.add_argument("--timeout", type=int, default=10,
                       help="Timeout for curl requests in seconds")

    args = parser.parse_args()

    # Define base directory
    base_dir = Path(__file__).parent.parent.parent

    # Define sites to check
    sites_to_check = []
    if args.site in ['htm', 'both']:
        htm_dir = base_dir / "docs" / "htm"
        if htm_dir.exists():
            sites_to_check.append(('htm', htm_dir))
        else:
            print(f"Warning: {htm_dir} not found")

    if args.site in ['new', 'both']:
        new_dir = base_dir / "docs" / "new"
        if new_dir.exists():
            sites_to_check.append(('new', new_dir))
        else:
            print(f"Warning: {new_dir} not found")

    if not sites_to_check:
        print("Error: No valid directories found to check")
        sys.exit(1)

    print(f"AuntieRuth.com Link Checker")
    print(f"Checking {len(sites_to_check)} site(s)")
    print(f"Timeout: {args.timeout} seconds")

    if args.dry_run:
        print("DRY RUN MODE - No actual HTTP requests will be made")

    all_reports = []
    total_broken = 0

    for site_name, site_dir in sites_to_check:
        broken_links, total_files, total_links, broken_count = check_links_in_directory(
            site_dir, site_name, args.dry_run
        )

        total_broken += broken_count

        # Generate report for this site
        output_file = None
        if args.output and len(sites_to_check) == 1:
            output_file = args.output
        elif args.output:
            base_name = os.path.splitext(args.output)[0]
            ext = os.path.splitext(args.output)[1] or '.txt'
            output_file = f"{base_name}_{site_name}{ext}"

        report = generate_report(broken_links, site_name, output_file)
        all_reports.append(report)

    # Summary
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Sites checked: {len(sites_to_check)}")
    if not args.dry_run:
        print(f"Total broken links: {total_broken}")
        if total_broken == 0:
            print("🎉 All links are working correctly!")
        else:
            print("⚠️  Broken links found. See reports above for details.")

    return 0 if total_broken == 0 else 1

if __name__ == "__main__":
    sys.exit(main())