#!/usr/bin/env python3
"""
Simple web server for testing genealogy site locally.
Serves /home/ken/wip/fam/auntruth/docs/ at localhost:8000/auntruth/

This allows testing the modernized genealogy site before deploying to GitHub Pages.
"""

import http.server
import socketserver
import os
import sys
import signal
from urllib.parse import unquote
from pathlib import Path

class GenealogyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve docs/ content at /auntruth/ path"""

    def __init__(self, *args, **kwargs):
        # Set the document root to the docs directory
        self.docs_path = Path('/home/ken/wip/fam/auntruth/docs').resolve()
        super().__init__(*args, directory=str(self.docs_path), **kwargs)

    def translate_path(self, path):
        """Translate URL path to filesystem path"""
        # Remove query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = unquote(path)

        # Handle /auntruth/ prefix
        if path.startswith('/auntruth/'):
            # Remove /auntruth/ prefix and serve from docs/
            path = path[9:]  # Remove '/auntruth'
        elif path == '/auntruth':
            # Redirect /auntruth to /auntruth/
            path = '/'
        elif path == '/':
            # Root should show the docs index
            path = '/'

        # Convert to filesystem path
        if path.startswith('/'):
            path = path[1:]

        # Resolve the final path
        final_path = self.docs_path / path

        # Security check - ensure we stay within docs directory
        try:
            final_path = final_path.resolve()
            if not str(final_path).startswith(str(self.docs_path)):
                return str(self.docs_path / 'index.html')
        except:
            return str(self.docs_path / 'index.html')

        return str(final_path)

    def end_headers(self):
        """Add CORS headers for local development"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.date_time_string()}] {format % args}")

def start_server(port=8000):
    """Start the genealogy development server"""

    # Check if docs directory exists
    docs_path = Path('/home/ken/wip/fam/auntruth/docs')
    if not docs_path.exists():
        print(f"Error: docs directory not found at {docs_path}")
        sys.exit(1)

    print(f"Starting genealogy development server...")
    print(f"Serving: {docs_path}")
    print(f"URL: http://localhost:{port}/auntruth/")
    print(f"Direct docs access: http://localhost:{port}/")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        httpd = socketserver.TCPServer(("", port), GenealogyHTTPRequestHandler)
        httpd.allow_reuse_address = True

        def signal_handler(signum, frame):
            print("\nShutting down server...")
            httpd.shutdown()
            httpd.server_close()
            sys.exit(0)

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {port} is already in use.")
            print("Try a different port or stop the existing server.")
        else:
            print(f"Error starting server: {e}")
        sys.exit(1)
    finally:
        if 'httpd' in locals():
            httpd.server_close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Genealogy site development server')
    parser.add_argument('--port', '-p', type=int, default=8000,
                       help='Port to serve on (default: 8000)')

    args = parser.parse_args()
    start_server(args.port)