#!/usr/bin/env python3
"""
Analyze Broken Link Patterns - Pattern Analysis Tool

This script analyzes broken link CSV reports to identify systematic patterns
that can be fixed with targeted scripts. It provides detailed breakdowns
of broken URL patterns, frequency analysis, and actionable insights.

Usage: python3 analyze-broken-link-patterns.py [csv_file1] [csv_file2] ...
"""

import sys
import csv
from collections import defaultdict, Counter
from urllib.parse import urlparse
import re
import argparse


def parse_csv_file(csv_path):
    """Parse a broken links CSV file and return list of records."""
    records = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        print(f"✅ Loaded {len(records)} records from {csv_path}")
        return records
    except Exception as e:
        print(f"❌ Error reading {csv_path}: {e}")
        return []


def analyze_url_patterns(records):
    """Analyze patterns in broken URLs."""
    patterns = defaultdict(list)

    for record in records:
        url = record.get('Broken_URL', '')
        original_link = record.get('Original_Link_Text', '')

        # Extract path from URL
        try:
            parsed = urlparse(url)
            path = parsed.path
        except:
            path = url

        # Categorize patterns
        if '/auntruth/new/L' in path and '/htm/L' not in path:
            patterns['missing_htm_prefix'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })
        elif '/htm/htm/' in path:
            patterns['double_htm'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })
        elif 'INDEX.htm' in path:
            patterns['uppercase_index'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })
        elif path.endswith('.jpg') and 'index_files' in path:
            patterns['missing_image_files'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })
        elif '/auntruth/jpg/ ' in path:
            patterns['malformed_jpg_paths'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })
        elif '\\AuntRuth\\' in original_link:
            patterns['backslash_paths'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })
        elif 'file:///' in original_link:
            patterns['file_protocol_urls'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })
        elif '/auntruth/index' in path and path.endswith('.htm'):
            patterns['missing_index_files'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })
        else:
            patterns['other_missing_files'].append({
                'url': url,
                'original': original_link,
                'source': record.get('Source_File', '')
            })

    return patterns


def analyze_frequency_by_file(records):
    """Analyze which source files have the most broken links."""
    file_counts = Counter()

    for record in records:
        source_file = record.get('Source_File', '')
        file_counts[source_file] += 1

    return file_counts


def analyze_broken_filenames(records):
    """Analyze the actual filenames that are broken."""
    filename_counts = Counter()

    for record in records:
        url = record.get('Broken_URL', '')
        try:
            parsed = urlparse(url)
            path = parsed.path
            if '/' in path:
                filename = path.split('/')[-1]
                if filename and filename != '':
                    filename_counts[filename] += 1
        except:
            pass

    return filename_counts


def print_pattern_analysis(patterns):
    """Print detailed analysis of patterns found."""
    print("\n" + "="*60)
    print("🔍 BROKEN LINK PATTERN ANALYSIS")
    print("="*60)

    total_patterns = sum(len(pattern_list) for pattern_list in patterns.values())
    print(f"\nTotal broken links analyzed: {total_patterns}")

    for pattern_name, pattern_list in patterns.items():
        if not pattern_list:
            continue

        print(f"\n📊 {pattern_name.replace('_', ' ').title()}: {len(pattern_list)} occurrences")
        print("-" * 50)

        # Show sample URLs and suggest fixes
        samples = pattern_list[:5]  # Show first 5 examples

        for i, item in enumerate(samples, 1):
            print(f"  {i}. URL: {item['url']}")
            print(f"     Original: {item['original']}")
            print(f"     Source: {item['source']}")

            # Suggest specific fixes
            if pattern_name == 'missing_htm_prefix':
                fixed_url = item['url'].replace('/auntruth/new/L', '/auntruth/new/htm/L')
                print(f"     Suggested fix: {fixed_url}")
            elif pattern_name == 'double_htm':
                fixed_url = item['url'].replace('/htm/htm/', '/htm/')
                print(f"     Suggested fix: {fixed_url}")
            elif pattern_name == 'uppercase_index':
                fixed_url = item['url'].replace('INDEX.htm', 'index.htm')
                print(f"     Suggested fix: {fixed_url}")
            elif pattern_name == 'backslash_paths':
                fixed_original = item['original'].replace('\\', '/')
                print(f"     Suggested fix: {fixed_original}")

            print()

        if len(pattern_list) > 5:
            print(f"  ... and {len(pattern_list) - 5} more similar cases")

        print()


def print_frequency_analysis(file_counts, filename_counts):
    """Print frequency analysis of broken links."""
    print("\n" + "="*60)
    print("📈 FREQUENCY ANALYSIS")
    print("="*60)

    print(f"\n🗂️ Top 10 Source Files with Most Broken Links:")
    print("-" * 50)
    for file, count in file_counts.most_common(10):
        print(f"  {count:3d} broken links: {file}")

    print(f"\n📄 Top 15 Most Frequently Broken Filenames:")
    print("-" * 50)
    for filename, count in filename_counts.most_common(15):
        print(f"  {count:3d} references: {filename}")


