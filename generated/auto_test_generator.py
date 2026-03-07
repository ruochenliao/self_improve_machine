#!/usr/bin/env python3
"""
⚙️ AutoTest Generator
Uses the /write-tests API to generate and run tests for Python functions.

Usage:
$ curl -s http://YOUR_URL/write-tests-pro -d '{"code": open("my_script.py").read()}'
"""
import requests
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: {} <source_file.py>").format(sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    response = requests.post(
        'http://localhost:8402/write-tests-pro',
        json={'code': code},
        headers={'Authorization': 'Bearer YOUR_API_KEY'}
    )

    print(response.json().get('tests', 'Error generating tests'))

if __name__ == '__main__':
    main()