#!/usr/bin/env python3
"""
Code Review CLI - Uses Bold-Helix API to review code

Usage: python code_review_cli.py <file.py>
"""
import sys
import requests

if len(sys.argv) != 2:
    print("Usage: code_review_cli.py <file>")
    sys.exit(1)

with open(sys.argv[1], 'r') as f:
    code = f.read()

response = requests.post(
    'https://<tunnel-not-configured>.trycloudflare.com/code-review',
    json={'code': code}
)

print(response.json().get('review', 'No review available'))