#!/usr/bin/env python3
"""
Find All Broken Links - Optimized for Performance

This script finds all broken links in the AuntieRuth.com genealogy site.
It ensures each URL is only checked once and provides progress feedback.

Usage: python3 find-broken-links.py [--site=htm|new|both] [--timeout=5]
"""

import os
import sys
import argparse
import re
import subprocess
import json
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from urllib.parse import urljoin, urlparse

def run_curl(url, timeout=5):
    """Run curl to check if URL is accessible."""
    try:
        result = subprocess.run([
            'curl', '-s', '-I', '--max-time', str(timeout), url
        ], capture_output=True, text=True, timeout=timeout+2)

        if result.returncode == 0:
            first_line = result.stdout.split('\n')[0]
            if 'HTTP/' in first_line:
                status_code = first_line.split()[1]
                return int(status_code)
        return 0
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
                    not link.startswith(('http://', 'https://', 'mailto:', '#', 'javascript:', 'tel:'))
                    and link and not link.startswith('data:')
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
        return f"http://localhost:8000/auntruth/{link.replace('../', '')}"
    else:
        # Relative path without leading slash
        return f"http://localhost:8000/auntruth/{base_site}/{link}"

def find_broken_links(directory, base_site, timeout=5):
    """Find all broken links in HTML files within a directory."""
    print(f"\n=== Scanning {directory} for links ===")

    # Collect all HTML files
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.htm', '.html')):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files")

    # Extract all unique links first
    all_links = set()
    link_sources = defaultdict(list)  # Track which files reference each link

    print("Extracting links from files...")
    for i, html_file in enumerate(html_files):
        if i % 500 == 0:
            print(f"  Progress: {i}/{len(html_files)} files scanned...")

        rel_path = os.path.relpath(html_file, directory)
        links = extract_links_from_file(html_file)

        for link in links:
            abs_url = normalize_link(link, base_site)

            # Skip certain file types that might not be accessible via HTTP
            if any(abs_url.lower().endswith(ext) for ext in ['.mp3', '.wav', '.au', '.pdf', '.zip']):
                continue

            all_links.add(abs_url)
            link_sources[abs_url].append({
                'file': rel_path,
                'original_link': link
            })

    print(f"Found {len(all_links)} unique links to check")

    # Now check each unique link only once
    broken_links = {}
    checked_count = 0

    print("\nChecking link accessibility...")
    for url in sorted(all_links):
        checked_count += 1
        if checked_count % 100 == 0:
            print(f"  Progress: {checked_count}/{len(all_links)} links checked...")

        status_code = run_curl(url, timeout)

        if status_code != 200:
            broken_links[url] = {
                'status': status_code,
                'sources': link_sources[url]
            }

    return broken_links, len(html_files), len(all_links)

def save_csv_report(broken_links, site_name, total_files, total_links):
    """Save detailed broken links report to CSV file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    csv_file = reports_dir / f"broken_links_{site_name}_{timestamp}.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            'Broken_URL',
            'HTTP_Status',
            'Source_File',
            'Original_Link_Text',
            'Issue_Type',
            'Suggested_Fix'
        ])

        # Write broken links data
        for url, data in broken_links.items():
            status = data['status']
            sources = data['sources']

            # Determine issue type and suggested fix
            issue_type = "Unknown"
            suggested_fix = "Manual investigation required"

            if status == 404:
                issue_type = "File Not Found"
                if '.htm' in url.lower():
                    suggested_fix = "Check if file exists in different lineage directory (L0/L1/L2) or was renamed"
                elif '.jpg' in url.lower() or '.gif' in url.lower():
                    suggested_fix = "Check if image file exists with different case (.JPG vs .jpg)"
                else:
                    suggested_fix = "Verify file path and existence"
            elif status == 0:
                issue_type = "Connection Failed"
                suggested_fix = "Check if localhost:8000 server is running"
            elif status >= 500:
                issue_type = "Server Error"
                suggested_fix = "Server configuration issue"
            elif status >= 400:
                issue_type = "Client Error"
                suggested_fix = "Check URL format and permissions"

            # Write one row per source file
            for source in sources:
                writer.writerow([
                    url,
                    status,
                    source['file'],
                    source['original_link'],
                    issue_type,
                    suggested_fix
                ])

    return csv_file

def generate_report(broken_links, site_name, total_files, total_links):
    """Generate a detailed report of broken links."""
    print(f"\n=== BROKEN LINKS REPORT: {site_name.upper()} ===")
    print(f"Files scanned: {total_files}")
    print(f"Unique links checked: {total_links}")
    print(f"Broken links found: {len(broken_links)}")

    # Save detailed CSV report
    csv_file = save_csv_report(broken_links, site_name, total_files, total_links)
    print(f"📄 Detailed CSV report saved: {csv_file}")

    if not broken_links:
        print("🎉 No broken links found!")
        return csv_file

    # Group by status code for console summary
    by_status = defaultdict(list)
    for url, data in broken_links.items():
        status = data['status']
        by_status[status].append((url, data))

    # Show summary by status code
    for status_code in sorted(by_status.keys()):
        urls = by_status[status_code]
        print(f"\n--- Status {status_code}: {len(urls)} URLs ---")

        # Show first few examples
        for url, data in urls[:5]:
            print(f"  ❌ {url}")
            sources = data['sources']
            print(f"     Referenced in {len(sources)} file(s): {sources[0]['file']}")
            if len(sources) > 1:
                print(f"     ... and {len(sources) - 1} more files")

        if len(urls) > 5:
            print(f"     ... and {len(urls) - 5} more broken URLs")

    # Common fixes
    print(f"\n=== COMMON FIXES ===")
    if 404 in by_status:
        print("• 404 errors: File not found")
        print("  - Check if file was renamed or moved")
        print("  - Verify lineage directory (L0 vs L1 vs L2, etc.)")
        print("  - Check case sensitivity (.HTM vs .htm)")
    if 0 in by_status:
        print("• Connection failed: Check if server is running on localhost:8000")

    return csv_file

def main():
    parser = argparse.ArgumentParser(description="Find all broken links in AuntieRuth.com")
    parser.add_argument("--site", choices=['htm', 'new', 'both'], default='both',
                       help="Which site to check (default: both)")
    parser.add_argument("--timeout", type=int, default=5,
                       help="Timeout for curl requests in seconds (default: 5)")

    args = parser.parse_args()

    # Define base directory
    base_dir = Path(__file__).parent.parent.parent.parent

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

    print(f"AuntieRuth.com Broken Link Finder")
    print(f"Checking {len(sites_to_check)} site(s)")
    print(f"Timeout: {args.timeout} seconds")

    total_broken = 0
    csv_reports = []

    for site_name, site_dir in sites_to_check:
        broken_links, total_files, total_links = find_broken_links(
            site_dir, site_name, args.timeout
        )

        total_broken += len(broken_links)
        csv_file = generate_report(broken_links, site_name, total_files, total_links)
        csv_reports.append(csv_file)

    # Summary
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Sites checked: {len(sites_to_check)}")
    print(f"Total broken links: {total_broken}")
    print(f"CSV reports generated:")
    for csv_report in csv_reports:
        print(f"  📄 {csv_report}")

    if total_broken == 0:
        print("🎉 All links are working correctly!")
    else:
        print("⚠️  Broken links found. See CSV reports for complete details.")

    return 0 if total_broken == 0 else 1

if __name__ == "__main__":
    sys.exit(main())