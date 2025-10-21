#!/usr/bin/env python3
"""
Remove Orphan Data Entries

Removes duplicate/orphan person entries from docs/new/js/data.json that
reference deleted HTML files.

Specifically targets XF191 entry in lineage "0" (L0) which was deleted
as part of the orphaned file cleanup.
"""

import json
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    data_file = repo_root / "docs" / "new" / "js" / "data.json"

    print(f"Loading data from: {data_file}")

    # Load data.json
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_count = len(data.get('people', []))
    print(f"Original person count: {original_count}")

    # Find and remove orphan entries
    removed = []
    if 'people' in data:
        filtered_people = []
        for person in data['people']:
            # Remove if it's ID "191" in lineage "0" (orphan L0/XF191.htm)
            if person.get('id') == '191' and person.get('lineage') == '0':
                removed.append(person)
                print(f"\n❌ Removing orphan entry:")
                print(f"   ID: {person.get('id')}")
                print(f"   Name: {person.get('name')}")
                print(f"   URL: {person.get('url')}")
                print(f"   Lineage: {person.get('lineage')}")
            else:
                filtered_people.append(person)

        data['people'] = filtered_people

    new_count = len(data.get('people', []))
    print(f"\nNew person count: {new_count}")
    print(f"Removed {original_count - new_count} orphan entries")

    # Write updated data.json
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated {data_file}")

    # Verify the correct entry still exists
    print("\n🔍 Verifying correct XF191 entry in L1...")
    for person in data['people']:
        if person.get('filename') == 'XF191.htm' and person.get('lineage') == '1':
            print(f"   ✅ Found ID: {person.get('id')} in lineage 1 (L1)")
            print(f"   URL: {person.get('url')}")
            break

    return 0


if __name__ == "__main__":
    exit(main())
