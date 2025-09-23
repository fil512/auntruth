# Website Navigation Modernization Plan - New Site in docs/new

## Overview
Create a complete copy of the genealogy site in `docs/new` with modernized navigation while preserving the original site intact.

## Implementation Steps

### 1. Create Site Copy
- Copy entire `docs/htm` directory to `docs/new`
- Copy CSS files to `docs/new/css`
- Create new JavaScript directory `docs/new/js`

### 2. Modern Navigation Structure
```
docs/new/
├── index.html          (main landing page)
├── css/
│   ├── main.css       (modernized styles)
│   └── navigation.css (nav-specific styles)
├── js/
│   ├── navigation.js  (navigation component)
│   ├── search.js      (search functionality)
│   └── data.json      (people/lineage index)
├── htm/               (copied site structure)
│   ├── L0/ through L9/
│   └── all pages
└── includes/
    └── nav.html       (navigation template)
```

### 3. Navigation Features

#### Sticky Top Navigation Bar:
- Logo/Home | Browse Lineages | Search People | Timeline | About | Contact
- "Original Site" link (→ original site at /auntruth/htm/)

#### Side Navigation Panel (collapsible):
- Current lineage tree
- Quick links to related people
- Recently viewed history

#### Search Features:
- Instant search with autocomplete
- Filter by: Name, Date, Location, Lineage
- Search results in modal/dropdown

### 4. Technical Implementation
- **Progressive Enhancement**: Site works without JS, enhanced with it
- **Single Navigation Include**: All pages load same nav via JS
- **Local Storage**: Remember user preferences, recent views
- **Responsive Design**: Mobile-first approach
- **Keyboard Navigation**: Tab through menus, arrow keys in dropdowns

### 5. Navigation Component (navigation.js)
```javascript
// Inject navigation HTML
// Highlight current section
// Handle search autocomplete
// Manage navigation state
// Mobile menu toggle
```

### 6. Data Index Generation
- Parse all person pages (XF*.htm files)
- Extract: names, dates, lineages, relationships
- Generate searchable JSON index
- Enable instant client-side search

### 7. URL Structure
- Original site: `http://localhost:8000/auntruth/htm/`
- New site: `http://localhost:8000/auntruth/new/`
- Both sites link to each other

### 8. Cross-Linking
- Add banner to original site: "Try the New Site →"
- Add link in new site: "Original Site"
- Maintain same file names for easy mapping between versions

## Benefits
- **Preserves Original**: Complete original site remains untouched
- **A/B Testing**: Users can choose their preferred version
- **Safe Migration**: No risk to existing functionality
- **Modern UX**: Contemporary navigation patterns
- **Better Discovery**: Search makes finding people much easier
- **Mobile Friendly**: Responsive navigation for all devices
- **Maintainable**: Centralized navigation code

## Next Steps
1. Copy site structure to docs/new
2. Create navigation JavaScript component
3. Generate people/lineage data index
4. Update all HTML files with navigation script
5. Add bidirectional links between sites
6. Test on various devices/browsers

## Current Site Analysis

### Issues Identified
1. **Repetitive Navigation Code**: Every page has hardcoded navigation (just "Home |" link)
2. **Poor Navigation Structure**: No proper menu system, users must navigate through dropdown selects
3. **No JavaScript**: Site has no JS directory or dynamic functionality
4. **Limited User Experience**: Navigation relies on 1990s-style dropdown forms
5. **Inconsistent Paths**: Mix of relative paths (../), absolute paths (/auntruth/), and hardcoded links

### Site Structure
- Main entry: `docs/htm/all.htm`
- Lineages: L0 through L9 directories
- Person pages: XF*.htm files
- Thumbnail pages: THF*.htm files
- CSS: Mobile-responsive CSS already in place
- Total pages: Thousands of individual person/family pages