#!/usr/bin/env python3
"""
Fix Carousel Navigation Issues

This script fixes several issues with the carousel navigation:
1. Ensures proper image indexing in carousels
2. Fixes XI file extensions (.HTM vs .htm)
3. Updates onclick handlers with correct parameters
4. Ensures JavaScript functions are properly defined
"""

import os
import re
from pathlib import Path

def extract_images_from_thf_file(thf_path):
    """Extract images with their XI links from THF file"""
    if not os.path.exists(thf_path):
        return []

    try:
        with open(thf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        images = []
        # Pattern to match img + map combinations with XI links
        img_map_pattern = r'<img\s+src="([^"]*)"[^>]*usemap="#([^"]*)"[^>]*>.*?<map\s+name="\2"[^>]*>.*?<area[^>]*href="([^"]*XI[^"]*\.htm[^"]*)"[^>]*>.*?</map>'

        matches = re.findall(img_map_pattern, content, re.IGNORECASE | re.DOTALL)

        for i, match in enumerate(matches):
            src, map_name, link_href = match
            # Ensure the link uses the correct case
            link_href = link_href.replace('.htm', '.HTM')
            images.append({
                'src': src,
                'link': link_href,
                'index': i
            })

        return images
    except Exception as e:
        print(f"Error extracting images from {thf_path}: {e}")
        return []

def fix_carousel_in_file(file_path):
    """Fix carousel navigation in a person file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if 'image-carousel' not in content:
            return False, "No carousel found"

        # Find the THF link to get the actual images
        thf_pattern = r'<center><h2>Photo Gallery</h2></center>\s*<div class="image-carousel" id="([^"]*)"'
        carousel_match = re.search(thf_pattern, content)

        if not carousel_match:
            return False, "Could not find carousel"

        carousel_id = carousel_match.group(1)

        # Try to find the corresponding THF file
        # Look for THF files in the same directory
        file_dir = os.path.dirname(file_path)
        person_file_name = os.path.basename(file_path)

        # Extract person number (XF123.htm -> 123)
        person_match = re.search(r'XF(\d+)\.htm', person_file_name)
        if person_match:
            person_num = person_match.group(1)
            thf_path = os.path.join(file_dir, f"THF{person_num}.htm")

            if os.path.exists(thf_path):
                images = extract_images_from_thf_file(thf_path)

                if images:
                    # Update the carousel with proper onclick handlers
                    updated_content = update_carousel_images(content, images, carousel_id)

                    if updated_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        return True, f"Updated carousel with {len(images)} images"

        return False, "No updates needed"

    except Exception as e:
        return False, f"Error: {e}"

def update_carousel_images(content, images, carousel_id):
    """Update carousel images with proper onclick handlers"""

    # Find all thumbnail items and update them with correct onclick
    def replace_onclick(match):
        img_tag = match.group(0)

        # Find which image this corresponds to by src
        src_match = re.search(r'src="([^"]*)"', img_tag)
        if src_match:
            src = src_match.group(1)

            # Find corresponding image in our list
            for img in images:
                if img['src'] in src or src in img['src']:
                    # Replace the onclick with correct parameters
                    new_onclick = f"onclick=\"openFullImage('{img['link']}', {img['index']}, '{carousel_id}')\""

                    # Remove old onclick and add new one
                    img_tag = re.sub(r'onclick="[^"]*"', new_onclick, img_tag)
                    return img_tag

        return match.group(0)

    # Update all img tags within carousel
    carousel_pattern = r'<div class="image-carousel"[^>]*>.*?</div>(?=<section|$)'

    def update_carousel_section(match):
        carousel_html = match.group(0)
        # Update img tags within this carousel
        updated_carousel = re.sub(r'<img[^>]*onclick="[^"]*"[^>]*>', replace_onclick, carousel_html)
        return updated_carousel

    updated_content = re.sub(carousel_pattern, update_carousel_section, content, flags=re.DOTALL)

    # Also ensure the JavaScript gallery array is populated
    js_injection = f'''
    // Gallery data for {carousel_id}
    const gallery_{carousel_id.replace('-', '_')} = {str(images).replace("'", '"')};

    // Override the openFullImage function to use actual gallery data
    function openFullImage(imageLink, imageIndex, carouselId) {{
        console.log('Navigating to:', imageLink, 'Index:', imageIndex, 'Carousel:', carouselId);

        // Navigate to image with gallery context
        const urlParams = new URLSearchParams();
        urlParams.set('gallery', carouselId);
        urlParams.set('index', imageIndex || 0);
        urlParams.set('source', window.location.href);

        window.location.href = imageLink + '?' + urlParams.toString();
    }}'''

    # Inject the gallery data before the existing openFullImage function
    if 'function openFullImage' in updated_content:
        updated_content = re.sub(
            r'(function openFullImage.*?\})',
            js_injection + '\n\n// Original function replaced above',
            updated_content,
            flags=re.DOTALL
        )
    else:
        # Add before closing script tag
        updated_content = re.sub(
            r'(</script>\s*</body>)',
            js_injection + '\n\\1',
            updated_content
        )

    return updated_content

def main():
    """Main function to fix carousel navigation"""
    current_path = Path(".")
    htm_path = current_path / "htm"

    if not htm_path.exists():
        docs_new_path = Path("docs/new")
        htm_path = docs_new_path / "htm"
        if not htm_path.exists():
            print(f"Error: Neither ./htm nor docs/new/htm exists")
            return

    print("Fixing carousel navigation...")

    total_files = 0
    fixed_files = 0
    errors = 0

    # Process files that have carousels
    for html_file in htm_path.rglob("XF*.htm"):
        total_files += 1
        success, message = fix_carousel_in_file(html_file)

        if success:
            fixed_files += 1
            print(f"Fixed {html_file.name}: {message}")
        elif "Error:" in message:
            errors += 1
            print(f"Error processing {html_file.name}: {message}")

        # Progress indicator for large batches
        if total_files % 100 == 0:
            print(f"Processed {total_files} files...")

    print(f"\nCarousel navigation fix complete:")
    print(f"Total files processed: {total_files}")
    print(f"Files fixed: {fixed_files}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()