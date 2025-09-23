#!/usr/bin/env python3
"""
Modernize Image Pages and Implement Breadcrumb Navigation

This script:
1. Modernizes XI image detail pages to match the new site structure
2. Updates carousel navigation to use breadcrumb approach instead of new tabs
3. Adds next/previous navigation within image galleries
4. Implements proper back navigation to return to photo galleries
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse

def modernize_xi_file(file_path):
    """Modernize an XI image page to match new site structure"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Extract title and image info
        title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Image - AuntieRuth.com"

        # Extract image src
        img_match = re.search(r'<img src\s*=\s*"([^"]+)"', content, re.IGNORECASE)
        if not img_match:
            return False, "No image found"

        old_img_src = img_match.group(1)
        # Convert old path to new path
        new_img_src = old_img_src.replace('/AuntRuth/', '/auntruth/new/')

        # Extract metadata table content
        table_pattern = r"<table id='List'[^>]*>.*?</table>"
        table_match = re.search(table_pattern, content, re.DOTALL | re.IGNORECASE)
        table_content = ""
        if table_match:
            table_content = table_match.group(0)
            # Update links in table content
            table_content = re.sub(r'/AuntRuth/htm/', '/auntruth/new/htm/', table_content)

        # Get file info for navigation context
        file_name = os.path.basename(file_path)
        lineage_match = re.search(r'/L(\d+)/', str(file_path))
        lineage = f"L{lineage_match.group(1)}" if lineage_match else "L0"

        # Create modernized HTML
        modernized_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="/auntruth/new/css/main.css" rel="stylesheet" type="text/css">
    <link href="/auntruth/new/css/navigation.css" rel="stylesheet">
    <link rel="preload" href="/auntruth/new/js/navigation.js" as="script">
    <link rel="preload" href="/auntruth/new/js/search.js" as="script">
    <!-- MODERNIZED -->
    <style>
    .image-detail {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }}

    .breadcrumb-nav {{
        background: #f8f9fa;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-size: 14px;
    }}

    .breadcrumb-nav a {{
        color: #007cba;
        text-decoration: none;
        margin-right: 8px;
    }}

    .breadcrumb-nav a:hover {{
        text-decoration: underline;
    }}

    .breadcrumb-separator {{
        margin: 0 8px;
        color: #6c757d;
    }}

    .image-container {{
        text-align: center;
        margin: 30px 0;
        background: #fff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    .image-container img {{
        max-width: 100%;
        height: auto;
        border: 1px solid #ddd;
        border-radius: 4px;
    }}

    .image-navigation {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 5px;
    }}

    .nav-btn {{
        background: #007cba;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
    }}

    .nav-btn:hover {{
        background: #005a8b;
        color: white;
        text-decoration: none;
    }}

    .nav-btn:disabled {{
        background: #ccc;
        cursor: not-allowed;
    }}

    .back-btn {{
        background: #6c757d;
    }}

    .back-btn:hover {{
        background: #545b62;
    }}

    .image-counter {{
        font-weight: bold;
        color: #333;
    }}

    .metadata-table {{
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }}

    .metadata-table table {{
        width: 100%;
        border-collapse: collapse;
    }}

    .metadata-table td {{
        padding: 12px 15px;
        border-bottom: 1px solid #eee;
    }}

    .metadata-table td:first-child {{
        background: #f8f9fa;
        font-weight: bold;
        width: 150px;
    }}

    @media (max-width: 768px) {{
        .image-detail {{
            padding: 10px;
        }}

        .image-navigation {{
            flex-direction: column;
            gap: 10px;
        }}

        .metadata-table td:first-child {{
            width: auto;
        }}
    }}
    </style>
