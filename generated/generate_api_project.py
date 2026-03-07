#!/usr/bin/env python3
# Auto-generated CLI tool to scaffold FastAPI projects using Silent-Nexus API
import requests
import sys
import json

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'

if len(sys.argv) < 2:
    print('Usage: ./generate_api_project.py "Project description"')
    sys.exit(1)

description = sys.argv[1]
response = requests.post(API_URL, json={"prompt": description})

if response.status_code == 200:
    code = response.json()['code']
    with open('app.py', 'w') as f:
        f.write(code)
    print(f'Generated app.py with {len(code)} characters')
else:
    print('Error:', response.text)