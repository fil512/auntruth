# PRP-03: Implement Smart Search & Filtering

## Executive Summary

**Priority:** High Impact (3 of 8)
**Estimated Effort:** 3-4 days
**Impact:** High - Transforms genealogy research from browsing to targeted discovery

The current AuntieRuth.com search functionality provides basic name-based search across 2,985 people but lacks the advanced filtering capabilities essential for genealogy research. Users cannot filter by birth/death date ranges, locations, lineages, or relationships, making it difficult to conduct meaningful genealogical research or discover family connections.

## Background & Context

### Prerequisites - Required Reading
Before starting this PRP, read:
- `../docs/README.md` - Understanding genealogy file naming conventions and directory structure
- `docs/new/CLAUDE.md` - Architecture and development guidelines for the modernization project
- `../PLAN/site-architecture.md` - Core site structure and data organization
- `../PLAN/technical-requirements.md` - Technical constraints and browser support
- `../PLAN/component-architecture.md` - Component patterns and base classes
- `PRPs/priority-01.md` - Navigation improvements that integrate with search access

### Current Search Implementation
The existing `SearchComponent` class in `js/search.js` provides:
- Basic client-side search using the Lunr.js library
- Search across person names with fuzzy matching
- Simple autocomplete functionality
- Results display with basic person information

### Available Data for Enhanced Search
The `js/data.json` contains rich searchable fields:
```json
{
  "id": "191",
  "name": "David Walter Hagborg",
  "birthDate": "Sunday, November 12, 1944",
  "birthLocation": "Winnipeg MB   CAN",
  "deathDate": "",
  "deathLocation": "",
  "spouse": "Ruth Ann Nelson-Hagborg [Nelson]",
  "father": "Walter Arnold Hagborg [Hagborg-Hansson]",
  "mother": "Mary Irene Pringle-Hagborg [Pringle-Hambley]",
  "occupation": "Manager, Health & Welfare Canada",
  "address": "235-150 Baylor Avenue Winnipeg MB R3M 2G6 CAN",
  "lineage": "1",
  "lineageName": "Hagborg-Hansson"
}
```

## Current State Analysis

### Search Limitations
1. **Basic Name Search Only:** Cannot search by dates, locations, occupations, or relationships
2. **No Date Range Filtering:** Essential for genealogy research (e.g., "born 1940-1950")
3. **No Location-based Search:** Cannot find all people from specific cities or regions
4. **No Lineage Filtering:** Cannot limit search to specific family branches
5. **No Relationship Search:** Cannot find "descendants of" or "ancestors of"
6. **Poor Mobile Experience:** Search interface not optimized for mobile genealogy research
7. **Limited Result Context:** Results don't show relationship context or life span

### Genealogy Research Use Cases
1. **Date Range Research:** "Show all people born between 1920-1930"
2. **Location Studies:** "Find all family members who lived in Winnipeg"
3. **Lineage Exploration:** "Search within the Nelson lineage only"
4. **Relationship Discovery:** "Find all descendants of Walter Hagborg"
5. **Life Event Research:** "Find people who died in the same year they were born"
6. **Migration Patterns:** "Show birth and death locations for location analysis"

## Proposed Solution

### Enhanced SearchComponent Architecture
Extend the existing `SearchComponent` class with advanced filtering capabilities while maintaining the current progressive enhancement approach.

### Core Enhancement Features

#### 1. Multi-Field Search
- **Name Search:** Enhanced fuzzy matching with nickname support
- **Date Search:** Birth/death date range filtering with flexible date formats
- **Location Search:** Birth/death location with partial matching and regional grouping
- **Occupation Search:** Job titles and professional information
- **Relationship Search:** Father/mother/spouse name matching

#### 2. Advanced Filter Panel
- **Date Range Sliders:** Interactive birth/death year range selection
- **Location Autocomplete:** Smart location matching with historical spellings
- **Lineage Checkboxes:** Multi-select lineage filtering (L0-L9)
- **Relationship Type Filters:** Alive/deceased, married/single, has children/childless
- **Quick Filters:** Pre-configured searches for common genealogy queries

