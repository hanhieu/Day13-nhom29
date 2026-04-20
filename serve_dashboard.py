#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard.html file.
This eliminates CORS issues when accessing the metrics API.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8080
DASHBOARD_FILE = "dashboard.html"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

def main():
    # Check if dashboard file exists
    if not Path(DASHBOARD_FILE).exists():
        print(f"Error: {DASHBOARD_FILE} not found in current directory")
        return
    
    # Start HTTP server
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
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