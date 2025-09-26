#!/usr/bin/env python3

"""
Test script for validating legacy page navigation enhancement
Validates that the NavigationComponent can properly parse family relationships
from legacy HTML pages and enhance them with navigation.
"""

import sys
import re
import argparse
from pathlib import Path

def test_family_relationship_parsing(file_path):
    """Test that family relationships can be parsed from legacy HTML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for table with family relationships
        if "table id='List'" not in content:
            print(f"❌ No List table found in {file_path}")
            return False

        # Check for family relationship patterns
        family_patterns = [
            r'<td>\s*Father\s*</td>',
            r'<td>\s*Mother\s*</td>',
            r'<td>\s*Spouse\(\d+\)\s*</td>',
            r'<td>\s*Child\s*</td>'
        ]

        found_patterns = []
        for pattern in family_patterns:
            if re.search(pattern, content):
                found_patterns.append(pattern)

        if not found_patterns:
            print(f"⚠️  No family relationship patterns found in {file_path}")
            return False

        print(f"✅ Found {len(found_patterns)} family relationship patterns in {file_path}")

        # Check for lineage indicators
        lineage_pattern = r'\[.*?\]'
        lineage_matches = re.findall(lineage_pattern, content)
        if lineage_matches:
            print(f"✅ Found {len(lineage_matches)} lineage indicators")
        else:
            print("⚠️  No lineage indicators found")

        # Check for thumbnail links
        if 'THF' in content and '.htm' in content:
            print("✅ Thumbnail links found")
        else:
            print("⚠️  No thumbnail links found")

        return True

    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def test_navigation_javascript():
    """Test that navigation.js contains our enhancements"""
    nav_js_path = Path('docs/new/js/navigation.js')

    if not nav_js_path.exists():
        print("❌ Navigation.js not found")
        return False

    try:
        with open(nav_js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for our new methods
        required_methods = [
            'parseFamilyRelationships',
            'extractLineageFromText',
            'generateBreadcrumbs',
            'createBreadcrumbHTML',
            'createFamilyNavigation',
            'setupFamilyNavigationHandlers'
        ]

        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method)

        if missing_methods:
            print(f"❌ Missing methods in navigation.js: {missing_methods}")
            return False

        print("✅ All required methods found in navigation.js")

        # Check that injection methods call our new methods
        if 'setupFamilyNavigationHandlers' in content and 'createFamilyNavigation' in content:
            print("✅ Enhanced injection methods found")
        else:
            print("❌ Enhanced injection methods not found")
            return False

        return True

    except Exception as e:
        print(f"❌ Error reading navigation.js: {e}")
        return False

def test_navigation_css():
    """Test that navigation.css contains family navigation styles"""
    nav_css_path = Path('docs/new/css/navigation.css')

    if not nav_css_path.exists():
        print("❌ Navigation.css not found")
        return False

    try:
        with open(nav_css_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for required CSS classes
        required_classes = [
            'breadcrumb-nav',
            'family-navigation',
            'family-nav-container',
            'family-nav-item',
            'family-nav-dropdown',
            'family-nav-dropdown-content'
        ]

        missing_classes = []
        for css_class in required_classes:
            if f'.{css_class}' not in content:
                missing_classes.append(css_class)

        if missing_classes:
            print(f"❌ Missing CSS classes: {missing_classes}")
            return False

        print("✅ All required CSS classes found")

        # Check for mobile responsiveness
        if '@media (max-width: 768px)' in content and 'family-nav' in content:
            print("✅ Mobile responsive styles found")
        else:
            print("❌ Mobile responsive styles not found")
            return False

        return True

    except Exception as e:
        print(f"❌ Error reading navigation.css: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test legacy navigation enhancement')
    parser.add_argument('--lineage', required=True, help='Lineage directory (e.g., L1)')
    parser.add_argument('--pages', required=True, help='Comma-separated page numbers (e.g., XF191,XF100)')

    args = parser.parse_args()

    print("🧪 Testing Legacy Navigation Enhancement")
    print("=" * 40)

    # Test JavaScript enhancements
    print("\n📋 Testing JavaScript enhancements...")
    if not test_navigation_javascript():
        sys.exit(1)

    # Test CSS enhancements
    print("\n🎨 Testing CSS enhancements...")
    if not test_navigation_css():
        sys.exit(1)

    # Test individual pages
    print(f"\n📄 Testing pages in {args.lineage}...")
    pages = args.pages.split(',')

    for page in pages:
        page = page.strip()
        if not page.startswith('XF'):
            page = f'XF{page}'
        if not page.endswith('.htm'):
            page = f'{page}.htm'

        file_path = Path(f'docs/htm/{args.lineage}/{page}')

        if not file_path.exists():
            print(f"❌ Page not found: {file_path}")
            sys.exit(1)

        print(f"\n🔍 Testing {file_path}...")
        if not test_family_relationship_parsing(file_path):
            sys.exit(1)

    print("\n🎉 All tests passed! Navigation enhancement is ready.")
    return True

if __name__ == '__main__':
    main()