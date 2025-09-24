#!/usr/bin/env python3
"""
Simple web server for testing genealogy site locally.
Serves the docs/ directory at localhost:8000/auntruth/

This allows testing the modernized genealogy site before deploying to GitHub Pages.
"""

import os
import sys
import signal
from pathlib import Path
from flask import Flask, send_from_directory, request, abort
from werkzeug.serving import WSGIRequestHandler

class GenealogyWSGIRequestHandler(WSGIRequestHandler):
    """Custom WSGI handler with better logging"""

    def log_request(self, code='-', size='-'):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {self.requestline} - {code}")

def create_app():
    """Create and configure the Flask application"""
    # Set the document root to the docs directory
    docs_path = Path('../../docs').resolve()

    app = Flask(__name__, static_folder=str(docs_path), static_url_path='')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

    @app.after_request
    def after_request(response):
        """Add CORS headers for local development"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response

    @app.route('/auntruth/')
    @app.route('/auntruth/<path:filename>')
    def serve_auntruth(filename=''):
        """Serve files from /auntruth/ path"""
        if filename == '' or filename.endswith('/'):
            # Handle directory requests - try index.html first, then index.htm
            base_path = filename.rstrip('/') + '/' if filename else ''
            for index_file in ['index.html', 'index.htm']:
                try:
                    return app.send_static_file(base_path + index_file)
                except:
                    continue
            abort(404)

        # Handle file requests - try as-is first, then with .htm if .html fails
        try:
            return app.send_static_file(filename)
        except:
            if filename.endswith('.html'):
                try:
                    htm_filename = filename[:-5] + '.htm'
                    return app.send_static_file(htm_filename)
                except:
                    pass
            abort(404)

    # Root path serves static files directly
    @app.route('/')
    @app.route('/<path:filename>')
    def serve_root(filename=''):
        """Serve files from root path"""
        if filename == '' or filename.endswith('/'):
            # Handle directory requests
            base_path = filename.rstrip('/') + '/' if filename else ''
            for index_file in ['index.html', 'index.htm']:
                try:
                    return app.send_static_file(base_path + index_file)
                except:
                    continue
            abort(404)

        # Handle file requests
        try:
            return app.send_static_file(filename)
        except:
            if filename.endswith('.html'):
                try:
                    htm_filename = filename[:-5] + '.htm'
                    return app.send_static_file(htm_filename)
                except:
                    pass
            abort(404)

    return app

def start_server(port=8000):
    """Start the genealogy development server"""

    # Check if docs directory exists
    docs_path = Path('../../docs')
    if not docs_path.exists():
        print(f"Error: docs directory not found at {docs_path}")
        sys.exit(1)

    print(f"Starting genealogy development server...")
    print(f"Serving: {docs_path}")
    print(f"URL: http://localhost:{port}/auntruth/")
    print(f"Direct docs access: http://localhost:{port}/")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    app = create_app()

    try:
        # Flask's built-in server handles signals much better
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            request_handler=GenealogyWSGIRequestHandler
        )
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if e.errno == 98 or "Address already in use" in str(e):
            print(f"Error: Port {port} is already in use.")
            print("Try a different port or stop the existing server.")
        else:
            print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Genealogy site development server')
    parser.add_argument('--port', '-p', type=int, default=8000,
                       help='Port to serve on (default: 8000)')

    args = parser.parse_args()
    start_server(args.port)