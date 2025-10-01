# HTML Patterns Analysis - Person Pages

## Overview
Analysis of HTML structure in person pages (XF*.htm files) to guide data extraction.

## Page Structure

### Document Layout
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Person Name<br>AuntieRuth.com</title>
  <!-- CSS and meta tags -->
</head>
<body>
  <h1>Person Name<br>AuntieRuth.com</h1>
  <table id="List"><!-- Person data --></table>
  <table id="List"><!-- Children --></table>
  <table id="List"><!-- Photos of person --></table>
  <table id="List"><!-- Photos by person --></table>
  <!-- Footer with last updated date -->
</body>
</html>
```

### Key Finding: Multiple Tables with Same ID
**CRITICAL**: There are **4 tables** all using `id="List"`:
1. Person biographical data
2. Children list
3. Photos of this person
4. Photos photographed by this person

Must use `soup.find_all('table', id='List')` and access by index.

## Table 1: Person Biographical Data

### Structure Pattern
```html
<table id="List" rules="all">
  <tbody>
    <tr>
      <td>Field Label</td>
      <td><strong>Value</strong></td>  <!-- Plain text -->
    </tr>
    <tr>
      <td>Field Label</td>
      <td><a href="URL"><strong>Linked Value</strong></a></td>  <!-- Link -->
    </tr>
  </tbody>
</table>
```

### Field Labels Found

**Family Relationships:**
- `Father` - Link to XF*.htm or empty `<strong></strong>`
- `Mother` - Link to XF*.htm or empty `<strong></strong>`
- `Spouse(1)`, `Spouse(2)`, `Spouse(3)`, `Spouse(4)` - Multiple spouse fields
- `Marriage Date(1)`, `Marriage Date(2)`, etc. - Corresponding marriage dates

**Vital Statistics:**
- `BirthDate` - Various formats (empty, "0", full date like "Sunday, January 01, 1860")
- `Birth Location` - Text like "SWE", "Hagestad S0   SWE"
- `Deceased?` - Values: "Yes", "No", "Don't Know"
- `Death Date` - Same format as BirthDate
- `Cause of Death` - Text or empty

**Contact Information:**
- `Address` - Text or empty
- `WebSite` - URL or empty
- `EMail` - Email or empty
- `Telephone` - Phone or "0"
- `FAX` - Fax or "0" or empty
- `Home Phone` - Often "0"
- `Home FAX` - Often "0"
- `Cell` - Often "0"

**Languages:**
- `Language(1)`, `Language(2)`, `Language(3)` - Usually empty

**Other:**
- `Occupation` - Text or empty
- `Lineage` - Link to L*/index.htm (e.g., "Hagborg-Hansson")
- `Genetics` - Usually empty
- `Source` - Text (e.g., "Hemfrid Johnsson")
- `Notes` - Text (can be multi-line, Swedish characters)
- `Waiting?` - Usually "Don't Know"

## Table 2: Children List

### Structure Pattern
```html
<h2><font color="#FF0000">Children</font></h2>
<hr noshade size="6" color="#0000FF">
<table id="List" rules="all">
  <tbody>
    <tr>
      <td><b>Child</b></td>
      <td><b>Born</b></td>
    </tr>
    <tr>
      <td><a href="/auntruth/new/htm/L1/XF106.htm"><b>Anna</b></a></td>
      <td>0</td>
    </tr>
  </tbody>
</table>
```

### Key Points
- First row is header (Child | Born)
- Subsequent rows contain child data
- Child name is a link to their XF page
- Birth date often "0" (unknown)
- Empty table if no children (only header row)

## Table 3: Photos of this Person

### Structure Pattern
```html
<h2><font color="#FF0000">Pictures of this Person</font></h2>
<hr noshade size="6" color="#0000FF">
<table id="List" rules="all">
  <tbody>
    <tr>
      <td><b>Name</b></td>
      <td><b>Date</b></td>
      <td><b>Location</b></td>
    </tr>
    <!-- Photo rows would go here, but often empty -->
  </tbody>
