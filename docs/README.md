# AuntieRuth.com Genealogy Website Documentation

This directory contains the static HTML files for the AuntieRuth.com genealogy website, a comprehensive family history archive documenting multiple family lineages with photos and biographical information.

## File Naming Conventions

Understanding the file naming system is crucial for navigating and maintaining this genealogy website. Each prefix indicates a specific type of content:

### Person & Family Files

- **`XF###.htm`** - **Family/Person Detail Pages**
  - Individual biographical pages with complete person information
  - Contains: Birth/death dates, parents, spouse(s), children, photos, notes
  - Example: `XF191.htm` = David Walter Hagborg's complete biography
  - Numbers appear to be sequential IDs assigned chronologically

- **`XI###.htm`** - **Individual Image Detail Pages**
  - Detailed pages for specific photographs or images
  - Contains: Photo metadata, date taken, location, people in photo
  - Example: `XI2717.htm` = "In the Early Morning" photo from Dec 15, 2005
  - Higher numbers typically indicate more recent photos

### Thumbnail & Index Pages

- **`TH####.htm`** - **Year-based Thumbnail Pages**
  - Photo thumbnails organized by year
  - Example: `TH1995.htm` = thumbnail gallery for all 1995 photos
  - Format: TH + 4-digit year

- **`THF###.htm`** - **Person Thumbnail Pages**
  - Photo thumbnails for a specific person
  - Links to all XI pages featuring that person
  - Example: `THF191.htm` = thumbnail gallery for David Walter Hagborg
  - Number matches corresponding XF person ID

- **`THSP##.htm`** - **Special Collection Thumbnails**
  - Themed photo collections or special groupings
  - Example: `THSP10.htm` = "Since April 20 1983" collection
  - Example: `THSP44.htm` = "Home - 235-150 Baylor Avenue" collection

- **`TH[Location].htm`** - **Location-based Thumbnails**
  - Photo thumbnails organized by geographic location
  - Example: `THWinnip.htm` = all Winnipeg photos
  - Example: `THParis.htm` = all Paris photos

### Picture Listing Pages

- **`PICS####.htm`** - **Year Picture Lists**
  - Detailed listings of photos by year (text-based, not thumbnails)
  - Example: `PICS1967.htm` = complete list of 1967 photographs

- **`PICS[Code].htm`** - **Regional Picture Lists**
  - Photo lists organized by region/province
  - Example: `PICSBC.htm` = British Columbia photos
  - Example: `PICSMB.htm` = Manitoba photos

### City & Location Indexes

- **`CX[Location].htm`** - **City/Location Picture Indexes**
  - Comprehensive indexes of photos taken in specific locations
  - Example: `CXWinnip.htm` = index of all Winnipeg pictures
  - Example: `CXParis.htm` = index of all Paris pictures

### Common Navigation Files

- **`EVERYONE.htm`** - Complete alphabetical listing of all people
- **`WAITING.htm`** - People awaiting biographical updates
- **`IMAGES.htm`** - Master image index
- **`index.htm`** - Main page for each lineage directory

## Directory Structure

### Lineage Directories

The website is organized by family lineages in numbered directories:

- **`L0/`** - Base lineage (primary family line)
- **`L1/`** - Hagborg-Hansson lineage
- **`L2/`** - Nelson lineage
- **`L3/`** - Pringle-Hambley lineage
- **`L4/`** - [Additional lineage]
- **`L5/`** - [Additional lineage]
- **`L6/`** - Selch-Weiss lineage
- **`L7/`** - [Additional lineage]
- **`L8/`** - [Additional lineage]
- **`L9/`** - Phoenix-Rogerson lineage

Each lineage directory contains:
- Person detail pages (XF files)
- Photo detail pages (XI files)
- Thumbnail pages (THF, TH, THSP files)
- Location-specific pages (CX files)
- Index and navigation files

### Root Directory

Contains year-based thumbnail pages and overall site navigation:
- `TH1890.htm` through `TH2002.htm` - Annual photo thumbnails
- Master index files
- Site-wide navigation pages

## File Numbering System

### Sequential ID Assignment
- **XF/XI numbers**: Appear to be assigned sequentially as people/photos are added
- **Higher numbers**: Generally indicate more recent additions to the database
- **Gaps in sequence**: Some numbers may be missing due to deleted or never-created entries

### Missing Files
Some referenced files may not exist, typically indicating:
- Photos that were catalogued but detail pages never created (e.g., XI2674.htm, XI2675.htm)
- People who were planned to be added but biographical pages never completed
- Files that were deleted during site maintenance

## Technical Notes

### Case Sensitivity
- File references are case-sensitive
- Most files use uppercase prefixes (XF, XI, TH)
- Some older files may use different casing (hh1.htm vs HH1.htm)

### Cross-References
- XF pages link to corresponding THF thumbnail pages
- XI pages are referenced from thumbnail pages and person biography pages
- Extensive cross-linking maintains family relationship connections

### Image References
- Photos stored in `/jpg/` directory
- Thumbnail images often use `hs###.jpg` naming convention
- Full-size images may use different naming patterns

## Maintenance Guidelines

### When Adding New Content
1. **Person Pages**: Use next sequential XF number
2. **Photo Pages**: Use next sequential XI number
3. **Update Cross-References**: Add new entries to relevant thumbnail and index pages
4. **Maintain Consistency**: Follow established naming conventions

### Common Issues
1. **Broken Links**: May indicate missing detail pages that were never created
2. **Case Mismatches**: Check for incorrect capitalization in file references
3. **Path Issues**: Verify relative vs absolute path usage
4. **Missing Images**: Check `/jpg/` directory for referenced image files

## Historical Context

This genealogy website represents a comprehensive digital archive spanning multiple generations and geographic locations. The systematic file organization reflects the methodical approach taken to document family history, with particular attention to:

- Photographic documentation (extensive XI file series)
- Geographic documentation (location-based organization)
- Temporal organization (year-based thumbnail system)
- Relationship mapping (cross-referenced family connections)

The numbering system and file organization provide insights into the chronological development of the archive, with higher-numbered entries generally representing more recent additions to the family history database.

---

*This documentation was created to assist future maintainers in understanding and preserving the organizational structure of the AuntieRuth.com genealogy archive.*