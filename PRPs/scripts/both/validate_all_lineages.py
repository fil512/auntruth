#!/usr/bin/env python3
"""
Validate all lineages - wrapper script to validate all 10 lineages.

This script runs schema validation on all lineage directories and creates
a combined report.
"""

from pathlib import Path
import subprocess
import json

def main():
    people_dir = Path("data/people")

    lineages = {
        "Hagborg-Hansson": people_dir / "Hagborg-Hansson",
        "Lentz": people_dir / "Lentz",
        "Ward": people_dir / "Ward",
        "Stebbe": people_dir / "Stebbe",
        "Nelson": people_dir / "Nelson",
        "Selch-Weiss": people_dir / "Selch-Weiss",
        "Phoenix-Rogerson": people_dir / "Phoenix-Rogerson",
        "Pringle-Hambley": people_dir / "Pringle-Hambley",
        "Lathrop-Lothropp": people_dir / "Lathrop-Lothropp",
        "Other": people_dir / "Other",
    }

    print("\n" + "="*60)
    print("VALIDATING ALL LINEAGES")
    print("="*60 + "\n")

    all_results = {}
    total_files = 0
    total_passed = 0
    total_failed = 0

    for lineage_name, lineage_dir in lineages.items():
        if not lineage_dir.exists():
            print(f"⚠️  {lineage_name}: Directory not found, skipping")
            continue

        json_files = list(lineage_dir.glob('*.json'))
        file_count = len(json_files)

        print(f"\n📁 {lineage_name}: {file_count} files")

        # Run validation
        result = subprocess.run(
            [
                "python3", "PRPs/scripts/both/validate_json_data.py",
                "--input-dir", str(lineage_dir),
                "--report", f"data/validation-{lineage_name}.md"
            ],
            capture_output=True,
            text=True
        )

        # Parse output for summary
        output_lines = result.stdout.split('\n')
        passed = 0
        failed = 0

        for line in output_lines:
            if '✓ Passed:' in line:
                passed = int(line.split(':')[1].strip())
            elif '✗ Failed:' in line:
                failed = int(line.split(':')[1].strip())

        total_files += file_count
        total_passed += passed
        total_failed += failed

        all_results[lineage_name] = {
            'files': file_count,
            'passed': passed,
            'failed': failed,
            'success_rate': f"{(passed/file_count*100):.1f}%" if file_count > 0 else "N/A"
        }

        print(f"   ✓ Passed: {passed}/{file_count} ({(passed/file_count*100):.1f}%)")
        if failed > 0:
            print(f"   ✗ Failed: {failed}")

    # Print combined summary
    print("\n" + "="*60)
    print("COMBINED SUMMARY")
    print("="*60)
    print(f"\nTotal files validated: {total_files}")
    print(f"✓ Passed: {total_passed}")
    print(f"✗ Failed: {total_failed}")
    print(f"Success rate: {(total_passed/total_files*100):.1f}%")

    # Create combined report
    report_path = Path("data/phase3-combined-validation-report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Phase 3: Combined Schema Validation Report\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total Files**: {total_files}\n")
        f.write(f"- **✓ Passed**: {total_passed}\n")
        f.write(f"- **✗ Failed**: {total_failed}\n")
        f.write(f"- **Success Rate**: {(total_passed/total_files*100):.1f}%\n\n")

        f.write("## Lineage Breakdown\n\n")
        f.write("| Lineage | Files | Passed | Failed | Success Rate |\n")
        f.write("|---------|-------|--------|--------|-------------|\n")

        for lineage_name, result in all_results.items():
            f.write(f"| {lineage_name} | {result['files']} | {result['passed']} | {result['failed']} | {result['success_rate']} |\n")

        f.write("\n## Individual Reports\n\n")
        for lineage_name in all_results.keys():
            f.write(f"- `data/validation-{lineage_name}.md`\n")

    print(f"\nCombined report saved to: {report_path}")

    return 0 if total_failed == 0 else 1

if __name__ == '__main__':
    exit(main())
