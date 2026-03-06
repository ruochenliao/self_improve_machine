#!/usr/bin/env python3
"""
✍️ AutoDocstr ✍️
Automatically generate docstrings for your Python code using AI

Usage: python auto_docstr.py your_script.py
API: https://<tunnel-not-configured>.trycloudflare.com
"""
import sys
import requests

def generate_docstrings(code):
    response = requests.post(
        'https://<tunnel-not-configured>.trycloudflare.com/explain-code',
        json={'code': code}
    ).json()
    return response['docstring']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python {} filename.py'.format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    new_code = generate_docstrings(code)

    with open(sys.argv[1] + '.with-docs.py', 'w') as f:
        f.write(new_code)

    print('Saved to: {}.with-docs.py'.format(sys.argv[1]))