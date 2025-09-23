#!/usr/bin/env python3
"""
Fix Thumbnail Images Script

This script processes HTML files to fix the thumbnail image sections by:
1. Removing "ThumbNails for this Person" sections when no images exist
2. Creating modern image carousel widgets for sections with images
3. Adding next/prev navigation for scrolling through thumbnails
4. Showing 10 images at a time with navigation controls
5. Adding click functionality for popup full images

Usage: python3 fix_thumbnails.py
"""

import os
import re
from pathlib import Path

def has_images_in_thf_file(thf_path):
    """Check if a THF file actually contains images"""
    if not os.path.exists(thf_path):
        return False

    try:
        with open(thf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Look for img tags
        img_pattern = r'<img\s+src="[^"]*"'
        images = re.findall(img_pattern, content, re.IGNORECASE)
        return len(images) > 0
    except Exception:
        return False

def extract_images_from_thf(thf_path):
    """Extract image information from THF file"""
    if not os.path.exists(thf_path):
        return []

    try:
        with open(thf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        images = []
        # Pattern to match img + map combinations
        img_map_pattern = r'<img\s+src="([^"]*)"[^>]*usemap="#([^"]*)"[^>]*alt="([^"]*)"[^>]*>.*?<map\s+name="\2"[^>]*>.*?<area[^>]*href="([^"]*)"[^>]*>.*?</map>'

        matches = re.findall(img_map_pattern, content, re.IGNORECASE | re.DOTALL)

        for match in matches:
            src, map_name, alt_text, link_href = match
            images.append({
                'src': src,
                'alt': alt_text.strip(),
                'link': link_href,
                'map_name': map_name
            })

        return images
    except Exception as e:
        print(f"Error extracting images from {thf_path}: {e}")
        return []

def create_image_carousel_html(images):
    """Create modern image carousel HTML"""
    if not images:
        return ""

    carousel_id = f"carousel_{hash(str(images)) % 10000}"

    html = f'''<div class="image-carousel" id="{carousel_id}">
    <div class="carousel-controls">
        <button class="carousel-btn prev-btn" onclick="previousImages('{carousel_id}')" aria-label="Previous images">‹</button>
        <span class="carousel-info">
            <span class="current-page">1</span> / <span class="total-pages">{(len(images) + 9) // 10}</span>
        </span>
        <button class="carousel-btn next-btn" onclick="nextImages('{carousel_id}')" aria-label="Next images">›</button>
    </div>
    <div class="carousel-container">
        <div class="carousel-track">'''

    # Group images into pages of 10
    for i in range(0, len(images), 10):
        page_images = images[i:i+10]
        html += f'\n            <div class="carousel-page" data-page="{i//10 + 1}">'

        for img in page_images:
            # Clean up the alt text for better display
            clean_alt = re.sub(r'\([^)]*\)$', '', img['alt']).strip()
            html += f'''
                <div class="thumbnail-item">
                    <img src="{img['src']}"
                         alt="{img['alt']}"
                         onclick="openFullImage('{img['link']}')"
                         title="{clean_alt}"
                         loading="lazy"
                         class="thumbnail-image">
                </div>'''

        html += '\n            </div>'

    html += '''
        </div>
    </div>
</div>'''

    return html

def add_carousel_css():
    """CSS for the image carousel"""
    return '''
<style>
.image-carousel {
    margin: 20px 0;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    background: #f9f9f9;
}

.carousel-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background: #f0f0f0;
    border-bottom: 1px solid #ddd;
}

.carousel-btn {
    background: #007cba;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 18px;
    font-weight: bold;
    min-width: 40px;
}

.carousel-btn:hover {
    background: #005a8b;
}

.carousel-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.carousel-info {
    font-weight: bold;
    color: #333;
}

.carousel-container {
    overflow: hidden;
    position: relative;
}

.carousel-track {
    display: flex;
    transition: transform 0.3s ease;
}

.carousel-page {
    min-width: 100%;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
    gap: 10px;
    padding: 15px;
    justify-items: center;
}

.thumbnail-item {
    text-align: center;
}

.thumbnail-item .thumbnail-image {
    width: 50px;
    height: 50px;
    object-fit: cover;
    border: 2px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: block;
}

.thumbnail-item .thumbnail-image:hover {
    border-color: #007cba;
    transform: scale(1.2);
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

@media (max-width: 768px) {
    .carousel-page {
        grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));
        gap: 8px;
        padding: 10px;
    }

    .thumbnail-item .thumbnail-image {
        width: 45px;
        height: 45px;
    }
}
</style>'''

def add_carousel_js():
    """JavaScript for the image carousel"""
    return '''
<script>
let carouselPages = {};

function initCarousel(carouselId) {
    if (!carouselPages[carouselId]) {
        carouselPages[carouselId] = {
            currentPage: 0,
            totalPages: document.querySelectorAll(`#${carouselId} .carousel-page`).length
        };
    }
    updateCarouselDisplay(carouselId);
}

function updateCarouselDisplay(carouselId) {
    const carousel = document.getElementById(carouselId);
    if (!carousel) return;

    const track = carousel.querySelector('.carousel-track');
    const currentPageSpan = carousel.querySelector('.current-page');
    const totalPagesSpan = carousel.querySelector('.total-pages');
    const prevBtn = carousel.querySelector('.prev-btn');
    const nextBtn = carousel.querySelector('.next-btn');

    const data = carouselPages[carouselId];
    const translateX = -data.currentPage * 100;

    track.style.transform = `translateX(${translateX}%)`;
    currentPageSpan.textContent = data.currentPage + 1;
    totalPagesSpan.textContent = data.totalPages;

    prevBtn.disabled = data.currentPage === 0;
    nextBtn.disabled = data.currentPage === data.totalPages - 1;
}

function previousImages(carouselId) {
    if (!carouselPages[carouselId]) initCarousel(carouselId);

    const data = carouselPages[carouselId];
    if (data.currentPage > 0) {
        data.currentPage--;
        updateCarouselDisplay(carouselId);
    }
}

function nextImages(carouselId) {
    if (!carouselPages[carouselId]) initCarousel(carouselId);

    const data = carouselPages[carouselId];
    if (data.currentPage < data.totalPages - 1) {
        data.currentPage++;
        updateCarouselDisplay(carouselId);
    }
}

function openFullImage(imageLink) {
    window.open(imageLink, '_blank');
}

// Initialize all carousels when page loads
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.image-carousel').forEach(carousel => {
        initCarousel(carousel.id);
    });
});
</script>'''

def process_person_file(file_path):
    """Process a person HTML file to fix thumbnail sections"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find ThumbNails for this Person link
        thumbnail_pattern = r'<center><a href="([^"]*THF[^"]*\.htm)"><h2>ThumbNails for this Person</h2></a></center>'
        match = re.search(thumbnail_pattern, content, re.IGNORECASE)

        if not match:
            return False, "No thumbnail section found"

        thf_link = match.group(1)
        # Convert relative path to absolute path
        file_dir = os.path.dirname(file_path)
        # Extract the THF filename from the link
        thf_filename = os.path.basename(thf_link)
        thf_path = os.path.join(file_dir, thf_filename)

        # Check if THF file has images
        if not has_images_in_thf_file(thf_path):
            # Remove the entire thumbnail section
            content = re.sub(thumbnail_pattern, '', content, flags=re.IGNORECASE)
            modified = True
            print(f"Removed empty thumbnail section from {os.path.basename(file_path)}")
        else:
            # Extract images and create carousel
            images = extract_images_from_thf(thf_path)
            if images:
                carousel_html = create_image_carousel_html(images)
                replacement = f'<center><h2>Photo Gallery</h2></center>\n{carousel_html}'
                content = re.sub(thumbnail_pattern, replacement, content, flags=re.IGNORECASE)

                # Add CSS and JS if not already present
                if 'image-carousel' not in content:
                    # Insert CSS before </head>
                    css = add_carousel_css()
                    content = re.sub(r'</head>', f'{css}\n</head>', content, flags=re.IGNORECASE)

                    # Insert JS before </body>
                    js = add_carousel_js()
                    content = re.sub(r'</body>', f'{js}\n</body>', content, flags=re.IGNORECASE)

                modified = True
                print(f"Added image carousel with {len(images)} images to {os.path.basename(file_path)}")
            else:
                return False, "No images found in THF file"

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Updated successfully"

        return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function to process all HTML files"""
    # Check if we're in the docs/new directory
    current_path = Path(".")
    htm_path = current_path / "htm"

    if not htm_path.exists():
        # Try from project root
        docs_new_path = Path("docs/new")
        htm_path = docs_new_path / "htm"
        if not htm_path.exists():
            print(f"Error: Neither ./htm nor docs/new/htm exists")
            print(f"Please run this script from the docs/new directory or project root")
            return

    print("Processing HTML files to fix thumbnail sections...")

    total_files = 0
    modified_files = 0
    errors = 0

    # Process all HTML files in htm directory
    for html_file in htm_path.rglob("*.htm"):
        # Skip THF files themselves
        if html_file.name.startswith("THF"):
            continue

        total_files += 1
        success, message = process_person_file(html_file)

        if success:
            modified_files += 1
        elif "Error:" in message:
            errors += 1
            print(f"Error processing {html_file.name}: {message}")

        # Progress indicator
        if total_files % 500 == 0:
            print(f"Processed {total_files} files...")

    print(f"\nProcessing complete:")
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {modified_files}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()