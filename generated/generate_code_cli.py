#!/usr/bin/env python
import requests
import sys

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/v1/generate-code'

if len(sys.argv) < 2:
    print('Usage: python generate_code_cli.py "Write a Python script to..."')
    sys.exit(1)

prompt = ' '.join(sys.argv[1:])
response = requests.post(API_URL, json={'prompt': prompt})
print(response.json().get('code', 'Error'))