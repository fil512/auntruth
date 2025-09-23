#!/usr/bin/env python3
"""
Comprehensive HTML Cleanup for Navigation Modernization

This script completely restructures all HTML files to work properly with
the JavaScript navigation system by:

1. Fixing malformed HTML structure
2. Removing old navigation elements that conflict
3. Adding proper semantic HTML5 structure
4. Ensuring JavaScript can inject navigation correctly
5. Cleaning up legacy formatting issues
"""

import os
import re
from pathlib import Path
from html.parser import HTMLParser

class HTMLCleaner:
    def __init__(self):
        self.title = ""
        self.head_content = []
        self.body_content = []
        self.css_links = []
        self.js_scripts = []

    def clean_html_file(self, file_path):
        """Completely restructure an HTML file for modern navigation"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Skip if already properly structured
            if self._is_already_clean(content):
                return False, "Already clean"

            # Extract components
            title = self._extract_title(content)
            head_links = self._extract_head_links(content)
            body_content = self._extract_body_content(content)

            # Clean up the body content
            cleaned_body = self._clean_body_content(body_content)

            # Build new HTML structure
            new_html = self._build_clean_html(title, head_links, cleaned_body)

            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_html)

            return True, "Cleaned successfully"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def _is_already_clean(self, content):
        """Check if file is already properly structured"""
        return (
            '<!-- MODERNIZED -->' in content or
            ('<body>' in content and
             '<main class="page-content">' in content and
             'Skip to main content' in content)
        )

    def _extract_title(self, content):
        """Extract title from HTML"""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up title - remove <br> tags and normalize
            title = re.sub(r'<br[^>]*>', ' - ', title)
            title = re.sub(r'<[^>]+>', '', title)  # Remove any other tags
            title = re.sub(r'\s+', ' ', title).strip()
            return title
        return "AuntieRuth.com"

    def _extract_head_links(self, content):
        """Extract CSS and JS links from head"""
        links = {
            'css': [],
            'js': [],
            'meta': []
        }

        # Extract CSS links
        css_patterns = [
            r'<link[^>]*href="[^"]*\.css"[^>]*>',
            r'<link[^>]*rel="stylesheet"[^>]*>'
        ]
        for pattern in css_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            links['css'].extend(matches)

        # Extract JS scripts
        js_patterns = [
            r'<script[^>]*src="[^"]*\.js"[^>]*></script>',
            r'<link[^>]*as="script"[^>]*>'
        ]
        for pattern in js_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            links['js'].extend(matches)

        return links

    def _extract_body_content(self, content):
        """Extract the actual content from body"""
        # Find content after </head>
        head_end = content.find('</head>')
        if head_end == -1:
            return content

        after_head = content[head_end + 7:]

        # Remove various opening elements
        after_head = re.sub(r'<html[^>]*>', '', after_head, flags=re.IGNORECASE)
        after_head = re.sub(r'<body[^>]*>', '', after_head, flags=re.IGNORECASE)
        after_head = re.sub(r'</body>', '', after_head, flags=re.IGNORECASE)
        after_head = re.sub(r'</html>', '', after_head, flags=re.IGNORECASE)

        # Remove navigation scripts from body (we'll add them properly)
        after_head = re.sub(r'<!-- Enhanced navigation.*?</script>', '', after_head, flags=re.DOTALL)

        return after_head.strip()

    def _clean_body_content(self, body_content):
        """Clean up legacy body content"""
        content = body_content

        # Remove old navigation elements that conflict
        content = re.sub(r'<div id="headlinks">.*?</div>', '', content, flags=re.DOTALL)

        # Fix broken image paths
        content = re.sub(r'src="/jpg/', 'src="/auntruth/jpg/', content)
        content = re.sub(r'src="/auntruth/jpg/', 'src="/auntruth/jpg/', content)  # Don't double-fix

        # Clean up excessive <br> tags at the start
        content = re.sub(r'^(\s*<br[^>]*>\s*){1,3}', '', content)

        # Fix old-style centering and add semantic structure
        content = self._add_semantic_structure(content)

        return content.strip()

    def _add_semantic_structure(self, content):
        """Add semantic HTML5 structure to content"""
        # Wrap main heading if it exists
        content = re.sub(
            r'<center><h1>(.*?)</h1></center>',
            r'<header class="page-header"><h1>\1</h1></header>',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Wrap image if it exists near the top
        content = re.sub(
            r'<center><img([^>]*)></center>',
            r'<figure class="page-image"><img\1></figure>',
            content,
            flags=re.IGNORECASE
        )

        # Wrap main data table
        content = re.sub(
            r'(<table id="List".*?</table>)',
            r'<section class="person-details">\1</section>',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        return content

    def _build_clean_html(self, title, head_links, body_content):
        """Build completely clean HTML structure"""

        # Standard CSS links (ensure we have the right ones)
        css_links = [
            '<link href="/auntruth/new/css/main.css" rel="stylesheet" type="text/css">',
            '<link href="/auntruth/new/css/navigation.css" rel="stylesheet">'
        ]

        # Standard JS preloads
        js_preloads = [
            '<link rel="preload" href="/auntruth/new/js/navigation.js" as="script">',
            '<link rel="preload" href="/auntruth/new/js/search.js" as="script">'
        ]

        # Standard JS scripts
        js_scripts = [
            '<script src="/auntruth/new/js/navigation.js" defer></script>',
            '<script src="/auntruth/new/js/search.js" defer></script>'
        ]

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {chr(10).join(css_links)}
    {chr(10).join(js_preloads)}
    <!-- MODERNIZED -->
</head>
<body>
    <!-- Skip link for accessibility -->
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <!-- Fallback navigation for no-JS users -->
    <noscript>
        <nav class="fallback-nav" style="background: #fff; padding: 1rem; border-bottom: 1px solid #ddd;">
            <a href="/auntruth/new/">Home</a> |
            <a href="/auntruth/new/htm/L0/">Base</a> |
            <a href="/auntruth/new/htm/L1/">Hagborg-Hansson</a> |
            <a href="/auntruth/new/htm/L2/">Nelson</a> |
            <a href="/auntruth/htm/">Original Site</a>
        </nav>
    </noscript>

    <!-- Main page content -->
    <main id="main-content" class="page-content">
{body_content}
    </main>

    <!-- Navigation and search scripts -->
    {chr(10).join(js_scripts)}
</body>
</html>'''


def main():
    print("Comprehensive HTML Cleanup for Navigation")
    print("=" * 45)

    base_dir = "htm"
    if not os.path.exists(base_dir):
        print(f"❌ Directory {base_dir} not found!")
        return

    cleaner = HTMLCleaner()

    # Test on sample files first
    sample_files = [
        "htm/L1/XF182.htm",
        "htm/L9/XF834.htm",
        "htm/L1/XI1831.htm",
        "htm/TH1890.htm",
        "htm/THNY.htm"
    ]

    print("Testing on sample files...")
    files_processed = 0
    files_cleaned = 0
    files_skipped = 0
    errors = 0

    for file_path in sample_files:
        if os.path.exists(file_path):
            files_processed += 1
            success, message = cleaner.clean_html_file(file_path)

            if success:
                files_cleaned += 1
                print(f"✅ Cleaned: {file_path}")
            elif "Already clean" in message:
                files_skipped += 1
                print(f"⏭️  Skipped: {file_path} - {message}")
            else:
                errors += 1
                print(f"❌ Error: {file_path} - {message}")

    print(f"\nSample Results:")
    print(f"Files processed: {files_processed}")
    print(f"Files cleaned: {files_cleaned}")
    print(f"Files skipped: {files_skipped}")
    print(f"Errors: {errors}")

    if files_cleaned > 0 or files_processed > 0:
        print(f"\n🚀 Applying cleanup to ALL {base_dir} files...")

        files_processed = 0
        files_cleaned = 0
        files_skipped = 0
        errors = 0

        # Process all HTML files
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.htm') and not file.endswith('.backup'):
                    file_path = os.path.join(root, file)
                    files_processed += 1

                    success, message = cleaner.clean_html_file(file_path)

                    if success:
                        files_cleaned += 1
                        if files_cleaned % 200 == 0:
                            print(f"Cleaned {files_cleaned} files...")
                    elif "Already clean" in message:
                        files_skipped += 1
                    else:
                        errors += 1
                        if errors <= 5:  # Show first few errors
                            print(f"❌ {file_path}: {message}")

        print(f"\n🎉 Final Results:")
        print(f"Files processed: {files_processed}")
        print(f"Files cleaned: {files_cleaned}")
        print(f"Files skipped (already clean): {files_skipped}")
        print(f"Errors: {errors}")

        if files_cleaned > 0:
            print(f"\n✅ Successfully cleaned {files_cleaned} HTML files!")
            print("Navigation should now work properly on all pages.")
        else:
            print("ℹ️  All files were already clean.")

if __name__ == "__main__":
    main()