</table>
```

### Key Points
- First row is header (Name | Date | Location)
- Often only header row (no photos)
- Photos would link to XI*.htm pages

## Table 4: Photos Photographed by this Person

### Structure Pattern
Same as Table 3, but for photos taken BY the person.

## URL Patterns

### Person Pages
```
/auntruth/new/htm/L1/XF100.htm
/auntruth/new/htm/L1/XF82.htm
```
Extract ID: `XF\d+` from path

### Thumbnail Pages
```
/auntruth/new/htm/L1/THF100.htm
```
Pattern: `THF{person_id}.htm`

### Lineage Index Pages
```
/auntruth/new/htm/L1/index.htm
```
L1 = Hagborg-Hansson lineage

## Empty Value Patterns

### Observed Empty Representations
1. `<strong></strong>` - Empty tag
2. `<strong>0</strong>` - Literal "0"
3. Empty string
4. "Don't Know" - For Deceased? and Waiting? fields

### Normalization Rules
- Empty `<strong>` tags → `null`
- "0" in phone/date fields → `null`
- Empty strings → `null`
- "Don't Know" → Keep as string literal

## Name Format Patterns

### With Lineage Suffix
```
Matts Hakansson [Hagborg-Hansson]
Else Hansdotter-Hakansson [Hagborg-Hansson]
```
Pattern: `Name [Lineage]`

### Without Lineage Suffix
```
Johanna  Hakanson
Anna
Edit
```

**Decision**: Keep `[Lineage]` suffix in names for now (as per data schema)

## Date Format Variations

### Observed Formats
1. Full: `Sunday, January 01, 1860`
2. Empty: `<strong></strong>`
3. Zero: `0`

**Decision**: Preserve original format, handle normalization in templates

## Special Character Handling

### Swedish Characters Found
```
Gift med Matts Hakonsson, skraddarnastare och kyrkovakmastare i Horup
Hagestad S0   SWE
```

**Important**: Use UTF-8 encoding when reading HTML files

## Last Updated Footer Pattern

```html
<b>WebPage Last Updated Monday, December 19, 2005 18:52:51 GMT/CUT</b>
```

Extract pattern: `WebPage Last Updated (.+)`

## Edge Cases Identified

1. **Multiple Spouses**: Up to 4 spouse fields
2. **Empty Parents**: Father/Mother can be empty `<strong>` tags
3. **No Children**: Children table may only have header row
4. **No Photos**: Photo tables often only have header rows
5. **Extra Whitespace**: Names like "Johanna  Hakanson" (double space)
6. **Swedish Notes**: Multi-language text in Notes field
7. **Lineage in Name**: Some names have `[Lineage]` suffix, others don't
8. **Birth Location Formatting**: Varies from "SWE" to "Hagestad S0   SWE"

## Extraction Strategy

### Step 1: Parse HTML
```python
from bs4 import BeautifulSoup

with open(html_file, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
```

### Step 2: Extract Name from h1
```python
h1 = soup.find('h1')
name = h1.get_text().split('\n')[0].strip()  # "Johanna  Hakanson"
```

### Step 3: Get All Tables
```python
tables = soup.find_all('table', id='List')
# tables[0] = person data
# tables[1] = children (if exists)
# tables[2] = photos of person (if exists)
# tables[3] = photos by person (if exists)
```

### Step 4: Extract Table 1 Data
```python
if len(tables) >= 1:
    person_table = tables[0]
    for row in person_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            label = cells[0].get_text().strip()
            value_cell = cells[1]

            # Check for link
            link = value_cell.find('a')
            if link:
                # Extract: name, URL, person ID
                pass
            else:
                # Extract plain text
                text = value_cell.get_text().strip()
                # Normalize empty values
                pass
```

### Step 5: Extract Children Table
```python
if len(tables) >= 2:
    children_table = tables[1]
    # Skip header row (index 0)
    for row in children_table.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) >= 2:
            child_link = cells[0].find('a')
            birth_date = cells[1].get_text().strip()
```

### Step 6: Extract Photos Tables
```python
if len(tables) >= 3:
    photos_of_table = tables[2]
    # Extract photo entries

if len(tables) >= 4:
    photos_by_table = tables[3]
    # Extract photo entries
```

### Step 7: Extract Last Updated Date
```python
# Find footer text
footer = soup.find('b', string=re.compile('WebPage Last Updated'))
if footer:
    text = footer.get_text()
    # Parse: "WebPage Last Updated Monday, December 19, 2005 18:52:51 GMT/CUT"
```

## Validation Checkpoints

1. **Person ID**: Must match pattern `XF\d+`
2. **Name**: Must not be empty
3. **Lineage**: Must not be empty
4. **URL Consistency**: All internal links should use `/auntruth/new/htm/` prefix
5. **Children Count**: Number of children in JSON should match HTML table rows - 1 (header)
6. **Data Completeness**: Every non-empty `<strong>` tag in HTML should map to JSON field

## Sample Extraction Mapping

### Input HTML (XF100.htm)
```html
<td>Father</td>
<td><a href="/auntruth/new/htm/L1/XF82.htm"><strong>Matts Hakansson [Hagborg-Hansson]</strong></a></td>
```

### Output JSON
```json
{
  "father": {
    "id": "XF82",
    "name": "Matts Hakansson [Hagborg-Hansson]",
    "url": "/auntruth/new/htm/L1/XF82.htm"
  }
}
```

### Input HTML (Empty Field)
```html
<td>BirthDate</td>
<td><strong></strong></td>
```

### Output JSON
```json
{
  "birthDate": null
}
```

### Input HTML (Zero Value)
```html
<td>Home Phone</td>
<td><strong>0</strong></td>
```

### Output JSON
```json
{
  "phone": null  // "0" normalized to null
}
```

## Conclusion

The HTML structure is consistent and predictable, making automated extraction feasible. Key challenges:
1. Multiple tables with same ID (use indexed access)
2. Varying empty value representations (normalize to null)
3. UTF-8 characters (use proper encoding)
4. Multiple spouses/children (iterate and collect)

This pattern analysis will guide the implementation of `extract_person_data.py`.
