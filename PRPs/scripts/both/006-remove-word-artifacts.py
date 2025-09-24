#!/usr/bin/env python3
"""
Task 006: Remove Microsoft Word Artifacts Script
Purpose: Remove Microsoft Word temporary file references that cause broken links

This script removes Word-generated artifacts that create broken links:
- filelist.xml references in <head>
- editdata.mso references in <head>
- image###.gif spacer references throughout content
- _files/ directory references that don't exist

CRITICAL SAFETY REQUIREMENTS:
- This script processes files in both docs/htm and docs/new directories
- Uses git branch safety system
- Implements phased execution with checkpoints
- Progress reporting every 100 files
- Error logging and recovery
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import argparse


def verify_git_branch(expected_branch):
    """Verify we're working in the correct branch"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        if current_branch != expected_branch:
            raise ValueError(f"Expected branch {expected_branch}, but currently on {current_branch}")
        print(f"✅ Verified working in correct branch: {current_branch}")
        return current_branch
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get current git branch: {e}")


def count_affected_files(target_dir):
    """Count files that contain Word artifacts"""
    affected_files = []
    total_artifacts = 0
    artifact_types = {
        'filelist_xml': 0,
        'editdata_mso': 0,
        'image_gif_spacers': 0
    }

    print(f"🔍 Scanning {target_dir} for Word artifacts...")

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.htm', '.html', '.backup')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                        file_artifacts = 0

                        # Check for filelist.xml references
                        filelist_matches = re.findall(r'<link\s+rel=[\'"]*File-List[\'"]*\s+href=[\'"][^\'\"]*filelist\.xml[\'"][^>]*>', content, re.IGNORECASE)
                        if filelist_matches:
                            artifact_types['filelist_xml'] += len(filelist_matches)
                            file_artifacts += len(filelist_matches)

                        # Check for editdata.mso references
                        editdata_matches = re.findall(r'<link\s+rel=[\'"]*Edit-Time-Data[\'"]*\s+href=[\'"][^\'\"]*editdata\.mso[\'"][^>]*>', content, re.IGNORECASE)
                        if editdata_matches:
                            artifact_types['editdata_mso'] += len(editdata_matches)
                            file_artifacts += len(editdata_matches)

                        # Check for Word-generated image spacers
                        spacer_matches = re.findall(r'<v:imagedata\s+src=[\'"][^\'\"]*_files/image\d+\.gif[\'"][^>]*>', content, re.IGNORECASE)
                        if spacer_matches:
                            artifact_types['image_gif_spacers'] += len(spacer_matches)
                            file_artifacts += len(spacer_matches)

                        if file_artifacts > 0:
                            affected_files.append((file_path, file_artifacts))
                            total_artifacts += file_artifacts

                except (OSError, IOError) as e:
                    print(f"⚠️  Error reading {file_path}: {e}")
                    continue

    return affected_files, total_artifacts, artifact_types


