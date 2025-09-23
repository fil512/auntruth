#!/usr/bin/env python3
"""
Fix Missing Carousel CSS Script

This script adds missing CSS and JavaScript to files that have image carousels
but are missing the proper styling and functionality.
"""

import os
import re
from pathlib import Path

def get_carousel_css():
    """Get the complete carousel CSS"""
    return '''<style>
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
    width: 50px !important;
    height: 50px !important;
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
        width: 45px !important;
        height: 45px !important;
    }
}
</style>'''

def get_carousel_js():
    """Get the complete carousel JavaScript"""
    return '''<script>
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

def fix_carousel_in_file(file_path):
    """Fix carousel CSS and JS in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if file has a carousel
        if 'image-carousel' not in content:
            return False, "No carousel found"

        modified = False

        # Check if CSS is missing
        if '.image-carousel' not in content or '.thumbnail-item .thumbnail-image' not in content:
            # Add CSS before </head>
            css = get_carousel_css()
            content = re.sub(r'(</head>)', f'{css}\n\\1', content, flags=re.IGNORECASE)
            modified = True

        # Check if JS is missing
        if 'function initCarousel' not in content:
            # Add JS before </body>
            js = get_carousel_js()
            content = re.sub(r'(</body>)', f'{js}\n\\1', content, flags=re.IGNORECASE)
            modified = True

        # Ensure all images have the thumbnail-image class
        img_pattern = r'(<img[^>]*class="[^"]*)(")([^>]*>)'
        def fix_img_class(match):
            prefix = match.group(1)
            quote = match.group(2)
            suffix = match.group(3)
            if 'thumbnail-image' not in prefix:
                return prefix + ' thumbnail-image' + quote + suffix
            return match.group(0)

        new_content = re.sub(img_pattern, fix_img_class, content)
        if new_content != content:
            content = new_content
            modified = True

        # Also handle images without existing class
        no_class_pattern = r'(<img[^>]*)(loading="lazy")([^>]*>)'
        def add_class_to_img(match):
            prefix = match.group(1)
            loading = match.group(2)
            suffix = match.group(3)
            if 'class=' not in prefix:
                return prefix + loading + ' class="thumbnail-image"' + suffix
            return match.group(0)

        new_content = re.sub(no_class_pattern, add_class_to_img, content)
        if new_content != content:
            content = new_content
            modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed carousel CSS and JS"

        return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function to fix all HTML files with carousels"""
    current_path = Path(".")
    htm_path = current_path / "htm"

    if not htm_path.exists():
        docs_new_path = Path("docs/new")
        htm_path = docs_new_path / "htm"
        if not htm_path.exists():
            print(f"Error: Neither ./htm nor docs/new/htm exists")
            return

    print("Fixing missing carousel CSS and JS...")

    total_files = 0
    modified_files = 0
    errors = 0

    # Process all HTML files in htm directory
    for html_file in htm_path.rglob("*.htm"):
        # Skip THF files themselves
        if html_file.name.startswith("THF"):
            continue

        total_files += 1
        success, message = fix_carousel_in_file(html_file)

        if success:
            modified_files += 1
            print(f"Fixed {html_file.name}")
        elif "Error:" in message:
            errors += 1
            print(f"Error processing {html_file.name}: {message}")

        # Progress indicator
        if total_files % 500 == 0:
            print(f"Processed {total_files} files...")

    print(f"\nCarousel fix complete:")
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {modified_files}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()