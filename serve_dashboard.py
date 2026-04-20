#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard.html file.
This eliminates CORS issues when accessing the metrics API.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8080
DASHBOARD_FILE = "dashboard.html"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        # Some browsers/extensions probe service worker and favicon automatically.
        if self.path in ("/sw.js", "/service-worker.js"):
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(
                b"self.addEventListener('install', () => self.skipWaiting());"
                b"self.addEventListener('activate', () => self.clients.claim());"
            )
            return

        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        super().do_GET()

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def main():
    # Check if dashboard file exists
    if not Path(DASHBOARD_FILE).exists():
        print(f"Error: {DASHBOARD_FILE} not found in current directory")
        return
    
    # Start HTTP server
    with ReusableTCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Dashboard server running at: http://localhost:{PORT}")
        print(f"Dashboard URL: http://localhost:{PORT}/{DASHBOARD_FILE}")
        print("Press Ctrl+C to stop the server")
        
        # Optionally open browser
        try:
            webbrowser.open(f"http://localhost:{PORT}/{DASHBOARD_FILE}")
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down dashboard server...")

if __name__ == "__main__":
    main()