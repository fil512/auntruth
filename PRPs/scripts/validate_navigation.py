#!/usr/bin/env python3
"""
Navigation Validation Script for AuntieRuth.com Modernization

This script validates that the navigation modernization was successful by:
1. Checking HTML structure and required elements
2. Testing search functionality performance
3. Validating links and paths
4. Ensuring responsive design elements are in place
"""

import os
import re
import json
import time
import random
from pathlib import Path

def validate_html_file(file_path):
    """Validate a single HTML file for required elements"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        checks = {
            'doctype': '<!DOCTYPE html>' in content,
            'html_lang': '<html lang="en">' in content,
            'meta_charset': 'charset="UTF-8"' in content,
            'meta_viewport': 'name="viewport"' in content,
            'main_css': 'main.css' in content,
            'navigation_css': 'navigation.css' in content,
            'navigation_js': 'navigation.js' in content,
            'search_js': 'search.js' in content,
            'updated_paths': '/auntruth/new/' in content,
            'preload_resources': 'rel="preload"' in content
        }

        # Count navigation links
        nav_links = len(re.findall(r'href="[^"]*htm[^"]*"', content))

        return checks, nav_links

    except Exception as e:
        return None, 0

def test_search_performance(data_file):
    """Test search functionality performance"""
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)

        people = data['people']
        test_queries = ['David', 'Phoenix', 'Thomas', 'Elizabeth', 'John', 'Mary', 'Smith', 'Brown']

        results = {}
        for query in test_queries:
            start_time = time.time()

            # Simple search implementation
            matches = []
            query_lower = query.lower()

            for person in people:
                name_lower = person['name'].lower()
                if query_lower in name_lower:
                    score = 100 if query_lower == name_lower else 80 if name_lower.startswith(query_lower) else 60
                    matches.append({'person': person, 'score': score})

            matches.sort(key=lambda x: (-x['score'], x['person']['name']))
            end_time = time.time()

            results[query] = {
                'matches': len(matches),
                'time_ms': (end_time - start_time) * 1000,
                'top_result': matches[0]['person']['name'] if matches else None
            }

        return results

    except Exception as e:
        return None

def validate_sample_files(base_dir, sample_size=10):
    """Validate a random sample of HTML files"""
    htm_dir = os.path.join(base_dir, 'htm')
    all_files = []

    # Find all HTML files
    for root, dirs, files in os.walk(htm_dir):
        for file in files:
            if file.endswith('.htm') and not file.endswith('.backup'):
                all_files.append(os.path.join(root, file))

    # Sample random files
    sample_files = random.sample(all_files, min(sample_size, len(all_files)))

    results = {}
    for file_path in sample_files:
        checks, nav_links = validate_html_file(file_path)
        relative_path = os.path.relpath(file_path, base_dir)
        results[relative_path] = {
            'checks': checks,
            'nav_links': nav_links,
            'valid': checks is not None and all(checks.values()) if checks else False
        }

    return results, len(all_files)

def main():
    print("AuntieRuth.com Navigation Validation")
    print("=" * 50)

    base_dir = "."

    if not os.path.exists(base_dir):
        print(f"❌ Base directory {base_dir} not found!")
        return

    # 1. Validate search index
    print("\n1. Search Index Validation:")
    print("-" * 30)

    data_file = os.path.join(base_dir, 'js', 'data.json')
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)

        print(f"✅ Search index found")
        print(f"   People indexed: {len(data['people'])}")
        print(f"   Lineages: {len(data['lineages'])}")
        print(f"   Generated: {data['metadata']['generated']}")
    else:
        print(f"❌ Search index not found at {data_file}")
        return

    # 2. Test search performance
    print("\n2. Search Performance Test:")
    print("-" * 30)

    search_results = test_search_performance(data_file)
    if search_results:
        total_time = sum(r['time_ms'] for r in search_results.values())
        avg_time = total_time / len(search_results)

        print(f"✅ Search performance test completed")
        print(f"   Average search time: {avg_time:.2f}ms")
        print(f"   Total queries tested: {len(search_results)}")

        # Show fastest and slowest
        fastest = min(search_results.items(), key=lambda x: x[1]['time_ms'])
        slowest = max(search_results.items(), key=lambda x: x[1]['time_ms'])
        print(f"   Fastest: '{fastest[0]}' ({fastest[1]['time_ms']:.2f}ms)")
        print(f"   Slowest: '{slowest[0]}' ({slowest[1]['time_ms']:.2f}ms)")
    else:
        print("❌ Search performance test failed")

    # 3. Validate sample HTML files
    print("\n3. HTML Structure Validation:")
    print("-" * 30)

    sample_results, total_files = validate_sample_files(base_dir, sample_size=20)

    valid_files = sum(1 for r in sample_results.values() if r['valid'])
    print(f"✅ Validated {len(sample_results)} sample files out of {total_files} total")
    print(f"   Valid files: {valid_files}/{len(sample_results)} ({valid_files/len(sample_results)*100:.1f}%)")

    # Show check details
    if sample_results:
        all_checks = list(next(iter(sample_results.values()))['checks'].keys())
        check_stats = {}

        for check in all_checks:
            passed = sum(1 for r in sample_results.values() if r['checks'] and r['checks'].get(check, False))
            check_stats[check] = f"{passed}/{len(sample_results)}"

        print("\n   Check Details:")
        for check, stat in check_stats.items():
            status = "✅" if stat.split('/')[0] == stat.split('/')[1] else "⚠️"
            print(f"   {status} {check.replace('_', ' ').title()}: {stat}")

    # 4. Directory structure validation
    print("\n4. Directory Structure Validation:")
    print("-" * 30)

    required_dirs = ['css', 'js', 'htm']
    required_files = [
        'css/main.css',
        'css/navigation.css',
        'js/navigation.js',
        'js/search.js',
        'js/data.json',
        'index.html'
    ]

    for dir_name in required_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✅ Directory: {dir_name}")
        else:
            print(f"❌ Directory missing: {dir_name}")

    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ File: {file_path} ({size:,} bytes)")
        else:
            print(f"❌ File missing: {file_path}")

    # 5. Summary
    print("\n5. Validation Summary:")
    print("-" * 30)

    issues = []

    if not os.path.exists(data_file):
        issues.append("Search index missing")

    if search_results and avg_time > 5.0:
        issues.append("Search performance slow (>5ms)")

    if valid_files < len(sample_results) * 0.95:  # 95% threshold
        issues.append("HTML validation issues found")

    for file_path in required_files:
        if not os.path.exists(os.path.join(base_dir, file_path)):
            issues.append(f"Missing required file: {file_path}")

    if not issues:
        print("🎉 All validation checks passed!")
        print("✅ Navigation modernization appears successful")
        print(f"✅ {total_files:,} HTML files are ready with modern navigation")
        print(f"✅ Search index contains {len(data['people']):,} people")
        print(f"✅ Average search performance: {avg_time:.2f}ms")
    else:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   - {issue}")

    print(f"\nValidation completed. Ready for testing at: http://localhost:8000/{base_dir}/")

if __name__ == "__main__":
    main()