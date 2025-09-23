#!/usr/bin/env python3
"""
Navigation Update Script for AuntieRuth.com Modernization
Updates all HTML files to include modern navigation components

This script processes ~11,070 HTML files to:
- Add proper DOCTYPE and meta tags
- Update CSS links to new enhanced versions
- Add navigation and search JavaScript
- Inject accessibility features
- Update internal links to new paths
- Preserve all original content
"""

import os
import re
import argparse
from pathlib import Path
from html.parser import HTMLParser
from typing import Dict, List, Optional, Set
import logging
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HTMLNavigationUpdater(HTMLParser):
    """HTML parser that updates navigation while preserving content"""

    def __init__(self):
        super().__init__()
        self.reset()
        self.output = []
        self.in_head = False
        self.in_body = False
        self.in_title = False
        self.has_doctype = False
        self.has_meta_charset = False
        self.has_meta_viewport = False
        self.title_content = ""
        self.head_content = []
        self.body_content = []
        self.current_tag = None
        self.tag_stack = []

    def handle_decl(self, decl):
        if 'DOCTYPE' in decl.upper():
            self.has_doctype = True
            # Always use HTML5 doctype
            self.output.append('<!DOCTYPE html>')
        else:
            self.output.append(f'<!{decl}>')

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.tag_stack.append(tag)

        if tag == 'html':
            # Ensure lang attribute
            attr_dict = dict(attrs)
            if 'lang' not in attr_dict:
                attrs = list(attrs) + [('lang', 'en')]
            self.output.append(self.reconstruct_tag(tag, attrs))
        elif tag == 'head':
            self.in_head = True
            self.output.append('<head>')
        elif tag == 'body':
            self.in_body = True
            self.output.append('<body>')
        elif tag == 'title':
            self.in_title = True
            self.output.append('<title>')
        elif self.in_head and tag == 'meta':
            attr_dict = dict(attrs)
            if attr_dict.get('charset'):
                self.has_meta_charset = True
            elif attr_dict.get('name') == 'viewport':
                self.has_meta_viewport = True
            self.output.append(self.reconstruct_tag(tag, attrs, self_closing=True))
        elif self.in_head and tag == 'link':
            # Update CSS links
            attr_dict = dict(attrs)
            if attr_dict.get('rel') == 'stylesheet':
                href = attr_dict.get('href', '')
                if 'htm.css' in href:
                    # Replace with new CSS
                    new_attrs = []
                    for name, value in attrs:
                        if name == 'href':
                            new_attrs.append(('href', '/auntruth/new/css/main.css'))
                        else:
                            new_attrs.append((name, value))
                    self.output.append(self.reconstruct_tag(tag, new_attrs, self_closing=True))
                    # Add navigation CSS
                    self.output.append('<link href="/auntruth/new/css/navigation.css" rel="stylesheet">')
                else:
                    self.output.append(self.reconstruct_tag(tag, attrs, self_closing=True))
            else:
                self.output.append(self.reconstruct_tag(tag, attrs, self_closing=True))
        else:
            self.output.append(self.reconstruct_tag(tag, attrs))

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

        if tag == 'head':
            self.in_head = False
            # Add missing meta tags and new resources
            if not self.has_meta_charset:
                self.output.append('<meta charset="UTF-8">')
            if not self.has_meta_viewport:
                self.output.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')

            # Add preload for critical resources
            self.output.append('<link rel="preload" href="/auntruth/new/js/navigation.js" as="script">')
            self.output.append('<link rel="preload" href="/auntruth/new/js/search.js" as="script">')

            self.output.append('</head>')
        elif tag == 'body':
            self.in_body = False
            # Add JavaScript before closing body
            self.output.append('<!-- Enhanced navigation and search scripts -->')
            self.output.append('<script src="/auntruth/new/js/navigation.js" defer></script>')
            self.output.append('<script src="/auntruth/new/js/search.js" defer></script>')
            self.output.append('</body>')
        elif tag == 'title':
            self.in_title = False
            self.output.append('</title>')
        else:
            self.output.append(f'</{tag}>')

    def handle_data(self, data):
        if self.in_title:
            self.title_content += data
        self.output.append(data)

    def reconstruct_tag(self, tag, attrs, self_closing=False):
        """Reconstruct HTML tag with attributes"""
        if not attrs:
            return f'<{tag}>' if not self_closing else f'<{tag}>'

        attr_strings = []
        for name, value in attrs:
            if value is None:
                attr_strings.append(name)
            else:
                # Escape quotes in attribute values
                escaped_value = value.replace('"', '&quot;')
                attr_strings.append(f'{name}="{escaped_value}"')

        attrs_str = ' ' + ' '.join(attr_strings) if attr_strings else ''
        return f'<{tag}{attrs_str}>'

    def get_updated_html(self):
        """Get the updated HTML content"""
        result = ''.join(self.output)

        # Ensure DOCTYPE is present
        if not self.has_doctype:
            result = '<!DOCTYPE html>\n' + result

        return result

