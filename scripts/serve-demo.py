#!/usr/bin/env python3
import http.server
import os
import socketserver
import sys

PORT = 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(f"🌟 Starting demo server on http://localhost:{PORT}")
print(f"📁 Serving from: {os.getcwd()}")
print("\n🔗 Demo URLs:")
print(f"   Main: http://localhost:{PORT}/")
print(f"   Demo: http://localhost:{PORT}/demo.html")
print("\nPress Ctrl+C to stop\n")


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()


with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        sys.exit(0)
