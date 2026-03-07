#!/usr/bin/env python3
"""
CLI tool to generate code using Swift-Flux API

Usage: python generate_code_cli.py 'Describe your code'
"""
import sys
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'

def generate_code(prompt):
    response = requests.post(API_URL, json={'query': prompt})
    return response.json().get('code', '')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python', sys.argv[0], '<prompt>')
        sys.exit(1)
    print(generate_code(sys.argv[1]))