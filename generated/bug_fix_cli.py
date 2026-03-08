#!/usr/bin/env python3
"""
Bug Fix CLI - Fix code bugs using Silent-Nexus API
Usage: python bug_fix_cli.py <file_with_bug.py>

Requires your code file to be passed as argument.
Uses the fix-bug-pro endpoint ($0.30/request) for best results.

API: https://silent-nexus.trycloudflare.com
"""
import sys
import requests
import json

def fix_bug(code_content):
    url = "https://silent-nexus.trycloudflare.com/fix-bug-pro"
    payload = {"code": code_content}
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bug_fix_cli.py <file_with_bug.py>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    
    print("Fixing bug...")
    result = fix_bug(code)
    print(result.get('fixed_code', result))