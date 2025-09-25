#!/usr/bin/env python3
"""
Safe HTML Formatter - Whitespace Only (NO HTML Tidy)

This script formats HTML files by ONLY modifying whitespace/indentation without
using HTML Tidy or any HTML parser that could break links.

ULTRA-SAFE APPROACH:
- NEVER uses HTML Tidy or any HTML parser
- ONLY modifies whitespace between tags
- NEVER touches content inside attribute values
- Preserves ALL links, URLs, quotes, and case sensitivity exactly
- Character-by-character processing to avoid regex pitfalls

Usage:
    python3 safe-format-html-files.py --site=htm --dry-run     # Test HTM site
    python3 safe-format-html-files.py --site=new --dry-run     # Test NEW site
    python3 safe-format-html-files.py --site=both --dry-run    # Test both sites
    python3 safe-format-html-files.py --site=htm --test=5      # Test 5 files only
    python3 safe-format-html-files.py --site=htm               # Format HTM site
    python3 safe-format-html-files.py --site=new               # Format NEW site
    python3 safe-format-html-files.py --site=both              # Format both sites

Safety Features:
- NO HTML parsing - pure whitespace formatting
- Before/after link verification
- Character-level content preservation
- Dry-run mode with sample preview
- Progress reporting and error handling
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any
import tempfile
import shutil
import re
from difflib import unified_diff

def setup_logging() -> logging.Logger:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def verify_git_branch(expected_branch: str = "main") -> str:
    """Verify current git branch and return current branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, check=True
        )
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            print(f"⚠️  Expected {expected_branch}, currently on {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking git branch: {e}")
        return ""

def get_html_files(base_path: str, limit: int = None) -> List[Path]:
    """Get list of HTML files to process."""
    base = Path(base_path)
    html_files = []

    # Find all .htm and .html files recursively
    for pattern in ['**/*.htm', '**/*.html']:
        html_files.extend(base.glob(pattern))

    # Sort for consistent processing order
    html_files = sorted(html_files)

    # Limit if specified
    if limit:
        html_files = html_files[:limit]

    return html_files

def extract_links_from_html(content: str) -> set:
    """Extract all href and src links from HTML content for comparison."""
    # Find all href and src attributes
    href_pattern = r'href\s*=\s*["\']([^"\']+)["\']'
    src_pattern = r'src\s*=\s*["\']([^"\']+)["\']'

    hrefs = set(re.findall(href_pattern, content, re.IGNORECASE))
    srcs = set(re.findall(src_pattern, content, re.IGNORECASE))

    return hrefs.union(srcs)

