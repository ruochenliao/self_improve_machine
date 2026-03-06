#!/usr/bin/env python3
"""
AutoFixer 🐞
Sends broken Python code to Stark-Vortex API to get automatic fixes.

Usage: python autofixer.py broken_code.py
"""
import sys
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/fix-bug'

if len(sys.argv)!=2:
    print('Error: Provide code file')
    sys.exit(1)

with open(sys.argv[1]) as f:
    code = f.read()

response = requests.post(API_URL, json={'code': code})
if response.status_code == 200:
    print('✅ FIXED:')
    print(response.json()['fixed_code'])
else:
    print(f'Error {response.status_code}: {response.text}')