#!/usr/bin/env python3
"""
✨ CODE MAGIC ✨
Automagically generate:
1. Code review
2. Unit tests
3. README.md
From any Python file

Usage: python code_magic.py your_script.py
"""
import sys
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: code_magic.py <python_file>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    # Get code review
    review = requests.post(f'{API_URL}/code-review', json={'code': code}).json()['review']

    # Generate tests
    tests = requests.post(f'{API_URL}/generate-tests', json={'code': code}).json()['tests']

    # Create README
    readme = requests.post(f'{API_URL}/explain-code', json={'code': code}).json()['summary']

    print(f'\n✅ CODE REVIEW:\n{review}\n\n⚙ UNIT TESTS:\n{tests}\n\n✍ README.md:\n{readme}')