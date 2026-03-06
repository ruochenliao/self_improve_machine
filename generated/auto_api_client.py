#!/usr/bin/env python3
"""
⚖ AUTO-API-GEN
Generate Python API client from OpenAPI spec in 1 line

Usage:
$ python auto_api_client.py petstore.yaml

Requires: pip install pyyaml requests
"""
import sys
import yaml
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python $0 <openapi.yaml>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        spec = yaml.safe_load(f.read())

    response = requests.post(API_URL, json={
        'prompt': f'Generate Python client for this OpenAPI spec: {spec}',
        'model': 'claude-sonnet-4-20250514'
    })

    print("Generated client:")
    print(response.json()['code'])