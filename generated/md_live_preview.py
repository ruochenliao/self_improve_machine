#!/usr/bin/env python3
"""
✨ Live Markdown to HTML Preview ✨
Drag a .md file here to see real-time HTML preview powered by AI API

Usage:
  ./md_live_preview.py your_doc.md

Opens a local web server showing auto-updating HTML view
"""
import sys
import time
import http.server
from pathlib import Path
import requests

API_URL = "https://your-public-url.trycloudflare.com/summarize"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} your_file.md")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    html_content = ""

    class SimpleHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            global html_content
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())

    server = http.server.HTTPServer(('localhost', 8000), SimpleHandler)
    print(f"Serving at http://localhost:8000 - Ctrl+C to exit")

    try:
        while True:
            with open(md_path, 'r') as f:
                md_text = f.read()
                response = requests.post(API_URL, json={'text': md_text}).json()
                html_content = response['summary']
            time.sleep(1)
            server.handle_request()
    except KeyboardInterrupt:
        pass