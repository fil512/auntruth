# Genealogy Development Server

A simple web server for testing the modernized genealogy site locally before deploying to GitHub Pages.

## Usage

### Installation
```bash
cd /home/ken/wip/fam/auntruth/PRPs/server
pip3 install -r requirements.txt
```

### Quick Start
```bash
cd /home/ken/wip/fam/auntruth/PRPs/server
python3 genealogy_server.py
```

### With Custom Port
```bash
python3 genealogy_server.py --port 8080
```

## Access URLs

- **Main site:** http://localhost:8000/auntruth/
- **Direct docs access:** http://localhost:8000/
- **Index page:** http://localhost:8000/auntruth/index.html

## Features

- **Path Mapping:** Serves `/home/ken/wip/fam/auntruth/docs/` at `localhost:8000/auntruth/`
- **GitHub Pages Simulation:** Mimics the URL structure of `https://fil512.github.io/auntruth/`
- **CORS Headers:** Includes CORS headers for local development
- **Security:** Prevents directory traversal attacks
- **Logging:** Shows request information for debugging

## Testing Path Fixes

This server allows you to test the path modernization changes:

1. **Start the server:**
   ```bash
   python3 genealogy_server.py
   ```

2. **Test the fixed paths:**
   - Visit http://localhost:8000/auntruth/
   - Navigate through the lineage sections (L0-L9)
   - Verify that internal links work correctly
   - Check that images and resources load properly

3. **Verify specific fixes:**
   - **Task 001:** Windows-style paths (`\auntruth\htm\` → relative paths)
   - **Task 002:** Absolute paths (`/AuntRuth/` → `/auntruth/`)

## Troubleshooting

### Port Already in Use
```bash
# Try a different port
python3 genealogy_server.py --port 8080
```

### Permission Errors
```bash
# Ensure script is executable
chmod +x genealogy_server.py
```

### Path Issues
- Server expects docs directory at `/home/ken/wip/fam/auntruth/docs/`
- Check that the directory exists and contains HTML files

## Development Notes

- **URL Structure:** `/auntruth/` prefix matches GitHub Pages deployment
- **File Handling:** Serves `.htm`, `.html`, `.jpg`, `.css`, and other static files
- **Index Files:** Automatically serves `index.html` for directory requests
- **Encoding:** Handles UTF-8 encoding for genealogy content

## Stopping the Server

Press `Ctrl+C` to stop the server.

---

**Created:** 2025-09-22
**Purpose:** Local testing of genealogy site modernization
**Project:** AuntieRuth.com GitHub Pages Migration