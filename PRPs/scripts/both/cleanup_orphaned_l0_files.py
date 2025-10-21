#!/usr/bin/env python3
"""
Cleanup Orphaned L0 Files

Identifies and removes HTML files in docs/new/htm/L0/ that don't have
corresponding JSON source files in data/people/Other/.

The L0 directory should only contain files for the "Other" lineage,
but currently has 889+ orphaned legacy files that were incorrectly copied.

Usage:
    python3 cleanup_orphaned_l0_files.py --dry-run    # List orphans, don't delete
    python3 cleanup_orphaned_l0_files.py --delete     # Delete orphans
"""

import argparse
import json
import os
from pathlib import Path


def find_orphaned_files(l0_dir: Path, other_json_dir: Path, dry_run: bool = True):
    """
    Find HTML files in L0 that don't have corresponding JSON sources.

    Args:
        l0_dir: Path to docs/new/htm/L0 directory
        other_json_dir: Path to data/people/Other directory
        dry_run: If True, only list orphans; if False, delete them

    Returns:
        Tuple of (orphan_count, kept_count, orphan_list)
    """
    # Get all HTML files in L0 (person files only, XF*.htm pattern)
    l0_html_files = list(l0_dir.glob("XF*.htm"))

    # Get all JSON files in Other lineage
    other_json_files = list(other_json_dir.glob("XF*.json"))

    # Build set of valid person IDs from JSON
    valid_ids = set()
    for json_file in other_json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            person_id = data.get('id')
            if person_id:
                valid_ids.add(person_id)

    print(f"\n📊 Analysis:")
    print(f"   HTML files in L0: {len(l0_html_files)}")
    print(f"   JSON files in Other: {len(other_json_files)}")
    print(f"   Valid person IDs: {len(valid_ids)}")

    # Find orphans
    orphans = []
    kept = []

    for html_file in l0_html_files:
        person_id = html_file.stem  # e.g., "XF191" from "XF191.htm"

        if person_id in valid_ids:
            kept.append(html_file)
        else:
            orphans.append(html_file)

    print(f"\n🔍 Results:")
    print(f"   ✅ Files to KEEP: {len(kept)}")
    print(f"   ❌ Orphaned files: {len(orphans)}")

    # Show some examples
    if orphans:
        print(f"\n📋 Example orphaned files (first 20):")
        for orphan in sorted(orphans)[:20]:
            file_size = orphan.stat().st_size
            size_kb = file_size / 1024
            print(f"   - {orphan.name} ({size_kb:.1f} KB)")

        if len(orphans) > 20:
            print(f"   ... and {len(orphans) - 20} more")

    # Show kept files for verification
    if kept:
        print(f"\n✅ Files being kept (should match Other lineage):")
        for keep_file in sorted(kept)[:10]:
            print(f"   - {keep_file.name}")
        if len(kept) > 10:
            print(f"   ... and {len(kept) - 10} more")

    # Delete if requested
    if not dry_run and orphans:
        print(f"\n🗑️  Deleting {len(orphans)} orphaned files...")
        deleted_count = 0
        for orphan in orphans:
            try:
                orphan.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"   ⚠️  Failed to delete {orphan.name}: {e}")

        print(f"   ✅ Deleted {deleted_count} files")

    return len(orphans), len(kept), [str(f) for f in orphans]


def main():
    parser = argparse.ArgumentParser(
        description="Cleanup orphaned HTML files in docs/new/htm/L0/",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='List orphaned files without deleting (default)'
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Actually delete orphaned files'
    )

    args = parser.parse_args()

    # Set dry_run mode
    dry_run = not args.delete

    # Paths (script is in PRPs/scripts/both, so go up 3 levels to repo root)
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent.parent
    l0_dir = repo_root / "docs" / "new" / "htm" / "L0"
    other_json_dir = repo_root / "data" / "people" / "Other"

    # Validate paths
    if not l0_dir.exists():
        print(f"❌ Error: L0 directory not found: {l0_dir}")
        return 1

    if not other_json_dir.exists():
        print(f"❌ Error: Other JSON directory not found: {other_json_dir}")
        return 1

    # Show mode
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
        print("   Run with --delete to actually remove orphaned files")
    else:
        print("⚠️  DELETE MODE - Orphaned files will be removed!")

    # Run cleanup
    orphan_count, kept_count, orphan_list = find_orphaned_files(
        l0_dir, other_json_dir, dry_run
    )

    # Summary
    print(f"\n" + "="*60)
    print(f"Summary:")
    print(f"  Orphaned files found: {orphan_count}")
    print(f"  Legitimate files kept: {kept_count}")

    if dry_run and orphan_count > 0:
        print(f"\n💡 To delete these orphans, run:")
        print(f"   python3 PRPs/scripts/both/cleanup_orphaned_l0_files.py --delete")

    return 0


if __name__ == "__main__":
    exit(main())