def suggest_fix_scripts(patterns):
    """Suggest specific fix scripts based on patterns found."""
    print("\n" + "="*60)
    print("🛠️ RECOMMENDED FIX SCRIPTS")
    print("="*60)

    script_suggestions = []

    if patterns['missing_htm_prefix']:
        script_suggestions.append({
            'priority': 'HIGH',
            'name': 'fix-missing-htm-prefix.py',
            'description': f'Add missing /htm/ prefix to {len(patterns["missing_htm_prefix"])} NEW site references',
            'pattern': 'Replace /auntruth/new/L[0-9]+/ with /auntruth/new/htm/L[0-9]+/',
            'impact': f'{len(patterns["missing_htm_prefix"])} broken links'
        })

    if patterns['uppercase_index']:
        script_suggestions.append({
            'priority': 'HIGH',
            'name': 'fix-case-sensitivity.py',
            'description': f'Fix uppercase INDEX.htm to lowercase in {len(patterns["uppercase_index"])} references',
            'pattern': 'Replace INDEX.htm with index.htm',
            'impact': f'{len(patterns["uppercase_index"])} broken links'
        })

    if patterns['double_htm']:
        script_suggestions.append({
            'priority': 'MEDIUM',
            'name': 'fix-double-htm-paths.py',
            'description': f'Remove duplicate /htm/htm/ paths in {len(patterns["double_htm"])} references',
            'pattern': 'Replace /htm/htm/ with /htm/',
            'impact': f'{len(patterns["double_htm"])} broken links'
        })

    if patterns['backslash_paths']:
        script_suggestions.append({
            'priority': 'MEDIUM',
            'name': 'fix-backslash-paths.py',
            'description': f'Convert backslash paths to forward slashes in {len(patterns["backslash_paths"])} references',
            'pattern': 'Replace \\ with / in href attributes',
            'impact': f'{len(patterns["backslash_paths"])} broken links'
        })

    if patterns['malformed_jpg_paths']:
        script_suggestions.append({
            'priority': 'LOW',
            'name': 'fix-malformed-jpg-paths.py',
            'description': f'Fix malformed JPG paths with spaces in {len(patterns["malformed_jpg_paths"])} references',
            'pattern': 'Fix /auntruth/jpg/ .jpg and similar malformed paths',
            'impact': f'{len(patterns["malformed_jpg_paths"])} broken links'
        })

    if patterns['missing_index_files']:
        script_suggestions.append({
            'priority': 'LOW',
            'name': 'create-missing-index-files.py',
            'description': f'Create missing index files rather than fixing {len(patterns["missing_index_files"])} references',
            'pattern': 'Create actual index.htm, index1.htm, etc. files',
            'impact': f'{len(patterns["missing_index_files"])} broken links'
        })

    # Sort by priority
    priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    script_suggestions.sort(key=lambda x: priority_order[x['priority']])

    print("\nRecommended scripts in priority order:")
    print("-" * 50)

    for i, script in enumerate(script_suggestions, 1):
        print(f"\n{i}. [{script['priority']} PRIORITY] {script['name']}")
        print(f"   Description: {script['description']}")
        print(f"   Pattern: {script['pattern']}")
        print(f"   Expected Impact: {script['impact']}")


def main():
    parser = argparse.ArgumentParser(description='Analyze broken link patterns from CSV reports')
    parser.add_argument('csv_files', nargs='*',
                       help='CSV files to analyze (default: use latest reports)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose output')

    args = parser.parse_args()

    # Default to latest reports if no files specified
    csv_files = args.csv_files
    if not csv_files:
        import glob
        import os
        reports_dir = 'PRPs/scripts/reports'
        if os.path.exists(reports_dir):
            htm_reports = glob.glob(f'{reports_dir}/broken_links_htm_*.csv')
            new_reports = glob.glob(f'{reports_dir}/broken_links_new_*.csv')

            if htm_reports:
                csv_files.append(sorted(htm_reports)[-1])  # Latest HTM report
            if new_reports:
                csv_files.append(sorted(new_reports)[-1])  # Latest NEW report

    if not csv_files:
        print("❌ No CSV files found. Please specify files or ensure reports exist.")
        sys.exit(1)

    print("🔍 Analyzing broken link patterns...")
    print("=" * 60)

    all_records = []
    for csv_file in csv_files:
        records = parse_csv_file(csv_file)
        all_records.extend(records)

    print(f"\nTotal records across all files: {len(all_records)}")

    # Perform analysis
    patterns = analyze_url_patterns(all_records)
    file_counts = analyze_frequency_by_file(all_records)
    filename_counts = analyze_broken_filenames(all_records)

    # Print results
    print_pattern_analysis(patterns)
    print_frequency_analysis(file_counts, filename_counts)
    suggest_fix_scripts(patterns)

    print(f"\n✅ Analysis complete! Found {len(patterns)} distinct patterns.")
    print("💡 Focus on HIGH priority scripts first for maximum impact.")


if __name__ == '__main__':
    main()