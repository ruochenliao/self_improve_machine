#!/usr/bin/env python
import requests, sys
API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/fix-bug'

def fix_code(code):
    response = requests.post(API_URL, json={'code': code}).json()
    return response['fixed_code']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python fix_bug_cli.py "your code here"')
    else:
        fixed = fix_code(sys.argv[1])
        print('\n--- Fixed Code ---\n')
        print(fixed)