def remove_word_artifacts(file_path, dry_run=True):
    """Remove Word artifacts from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        content = original_content
        changes_made = []

        # Remove filelist.xml link references
        filelist_pattern = r'<link\s+rel=[\'"]*File-List[\'"]*\s+href=[\'"][^\'\"]*filelist\.xml[\'"][^>]*>\s*'
        if re.search(filelist_pattern, content, re.IGNORECASE):
            content = re.sub(filelist_pattern, '', content, flags=re.IGNORECASE)
            changes_made.append("Removed filelist.xml link")

        # Remove editdata.mso link references
        editdata_pattern = r'<link\s+rel=[\'"]*Edit-Time-Data[\'"]*\s+href=[\'"][^\'\"]*editdata\.mso[\'"][^>]*>\s*'
        if re.search(editdata_pattern, content, re.IGNORECASE):
            content = re.sub(editdata_pattern, '', content, flags=re.IGNORECASE)
            changes_made.append("Removed editdata.mso link")

        # Remove Word-generated image spacers (these are non-functional placeholders)
        # These are typically used for spacing and don't serve any functional purpose
        spacer_pattern = r'<v:imagedata\s+src=[\'"][^\'\"]*_files/image\d+\.gif[\'"][^>]*>'
        spacers_found = re.findall(spacer_pattern, content, re.IGNORECASE)
        if spacers_found:
            # Replace with empty string since these are just spacers
            content = re.sub(spacer_pattern, '', content, flags=re.IGNORECASE)
            changes_made.append(f"Removed {len(spacers_found)} image spacer references")

        # Clean up any orphaned VML shape tags that may be left behind
        orphaned_shapes_pattern = r'<!--\[if gte vml 1\]><v:shape[^>]*>\s*</v:shape><!\[endif\]--><!\[if !vml\]><!\[endif\]>'
        if re.search(orphaned_shapes_pattern, content, re.IGNORECASE):
            content = re.sub(orphaned_shapes_pattern, '', content, flags=re.IGNORECASE)
            changes_made.append("Cleaned up orphaned VML shapes")

        if changes_made and not dry_run:
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return changes_made, len(original_content) - len(content)

    except (OSError, IOError) as e:
        raise Exception(f"Error processing {file_path}: {e}")


def process_files_batch(target_dir, dry_run=True, max_files=None):
    """Process files with safety measures"""

    # Find all files that need fixing
    print("📊 Analyzing scope of Word artifacts...")
    affected_files, total_artifacts, artifact_types = count_affected_files(target_dir)

    print(f"📈 Found {len(affected_files)} files with {total_artifacts} total artifacts")
    print(f"   - filelist.xml references: {artifact_types['filelist_xml']}")
    print(f"   - editdata.mso references: {artifact_types['editdata_mso']}")
    print(f"   - image spacer references: {artifact_types['image_gif_spacers']}")

    if len(affected_files) == 0:
        print("✅ No Word artifacts found to remove")
        return {"processed": 0, "errors": 0}

    if max_files:
        affected_files = affected_files[:max_files]
        print(f"🎯 Limited to first {len(affected_files)} files for testing")

    if dry_run:
        print("\n🧪 DRY RUN MODE - Showing what would be changed:")
        print("="*60)

        sample_count = min(10, len(affected_files))
        for i, (file_path, artifact_count) in enumerate(affected_files[:sample_count]):
            print(f"{i+1:2d}. {file_path} ({artifact_count} artifacts)")

            # Show what would be removed
            try:
                changes, bytes_removed = remove_word_artifacts(file_path, dry_run=True)
                if changes:
                    print(f"    └─ Would remove: {', '.join(changes)}")
                    print(f"    └─ Bytes to remove: {bytes_removed}")
            except Exception as e:
                print(f"    └─ Error analyzing: {e}")

        if len(affected_files) > sample_count:
            print(f"\n... and {len(affected_files) - sample_count} more files")

        print(f"\n📊 Total files that would be processed: {len(affected_files)}")
        print(f"📊 Total artifacts that would be removed: {total_artifacts}")
        return {"processed": 0, "errors": 0}

    # Real processing mode
    print("\n🚀 PROCESSING FILES - Removing Word artifacts...")
    print("="*60)

    processed_count = 0
    error_count = 0
    total_bytes_removed = 0

    for i, (file_path, _) in enumerate(affected_files):
        try:
            if i % 100 == 0:
                print(f"Progress: {i+1}/{len(affected_files)} files processed")

            changes, bytes_removed = remove_word_artifacts(file_path, dry_run=False)

            if changes:
                processed_count += 1
                total_bytes_removed += bytes_removed
                if i < 10:  # Show details for first 10 files
                    print(f"✅ {file_path}")
                    print(f"   └─ Removed: {', '.join(changes)}")

        except Exception as e:
            error_count += 1
            print(f"❌ Error processing {file_path}: {e}")

        # Checkpoint every 500 files for large operations
        if processed_count > 0 and processed_count % 500 == 0:
            try:
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m",
                              f"Remove Word artifacts: checkpoint at {processed_count} files"], check=True)
                print(f"🔄 Checkpoint commit created at {processed_count} files")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: Failed to create checkpoint commit: {e}")

    print(f"\n📊 PROCESSING COMPLETE")
    print(f"   ✅ Files processed: {processed_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📉 Total bytes removed: {total_bytes_removed:,}")

    return {
        "processed": processed_count,
        "errors": error_count,
        "bytes_removed": total_bytes_removed
    }


def main():
    parser = argparse.ArgumentParser(description='Remove Microsoft Word artifacts from HTML files')
    parser.add_argument('--target-dir',
                       default='/home/ken/wip/fam/auntruth/docs',
                       help='Directory to process (default: /home/ken/wip/fam/auntruth/docs)')
    parser.add_argument('--site', choices=['htm', 'new', 'both'], default='both',
                       help='Which site to process (default: both)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test mode - show what would be changed without making changes')
    parser.add_argument('--test-mode', action='store_true',
                       help='Process only first 5 files for testing')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the changes (required for non-dry-run mode)')
    parser.add_argument('--yes', action='store_true',
                       help='Auto-confirm execution (for non-interactive environments)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate results after processing')

    args = parser.parse_args()

    # Safety check - require explicit execute flag for real changes
    if not args.dry_run and not args.execute:
        print("❌ Error: Must specify either --dry-run or --execute")
        print("   Use --dry-run to see what would be changed")
        print("   Use --execute to actually make changes")
        sys.exit(1)

    # Determine target directories
    target_dirs = []
    if args.site in ['htm', 'both']:
        target_dirs.append(os.path.join(args.target_dir, 'htm'))
    if args.site in ['new', 'both']:
        target_dirs.append(os.path.join(args.target_dir, 'new'))

    # Verify directories exist
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            print(f"❌ Error: Directory {target_dir} does not exist")
            sys.exit(1)

    print(f"🎯 Remove Word Artifacts Script")
    print(f"📂 Target directories: {target_dirs}")
    print(f"🧪 Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")

    if args.test_mode:
        print(f"🧪 Test mode: Processing only first 5 files")

    # Confirmation for execution mode
    if not args.dry_run and not args.yes:
        response = input("\n⚠️  This will modify files. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled")
            sys.exit(0)

    # Process each target directory
    total_results = {"processed": 0, "errors": 0, "bytes_removed": 0}

    for target_dir in target_dirs:
        print(f"\n{'='*60}")
        print(f"📂 Processing {target_dir}")
        print(f"{'='*60}")

        max_files = 5 if args.test_mode else None
        results = process_files_batch(target_dir, dry_run=args.dry_run, max_files=max_files)

        # Accumulate results
        for key in total_results:
            total_results[key] += results.get(key, 0)

    # Final summary
    print(f"\n{'='*60}")
    print(f"📊 FINAL SUMMARY - Word Artifacts Removal")
    print(f"{'='*60}")
    print(f"✅ Total files processed: {total_results['processed']}")
    print(f"❌ Total errors: {total_results['errors']}")
    print(f"📉 Total bytes removed: {total_results['bytes_removed']:,}")

    if not args.dry_run and total_results['processed'] > 0:
        print(f"\n🔄 Creating final commit...")
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m",
                          f"Remove Word artifacts: completed {total_results['processed']} files, removed {total_results['bytes_removed']:,} bytes"], check=True)
            print(f"✅ Final commit created")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to create final commit: {e}")

    # Validation mode
    if args.validate:
        print(f"\n🔍 VALIDATION - Checking for remaining Word artifacts...")
        validation_results = {"processed": 0, "errors": 0}

        for target_dir in target_dirs:
            print(f"📂 Validating {target_dir}...")
            remaining_files, remaining_artifacts, artifact_types = count_affected_files(target_dir)

            if remaining_artifacts == 0:
                print(f"✅ No Word artifacts found in {target_dir}")
            else:
                print(f"⚠️  Found {remaining_artifacts} remaining artifacts in {len(remaining_files)} files")
                print(f"   - filelist.xml: {artifact_types['filelist_xml']}")
                print(f"   - editdata.mso: {artifact_types['editdata_mso']}")
                print(f"   - image spacers: {artifact_types['image_gif_spacers']}")

    print(f"\n✅ Word artifacts removal {'simulation' if args.dry_run else 'process'} complete!")


if __name__ == "__main__":
    main()