#### 3. Smart Search Results
- **Relationship Context:** Show how people relate to each other in results
- **Life Span Indicators:** Visual timeline showing birth-death range
- **Location Breadcrumbs:** Birth location → Death location for migration patterns
- **Photo Previews:** Include thumbnail images when available
- **Result Grouping:** Group by family, location, or time period

#### 4. Search Suggestions & Discovery
- **Related Searches:** "Also search for relatives of this person"
- **Pattern Discovery:** "Find others with similar life patterns"
- **Location Clustering:** "Show all people from this region"
- **Time Period Exploration:** "Explore this era (1940-1950)"

## Implementation Steps

### Phase 1: Enhanced Search Index (Day 1)
1. **Extend Search Index Creation:**
   - Add all searchable fields to Lunr.js index (dates, locations, occupations, relationships)
   - Implement date normalization for flexible date searching
   - Create location hierarchy (country → province/state → city)
   - Build relationship mapping for family connection searches

2. **Date Processing Enhancement:**
   - Parse various date formats in source data
   - Create searchable year ranges and decade groupings
   - Handle approximate dates and "circa" date matching
   - Build chronological indexing for timeline searches

### Phase 2: Advanced Filter Interface (Day 2)
1. **Create Filter Panel Component:**
   - Date range sliders with min/max year bounds based on data
   - Location autocomplete with intelligent matching
   - Lineage multi-select with family branch names
   - Relationship status filters and life event filters

2. **Enhanced Search Input:**
   - Smart search suggestions as user types
   - Search history and saved searches functionality
   - Quick filter buttons for common genealogy queries
   - Advanced query syntax support ("born:1944 location:Winnipeg")

3. **Results Enhancement:**
   - Rich result cards with photos, dates, locations, relationships
   - Sort options: relevance, birth date, death date, name
   - Result export functionality for research notes
   - Pagination and infinite scroll for large result sets

### Phase 3: Smart Discovery Features (Day 3-4)
1. **Relationship-based Search:**
   - "Find descendants of" functionality using family tree data
   - "Find ancestors of" with generation limiting
   - Sibling and cousin discovery across lineages
   - Marriage connection analysis

2. **Pattern Discovery:**
   - Migration pattern visualization (birth location → death location)
   - Family clustering by location and time period
   - Occupation pattern analysis within families
   - Life span analysis and historical context

3. **Mobile Optimization:**
   - Touch-friendly filter controls
   - Simplified mobile search interface
   - Swipe gestures for result navigation
   - Offline search capability for downloaded results

## Technical Requirements

Read `../PLAN/technical-requirements.md` for complete technical constraints and browser support requirements.

### Component-Specific Dependencies
- **Existing Infrastructure:** Current `SearchComponent` class and Lunr.js integration
- **Data Source:** Enhanced utilization of `js/data.json` structure
- **UI Framework:** Integration with existing CSS framework
- **Progressive Enhancement:** Maintain fallback functionality without JavaScript

### New Dependencies
- **Date Processing:** Date parsing library (e.g., date-fns or moment.js) for flexible date handling
- **UI Components:** Range sliders and multi-select components
- **Export Functionality:** CSV/PDF export for search results

### Performance Requirements
- **Search Response:** Advanced searches complete within 200ms for typical queries
- **Filter Updates:** Filter changes update results within 100ms
- **Index Size:** Efficient indexing to keep client-side search data under 2MB
- **Mobile Performance:** Smooth filtering on mid-range mobile devices

## Success Criteria

### Core Functionality
1. **Advanced Filtering:** Users can filter by date ranges, locations, lineages, and relationships
2. **Discovery Enhancement:** Users discover previously unknown family connections
3. **Research Efficiency:** Genealogy research tasks complete 50% faster than current browsing
4. **Mobile Usability:** Full search functionality available on mobile devices

