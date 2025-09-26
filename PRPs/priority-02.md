# PRP-02: Add Interactive Family Tree Visualization

## Executive Summary

**Priority:** High Impact (2 of 8)
**Estimated Effort:** 4-5 days
**Impact:** High - Transforms genealogy site from static pages to interactive family exploration

Despite being a comprehensive genealogy website with 2,985+ people across 10 family lineages, AuntieRuth.com lacks any visual representation of family relationships. Users must navigate through individual person pages to understand family connections, making it difficult to grasp the broader family structure and relationships.

## Background & Context

### Prerequisites - Required Reading
Before starting this PRP, read:
- `../docs/README.md` - Understanding genealogy file naming conventions and directory structure
- `docs/new/CLAUDE.md` - Architecture and development guidelines for the modernization project
- `../PLAN/site-architecture.md` - Core site structure and data organization
- `../PLAN/technical-requirements.md` - Technical constraints and browser support
- `../PLAN/component-architecture.md` - Component patterns and base classes
- `PRPs/priority-01.md` - Navigation improvements that provide foundation for tree integration

### Current Data Structure
The `js/data.json` contains rich genealogy data for each person:
```json
{
  "id": "191",
  "name": "David Walter Hagborg",
  "lineage": "1",
  "lineageName": "Hagborg-Hansson",
  "birthDate": "Sunday, November 12, 1944",
  "father": "Walter Arnold Hagborg [Hagborg-Hansson]",
  "mother": "Mary Irene Pringle-Hagborg [Pringle-Hambley]",
  "spouse": "Ruth Ann Nelson-Hagborg [Nelson]"
}
```

## Current State Analysis

### Missing Capabilities
1. **No Visual Family Structure:** Users can't see family trees or relationship hierarchies
2. **Limited Relationship Context:** Difficult to understand how people connect across lineages
3. **Poor Discovery:** No way to explore extended family or find distant relatives
4. **Static Experience:** Genealogy exploration requires extensive clicking through individual pages

### Opportunities
1. **Rich Data Available:** Comprehensive family relationship data already structured
2. **Cross-lineage Connections:** Can show how different family branches intermarry
3. **Historical Timeline:** Birth/death dates enable chronological family visualization
4. **Photo Integration:** Can incorporate thumbnail images into tree nodes

## Proposed Solution

### Interactive Family Tree Component
Create a new `FamilyTreeComponent` class that renders dynamic, interactive family trees using modern web technologies.

### Core Features

#### 1. Multi-Generation Tree Visualization
- **3-generation default view:** Grandparents → Parents/Siblings → Children
- **Expandable nodes:** Click to load additional generations
- **Collapsible branches:** Hide/show family branches for clarity
- **Zoom and pan controls:** Navigate large family trees

#### 2. Smart Tree Layouts
- **Horizontal layout:** Traditional left-to-right genealogy format
- **Vertical layout:** Top-down tree structure
- **Radial layout:** Circular family arrangement for large families
- **Compact mode:** Mobile-optimized simplified view

#### 3. Interactive Node Features
- **Person cards:** Hover for quick info (dates, location)
- **Clickable navigation:** Click any person to view their full page
- **Photo thumbnails:** Show person photos when available
- **Relationship indicators:** Visual lines showing marriages, children, adoptions

#### 4. Cross-Lineage Integration
- **Multi-lineage visualization:** Show connections between different family lines
- **Lineage color coding:** Visual distinction between different family branches
- **Lineage switching:** Quick pivot to view different family trees

## Implementation Steps

### Phase 1: Core Tree Engine (Days 1-2)
1. **Technology Selection:**
   - Evaluate D3.js vs SVG.js vs Canvas-based solutions
   - Choose solution balancing performance with interactive features
   - Ensure mobile responsiveness and touch support

2. **Create FamilyTreeComponent class:**
   - Basic tree data processing from `js/data.json`
   - Family relationship parsing and tree structure building
   - Initial SVG/Canvas rendering setup

3. **Basic Tree Rendering:**
   - Simple node and link visualization
   - Person name display and basic styling
   - Click navigation to person pages

### Phase 2: Enhanced Visualization (Day 3)
1. **Advanced Tree Layouts:**
   - Implement multiple layout algorithms (horizontal, vertical, radial)
   - Dynamic spacing based on family size
   - Collision detection and optimal node positioning

2. **Interactive Features:**
   - Zoom and pan controls
   - Node hover effects with person details
   - Expand/collapse functionality for large families
   - Smooth transitions and animations

3. **Visual Enhancements:**
   - Photo thumbnail integration for person nodes
   - Relationship line styling (marriage, parent-child, adoption)
   - Lineage color coding system

### Phase 3: Integration & Mobile (Days 4-5)
1. **Site Integration:**
   - Add family tree widget to person pages (XF*.htm)
   - Integrate with navigation component from PRP-01
   - Create standalone family tree exploration page

2. **Cross-lineage Functionality:**
   - Handle relationships spanning multiple lineages
   - Lineage switching controls
   - Multi-lineage tree visualization

