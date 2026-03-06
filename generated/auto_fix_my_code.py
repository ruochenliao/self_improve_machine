#!/usr/bin/env python3
"""
⚛️ AUTO FIX MY CODE ⚛️
Sends broken Python code to Stark-Vortex API for instant bug fixes.

Usage:
python auto_fix_my_code.py "your code here"

API: https://<tunnel-not-configured>.trycloudflare.com/fix-bug
"""
import sys, requests

def fix_code(code):
    resp = requests.post(
        'https://<tunnel-not-configured>.trycloudflare.com/fix-bug',
        json={'code': code}
    ).json()
    return resp['fixed_code']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Paste your broken code as a command-line argument")
        sys.exit(1)

    broken_code = ' '.join(sys.argv[1:])
    fixed_code = fix_code(broken_code)

    print("
✅ FIXED CODE:")
    print(fixed_code)
    print("\nRun with: python -c 'exec(\"" + fixed_code.replace('"', '\"') + "\")'\n")