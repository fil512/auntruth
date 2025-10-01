#!/usr/bin/env python3
"""
Validate extracted JSON data against schema.

This script validates person JSON files against the schema defined in
PLAN/data-schema.md to ensure all required fields are present and properly
formatted.

Usage:
    # Validate single file
    python3 validate_json_data.py \
        --input data/people/Hagborg-Hansson/XF100.json

    # Validate entire directory
    python3 validate_json_data.py \
        --input-dir data/people/Hagborg-Hansson \
        --report data/schema-validation-report.md
"""

from pathlib import Path
import json
import argparse
import re
from typing import Dict, List, Any


class JSONSchemaValidator:
    """Validates JSON files against the person data schema."""

    def __init__(self):
        self.stats = {
            'files_validated': 0,
            'files_passed': 0,
            'files_failed': 0,
            'errors': []
        }

    def validate_person_schema(self, data: Dict, file_path: str) -> List[Dict]:
        """Validate a person record against the schema."""
        errors = []

        # Required fields
        required_fields = ['id', 'name', 'lineage']
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append({
                    'type': 'missing_required_field',
                    'field': field,
                    'severity': 'ERROR',
                    'message': f'Required field "{field}" is missing or null'
                })

        # Validate ID format
        if 'id' in data and data['id']:
            if not re.match(r'^XF\d+$', data['id']):
                errors.append({
                    'type': 'invalid_id_format',
                    'field': 'id',
                    'value': data['id'],
                    'severity': 'ERROR',
                    'message': f'ID "{data["id"]}" does not match pattern XF\\d+'
                })

        # Validate family relationships have proper structure
        for rel_field in ['father', 'mother']:
            if rel_field in data and data[rel_field] is not None:
                rel = data[rel_field]
                if not isinstance(rel, dict):
                    errors.append({
                        'type': 'invalid_field_type',
                        'field': rel_field,
                        'severity': 'ERROR',
                        'message': f'{rel_field} must be an object'
                    })
                else:
                    # Check required sub-fields
                    if 'id' not in rel or not rel['id']:
                        errors.append({
                            'type': 'missing_sub_field',
                            'field': f'{rel_field}.id',
                            'severity': 'WARNING',
                            'message': f'{rel_field} object missing id'
                        })

        # Validate spouses is an array
        if 'spouses' in data:
            if not isinstance(data['spouses'], list):
                errors.append({
                    'type': 'invalid_field_type',
                    'field': 'spouses',
                    'severity': 'ERROR',
                    'message': 'spouses must be an array'
                })

        # Validate children is an array
        if 'children' in data:
            if not isinstance(data['children'], list):
                errors.append({
                    'type': 'invalid_field_type',
                    'field': 'children',
                    'severity': 'ERROR',
                    'message': 'children must be an array'
                })

        # Validate photos arrays
        for photo_field in ['photos', 'photographedBy']:
            if photo_field in data:
                if not isinstance(data[photo_field], list):
                    errors.append({
                        'type': 'invalid_field_type',
                        'field': photo_field,
                        'severity': 'ERROR',
                        'message': f'{photo_field} must be an array'
                    })

        # Validate metadata exists
        if 'metadata' not in data:
            errors.append({
                'type': 'missing_metadata',
                'field': 'metadata',
                'severity': 'WARNING',
                'message': 'metadata object is missing'
            })

        return errors

    def validate_file(self, json_path: Path) -> Dict:
        """Validate a single JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate against schema
            errors = self.validate_person_schema(data, str(json_path))

            # Categorize errors
            error_count = len([e for e in errors if e['severity'] == 'ERROR'])
            warning_count = len([e for e in errors if e['severity'] == 'WARNING'])

            result = {
                'file': str(json_path),
                'person_id': data.get('id'),
                'person_name': data.get('name'),
                'status': 'PASS' if error_count == 0 else 'FAIL',
                'error_count': error_count,
                'warning_count': warning_count,
                'errors': errors
            }

            if error_count == 0:
                self.stats['files_passed'] += 1
            else:
                self.stats['files_failed'] += 1

            return result

        except json.JSONDecodeError as e:
            self.stats['files_failed'] += 1
            return {
                'file': str(json_path),
                'status': 'FAIL',
                'error_count': 1,
                'warning_count': 0,
                'errors': [{
                    'type': 'json_parse_error',
                    'severity': 'ERROR',
                    'message': f'Failed to parse JSON: {e}'
                }]
            }
        except Exception as e:
            self.stats['files_failed'] += 1
            return {
                'file': str(json_path),
                'status': 'FAIL',
                'error_count': 1,
                'warning_count': 0,
                'errors': [{
                    'type': 'validation_error',
                    'severity': 'ERROR',
                    'message': f'Validation error: {e}'
                }]
            }

    def validate_directory(self, input_dir: Path) -> List[Dict]:
        """Validate all JSON files in a directory."""
        json_files = sorted(input_dir.glob('*.json'))

        if not json_files:
            print(f"No JSON files found in {input_dir}")
            return []

        print(f"\n{'='*60}")
        print(f"Validating JSON Schema")
        print(f"Input: {input_dir}")
        print(f"Files found: {len(json_files)}")
        print(f"{'='*60}\n")

        results = []
        for i, json_file in enumerate(json_files, 1):
            self.stats['files_validated'] += 1

            # Progress reporting every 20 files
            if i % 20 == 0:
                print(f"Progress: {i}/{len(json_files)} files...")

            result = self.validate_file(json_file)
            results.append(result)

            # Show errors immediately
            if result['status'] == 'FAIL':
                print(f"✗ {json_file.name}: {result['error_count']} errors")
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"  - {error['message']}")

        return results

    def print_summary(self, results: List[Dict]):
        """Print validation summary."""
        print(f"\n{'='*60}")
        print("SCHEMA VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Files validated: {self.stats['files_validated']}")
        print(f"✓ Passed: {self.stats['files_passed']}")
        print(f"✗ Failed: {self.stats['files_failed']}")

        # Show failures
        failures = [r for r in results if r['status'] == 'FAIL']
        if failures:
            print(f"\nFailed files:")
            for result in failures[:10]:  # Show first 10
                print(f"  - {result.get('person_id', 'UNKNOWN')}: {result['error_count']} errors")
        else:
            print(f"\n✓ All files passed validation!")

    def generate_markdown_report(self, results: List[Dict], report_path: Path):
        """Generate markdown validation report."""
        from datetime import datetime
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# JSON Schema Validation Report\n\n")
            f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Files Validated**: {self.stats['files_validated']}\n")
            f.write(f"- **Passed**: {self.stats['files_passed']}\n")
            f.write(f"- **Failed**: {self.stats['files_failed']}\n\n")

            # Show failures
            failures = [r for r in results if r['status'] == 'FAIL']
            if failures:
                f.write("## Failures\n\n")
                for result in failures:
                    f.write(f"### {result.get('person_id', 'UNKNOWN')} - {result.get('person_name', 'Unknown')}\n\n")
                    f.write(f"**File**: `{result['file']}`\n\n")
                    f.write(f"**Errors**: {result['error_count']}, **Warnings**: {result['warning_count']}\n\n")

                    if result['errors']:
                        f.write("**Issues**:\n\n")
                        for error in result['errors']:
                            severity = error.get('severity', 'ERROR')
                            message = error.get('message', 'Unknown error')
                            f.write(f"- [{severity}] {message}\n")
                        f.write("\n")
            else:
                f.write("## ✓ All Files Passed\n\n")
                f.write("No validation errors found!\n")

        print(f"\nReport saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate person JSON files against schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Input options
    parser.add_argument('--input', type=str, help='Input JSON file')
    parser.add_argument('--input-dir', type=str, help='Input directory with JSON files')

    # Output options
    parser.add_argument('--report', type=str, help='Output markdown report path')

    args = parser.parse_args()

    validator = JSONSchemaValidator()

    if args.input:
        # Single file mode
        json_path = Path(args.input)
        if not json_path.exists():
            print(f"Error: File not found: {json_path}")
            return 1

        print(f"Validating: {json_path}")
        result = validator.validate_file(json_path)

        if result['status'] == 'PASS':
            print(f"✓ Validation passed!")
        else:
            print(f"✗ Validation failed with {result['error_count']} errors:")
            for error in result['errors']:
                print(f"  - {error['message']}")

        return 0 if result['status'] == 'PASS' else 1

    elif args.input_dir:
        # Directory mode
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            print(f"Error: Directory not found: {input_dir}")
            return 1

        results = validator.validate_directory(input_dir)
        validator.print_summary(results)

        # Generate report if requested
        if args.report:
            report_path = Path(args.report)
            validator.generate_markdown_report(results, report_path)

        return 0 if validator.stats['files_failed'] == 0 else 1

    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    exit(main())
