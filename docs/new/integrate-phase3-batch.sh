#!/bin/bash

# Phase 3 Batch Integration Script
# Applies Phase 3 integration template to all person pages (XF*.htm files)

echo "Phase 3 Batch Integration Script"
echo "================================"

# Counters
TOTAL_FILES=0
INTEGRATED_FILES=0
SKIPPED_FILES=0

# Find all XF*.htm files
echo "Finding person pages to integrate..."
find htm -name "XF*.htm" -type f | while read file; do
    TOTAL_FILES=$((TOTAL_FILES + 1))

    # Check if already integrated
    if grep -q "phase3-integration.js" "$file"; then
        echo "SKIP: $file (already integrated)"
        SKIPPED_FILES=$((SKIPPED_FILES + 1))
        continue
    fi

    echo "INTEGRATING: $file"

    # Get directory depth for relative paths
    # Use absolute paths consistent with existing site structure
    CSS_PATH="/auntruth/new/css/phase3-components.css"
    JS_PATH="/auntruth/new/js/phase3-integration.js?v=20250927f"

    # Create backup (in case of issues)
    cp "$file" "$file.backup"

    # Apply Phase 3 integration
    # 1. Add CSS link after existing preload links
    sed -i '' '/preload.*search\.js/a\
        <link rel="stylesheet" href="'$CSS_PATH'">
' "$file"

    # 2. Add data-phase3-enabled to body tag
    sed -i '' 's/<body/<body data-phase3-enabled/g' "$file"

    # 3. Add Phase 3 script before closing body tag
    sed -i '' '/<\/body>/i\
\
    <!-- Phase 3 Integration - Relationship Navigator, Timeline Visualization, URL Routing -->\
    <script type="module" src="'$JS_PATH'"></script>
' "$file"

    # Verify integration was successful
    if grep -q "phase3-integration.js" "$file" && grep -q "data-phase3-enabled" "$file"; then
        echo "SUCCESS: $file integrated"
        INTEGRATED_FILES=$((INTEGRATED_FILES + 1))
        # Remove backup file
        rm "$file.backup"
    else
        echo "ERROR: Integration failed for $file, restoring backup"
        mv "$file.backup" "$file"
    fi
done

echo ""
echo "Batch Integration Complete"
echo "========================="
echo "Total files found: $TOTAL_FILES"
echo "Files integrated: $INTEGRATED_FILES"
echo "Files skipped: $SKIPPED_FILES"
echo ""
echo "Phase 3 integration applied to person pages."
echo "Test the integration by visiting person pages in your browser."