</head>
<body>
    <!-- Skip link for accessibility -->
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

    <!-- Main page content -->
    <main id="main-content" class="page-content">
        <div class="image-detail">
            <!-- Breadcrumb Navigation -->
            <nav class="breadcrumb-nav" id="breadcrumb">
                <a href="/auntruth/new/">Home</a>
                <span class="breadcrumb-separator">›</span>
                <span id="breadcrumb-context">Loading...</span>
            </nav>

            <!-- Image Navigation Controls -->
            <div class="image-navigation">
                <button class="nav-btn back-btn" onclick="goBack()">← Back to Gallery</button>
                <div class="image-counter">
                    <span id="current-image">1</span> of <span id="total-images">1</span>
                </div>
                <div>
                    <button class="nav-btn" id="prev-image" onclick="previousImage()">← Previous</button>
                    <button class="nav-btn" id="next-image" onclick="nextImage()">Next →</button>
                </div>
            </div>

            <!-- Page Header -->
            <header class="page-header">
                <h1>{title}</h1>
            </header>

            <!-- Image Display -->
            <div class="image-container">
                <img src="{new_img_src}" alt="{title}" id="main-image">
            </div>

            <!-- Image Metadata -->
            <div class="metadata-table">
                {table_content}
            </div>
        </div>
    </main>

    <!-- Navigation and search scripts -->
    <script src="/auntruth/new/js/navigation.js" defer></script>
    <script src="/auntruth/new/js/search.js" defer></script>

    <script>
    // Image navigation data
    let imageGallery = [];
    let currentImageIndex = 0;
    let gallerySource = '';

    // Initialize page
    document.addEventListener('DOMContentLoaded', function() {{
        initializeImageNavigation();
    }});

    function initializeImageNavigation() {{
        // Get navigation context from URL parameters or referrer
        const urlParams = new URLSearchParams(window.location.search);
        const galleryId = urlParams.get('gallery');
        const imageIndex = parseInt(urlParams.get('index')) || 0;
        gallerySource = urlParams.get('source') || document.referrer;

        // If we have gallery context, load it
        if (galleryId && gallerySource) {{
            loadGalleryContext(galleryId, imageIndex);
        }} else {{
            // Try to extract from referrer
            tryExtractFromReferrer();
        }}

        updateBreadcrumb();
    }}

    function loadGalleryContext(galleryId, imageIndex) {{
        // This would ideally load from a gallery data source
        // For now, we'll implement basic navigation
        currentImageIndex = imageIndex;
        updateImageCounter();
        updateNavigationButtons();
    }}

    function tryExtractFromReferrer() {{
        if (document.referrer) {{
            const referrerUrl = new URL(document.referrer);
            if (referrerUrl.pathname.includes('/XF')) {{
                // We came from a person page with a gallery
                const breadcrumb = document.getElementById('breadcrumb-context');
                breadcrumb.innerHTML = '<a href="' + document.referrer + '">Person Gallery</a> <span class="breadcrumb-separator">›</span> Image Detail';
            }}
        }}
    }}

    function updateBreadcrumb() {{
        const breadcrumbContext = document.getElementById('breadcrumb-context');
        if (gallerySource && gallerySource.includes('/XF')) {{
            // Extract person name from referring page if possible
            breadcrumbContext.innerHTML = '<a href="' + gallerySource + '">Person Gallery</a> <span class="breadcrumb-separator">›</span> Image Detail';
        }} else {{
            breadcrumbContext.textContent = 'Image Detail';
        }}
    }}

    function updateImageCounter() {{
        document.getElementById('current-image').textContent = currentImageIndex + 1;
        // Total images would be loaded from gallery data
        document.getElementById('total-images').textContent = imageGallery.length || 1;
    }}

    function updateNavigationButtons() {{
        const prevBtn = document.getElementById('prev-image');
        const nextBtn = document.getElementById('next-image');

        prevBtn.disabled = currentImageIndex <= 0;
        nextBtn.disabled = currentImageIndex >= (imageGallery.length - 1) || imageGallery.length === 0;
    }}

    function goBack() {{
        if (gallerySource) {{
            window.location.href = gallerySource;
        }} else if (document.referrer) {{
            window.history.back();
        }} else {{
            window.location.href = '/auntruth/new/';
        }}
    }}

    function previousImage() {{
        if (currentImageIndex > 0 && imageGallery.length > 0) {{
            currentImageIndex--;
            navigateToImage(imageGallery[currentImageIndex]);
        }}
    }}

    function nextImage() {{
        if (currentImageIndex < imageGallery.length - 1) {{
            currentImageIndex++;
            navigateToImage(imageGallery[currentImageIndex]);
        }}
    }}

    function navigateToImage(imageData) {{
        // Navigate to the next/previous image with context
        const urlParams = new URLSearchParams();
        urlParams.set('gallery', 'gallery_id'); // This would be the actual gallery ID
        urlParams.set('index', currentImageIndex);
        urlParams.set('source', gallerySource);

        window.location.href = imageData.link + '?' + urlParams.toString();
    }}
    </script>
