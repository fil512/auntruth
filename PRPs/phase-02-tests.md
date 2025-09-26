# Phase 2 Manual Test Cases

## 🔍 Enhanced Search Testing

### Test Case 1: Basic Search Functionality
**Prerequisites:** Navigate to a page with the enhanced search component
1. **Open Search:** Press `Ctrl+K` (or `Cmd+K` on Mac) to open search
   - ✅ Search interface should appear
   - ✅ Input field should be focused
2. **Basic Search:** Type "John" in the search box
   - ✅ Results should appear within 200ms
   - ✅ Names containing "John" should be highlighted
   - ✅ Score percentages should be displayed
3. **Navigation:** Use arrow keys to navigate results
   - ✅ Results should highlight with keyboard navigation
   - ✅ Press Enter on selected result to navigate

### Test Case 2: Advanced Filtering
1. **Open Filters:** Click the gear icon to expand advanced filters
   - ✅ Filter options should expand smoothly
2. **Lineage Filtering:** Uncheck "Lineage 0" and search for a name
   - ✅ Results should exclude people from Lineage 0
3. **Year Range:** Adjust birth year range to 1900-1950
   - ✅ Results should only show people born in that range
4. **Location Search:** Search for "Pennsylvania"
   - ✅ Should find people with PA birth/death locations

### Test Case 3: Mobile Search Experience
**Prerequisites:** Test on mobile device or browser dev tools (375px width)
1. **Touch Targets:** Tap search interface elements
   - ✅ All buttons should be at least 44px touch targets
   - ✅ No accidental activations
2. **Filter Interface:** Open and use filters on mobile
   - ✅ Filters should stack vertically
   - ✅ Easy to tap checkboxes and sliders

## 🌳 Family Tree Testing

