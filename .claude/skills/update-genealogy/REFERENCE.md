# Genealogy Data Reference

## Complete JSON Schema

Full schema for person records in `data/people/{lineage}/{person_id}.json`:

```json
{
  "id": "XF100",
  "name": "Full Name (First Middle Last)",
  "lineage": "Hagborg-Hansson",
  "birthDate": "1850-05-15" | null,
  "birthLocation": "SWE" | "Location description" | null,
  "deathDate": "1920-12-31" | null,
  "deathLocation": "Winnipeg, MB" | null,
  "deceased": true | false | "Yes" | "No" | "Don't Know",
  "father": {
    "id": "XF82",
    "name": "Father Name",
    "url": "/auntruth/new/htm/L1/XF82.htm"
  } | null,
  "mother": {
    "id": "XF81",
    "name": "Mother Name",
    "url": "/auntruth/new/htm/L1/XF81.htm"
  } | null,
  "spouses": [
    {
      "id": "XF101",
      "name": "Spouse Name",
      "url": "/auntruth/new/htm/L1/XF101.htm",
      "marriageDate": "1875-06-20" | null
    }
  ],
  "children": [
    {
      "id": "XF106",
      "name": "Child Name",
      "url": "/auntruth/new/htm/L1/XF106.htm",
      "birthDate": "1876-03-15" | null
    }
  ],
  "occupation": "Farmer" | null,
  "address": "123 Main St, City, Province" | null,
  "email": "email@example.com" | null,
  "phone": "555-1234" | null,
  "website": "http://example.com" | null,
  "languages": ["English", "Swedish", "Norwegian"],
  "causeOfDeath": "Natural causes" | "Disease" | null,
  "genetics": "DNA test information or genetic notes" | null,
  "notes": "Biographical notes, stories, historical context" | null,
  "photos": [
    {
      "url": "/auntruth/photos/XF100_001.jpg",
      "caption": "Photo description",
      "year": "1895" | null,
      "location": "Winnipeg, MB" | null
    }
  ],
  "photographedBy": [
    {
      "photographerId": "XF200",
      "photoId": "XI1234",
      "url": "/auntruth/new/htm/photos/XI1234.htm"
    }
  ],
  "metadata": {
    "lastUpdated": "2025-10-21T10:00:00Z",
    "originalHtmlPath": "/auntruth/htm/L1/XF100.htm",
    "extractionDate": "2024-12-15T08:30:00Z"
  }
}
```

## Required Fields

Only three fields are strictly required:
- `id` (string, pattern: XF\d+)
- `name` (string, non-empty)
- `lineage` (string, one of the 10 lineage names)

All other fields can be `null` or empty arrays.

## Lineage Directory Mapping

| Lineage Name | Directory | L# | Person Count |
|--------------|-----------|-----|--------------|
| Other | data/people/Other | L0 | 72 |
| Hagborg-Hansson | data/people/Hagborg-Hansson | L1 | 404 |
| Nelson | data/people/Nelson | L2 | 308 |
| Pringle-Hambley | data/people/Pringle-Hambley | L3 | 409 |
| Lathrop-Lothropp | data/people/Lathrop-Lothropp | L4 | 686 (largest) |
| Ward | data/people/Ward | L5 | 123 |
| Selch-Weiss | data/people/Selch-Weiss | L6 | 384 |
| Stebbe | data/people/Stebbe | L7 | 153 |
| Lentz | data/people/Lentz | L8 | 77 (smallest) |
| Phoenix-Rogerson | data/people/Phoenix-Rogerson | L9 | 388 |

## Date Formats

All dates use ISO 8601 format: `YYYY-MM-DD`

Examples:
- Full date: `"1920-12-31"`
- Year only: `"1920"`
- Year-month: `"1920-12"`
- Unknown: `null`

## Location Codes

Common location abbreviations:
- `SWE` - Sweden
- `NOR` - Norway
- `ENG` - England
- `USA` - United States
- `CAN` - Canada
- Cities: "Winnipeg, MB", "Chicago, IL", "Stockholm, SWE"

