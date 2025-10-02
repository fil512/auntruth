# Person Data Schema

## JSON Schema Specification

This document defines the canonical structure for person records extracted from HTML and used to generate modern pages.

## Person Record Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "name", "lineage"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^XF\\d+$",
      "description": "Unique person identifier (e.g., XF100)"
    },
    "name": {
      "type": "string",
      "description": "Full name of the person"
    },
    "lineage": {
      "type": "string",
      "description": "Lineage name (e.g., Hagborg-Hansson)"
    },
    "birthDate": {
      "type": ["string", "null"],
      "description": "Birth date in various formats or null if unknown"
    },
    "birthLocation": {
      "type": ["string", "null"],
      "description": "Birth location (city, country, etc.)"
    },
    "deathDate": {
      "type": ["string", "null"],
      "description": "Death date in various formats or null if unknown/alive"
    },
    "deathLocation": {
      "type": ["string", "null"],
      "description": "Death location"
    },
    "deceased": {
      "type": ["boolean", "string"],
      "description": "Deceased status: true, false, 'No', 'Yes', 'Don't Know'"
    },
    "father": {
      "type": ["object", "null"],
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "url": {"type": "string"}
      },
      "description": "Father reference"
    },
    "mother": {
      "type": ["object", "null"],
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "url": {"type": "string"}
      },
      "description": "Mother reference"
    },
    "spouses": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "url": {"type": "string"},
          "marriageDate": {"type": ["string", "null"]}
        }
      },
      "description": "Array of spouse records"
    },
    "children": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "url": {"type": "string"},
          "birthDate": {"type": ["string", "null"]}
        }
      },
      "description": "Array of children records"
    },
    "occupation": {
      "type": ["string", "null"],
      "description": "Occupation or profession"
    },
    "address": {
      "type": ["string", "null"],
      "description": "Current/last known address"
    },
    "email": {
      "type": ["string", "null"],
      "description": "Email address"
    },
    "phone": {
      "type": ["string", "null"],
      "description": "Phone number"
    },
    "website": {
      "type": ["string", "null"],
      "description": "Personal website URL"
    },
    "languages": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Languages spoken (Language(1), Language(2), etc.)"
    },
    "causeOfDeath": {
      "type": ["string", "null"],
      "description": "Medical cause of death"
    },
    "genetics": {
      "type": ["string", "null"],
      "description": "DNA/Genetic testing information"
    },
    "waitingStatus": {
      "type": ["boolean", "string", "null"],
      "description": "Genealogy software waiting status"
    },
    "source": {
      "type": ["string", "null"],
      "description": "Research source attribution"
    },
    "notes": {
      "type": ["string", "null"],
      "description": "Biographical notes"
    },
    "photos": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "date": {"type": ["string", "null"]},
          "location": {"type": ["string", "null"]},
          "url": {"type": "string"}
        }
      },
      "description": "Photos of this person"
    },
    "photographedBy": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "date": {"type": ["string", "null"]},
          "location": {"type": ["string", "null"]},
          "url": {"type": "string"}
        }
      },
      "description": "Photos taken by this person"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "lastUpdated": {"type": "string", "format": "date-time"},
        "originalHtmlPath": {"type": "string"},
        "extractionDate": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

## Example: Complete Person Record

```json
{
  "id": "XF100",
  "name": "Johanna Hakanson",
  "lineage": "Hagborg-Hansson",
  "birthDate": null,
  "birthLocation": "SWE",
  "deathDate": null,
  "deathLocation": null,
  "deceased": "No",
  "father": {
    "id": "XF82",
    "name": "Matts Hakansson [Hagborg-Hansson]",
    "url": "/auntruth/new/htm/L1/XF82.htm"
  },
  "mother": {
    "id": "XF81",
    "name": "Else Hansdotter-Hakansson [Hagborg-Hansson]",
    "url": "/auntruth/new/htm/L1/XF81.htm"
  },
  "spouses": [
    {
      "id": "XF101",
      "name": "Albert [Hagborg-Hansson]",
      "url": "/auntruth/new/htm/L1/XF101.htm",
      "marriageDate": null
    }
  ],
  "children": [
    {
      "id": "XF106",
      "name": "Anna",
      "url": "/auntruth/new/htm/L1/XF106.htm",
      "birthDate": "0"
    },
    {
      "id": "XF104",
      "name": "Edit",
      "url": "/auntruth/new/htm/L1/XF104.htm",
      "birthDate": "0"
    }
  ],
  "occupation": null,
  "address": "SWE",
  "email": null,
  "phone": null,
  "website": null,
  "languages": [],
  "causeOfDeath": null,
  "genetics": null,
  "waitingStatus": null,
  "source": "Hemfrid Johnsson",
  "notes": null,
  "photos": [],
  "photographedBy": [],
  "metadata": {
    "lastUpdated": "2005-12-19T18:52:51Z",
    "originalHtmlPath": "docs/new/htm/L1/XF100.htm",
    "extractionDate": "2025-10-01T12:00:00Z"
  }
}
```

