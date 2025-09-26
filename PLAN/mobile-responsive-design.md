# Mobile & Responsive Design Requirements

## Mobile-First Design Principles

### Core Mobile Requirements
- **Mobile-First CSS:** All CSS written mobile-first with desktop enhancements
- **Touch-Friendly Interface:** All interactive elements minimum 44px touch target
- **Responsive Breakpoints:** 320px, 768px, 1024px, 1200px
- **Fluid Typography:** Typography that scales appropriately across screen sizes
- **Performance-Optimized:** Optimized for mobile device capabilities and bandwidth

### CSS Architecture
```css
:root {
  /* Fluid typography scale */
  --font-size-sm: clamp(0.8rem, 2vw, 0.875rem);
  --font-size-base: clamp(0.875rem, 2.5vw, 1rem);
  --font-size-lg: clamp(1rem, 3vw, 1.125rem);
  --font-size-xl: clamp(1.125rem, 4vw, 1.25rem);

  /* Spacing scale */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;

  /* Touch targets */
  --touch-target-min: 44px;
}
```

## Touch Interaction Patterns

### Touch Gestures
- **Tap:** Primary interaction for buttons and links
- **Long Press:** Context menus and additional options
- **Swipe:** Navigation between related content (family members, photos)
- **Pinch/Zoom:** Family tree and image viewing
- **Pan:** Large content areas (timeline, family tree)

### Touch Event Handling
```javascript
class TouchHandler {
  constructor(element) {
    this.element = element;
    this.touchStartTime = 0;
    this.longPressTimer = null;
  }

  setupTouchEvents() {
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this));
    this.element.addEventListener('touchend', this.handleTouchEnd.bind(this));
    this.element.addEventListener('touchmove', this.handleTouchMove.bind(this));
  }

  handleTouchStart(e) {
    this.touchStartTime = Date.now();
    this.longPressTimer = setTimeout(() => {
      this.handleLongPress(e);
    }, 500);
  }

  handleTouchEnd(e) {
    clearTimeout(this.longPressTimer);
    const touchDuration = Date.now() - this.touchStartTime;

    if (touchDuration < 500) {
      this.handleTap(e);
    }
  }
}
```

## Responsive Layout Patterns

### Table to Card Transformation
Legacy genealogy tables should transform to card layouts on mobile:

```css
/* Mobile: Convert tables to cards */
@media (max-width: 768px) {
  table, tbody, th, td, tr {
    display: block;
  }

  tr {
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: var(--space-md);
    padding: var(--space-md);
    background: var(--color-surface);
  }

  td {
    display: flex;
    align-items: flex-start;
    gap: var(--space-sm);
    padding: var(--space-xs) 0;
    min-height: var(--touch-target-min);
  }

  td:nth-child(1) {
    font-weight: bold;
    color: var(--color-secondary);
    min-width: 120px;
    flex-shrink: 0;
  }
}
```

### Navigation Patterns
```css
/* Mobile navigation */
.mobile-menu-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--touch-target-min);
  height: var(--touch-target-min);
  background: none;
  border: 1px solid var(--color-secondary);
  border-radius: 4px;
  cursor: pointer;
}

@media (min-width: 768px) {
  .mobile-menu-toggle {
    display: none;
  }

  .desktop-menu {
    display: flex;
    align-items: center;
    gap: var(--space-lg);
  }
}
```

## Mobile Performance Optimization

### Image Optimization
```html
<!-- Responsive images for mobile -->
<picture>
  <source media="(max-width: 767px)" srcset="image-mobile.jpg">
  <source media="(min-width: 768px)" srcset="image-desktop.jpg">
  <img src="image-fallback.jpg" alt="Description">
</picture>
```

### Lazy Loading
```javascript
class LazyLoader {
  constructor() {
    this.observer = new IntersectionObserver(this.handleIntersection.bind(this));
  }

  observe(element) {
    this.observer.observe(element);
  }

  handleIntersection(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        this.loadContent(entry.target);
        this.observer.unobserve(entry.target);
      }
    });
  }
}
```

## Accessibility Considerations

### Mobile Accessibility
- **Screen Reader Compatibility:** All components work with mobile screen readers
- **Voice Control:** Compatible with mobile voice navigation
- **High Contrast:** Support for mobile high contrast and dark modes
- **Reduced Motion:** Respect for user motion preferences

### Touch Accessibility
```css
/* Focus indicators for touch devices */
@media (pointer: coarse) {
  button:focus,
  a:focus {
    outline: 3px solid var(--color-primary);
    outline-offset: 2px;
  }
}
```

## Component-Specific Mobile Patterns

### Family Tree Mobile
- **Pinch-to-zoom** for tree navigation
- **Touch-pan** for tree movement
- **Simplified tree view** for small screens
- **Touch-friendly node interaction**

### Search Mobile
- **Simplified filter interface** with collapsible sections
- **Touch-friendly filter controls**
- **Voice search integration** where supported
- **Quick filter buttons** for common queries

### Timeline Mobile
- **Touch-scroll** for timeline navigation
- **Pinch-zoom** for timeline detail levels
- **Touch-tap** for event details
- **Simplified mobile timeline view**

### Navigation Mobile
- **Hamburger menu** for primary navigation
- **Bottom navigation** for core functions
- **Swipe gestures** for family member navigation
- **Touch-friendly breadcrumbs**