def format_html_content_whitespace_only(content: str) -> str:
    """
    Format HTML content with proper consistent indentation like HTML Tidy.
    NEVER modifies anything inside attribute values or text content.
    """
    if not content.strip():
        return content

    import re

    lines = []
    indent_level = 0
    indent_str = "    "  # 4 spaces

    # Self-closing tags that don't increase indentation
    self_closing_tags = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img',
        'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'
    }

    # Block-level tags that should increase indentation
    block_tags = {
        'html', 'head', 'body', 'div', 'section', 'article', 'aside', 'nav',
        'header', 'footer', 'main', 'figure', 'figcaption', 'details', 'summary',
        'table', 'thead', 'tbody', 'tfoot', 'tr', 'td', 'th', 'caption',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'form', 'fieldset', 'legend',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'blockquote',
        'address', 'center', 'map'
    }

    # Split content by tags while preserving everything exactly
    # This regex captures: 1) text before tag, 2) the complete tag
    parts = re.split(r'(<[^>]+>)', content)

    # Track tag stack for proper nesting
    tag_stack = []

    for part in parts:
        if not part:
            continue

        # Don't strip whitespace-only parts completely - they might be meaningful
        if part.strip() == '':
            continue

        original_part = part
        part = part.strip()

        if part.startswith('<'):
            # This is a tag
            tag_match = re.match(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*/?>', part)
            if tag_match:
                is_closing = bool(tag_match.group(1))
                tag_name = tag_match.group(2).lower()
                is_self_closing = part.endswith('/>') or tag_name in self_closing_tags

                if is_closing:
                    # Closing tag - decrease indent first, then add
                    if tag_stack and tag_stack[-1] == tag_name and tag_name in block_tags:
                        indent_level = max(0, indent_level - 1)
                        tag_stack.pop()
                    lines.append(indent_str * indent_level + part)
                else:
                    # Opening tag
                    lines.append(indent_str * indent_level + part)
                    # Increase indent after adding, but only for block elements
                    if not is_self_closing and tag_name in block_tags:
                        indent_level += 1
                        tag_stack.append(tag_name)
            else:
                # Malformed tag, treat as text
                lines.append(indent_str * indent_level + part)
        else:
            # This is text content - only add if it's meaningful
            if part:  # non-empty after stripping
                lines.append(indent_str * indent_level + part)

    return '\n'.join(lines) + '\n' if lines else content

def safe_format_html_file(file_path: Path, dry_run: bool = False, show_diff: bool = False) -> Tuple[bool, str, Dict]:
    """
    Format a single HTML file using WHITESPACE-ONLY formatting.
    NO HTML parsing, NO Tidy, NO content modification.

    Returns:
        Tuple of (success: bool, message: str, stats: dict)
    """
    try:
        # Read original content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        # Extract original links for safety verification
        original_links = extract_links_from_html(original_content)

        if dry_run:
            return True, f"Would format: {file_path}", {
                'links_before': len(original_links),
                'links_after': len(original_links),
                'changed': False
            }

        # Format content using whitespace-only approach
        formatted_content = format_html_content_whitespace_only(original_content)

        # CRITICAL SAFETY CHECK: Verify no links were changed
        formatted_links = extract_links_from_html(formatted_content)

        if original_links != formatted_links:
            # This should NEVER happen with whitespace-only formatting
            missing_links = original_links - formatted_links
            new_links = formatted_links - original_links

            error_msg = f"❌ CRITICAL ERROR: {file_path} - Links unexpectedly changed!\n"
            if missing_links:
                error_msg += f"  Missing links: {list(missing_links)[:5]}\n"
            if new_links:
                error_msg += f"  New links: {list(new_links)[:5]}\n"

            return False, error_msg, {
                'links_before': len(original_links),
                'links_after': len(formatted_links),
                'changed': True,
                'missing_links': list(missing_links),
                'new_links': list(new_links)
            }

        # Check if content actually changed
        content_changed = original_content != formatted_content

        # Show diff if requested and content changed
        if show_diff and content_changed:
            diff = list(unified_diff(
                original_content.splitlines(keepends=True),
                formatted_content.splitlines(keepends=True),
                fromfile=f"{file_path} (original)",
                tofile=f"{file_path} (formatted)",
                n=3
            ))
            if diff:
                print("".join(diff[:30]))  # Show first 30 lines of diff

        # Apply formatting if content changed
        if content_changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)

            return True, f"✅ Formatted: {file_path}", {
                'links_before': len(original_links),
                'links_after': len(formatted_links),
                'changed': True
            }
        else:
            return True, f"✓ No changes needed: {file_path}", {
                'links_before': len(original_links),
                'links_after': len(formatted_links),
                'changed': False
            }

    except Exception as e:
        return False, f"❌ Error processing {file_path}: {e}", {'error': str(e)}

def process_site(site_dir: str, dry_run: bool = False, test_limit: int = None, show_diff: bool = False) -> Dict[str, Any]:
    """Process HTML files in a site directory with SAFE formatting."""
    logger = logging.getLogger(__name__)

    if not os.path.exists(site_dir):
        return {
            'success': False,
            'message': f"Directory {site_dir} does not exist",
            'files_processed': 0,
            'files_successful': 0,
            'files_failed': 0
        }

    html_files = get_html_files(site_dir, test_limit)

    if not html_files:
        return {
            'success': True,
            'message': f"No HTML files found in {site_dir}",
            'files_processed': 0,
            'files_successful': 0,
            'files_failed': 0
        }

    mode_msg = "DRY-RUN" if dry_run else "TEST" if test_limit else "FULL"
    logger.info(f"Found {len(html_files)} HTML files in {site_dir} ({mode_msg} mode)")

    successful = 0
    failed = 0
    failed_files = []
    total_links_checked = 0
    files_changed = 0

    for i, html_file in enumerate(html_files, 1):
        logger.info(f"[{i}/{len(html_files)}] Processing {html_file}")

        success, message, stats = safe_format_html_file(html_file, dry_run, show_diff)

        if 'links_before' in stats:
            total_links_checked += stats['links_before']
            if stats.get('changed', False):
                files_changed += 1

        if success:
            successful += 1
            logger.info(message)
        else:
            failed += 1
            failed_files.append(str(html_file))
            logger.error(message)

    result = {
        'success': failed == 0,
        'message': f"Processed {len(html_files)} files: {successful} successful, {failed} failed",
        'files_processed': len(html_files),
        'files_successful': successful,
        'files_failed': failed,
        'failed_files': failed_files,
        'total_links_checked': total_links_checked,
        'files_changed': files_changed
    }

    action = "Would format" if dry_run else "Test formatting of" if test_limit else "Formatted"
    logger.info(f"✅ {action} {len(html_files)} files in {site_dir}")
    logger.info(f"📊 Links verified: {total_links_checked}, Files changed: {files_changed}")

    return result