## Deceased Field Values

The `deceased` field accepts multiple formats for historical compatibility:
- Boolean: `true`, `false`
- String: `"Yes"`, `"No"`, `"Don't Know"`

Use boolean `true`/`false` for new updates.

## URL Pattern Construction

### Person URLs
```
/auntruth/new/htm/L{lineage_num}/{person_id}.htm
```

Examples:
- XF100 in Hagborg-Hansson (L1): `/auntruth/new/htm/L1/XF100.htm`
- XF2451 in Lathrop-Lothropp (L4): `/auntruth/new/htm/L4/XF2451.htm`

### Photo URLs
```
/auntruth/new/htm/photos/{photo_id}.htm
```

Example: XI1234 photo page: `/auntruth/new/htm/photos/XI1234.htm`

## Bidirectional Relationship Rules

### Spouse Relationships
If person A lists person B as spouse, person B MUST list person A as spouse with the same marriage date.

**Valid example**:
- XF100.json: `spouses: [{"id": "XF101", "marriageDate": "1875-06-20"}]`
- XF101.json: `spouses: [{"id": "XF100", "marriageDate": "1875-06-20"}]`

**Invalid example** (will fail validation):
- XF100.json: `spouses: [{"id": "XF101", "marriageDate": "1875-06-20"}]`
- XF101.json: `spouses: []` ← MISSING RECIPROCAL REFERENCE

### Parent-Child Relationships
If person A lists person C as child, person C MUST list person A as mother or father.

**Valid example**:
- XF100.json: `children: [{"id": "XF106"}]`
- XF106.json: `mother: {"id": "XF100"}` or `father: {"id": "XF100"}`

**Invalid example** (will fail validation):
- XF100.json: `children: [{"id": "XF106"}]`
- XF106.json: `mother: null, father: null` ← MISSING PARENT REFERENCE

## Common Validation Errors

### Missing Required Fields
```
ERROR: Missing required field 'id'
FIX: Add "id": "XF###" to JSON
```

### Invalid ID Format
```
ERROR: ID must match pattern XF\d+
FIX: Ensure ID is "XF" followed by digits (e.g., "XF100", not "100" or "XF-100")
```

### Broken Bidirectional Relationship
```
ERROR: Person XF100 lists XF101 as spouse, but XF101 does not list XF100
FIX: Add spouse entry to XF101's spouses array
```

### Invalid Date Format
```
ERROR: Invalid date format "12/31/1920"
FIX: Use ISO format "1920-12-31"
```

### Wrong Field Type
```
ERROR: Field 'children' must be array, got string
FIX: Change "children": "XF106" to "children": [{"id": "XF106", ...}]
```

## Metadata Best Practices

### lastUpdated Timestamp
Always update to current UTC time in ISO 8601 format:
```bash
date -u +"%Y-%m-%dT%H:%M:%SZ"
```

Example: `"2025-10-21T15:30:45Z"`

### Do NOT Modify
These metadata fields should NOT be changed during updates:
- `originalHtmlPath` - path to source HTML file
- `extractionDate` - date data was extracted from HTML

Only update `lastUpdated` when making changes to person data.

## Advanced Patterns

### Multiple Spouses
Person can have multiple entries in `spouses` array:
```json
{
  "spouses": [
    {
      "id": "XF101",
      "name": "First Spouse",
      "marriageDate": "1875-06-20"
    },
    {
      "id": "XF205",
      "name": "Second Spouse",
      "marriageDate": "1920-04-15"
    }
  ]
}
```

Each spouse must reciprocate the relationship in their own file.

### Large Families
No limit on `children` array size. Lathrop-Lothropp lineage has families with 10+ children.

### Photo Arrays
Photos can be empty array `[]`, single entry, or multiple entries. Each photo object can have optional fields (caption, year, location).

### Language Lists
Common values: `["English"]`, `["English", "Swedish"]`, `["Norwegian", "Swedish", "English"]`

Can be empty array `[]` if unknown.
