# Template Structure & Design

## Template Architecture

Modern Jinja2 templates using Phase 4 design system, semantic HTML5, and component-based architecture.

## Template Hierarchy

```
templates/
├── base.html                    # Root template (navigation, footer, layout)
├── person.html                  # Main person page template (extends base)
├── thumbnail.html               # Photo gallery page template (extends base)
├── lineage-index.html          # Lineage navigation page (extends base)
├── components/
│   ├── person-header.html      # Person name, lineage, vital stats
│   ├── family-section.html     # Parents, spouses, children
│   ├── biographical-section.html  # Occupation, address, notes
│   ├── photos-section.html     # Photo galleries
│   ├── research-section.html   # Sources, research notes
│   └── data-table.html         # Reusable data display table
└── macros/
    ├── person-link.html        # Macro for consistent person links
    ├── date-display.html       # Macro for date formatting
    └── section-card.html       # Macro for card-based sections
```

## Base Template (`base.html`)

Provides consistent layout, navigation, and Phase 3/4 integration for all pages.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AuntieRuth.com{% endblock %}</title>

    <!-- Phase 4 Modern Design System -->
    <link rel="stylesheet" href="/auntruth/new/css/modern-design-system.css">
    <link rel="stylesheet" href="/auntruth/new/css/modern-overrides.css">

    <!-- Phase 2 Navigation -->
    <link rel="stylesheet" href="/auntruth/new/css/navigation.css">

    <!-- Phase 3 Components -->
    <link rel="stylesheet" href="/auntruth/new/css/phase3-components.css">

    {% block extra_css %}{% endblock %}
</head>
<body data-phase3-enabled>
    <!-- Navigation will be injected by navigation.js -->
    <div id="navigation-container"></div>

    <!-- Main Content -->
    <main class="container">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="site-footer">
        <center>
            <div id="headlinks">
                <a href="../">Home |</a>
            </div>
        </center>
        <hr>
        <center>
            <b>WebPage Last Updated {% block last_updated %}{{ person.metadata.lastUpdated|default('Unknown') }}{% endblock %}</b><br>
            Copyright 2003-2025<br>
            <strong><b><a href="http://www.hagborg.com">Hagborg Community Systems Ltd.</a></b></strong>
            All Rights Reserved.<br>
        </center>
    </footer>

    <!-- Phase 2 Scripts -->
    <script src="/auntruth/new/js/navigation.js" defer></script>
    <script src="/auntruth/new/js/search.js" defer></script>

    <!-- Phase 3 Integration -->
    <script type="module" src="/auntruth/new/js/phase3-integration.js?v=20250927f"></script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

## Person Page Template (`person.html`)

Main template for individual person pages.

```html
{% extends "base.html" %}
{% from "macros/person-link.html" import person_link %}
{% from "macros/section-card.html" import section_card %}

{% block title %}{{ person.name }} | AuntieRuth.com{% endblock %}

{% block content %}
<!-- Page Header -->
{% include "components/person-header.html" %}

<!-- Person Information Sections -->
<div class="person-sections">
    <!-- Essential Information -->
    {% if person.birthDate or person.birthLocation or person.deathDate or person.deathLocation %}
    {% call section_card("Essential Information", "INFO", open=true) %}
        {% include "components/essential-info.html" %}
    {% endcall %}
    {% endif %}

    <!-- Family Relationships -->
    {% if person.father or person.mother or person.spouses or person.children %}
    {% call section_card("Family Relationships", "FAMILY", open=true) %}
        {% include "components/family-section.html" %}
    {% endcall %}
    {% endif %}

    <!-- Biographical Details -->
    {% if person.occupation or person.address or person.notes %}
    {% call section_card("Biographical Details", "BIO", open=false) %}
        {% include "components/biographical-section.html" %}
    {% endcall %}
    {% endif %}

    <!-- Research & Sources -->
    {% if person.source %}
    {% call section_card("Research & Sources", "RESEARCH", open=false) %}
        {% include "components/research-section.html" %}
    {% endcall %}
    {% endif %}
</div>

<!-- Children Section (if any) -->
{% if person.children %}
<section class="children-section">
    <h2>Children</h2>
    <table class="data-table">
        <thead>
            <tr>
                <th>Child</th>
                <th>Born</th>
            </tr>
        </thead>
        <tbody>
            {% for child in person.children %}
            <tr>
                <td>{{ person_link(child) }}</td>
                <td>{{ child.birthDate|default('Unknown') }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</section>
{% endif %}

<!-- Photos Section -->
{% if person.photos %}
<section class="photos-section">
    <h2>Pictures of this Person</h2>
    {% include "components/photos-section.html" %}
</section>
{% endif %}

{% if person.photographedBy %}
<section class="photographer-section">
    <h2>Pictures Photographed by this Person</h2>
    {% include "components/photos-section.html" with context %}
</section>
{% endif %}
{% endblock %}
```

## Component Templates

### Person Header (`components/person-header.html`)

