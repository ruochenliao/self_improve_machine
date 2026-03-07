#!/usr/bin/env python3
# Auto-generated CLI tool to create code snippets via Silent-Nexus API
import requests
import sys

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} "What to generate"')
        sys.exit(1)
    prompt = ' '.join(sys.argv[1:])
    response = requests.post(API_URL, json={'query': prompt})
    print(response.json()['code'])