### Test Case 4: Tree Visualization
**Prerequisites:** Navigate to a person detail page (XF###.htm)
1. **Tree Loading:** Look for family tree component
   - ✅ Tree should load within 1 second
   - ✅ Focus person should be highlighted in gold
2. **Node Interaction:** Click on different family members
   - ✅ Tree should re-center on clicked person
   - ✅ Person details should show in tooltip (desktop)
3. **Zoom Controls:** Test the +, -, and center buttons
   - ✅ Zoom should work smoothly
   - ✅ Center button should reset view

### Test Case 5: Complex Relationships
1. **Multiple Spouses:** Find person with multiple marriages
   - ✅ Multiple spouse names should appear
   - ✅ Tree should handle complex relationships
2. **Missing Parents:** Find person with unknown parents
   - ✅ Tree should gracefully handle missing data
   - ✅ No broken connections or errors

### Test Case 6: Mobile Tree Interaction
**Prerequisites:** Mobile device or narrow browser window
1. **Touch Navigation:** Use pinch-to-zoom and pan gestures
   - ✅ Touch interactions should work smoothly
   - ✅ No lag or jumping during gestures
2. **Control Buttons:** Test tree control buttons
   - ✅ Larger touch targets (50px minimum)
   - ✅ Easy to tap without errors

## 📋 Information Disclosure Testing

### Test Case 7: Progressive Disclosure
**Prerequisites:** Navigate to a person detail page with data table
1. **Interface Transformation:** Page should show enhanced layout
   - ✅ Original table should be hidden
   - ✅ Organized sections should appear
   - ✅ Fallback toggle should be available
2. **Section Interaction:** Click on different section headers
   - ✅ Sections should expand/collapse smoothly
   - ✅ User preferences should persist on reload
3. **Fallback Mode:** Click "Original View" button
   - ✅ Should show original table
   - ✅ Can toggle back to enhanced view

### Test Case 8: Content Organization
1. **Essential Information:** Should always be expanded
   - ✅ Name, birth/death dates and locations visible
2. **Family Section:** Check family relationships
   - ✅ Parents, spouses, children properly categorized
   - ✅ Multiple spouses handled correctly
3. **Photos Section:** Look for image content
   - ✅ Photos should be displayed nicely
   - ✅ Images should be responsive

## 🔗 Component Integration Testing

### Test Case 9: Search to Tree Workflow
1. **Search for Person:** Use enhanced search to find someone
2. **View Family Tree:** Click on search result
   - ✅ Should navigate to person page
   - ✅ Family tree should focus on that person
3. **Cross-Navigation:** Click different tree nodes
   - ✅ URL should update with focus parameter
   - ✅ Bookmarking should work

### Test Case 10: URL State Management
1. **Bookmarkable Views:** Navigate around and bookmark pages
   - ✅ URLs should include state parameters
   - ✅ Refresh should maintain view state
2. **Back/Forward:** Use browser navigation
   - ✅ Component state should restore correctly
   - ✅ No broken functionality

## 📱 Mobile Responsiveness Testing

### Test Case 11: Responsive Breakpoints
**Test at these screen widths:** 320px, 768px, 1024px, 1200px
1. **Layout Adaptation:** Check each component
   - ✅ Search interface adapts to screen size
   - ✅ Tree controls stack appropriately
   - ✅ Disclosure sections work on mobile
2. **Touch Interactions:** Test all interactive elements
   - ✅ No elements smaller than 44px
   - ✅ Adequate spacing between touch targets

### Test Case 12: Performance on Mobile
1. **Loading Speed:** Test on slower mobile device/connection
   - ✅ Search indices load under 500ms
   - ✅ Tree renders under 1 second
   - ✅ Smooth scrolling and interactions
2. **Memory Usage:** Navigate between multiple pages
   - ✅ No memory leaks or performance degradation
   - ✅ Components clean up properly

## 🎯 Edge Cases & Error Handling

### Test Case 13: Data Edge Cases
1. **Empty Search:** Search for nonsense text "zzxxyy"
   - ✅ Should show "No results found" message
   - ✅ Helpful suggestions provided
2. **Missing Data:** Find person with minimal information
   - ✅ Components should handle gracefully
   - ✅ No JavaScript errors in console

### Test Case 14: Browser Compatibility
**Test in:** Chrome, Firefox, Safari, Edge
1. **Core Functionality:** All test cases above
   - ✅ Consistent behavior across browsers
   - ✅ No browser-specific issues
2. **Fallback Support:** Disable JavaScript
   - ✅ Original table structure still works
   - ✅ Graceful degradation

## 🧪 Automated Validation

### Test Case 15: Run Test Suite
```bash
# Run all Phase 2 tests
npm run test:phase2

# Individual component tests
npm run test:search    # Should pass 5/5 tests
npm run test:tree      # Should pass 5/5 tests
npm run test:mobile    # Should pass 5/5 tests
```
- ✅ All tests should pass with 100% success rate
- ✅ Performance metrics should meet targets

## 🎨 Accessibility Testing

### Test Case 16: Screen Reader Testing
1. **Keyboard Navigation:** Navigate using only keyboard
   - ✅ All interactive elements reachable
   - ✅ Logical tab order maintained
2. **Screen Reader:** Test with screen reader software
   - ✅ Proper announcements for search results
   - ✅ Section headings properly labeled
   - ✅ Form controls have labels

### Test Case 17: Reduced Motion Testing
1. **Browser Setting:** Enable "prefers-reduced-motion"
   - ✅ Animations should be minimal or removed
   - ✅ Functionality should remain intact

## 📊 Success Criteria Validation

After completing all test cases:
- ✅ **Search Performance:** < 200ms search responses
- ✅ **Tree Rendering:** < 1s for 3 generations
- ✅ **Mobile Performance:** Smooth on mid-range devices
- ✅ **Accessibility:** WCAG 2.1 AA compliance
- ✅ **Browser Support:** Works in all major browsers
- ✅ **URL Preservation:** All existing links still work
- ✅ **Progressive Enhancement:** Graceful fallbacks

---

## 🛠️ Testing Environment Setup

### Prerequisites
1. **Start Local Server:**
   ```bash
   npm run dev
   ```
2. **Navigate to Site:** `http://localhost:8000/docs`
3. **Browser Dev Tools:** Use for mobile simulation (F12 → Device toolbar)
4. **Console Monitoring:** Check for JavaScript errors during testing

### Test Data Locations
- **Person Pages:** Navigate to `/docs/new/htm/L*/XF*.htm` files
- **Search Interface:** Available on index pages and enhanced person pages
- **Family Tree:** Embedded in person detail pages
- **Information Disclosure:** Transforms existing table-based person pages

### Performance Testing Tools
- **Chrome DevTools:** Network and Performance tabs
- **Mobile Simulation:** Device toolbar with various screen sizes
- **Accessibility:** Lighthouse audit and screen reader testing

### Expected Results
**All ✅ checkboxes should pass for successful Phase 2 implementation.**

### Reporting Issues
If any test cases fail:
1. Note the specific test case number and step
2. Record browser version and screen size
3. Include console error messages if present
4. Test on multiple browsers to confirm issue scope
5. Check network connectivity for search/loading issues

---

## 📋 Test Execution Checklist

### Pre-Testing Setup
- [ ] Local server running (`npm run dev`)
- [ ] Browser dev tools ready
- [ ] Multiple browsers available for compatibility testing
- [ ] Mobile device or browser simulation ready
- [ ] Screen reader software installed (optional)

### Core Component Testing
- [ ] Enhanced Search (Test Cases 1-3)
- [ ] Family Tree (Test Cases 4-6)
- [ ] Information Disclosure (Test Cases 7-8)
- [ ] Component Integration (Test Cases 9-10)

### Responsive & Accessibility Testing
- [ ] Mobile Responsiveness (Test Cases 11-12)
- [ ] Edge Cases (Test Cases 13-14)
- [ ] Automated Tests (Test Case 15)
- [ ] Accessibility (Test Cases 16-17)

### Final Validation
- [ ] Success Criteria Review
- [ ] Performance Metrics Confirmed
- [ ] Cross-Browser Compatibility Verified
- [ ] Documentation Updated

**Testing Complete:** _____ Date: _____

**Tested By:** _____ Browser Versions: _____

**Overall Result:** PASS / FAIL (circle one)

**Notes:** ___________________________________