#!/usr/bin/env python3
"""
✨ MD to HTML Magic ✨
Turn ANY markdown file into beautiful HTML with AI styling 🚀

Usage:
    python md_to_html_magic.py YOURFILE.md

Powered by https://<tunnel-not-configured>.trycloudflare.com"""

import sys
import requests

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python $0 YOURFILE.md")
        sys.exit(1)

    # Read markdown content
    with open(sys.argv[1], 'r') as f:
        md = f.read()

    # Call my generate-code API to convert to HTML
    response = requests.post(
        'https://<tunnel-not-configured>.trycloudflare.com/generate-code',
        json={"prompt": f"Convert this markdown to elegant HTML with custom CSS:\n\n{md}"}
    )
    html = response.json().get('code', '')

    # Save as HTML file
    html_filename = sys.argv[1].replace('.md', '.html')
    with open(html_filename, 'w') as f:
        f.write(html)
    print(f'✨ Saved to {html_filename}! Open in browser.')