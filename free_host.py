"""
Free Asset Server for Autogram (free_host.py).
Serves rendered slide images from output/ over HTTP so Meta Instagram API can fetch them for $0.00.
Supports zero-cost public exposure via localtunnel, cloudflared, or ngrok.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 8000
DIRECTORY = str(Path(__file__).parent / "output")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def translate_path(self, path):
        # Normalize: if request starts with /output/, strip it so it maps to DIRECTORY directly
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        if clean_path.startswith('/output/'):
            clean_path = clean_path[len('/output'):]
        elif clean_path == '/output':
            clean_path = '/'
        
        # Now let standard implementation resolve within DIRECTORY
        orig_path = self.path
        self.path = clean_path
        translated = super().translate_path(clean_path)
        self.path = orig_path
        return translated

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"healthy","service":"autogram-free-host"}')
            return
        super().do_GET()

    def end_headers(self):
        # Enable CORS and caching headers for public Meta fetchers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'public, max-age=86400')
        super().end_headers()

def main():
    os.makedirs(DIRECTORY, exist_ok=True)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("==================================================")
        print(f" Autogram Free Asset Server running on Port {PORT}")
        print("==================================================")
        print(f" Serving directory: {DIRECTORY}")
        print(f" Local URL: http://localhost:{PORT}")
        print("\n To get a 100% FREE Public HTTPS URL for Instagram:")
        print(f" Run in a separate terminal:  npx localtunnel --port {PORT}")
        print(" Or:                          cloudflared tunnel --url http://localhost:8000")
        print("\n Then set PUBLIC_CDN_BASE in your .env file to that URL.")
        print(" Cost: $0.00 (Zero hosting fees)")
        print("==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