</body>
</html>'''

        # Write the modernized content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modernized_content)

        return True, "Modernized successfully"

    except Exception as e:
        return False, f"Error: {e}"

def update_carousel_navigation(file_path):
    """Update carousel to use breadcrumb navigation instead of new tabs"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if 'image-carousel' not in content:
            return False, "No carousel found"

        # Update the JavaScript to navigate instead of opening new tabs
        js_replacement = '''
function openFullImage(imageLink, imageIndex, carouselId) {
    // Navigate to image with gallery context
    const urlParams = new URLSearchParams();
    urlParams.set('gallery', carouselId);
    urlParams.set('index', imageIndex || 0);
    urlParams.set('source', window.location.href);

    window.location.href = imageLink + '?' + urlParams.toString();
}'''

        # Replace the existing openFullImage function
        if 'function openFullImage' in content:
            pattern = r'function openFullImage\([^}]+\}'
            content = re.sub(pattern, js_replacement.strip(), content, flags=re.DOTALL)
        else:
            # Add the function before the closing script tag
            content = re.sub(r'(</script>)(?!.*</script>)', js_replacement + '\n\\1', content, flags=re.DOTALL)

        # Update the onclick attributes to pass image index
        def update_onclick(match):
            prefix = match.group(1)
            link = match.group(2)
            suffix = match.group(3)

            # Extract or generate image index - this is a simplified approach
            # In a real implementation, you'd track the actual index
            return f'{prefix}{link}\', 0, \'carousel_id\'){suffix}'

        onclick_pattern = r"(onclick=\"openFullImage\(')([^']+)('\)\")"
        content = re.sub(onclick_pattern, update_onclick, content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True, "Updated carousel navigation"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function to modernize image pages and update navigation"""
    current_path = Path(".")
    htm_path = current_path / "htm"

    if not htm_path.exists():
        docs_new_path = Path("docs/new")
        htm_path = docs_new_path / "htm"
        if not htm_path.exists():
            print(f"Error: Neither ./htm nor docs/new/htm exists")
            return

    print("Modernizing image pages and updating navigation...")

    # Phase 1: Modernize XI files
    print("\\nPhase 1: Modernizing XI image pages...")
    xi_files = 0
    xi_modernized = 0
    xi_errors = 0

    for xi_file in htm_path.rglob("XI*.htm"):
        xi_files += 1
        success, message = modernize_xi_file(xi_file)

        if success:
            xi_modernized += 1
            if xi_files <= 5:  # Show first few
                print(f"Modernized {xi_file.name}")
        else:
            xi_errors += 1
            if xi_files <= 5:  # Show first few errors
                print(f"Error modernizing {xi_file.name}: {message}")

        if xi_files % 100 == 0:
            print(f"Processed {xi_files} XI files...")

    # Phase 2: Update carousel navigation
    print("\\nPhase 2: Updating carousel navigation...")
    carousel_files = 0
    carousel_updated = 0
    carousel_errors = 0

    for html_file in htm_path.rglob("XF*.htm"):
        carousel_files += 1
        success, message = update_carousel_navigation(html_file)

        if success:
            carousel_updated += 1
            if carousel_files <= 5:  # Show first few
                print(f"Updated {html_file.name}")
        elif "Error:" in message:
            carousel_errors += 1

        if carousel_files % 500 == 0:
            print(f"Processed {carousel_files} carousel files...")

    print(f"\\nModernization complete:")
    print(f"XI files processed: {xi_files}")
    print(f"XI files modernized: {xi_modernized}")
    print(f"XI errors: {xi_errors}")
    print(f"Carousel files processed: {carousel_files}")
    print(f"Carousel files updated: {carousel_updated}")
    print(f"Carousel errors: {carousel_errors}")

if __name__ == "__main__":
    main()