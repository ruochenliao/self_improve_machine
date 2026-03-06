#!/usr/bin/env python3
"""
✨ Code Wizard ✨
Generate & Perfect Code Automatically
Uses Stark-Vortex APIs to:
1. Generate code
2. Auto-review
3. Optimize
4. Format
Public API: https://<tunnel-not-configured>.trycloudflare.com
"""
import requests
import sys

def generate_code(problem):
    return requests.post(f'{API_URL}/generate-code', json={'query': problem}).json()['code']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: code_wizard.py 'Write a Python script to...'")
        sys.exit(1)
    problem = ' '.join(sys.argv[1:])
    print("\nGenerating...\n-----------")
    print(generate_code(problem))