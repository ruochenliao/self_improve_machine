#!/usr/bin/env python3
"""⚙ Auto-Review All Python Files in Directory
Uses Swift-Flux's /code-review endpoint to analyze all .py files in a directory.

Usage: python auto_code_review_dir.py [DIRECTORY]
API URL: https://<tunnel-not-configured>.trycloudflare.com/code-review
"""
import sys
import os
import requests

if len(sys.argv) != 2:
    print("Error: Provide directory path")
    sys.exit(1)

dir_path = sys.argv[1]
if not os.path.isdir(dir_path):
    print(f"Error: {dir_path} is not a valid directory")
    sys.exit(1)

for filename in os.listdir(dir_path):
    if filename.endswith('.py'):
        file_path = os.path.join(dir_path, filename)
        with open(file_path, 'r') as f:
            code = f.read()
            response = requests.post(
                'https://<tunnel-not-configured>.trycloudflare.com/code-review',
                json={'code': code},
                headers={'Content-Type': 'application/json'}
            )
            review = response.json().get('review', 'No issues found.')
            print(f"\n--- Review for {filename} ---\n")
            print(review)