```html
<header class="person-header card">
    <h1 class="person-name">{{ person.name }}</h1>
    <div class="person-meta">
        <span class="lineage-badge">{{ person.lineage }}</span>
        {% if person.birthDate or person.deathDate %}
        <span class="vital-dates">
            {% if person.birthDate %}b. {{ person.birthDate }}{% endif %}
            {% if person.deathDate %} - d. {{ person.deathDate }}{% endif %}
        </span>
        {% endif %}
    </div>
</header>
```

### Family Section (`components/family-section.html`)

```html
<div class="family-relationships">
    {% if person.father or person.mother %}
    <div class="parents-section">
        <h4>Parents</h4>
        <ul class="family-list">
            {% if person.father %}
            <li><strong>Father:</strong> {{ person_link(person.father) }}</li>
            {% endif %}
            {% if person.mother %}
            <li><strong>Mother:</strong> {{ person_link(person.mother) }}</li>
            {% endif %}
        </ul>
    </div>
    {% endif %}

    {% if person.spouses %}
    <div class="spouses-section">
        <h4>Spouse{{ 's' if person.spouses|length > 1 }}</h4>
        <ul class="family-list">
            {% for spouse in person.spouses %}
            <li>
                {{ person_link(spouse) }}
                {% if spouse.marriageDate %} (m. {{ spouse.marriageDate }}){% endif %}
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</div>
```

## Macros

### Person Link Macro (`macros/person-link.html`)

```html
{% macro person_link(person_obj) %}
    {% if person_obj and person_obj.url %}
        <a href="{{ person_obj.url }}" class="person-link">
            <strong>{{ person_obj.name }}</strong>
        </a>
    {% elif person_obj and person_obj.name %}
        <strong>{{ person_obj.name }}</strong>
    {% else %}
        <em>Unknown</em>
    {% endif %}
{% endmacro %}
```

### Section Card Macro (`macros/section-card.html`)

```html
{% macro section_card(title, icon, open=false) %}
<section class="disclosure-section {% if open %}open{% endif %}">
    <button class="disclosure-section-toggle"
            aria-expanded="{{ 'true' if open else 'false' }}"
            aria-label="Toggle {{ title }}">
        <span class="disclosure-icon">{{ icon }}</span>
        <span class="disclosure-title">{{ title }}</span>
        <span class="disclosure-toggle">{{ '▼' if open else '▶' }}</span>
    </button>
    <div class="disclosure-content" style="display: {{ 'block' if open else 'none' }}">
        {{ caller() }}
    </div>
</section>
{% endmacro %}
```

### Date Display Macro (`macros/date-display.html`)

```html
{% macro date_display(date_str) %}
    {% if date_str and date_str != '0' and date_str != 'Unknown' %}
        {{ date_str }}
    {% else %}
        <em class="text-tertiary">Unknown</em>
    {% endif %}
{% endmacro %}
```

## Design Principles

### 1. Semantic HTML5
- Use `<header>`, `<section>`, `<article>`, `<nav>`, `<footer>`
- Proper heading hierarchy (`<h1>` → `<h2>` → `<h3>`)
- Use `<dl>`, `<dt>`, `<dd>` for data lists
- Use `<table>` only for tabular data

### 2. Phase 4 Design System Integration
- Use CSS variables from `modern-design-system.css`
- Apply design tokens: `var(--color-primary)`, `var(--space-4)`, etc.
- Use utility classes: `.card`, `.data-table`, `.person-link`
- No inline styles

### 3. Progressive Enhancement
- Templates generate semantic HTML first
- Phase 3 JavaScript enhances functionality (optional)
- Works with JavaScript disabled
- Accessible to screen readers

### 4. DRY (Don't Repeat Yourself)
- Reusable components for common patterns
- Macros for repeated markup
- Template inheritance for layout consistency

### 5. Data-Driven Content
- All content from JSON, no hardcoded data
- Graceful handling of missing/null fields
- Conditional rendering based on data availability

## Conditional Rendering Rules

1. **Hide Empty Sections**: Don't show sections if all fields are null/empty
2. **Null Handling**: Display "Unknown" or hide field entirely, never show "null"
3. **Empty Arrays**: Don't render tables/lists if array is empty
4. **Zero Values**: Treat "0" in dates/phones as null (legacy data artifact)

## CSS Classes to Use

From Phase 4 design system (`modern-design-system.css`):

- `.card` - Card container
- `.data-table` - Modern table styling
- `.person-link` - Styled person links
- `.lineage-badge` - Lineage identifier badge
- `.disclosure-section` - Collapsible section
- `.text-primary`, `.text-secondary`, `.text-tertiary` - Text hierarchy
- `.mb-4`, `.mt-6`, `.p-6` - Spacing utilities

## Template Testing Requirements

Each template must:

1. **Validate HTML**: Pass W3C HTML5 validation
2. **Handle Missing Data**: Render correctly with minimal/null fields
3. **Responsive**: Work on mobile (375px) to desktop (1920px)
4. **Accessible**: WCAG 2.1 AA compliant
5. **Match Original**: Generated pages visually match or exceed originals

## Future Template Extensions

- `person-timeline.html` - Chronological life events view
- `family-tree.html` - Visual family tree diagram
- `lineage-statistics.html` - Demographics and statistics
- `search-results.html` - Search result listings