class NavigationUpdateProcessor:
    """Main class for processing HTML files and updating navigation"""

    def __init__(self, source_dir: str = 'docs/new/htm', dry_run: bool = False):
        self.source_dir = Path(source_dir)
        self.dry_run = dry_run
        self.processed_files = 0
        self.error_files = 0
        self.updated_files = 0
        self.skipped_files = 0

        # Track link updates
        self.link_updates = {
            '/auntruth/htm/': '/auntruth/new/htm/',
            '/AuntRuth/': '/auntruth/new/',
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed"""
        # Process all .htm and .html files
        if file_path.suffix.lower() not in ['.htm', '.html']:
            return False

        # Skip already modernized files (those that already have navigation.js)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)  # Check first 2KB
                if 'navigation.js' in content:
                    return False
        except Exception:
            return False

        return True

    def update_internal_links(self, content: str) -> str:
        """Update internal links to point to new paths"""
        updated_content = content

        for old_path, new_path in self.link_updates.items():
            updated_content = updated_content.replace(old_path, new_path)

        return updated_content

    def process_file(self, file_path: Path) -> bool:
        """Process a single HTML file"""
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Parse and update HTML
            parser = HTMLNavigationUpdater()
            parser.feed(content)
            updated_content = parser.get_updated_html()

            # Update internal links
            updated_content = self.update_internal_links(updated_content)

            # Add accessibility skip link if not present
            if 'skip-link' not in updated_content and '<body>' in updated_content:
                skip_link = '''<!-- Skip link for accessibility -->
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

    '''
                updated_content = updated_content.replace('<body>', f'<body>\n{skip_link}')

            # Wrap main content if not already wrapped
            if 'main-content' not in updated_content and '<body>' in updated_content:
                # Find content after navigation
                body_start = updated_content.find('<body>')
                if body_start != -1:
                    # Insert main wrapper after the fallback navigation
                    noscript_end = updated_content.find('</noscript>')
                    if noscript_end != -1:
                        insertion_point = noscript_end + 11
                        before_main = updated_content[:insertion_point]
                        after_main = updated_content[insertion_point:]

                        # Add main wrapper
                        main_start = '\n    <!-- Main content -->\n    <main id="main-content" class="main-content" role="main">\n'
                        main_end = '\n    </main>\n'

                        # Find where to close main (before scripts)
                        script_start = after_main.find('<!-- Enhanced navigation')
                        if script_start != -1:
                            content_part = after_main[:script_start]
                            scripts_part = after_main[script_start:]
                            updated_content = before_main + main_start + content_part + main_end + scripts_part
                        else:
                            # No scripts found, close before </body>
                            body_end = after_main.rfind('</body>')
                            if body_end != -1:
                                content_part = after_main[:body_end]
                                body_close = after_main[body_end:]
                                updated_content = before_main + main_start + content_part + main_end + body_close

            # Write updated content if not dry run
            if not self.dry_run:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                shutil.copy2(file_path, backup_path)

                # Write updated file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                logger.debug(f"Updated: {file_path}")
            else:
                logger.debug(f"Would update: {file_path}")

            self.updated_files += 1
            return True

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.error_files += 1
            return False

    def scan_and_process(self) -> bool:
        """Scan directories and process all HTML files"""
        logger.info(f"Starting navigation update from {self.source_dir}")

        if self.dry_run:
            logger.info("DRY RUN MODE - No files will be modified")

        if not self.source_dir.exists():
            logger.error(f"Source directory does not exist: {self.source_dir}")
            return False

        # Find all HTML files
        html_files = []
        for pattern in ['**/*.htm', '**/*.html']:
            html_files.extend(self.source_dir.glob(pattern))

        logger.info(f"Found {len(html_files)} HTML files to check")

        # Process each file
        for i, file_path in enumerate(html_files):
            if i % 100 == 0 and i > 0:
                logger.info(f"Processed {i}/{len(html_files)} files...")

            if self.should_process_file(file_path):
                self.process_file(file_path)
                self.processed_files += 1
            else:
                self.skipped_files += 1

        logger.info(f"Processing complete!")
        logger.info(f"Total files checked: {len(html_files)}")
        logger.info(f"Files processed: {self.processed_files}")
        logger.info(f"Files updated: {self.updated_files}")
        logger.info(f"Files skipped: {self.skipped_files}")
        logger.info(f"Errors: {self.error_files}")

        return True

    def restore_backups(self) -> bool:
        """Restore all files from backups"""
        logger.info("Restoring files from backups...")

        backup_files = list(self.source_dir.glob('**/*.backup'))

        for backup_file in backup_files:
            original_file = backup_file.with_suffix('')
            try:
                shutil.move(backup_file, original_file)
                logger.debug(f"Restored: {original_file}")
            except Exception as e:
                logger.error(f"Error restoring {original_file}: {e}")

        logger.info(f"Restored {len(backup_files)} files from backups")
        return True

    def clean_backups(self) -> bool:
        """Remove all backup files"""
        logger.info("Cleaning backup files...")

        backup_files = list(self.source_dir.glob('**/*.backup'))

        for backup_file in backup_files:
            try:
                backup_file.unlink()
                logger.debug(f"Removed backup: {backup_file}")
            except Exception as e:
                logger.error(f"Error removing backup {backup_file}: {e}")

        logger.info(f"Removed {len(backup_files)} backup files")
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Update navigation for AuntieRuth.com modernization')
    parser.add_argument('--source-dir', default='docs/new/htm',
                       help='Source directory containing HTML files (default: docs/new/htm)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without modifying files')
    parser.add_argument('--restore', action='store_true',
                       help='Restore files from backups')
    parser.add_argument('--clean-backups', action='store_true',
                       help='Remove backup files')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    processor = NavigationUpdateProcessor(args.source_dir, args.dry_run)

    try:
        if args.restore:
            success = processor.restore_backups()
        elif args.clean_backups:
            success = processor.clean_backups()
        else:
            success = processor.scan_and_process()

        if success:
            logger.info("Operation completed successfully!")
            return 0
        else:
            logger.error("Operation failed!")
            return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())