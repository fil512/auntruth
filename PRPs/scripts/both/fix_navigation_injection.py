#!/usr/bin/env python3
"""
Fix Navigation Injection Issues

This script fixes HTML files that have malformed structure which breaks
the JavaScript navigation injection. It ensures proper body structure
and adds fallback navigation elements.
"""

import os
import re
from pathlib import Path

def fix_html_structure(file_path):
    """Fix HTML structure issues that break navigation injection"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if file needs fixing
        if '<body>' in content or 'top-nav' in content:
            return False, "Already has proper structure"

        # Find where head ends
        head_end = content.find('</head>')
        if head_end == -1:
            return False, "No </head> found"

        # Split content at head end
        before_body = content[:head_end + 7]  # Include </head>
        after_head = content[head_end + 7:]

        # Remove any existing body tags that might be malformed
        after_head = re.sub(r'<body[^>]*>', '', after_head, flags=re.IGNORECASE)
        after_head = re.sub(r'</body>', '', after_head, flags=re.IGNORECASE)

        # Clean up any orphaned HTML tags at the start
        after_head = re.sub(r'^\s*</html>\s*', '', after_head.strip())

        # Add proper body structure with skip link and fallback navigation
        proper_body = f'''<body>
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

    <!-- Main content will be wrapped by JavaScript -->
    <main id="main-content">
{after_head.strip()}
    </main>
</body>
</html>'''

        # Reconstruct the file
        new_content = before_body + proper_body

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, "Fixed HTML structure"

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("Fixing Navigation Injection Issues")
    print("=" * 35)

    base_dir = "htm"
    if not os.path.exists(base_dir):
        print(f"❌ Directory {base_dir} not found!")
        return

    files_processed = 0
    files_fixed = 0
    files_skipped = 0
    errors = 0

    # Process sample files first to test
    sample_files = [
        "htm/L1/XF182.htm",
        "htm/L9/XF834.htm",
        "htm/L1/XI1831.htm"
    ]

    print("Testing on sample files first...")
    for file_path in sample_files:
        if os.path.exists(file_path):
            files_processed += 1
            success, message = fix_html_structure(file_path)

            if success:
                files_fixed += 1
                print(f"✅ Fixed: {file_path}")
            elif "Already has proper structure" in message:
                files_skipped += 1
                print(f"⏭️  Skipped: {file_path} - {message}")
            else:
                errors += 1
                print(f"❌ Error: {file_path} - {message}")

    print(f"\nSample Results:")
    print(f"Files processed: {files_processed}")
    print(f"Files fixed: {files_fixed}")
    print(f"Files skipped: {files_skipped}")
    print(f"Errors: {errors}")

    if files_fixed > 0:
        print(f"\n✅ Sample fixes successful. Applying to ALL files...")
        if True:  # Auto-apply
            print("\nApplying to all files...")

            files_processed = 0
            files_fixed = 0
            files_skipped = 0
            errors = 0

            # Find all HTML files
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.htm') and not file.endswith('.backup'):
                        file_path = os.path.join(root, file)
                        files_processed += 1

                        success, message = fix_html_structure(file_path)

                        if success:
                            files_fixed += 1
                            if files_fixed % 100 == 0:
                                print(f"Fixed {files_fixed} files...")
                        elif "Already has proper structure" in message:
                            files_skipped += 1
                        else:
                            errors += 1

            print(f"\nFinal Results:")
            print(f"Files processed: {files_processed}")
            print(f"Files fixed: {files_fixed}")
            print(f"Files skipped: {files_skipped}")
            print(f"Errors: {errors}")

if __name__ == "__main__":
    main()