### User Experience Metrics
1. **Search Utilization:** Increased use of search vs. browsing navigation
2. **Filter Adoption:** Regular use of advanced filters by genealogy researchers
3. **Discovery Success:** Users find relevant family connections through search
4. **Research Workflow:** Seamless integration with family tree and person page viewing

### Technical Validation
1. **Search Accuracy:** Advanced searches return genealogically relevant results
2. **Performance:** All search operations meet response time requirements
3. **Data Integrity:** All 2,985+ people searchable across all enhanced fields
4. **Cross-browser Compatibility:** Consistent experience across supported platforms

## Testing Plan

Read `../PLAN/testing-qa-standards.md` for comprehensive testing requirements and quality assurance standards.

### Component-Specific Testing
1. **Filter Combination Testing:**
   - Test all filter combinations (date + location + lineage)
   - Verify edge cases (empty date fields, partial locations)
   - Test complex queries combining multiple search criteria

2. **Genealogy Use Case Testing:**
   - Test common genealogy research scenarios
   - Verify relationship-based searches work accurately
   - Test migration pattern discovery functionality

3. **Data Accuracy Validation:**
   - Compare search results with source person pages
   - Verify date range filtering accuracy
   - Confirm location matching includes variations and historical spellings

## Integration with Existing Architecture

### Component Integration
- **Navigation Integration:** Search accessible from all pages via PRP-01 navigation
- **Family Tree Integration:** Search results can launch family tree views (PRP-02)
- **Progressive Enhancement:** Works without JavaScript using server-side fallbacks

### URL Structure Enhancement
- **Search URLs:** `/auntruth/new/search/?q=hagborg&birth=1940-1950&lineage=1`
- **Shareable Searches:** Users can bookmark and share complex search queries
- **SEO Optimization:** Search result pages can be indexed by search engines

### Data Flow
- **Client-side Processing:** Maintain fast search using enhanced local indexing
- **Future Server Integration:** Architecture allows future server-side search enhancement
- **Export Integration:** Search results can be exported for external genealogy tools

## Compatibility Notes

### Legacy Preservation
- **Current Search Maintains:** Existing basic search functionality preserved
- **Progressive Enhancement:** Advanced features enhance but don't replace basic search
- **URL Compatibility:** Existing search URLs continue working
- **No Data Changes:** Works with existing `js/data.json` without modification

### Future Enhancement Enablers
This enhanced search system provides foundation for:
- **PRP-04:** Relationship Navigator (uses advanced relationship searches)
- **PRP-06:** Timeline View (leverages date-based search capabilities)
- **Advanced Analytics:** Family pattern discovery and migration analysis

## Implementation Files

### Files to Modify
- `js/search.js` - Enhance SearchComponent class with advanced filtering
- `css/main.css` - Add styles for filter panels and enhanced results
- `js/navigation.js` - Integrate advanced search access into navigation

### New Files to Create
- `js/search-filters.js` - Advanced filter components and logic
- `css/search-filters.css` - Styling for advanced search interface
- `js/search-export.js` - Result export functionality

### Optional Enhancement Files
- `search-help.html` - Search syntax and genealogy research guide
- `js/search-history.js` - Search history and saved searches functionality

## Post-Implementation

### Analytics & Usage Monitoring
- Track advanced filter usage patterns
- Monitor search performance across different query types
- Analyze discovery patterns and successful genealogy research workflows

### Iterative Improvements
- Add additional filter options based on user feedback
- Enhance location matching with geographical intelligence
- Implement machine learning for better search relevance
- Add collaborative features for family research sharing

### Research Integration
- Integration with external genealogy databases
- Export functionality to popular genealogy software
- Advanced reporting for family research projects

---

**Implementation Note:** This PRP significantly enhances the research capabilities of the genealogy site, transforming it from a browsing-based experience to a powerful genealogy research tool. The advanced search capabilities will serve as a foundation for many other UX improvements.