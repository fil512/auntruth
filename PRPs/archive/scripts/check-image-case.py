#!/usr/bin/env python3
"""
Image Case Sensitivity Checker for Genealogy Site

Checks all HTML files for image references and verifies that the case
matches the actual image files on disk. This prevents broken images
on case-sensitive hosting like GitHub Pages.

Usage:
    python3 check-image-case.py [--fix] [--dry-run]
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

class ImageCaseChecker:
    def __init__(self, docs_path="/home/ken/wip/fam/auntruth/docs"):
        self.docs_path = Path(docs_path).resolve()
        self.htm_path = self.docs_path / "htm"
        self.jpg_path = self.docs_path / "jpg"

        # Build index of actual image files (case-sensitive)
        self.actual_images = {}
        self.build_image_index()

        # Track issues found
        self.case_mismatches = []
        self.missing_images = []
        self.files_checked = 0
        self.images_checked = 0

    def build_image_index(self):
        """Build index of all actual image files on disk"""
        print(f"Building image index from {self.jpg_path}")

        if not self.jpg_path.exists():
            print(f"Warning: jpg directory not found at {self.jpg_path}")
            return

        for img_file in self.jpg_path.iterdir():
            if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                # Store both the actual filename and lowercase version for lookup
                self.actual_images[img_file.name.lower()] = img_file.name

        print(f"Found {len(self.actual_images)} image files")

    def extract_image_references(self, html_content):
        """Extract all image references from HTML content"""
        # Pattern for img src attributes
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'

        # Pattern for background images in CSS
        bg_pattern = r'background[^:]*:\s*url\(["\']?([^"\'()]+)["\']?\)'

        images = []

        # Find img tags
        for match in re.finditer(img_pattern, html_content, re.IGNORECASE):
            img_src = match.group(1)
            images.append(('img', img_src, match.start(), match.end()))

        # Find background images
        for match in re.finditer(bg_pattern, html_content, re.IGNORECASE):
            bg_src = match.group(1)
            images.append(('background', bg_src, match.start(), match.end()))

        return images

    def normalize_image_path(self, img_src):
        """Normalize image path to just the filename"""
        # Remove leading slashes and path components
        img_src = img_src.strip()

        # Handle absolute paths like /auntruth/jpg/image.jpg
        if img_src.startswith('/auntruth/jpg/'):
            return img_src[14:]  # Remove '/auntruth/jpg/'
        elif img_src.startswith('/jpg/'):
            return img_src[5:]   # Remove '/jpg/'
        elif img_src.startswith('../jpg/'):
            return img_src[7:]   # Remove '../jpg/'
        elif img_src.startswith('jpg/'):
            return img_src[4:]   # Remove 'jpg/'

        # If it's just a filename or has other path structure
        return os.path.basename(img_src)

    def check_file(self, html_file):
        """Check a single HTML file for image case issues"""
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
            return []

        issues = []
        images = self.extract_image_references(content)

        for img_type, img_src, start_pos, end_pos in images:
            self.images_checked += 1
            filename = self.normalize_image_path(img_src)

            # Skip non-jpg images or external URLs
            if not filename or filename.startswith('http') or not filename.lower().endswith(('.jpg', '.jpeg')):
                continue

            filename_lower = filename.lower()

            if filename_lower in self.actual_images:
                actual_filename = self.actual_images[filename_lower]
                if filename != actual_filename:
                    # Case mismatch found
                    issue = {
                        'file': html_file,
                        'type': img_type,
                        'wrong_name': filename,
                        'correct_name': actual_filename,
                        'full_src': img_src,
                        'start_pos': start_pos,
                        'end_pos': end_pos
                    }
                    issues.append(issue)
                    self.case_mismatches.append(issue)
            else:
                # Image file not found
                issue = {
                    'file': html_file,
                    'type': img_type,
                    'missing_name': filename,
                    'full_src': img_src,
                    'start_pos': start_pos,
                    'end_pos': end_pos
                }
                issues.append(issue)
                self.missing_images.append(issue)

        return issues

    def fix_file(self, html_file, issues):
        """Fix case sensitivity issues in a single file"""
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
            return False

        # Sort issues by position (reverse order to maintain positions)
        issues_to_fix = [issue for issue in issues if 'correct_name' in issue]
        issues_to_fix.sort(key=lambda x: x['start_pos'], reverse=True)

        changes_made = 0

        for issue in issues_to_fix:
            old_src = issue['full_src']
            # Replace the filename part with correct case
            if '/jpg/' in old_src:
                new_src = old_src.replace(issue['wrong_name'], issue['correct_name'])
            else:
                new_src = old_src.replace(issue['wrong_name'], issue['correct_name'])

            # Replace in content
            content = content.replace(old_src, new_src)
            changes_made += 1

        if changes_made > 0:
            try:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed {changes_made} image references in {html_file}")
                return True
            except Exception as e:
                print(f"Error writing {html_file}: {e}")
                return False

        return False

    def scan_all_files(self, fix_issues=False, dry_run=False):
        """Scan all HTML files for image case issues"""
        if not self.htm_path.exists():
            print(f"Error: htm directory not found at {self.htm_path}")
            return

        print(f"Scanning HTML files in {self.htm_path}")
        print(f"Mode: {'FIX' if fix_issues and not dry_run else 'DRY-RUN' if dry_run else 'CHECK'}")
        print("-" * 50)

        for root, dirs, files in os.walk(self.htm_path):
            for file in files:
                if file.lower().endswith(('.html', '.htm')):
                    html_file = Path(root) / file
                    self.files_checked += 1

                    issues = self.check_file(html_file)

                    if issues:
                        print(f"\nIssues in {html_file}:")
                        for issue in issues:
                            if 'correct_name' in issue:
                                print(f"  Case mismatch: {issue['wrong_name']} → {issue['correct_name']}")
                            else:
                                print(f"  Missing image: {issue['missing_name']}")

                        if fix_issues and not dry_run:
                            self.fix_file(html_file, issues)

    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "="*60)
        print("IMAGE CASE SENSITIVITY REPORT")
        print("="*60)
        print(f"Files checked: {self.files_checked}")
        print(f"Image references checked: {self.images_checked}")
        print(f"Case mismatches found: {len(self.case_mismatches)}")
        print(f"Missing images found: {len(self.missing_images)}")

        if self.case_mismatches:
            print(f"\nCASE MISMATCHES ({len(self.case_mismatches)}):")
            files_affected = defaultdict(list)
            for issue in self.case_mismatches:
                files_affected[issue['file']].append(f"{issue['wrong_name']} → {issue['correct_name']}")

            for file_path, fixes in files_affected.items():
                print(f"  {file_path}:")
                for fix in fixes:
                    print(f"    {fix}")

        if self.missing_images:
            print(f"\nMISSING IMAGES ({len(self.missing_images)}):")
            files_affected = defaultdict(list)
            for issue in self.missing_images:
                files_affected[issue['file']].append(issue['missing_name'])

            for file_path, missing in files_affected.items():
                print(f"  {file_path}:")
                for img in missing:
                    print(f"    {img}")

def main():
    parser = argparse.ArgumentParser(description='Check image case sensitivity for genealogy site')
    parser.add_argument('--fix', action='store_true',
                       help='Fix case sensitivity issues automatically')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be fixed without making changes')
    parser.add_argument('--docs-path', default='/home/ken/wip/fam/auntruth/docs',
                       help='Path to docs directory (default: /home/ken/wip/fam/auntruth/docs)')

    args = parser.parse_args()

    checker = ImageCaseChecker(args.docs_path)
    checker.scan_all_files(fix_issues=args.fix, dry_run=args.dry_run)
    checker.print_summary()

    if checker.case_mismatches and not args.fix:
        print(f"\nTo fix these issues, run:")
        print(f"python3 {sys.argv[0]} --fix")

    elif checker.case_mismatches and args.fix and not args.dry_run:
        print(f"\nFixed {len(checker.case_mismatches)} case sensitivity issues!")
        print("Remember to commit these changes to git.")

if __name__ == "__main__":
    main()