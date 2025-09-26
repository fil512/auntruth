# AuntieRuth.com Site Architecture

## Core Site Structure

### File Organization
- **11,120+ HTML files** organized in genealogy format across 10 lineage directories (L0-L9)
- **2,985+ people** in structured JSON database (`js/data.json`)
- **Legacy compatibility** - existing URLs and structure must be preserved
- **Progressive enhancement** approach - site must work without JavaScript

### Lineage Structure
- **L0:** Base lineage
- **L1:** Hagborg-Hansson
- **L2:** Nelson
- **L3:** Pringle-Hambley
- **L4:** Lathrop-Lothropp
- **L5:** Ward
- **L6:** Selch-Weiss
- **L7:** Stebbe
- **L8:** Lentz
- **L9:** Phoenix-Rogerson

### Page Types
- **Person Pages (XF*.htm):** Individual person detail pages
- **Image Pages (XI*.htm):** Individual photo detail pages
- **Thumbnail Pages (THF*.htm):** Photo gallery pages for individuals
- **Index Pages:** Lineage directory listings

### Data Structure
Each person record contains:
```json
{
  "id": "191",
  "name": "David Walter Hagborg",
  "lineage": "1",
  "lineageName": "Hagborg-Hansson",
  "birthDate": "Sunday, November 12, 1944",
  "birthLocation": "Winnipeg MB   CAN",
  "deathDate": "",
  "deathLocation": "",
  "father": "Walter Arnold Hagborg [Hagborg-Hansson]",
  "mother": "Mary Irene Pringle-Hagborg [Pringle-Hambley]",
  "spouse": "Ruth Ann Nelson-Hagborg [Nelson]",
  "spouse2": "",
  "spouse3": "",
  "spouse4": "",
  "occupation": "Manager, Health & Welfare Canada",
  "address": "235-150 Baylor Avenue Winnipeg MB R3M 2G6 CAN",
  "url": "/auntruth/new/htm/L1/XF191.htm"
}
```

### Cross-Lineage Relationships
- People can have family members from different lineages
- Marriage connections span multiple family branches
- Requires careful handling in all components

## Hosting & Deployment
- **GitHub Pages hosting** - static site with no server-side processing
- **CDN compatibility** required for performance
- **Build pipeline** must work within GitHub Actions constraints