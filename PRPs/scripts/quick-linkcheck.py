#!/usr/bin/env python3
"""
Quick Link Checker for specific files or directories

This script quickly checks links in specific files to identify issues like the XI2627.htm problem.

Usage: python3 quick-linkcheck.py <file_or_directory>
"""

import os
import sys
import re
import subprocess
from pathlib import Path

def run_curl(url, timeout=3):
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

def extract_auntruth_links(file_path):
    """Extract all /auntruth/ links from an HTML file."""
    links = set()

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find all href attributes with /auntruth/ links
        pattern = r'href=["\']([^"\']*\/auntruth\/[^"\']*)["\']'
        matches = re.finditer(pattern, content, re.IGNORECASE)

        for match in matches:
            link = match.group(1)
            # Convert to full URL
            if link.startswith('/auntruth/'):
                links.add(f"http://localhost:8000{link}")

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return links

def check_file(file_path):
    """Check all /auntruth/ links in a single file."""
    print(f"Checking: {file_path}")

    links = extract_auntruth_links(file_path)
    broken_links = []

    for link in links:
        status_code = run_curl(link)
        if status_code != 200:
            broken_links.append((link, status_code))
            print(f"  ❌ {link} - Status: {status_code}")

    if not broken_links:
        print(f"  ✅ All {len(links)} links OK")
    else:
        print(f"  ⚠️  {len(broken_links)} broken out of {len(links)} links")

    return broken_links

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 quick-linkcheck.py <file_or_directory>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if target.is_file():
        broken_links = check_file(target)
        if broken_links:
            print(f"\nBroken links found:")
            for link, status in broken_links:
                print(f"  {link} (Status: {status})")
    elif target.is_dir():
        html_files = list(target.glob("*.htm"))
        print(f"Found {len(html_files)} HTML files in {target}")

        all_broken = []
        for html_file in html_files[:10]:  # Limit to first 10 files for quick check
            broken = check_file(html_file)
            all_broken.extend(broken)

        print(f"\nTotal broken links found: {len(all_broken)}")
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

if __name__ == "__main__":
    main()