3. **Mobile Optimization:**
   - Touch-friendly controls (pinch zoom, drag pan)
   - Responsive layout for smaller screens
   - Simplified mobile tree view
   - Performance optimization for mobile devices

## Technical Requirements

Read `../PLAN/technical-requirements.md` for complete technical constraints and browser support requirements.

### Component-Specific Dependencies
- **Visualization Library:** D3.js v7+ (recommended) or comparable SVG manipulation library
- **Data Processing:** Integration with existing `js/data.json` structure
- **CSS Framework:** Extension of existing `css/main.css` and `css/navigation.css`
- **Progressive Enhancement:** Must work without JavaScript (static fallback)

### Performance Requirements
- **Initial Load:** Tree rendering completes within 500ms for 3 generations
- **Interaction Response:** Node clicks and hovers respond within 100ms
- **Memory Usage:** Efficient handling of large family trees (100+ people)
- **Mobile Performance:** Smooth interactions on mid-range mobile devices

## Success Criteria

### Primary Features
1. **Visual Family Exploration:** Users can see and navigate family relationships visually
2. **Multi-generation Views:** Display at least 3 generations of family relationships
3. **Interactive Navigation:** Click any person in tree to view their detail page
4. **Cross-lineage Support:** Show relationships between different family lineages

### User Experience Metrics
1. **Engagement:** Increased time spent exploring family relationships
2. **Discovery:** Users find previously unknown family connections
3. **Intuitive Use:** New users understand family relationships without instruction
4. **Mobile Usability:** Tree remains functional on mobile devices

### Technical Validation
1. **Performance:** Tree loads and renders within performance requirements
2. **Accuracy:** All family relationships display correctly
3. **Compatibility:** Works across supported browsers and devices
4. **Progressive Enhancement:** Degrades gracefully without JavaScript

## Testing Plan

Read `../PLAN/testing-qa-standards.md` for comprehensive testing requirements and quality assurance standards.

### Component-Specific Testing
1. **Data Accuracy Validation:**
   - Compare tree relationships with source HTML pages
   - Verify cross-lineage relationships display correctly
   - Test with various family structures (large families, single children, multiple spouses)

2. **Interactive Testing:**
   - Test all zoom/pan controls
   - Verify node expansion/collapse functionality
   - Confirm click navigation to person pages

3. **Cross-lineage Testing:**
   - Test relationships spanning L1-L9 lineages
   - Verify lineage switching functionality
   - Confirm color coding accuracy

## Integration with Existing Architecture

### Component Architecture
- **Standalone Component:** `FamilyTreeComponent` class in new `js/family-tree.js` file
- **CSS Integration:** Extend existing stylesheets with tree-specific styles
- **Data Integration:** Leverage existing `js/data.json` without modification

### Page Integration Points
1. **Person Pages (XF*.htm):** Add family tree widget showing immediate family
2. **Lineage Index Pages:** Create comprehensive lineage family trees
3. **Main Navigation:** Add "Family Tree" option to primary navigation
4. **Search Results:** Include tree preview for search results

### URL Structure
- **Standalone Tree Page:** `/auntruth/new/family-tree/`
- **Person-Centered Tree:** `/auntruth/new/family-tree/?person=191`
- **Lineage Tree:** `/auntruth/new/family-tree/?lineage=1`
- **Maintain Compatibility:** All existing URLs continue working

## Compatibility Notes

### Legacy Preservation
- **No HTML Modification:** Existing person pages remain unchanged
- **Progressive Enhancement:** Tree component enhances existing experience
- **URL Compatibility:** All existing genealogy links continue working
- **Graceful Degradation:** Site functions fully without tree component

### Future Enhancement Foundation
This component enables:
- **PRP-04:** Relationship Navigator (uses tree data structures)
- **PRP-06:** Timeline View (integrates with tree chronology)
- Enhanced search with visual relationship context

## Implementation Files

### New Files to Create
- `js/family-tree.js` - FamilyTreeComponent class and tree rendering logic
- `css/family-tree.css` - Tree-specific styling and responsive layouts
- `family-tree.html` - Standalone family tree exploration page (optional)

### Files to Modify
- `js/navigation.js` - Add family tree links to navigation
- `css/main.css` - Ensure tree component integrates with existing styles
- Person page templates (if adding tree widgets directly to XF pages)

## Post-Implementation

### Analytics & Monitoring
- Track family tree usage patterns
- Monitor performance across different devices
- Collect user feedback on tree navigation experience

### Iterative Improvements
- Add additional layout options based on user preference
- Enhance visual design based on user feedback
- Optimize performance for larger family trees
- Add advanced filtering options (birth date ranges, locations)

### Documentation Updates
- Update `docs/new/CLAUDE.md` with family tree component information
- Document tree data structures for future developers
- Create user guide for family tree exploration

---

**Implementation Note:** This PRP builds on the navigation improvements from PRP-01 and provides the foundation for several other UX enhancements. The family tree becomes a central hub for genealogy exploration.