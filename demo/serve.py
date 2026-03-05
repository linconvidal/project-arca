"""
Local dev server for the Arca demo.
Serves from the project root so /demo/ and /arca/ paths work.

Usage: python demo/serve.py
"""
import http.server
import os

PORT = 8090

# Serve from project root (parent of demo/)
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching during development
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()


print(f'Serving at http://localhost:{PORT}/demo/index.html')
http.server.HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