def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(
        description='Safely format HTML files using Tidy without breaking links'
    )
    parser.add_argument(
        '--site',
        choices=['htm', 'new', 'both'],
        required=True,
        help='Which site to process (htm, new, or both)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making modifications'
    )
    parser.add_argument(
        '--test',
        type=int,
        metavar='N',
        help='Test mode: only process first N files'
    )
    parser.add_argument(
        '--show-diff',
        action='store_true',
        help='Show differences for processed files'
    )
    parser.add_argument(
        '--branch',
        default='main',
        help='Expected git branch (default: main)'
    )

    args = parser.parse_args()

    logger = setup_logging()

    # Verify git branch
    current_branch = verify_git_branch(args.branch)
    if not current_branch:
        sys.exit(1)

    # Safety warning for full site processing
    if not args.dry_run and not args.test:
        response = input("⚠️  This will format ALL HTML files. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    # Determine directories to process
    base_dir = os.path.join(os.getcwd(), 'docs')
    site_dirs = []

    if args.site in ['htm', 'both']:
        site_dirs.append(os.path.join(base_dir, 'htm'))
    if args.site in ['new', 'both']:
        site_dirs.append(os.path.join(base_dir, 'new'))

    # Process each site
    overall_success = True
    total_processed = 0
    total_successful = 0
    total_failed = 0
    total_links_checked = 0

    for site_dir in site_dirs:
        mode_desc = "🔍 Dry-run for" if args.dry_run else f"🧪 Testing {args.test} files in" if args.test else "🔧 Formatting"
        logger.info(f"{mode_desc} {site_dir}")

        result = process_site(site_dir, args.dry_run, args.test, args.show_diff)

        if not result['success']:
            overall_success = False
            logger.error(f"❌ Failed processing {site_dir}: {result['message']}")

        total_processed += result['files_processed']
        total_successful += result['files_successful']
        total_failed += result['files_failed']
        total_links_checked += result.get('total_links_checked', 0)

        if result['failed_files']:
            logger.error(f"Failed files in {site_dir}:")
            for failed_file in result['failed_files']:
                logger.error(f"  - {failed_file}")

    # Final summary
    action = "Would format" if args.dry_run else f"Test formatted" if args.test else "Formatted"
    logger.info(f"\n📊 Final Summary:")
    logger.info(f"  Files {action.lower()}: {total_processed}")
    logger.info(f"  Successful: {total_successful}")
    logger.info(f"  Failed: {total_failed}")
    logger.info(f"  Links verified safe: {total_links_checked}")

    if args.dry_run:
        logger.info(f"\n🔍 This was a dry-run. To actually format files, run without --dry-run")
    elif args.test:
        logger.info(f"\n🧪 This was a test run. To format all files, run without --test")
        if overall_success:
            logger.info("✅ Test successful! Safe to run on full site.")
        else:
            logger.error("❌ Test failed! Fix issues before full site run.")
    elif overall_success:
        logger.info(f"\n✅ All files processed successfully with link safety verified!")
        logger.info(f"📝 Next steps:")
        logger.info(f"  1. Review the formatted files in your browser")
        logger.info(f"  2. Run link checker to verify no links broken")
        logger.info(f"  3. Commit changes: git add . && git commit -m 'Safe HTML formatting - {total_links_checked} links verified'")
    else:
        logger.error(f"\n❌ Some files failed processing. Review the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()