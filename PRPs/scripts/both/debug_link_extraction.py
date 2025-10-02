#!/usr/bin/env python3
"""
Debug link extraction to compare original and generated HTML files.

Usage:
    python3 debug_link_extraction.py \
        --original docs/new/htm/L1/XF100.htm \
        --generated docs/new/htm/L1-generated-test/XF100.htm
"""

import argparse
from bs4 import BeautifulSoup
from pathlib import Path


def debug_links(original_path: Path, generated_path: Path):
    """Compare links between original and generated HTML."""

    # Read original
    with open(original_path, 'r', encoding='utf-8') as f:
        orig_soup = BeautifulSoup(f.read(), 'html.parser')

    # Read generated
    with open(generated_path, 'r', encoding='utf-8') as f:
        gen_soup = BeautifulSoup(f.read(), 'html.parser')

    # Find all links in original
    print("="*60)
    print("ORIGINAL LINKS:")
    print("="*60)
    for link in orig_soup.find_all('a'):
        text = link.get_text().strip()
        href = link.get('href')
        print(f"  Text: '{text}'")
        print(f"  Href: '{href}'")
        print(f"  Text (normalized): '{' '.join(text.split())}'")
        print()

    print("\n" + "="*60)
    print("GENERATED LINKS:")
    print("="*60)
    for link in gen_soup.find_all('a'):
        text = link.get_text().strip()
        href = link.get('href')
        print(f"  Text: '{text}'")
        print(f"  Href: '{href}'")
        print(f"  Text (normalized): '{' '.join(text.split())}'")
        print()


def main():
    parser = argparse.ArgumentParser(description='Debug link extraction between original and generated HTML')
    parser.add_argument('--original', required=True, help='Original HTML file path')
    parser.add_argument('--generated', required=True, help='Generated HTML file path')

    args = parser.parse_args()

    debug_links(Path(args.original), Path(args.generated))


if __name__ == '__main__':
    main()