## Field Mapping from HTML

### Table Row Mapping

Based on analysis of existing `table#List` structure:

| HTML Table Row Label | JSON Field | Type | Notes |
|---------------------|------------|------|-------|
| Father | `father` | object | Extract name, derive ID from link href |
| Mother | `mother` | object | Extract name, derive ID from link href |
| BirthDate | `birthDate` | string\|null | Keep as-is, handle various formats |
| Birth Location | `birthLocation` | string\|null | |
| Spouse(1), Spouse(2)... | `spouses[]` | array | Combine all spouse entries |
| Marriage Date(1)... | `spouses[].marriageDate` | string\|null | Associate with corresponding spouse |
| Address | `address` | string\|null | |
| WebSite | `website` | string\|null | Extract href from `<a>` tag |
| EMail | `email` | string\|null | Extract href from `<a>` tag, strip mailto: |
| Telephone, Home Phone, Cell | `phone` | string\|null | Combine all phone fields |
| Occupation | `occupation` | string\|null | |
| Language(1), Language(2), Language(3) | `languages[]` | array | Collect all language entries |
| Cause of Death | `causeOfDeath` | string\|null | Medical cause of death |
| Genetics | `genetics` | string\|null | DNA/Genetic test information |
| Waiting? | `waitingStatus` | boolean\|string\|null | Genealogy software status |
| Lineage | `lineage` | string | Extract from link, remove from name |
| Deceased? | `deceased` | boolean\|string | "Yes", "No", "Don't Know" |
| Death Date | `deathDate` | string\|null | |
| Source | `source` | string\|null | |
| Notes | `notes` | string\|null | Preserve full text, including long content |

### Children Table Mapping

Extract from second `table#List`:

```html
<table id="List">
  <tr><td>Child</td><td>Born</td></tr>
  <tr>
    <td><a href="/path/XF106.htm">Anna</a></td>
    <td>0</td>
  </tr>
</table>
```

Maps to:
```json
{
  "children": [
    {
      "id": "XF106",
      "name": "Anna",
      "url": "/auntruth/new/htm/L1/XF106.htm",
      "birthDate": "0"
    }
  ]
}
```

### Photos Tables Mapping

Third and fourth `table#List` tables contain photo information.

## Data Normalization Rules

1. **Empty Values**: Convert empty strings, "0", and missing data to `null`
2. **URLs**: Store as absolute paths starting with `/auntruth/`
3. **Person IDs**: Extract from URLs (e.g., `/path/XF100.htm` → `XF100`)
4. **Lineage Names**: Standardize casing and format
5. **Dates**: Preserve original format (don't convert), handle in templates
6. **Brackets in Names**: Keep `[Lineage]` suffix in names for now

## Validation Rules

During extraction, validate:

1. **Required Fields**: `id`, `name`, `lineage` must not be null
2. **ID Format**: Must match pattern `XF\d+`
3. **URL Consistency**: All URLs must be valid paths
4. **Circular References**: Verify parent/child/spouse relationships are consistent
5. **Data Completeness**: No data loss from original HTML

## Storage Structure

```
data/
└── people/
    ├── Hagborg-Hansson/
    │   ├── XF82.json
    │   ├── XF100.json
    │   └── XF101.json
    ├── Anderson/
    │   └── XF*.json
    └── {lineage}/
        └── {person_id}.json
```

## Future Extensions

Fields that may be added later:

- `birthPlace` (structured location data)
- `occupation.title`, `occupation.startDate`, `occupation.endDate`
- `residences[]` (multiple addresses over time)
- `events[]` (life events with dates/locations)
- `sources[]` (multiple research sources with citations)
- `dna` (genetic test information)
