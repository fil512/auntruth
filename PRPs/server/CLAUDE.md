# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the server component of the AuntieRuth.com genealogy site modernization project. It's a simple Python HTTP server designed to locally test the genealogy site before deploying to GitHub Pages.

## Development Commands

### Installation
```bash
pip3 install -r requirements.txt
```

### Starting the Development Server
```bash
# Default port (8000)
python3 genealogy_server.py

# Custom port
python3 genealogy_server.py --port 8080
```

### Testing URLs
- **Main site:** http://localhost:8000/auntruth/
- **Direct docs access:** http://localhost:8000/
- **Index page:** http://localhost:8000/auntruth/index.html

## Architecture

### Core Components
- **genealogy_server.py**: Main server script using Flask web framework
- **Flask Routes**: Two main route handlers:
  - `/auntruth/` routes that serve content from `../../docs/` directory
  - Root `/` routes for direct docs access
  - Both provide CORS headers for local development
  - Security checks to prevent directory traversal
  - Automatic `.htm`/`.html` file extension handling

### Path Mapping Strategy
The server translates URLs to simulate the GitHub Pages deployment:
- `/auntruth/` → serves from `../../docs/` directory
- Root `/` → serves docs index directly
- Handles both `.htm` and `.html` files for genealogy content

### Directory Structure Context
This server expects to be run from `PRPs/server/` and serves content from `docs/` (two levels up). The genealogy content includes:
- HTML files in various lineage directories (L0-L9)
- Images and CSS resources
- Index pages for navigation

## Important Notes

- **Dependencies**: Uses Flask web framework (install via `pip3 install -r requirements.txt`)
- **Security**: Built-in path traversal protection to keep serving within the docs directory
- **Encoding**: Handles UTF-8 encoding for genealogy content with international characters
- **Signal Handling**: Flask provides robust signal handling and graceful shutdown with Ctrl+C
- **File Extensions**: Automatically handles both `.htm` and `.html` extensions for genealogy files

## Python Script Execution
- Execute Python scripts as arguments to `python3` (never chmod them)
- The server script is executable but should be run as `python3 genealogy_server.py`