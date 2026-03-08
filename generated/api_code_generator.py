#!/usr/bin/env python3
"""
Simple CLI tool to generate code using Silent-Nexus API
Usage: ./api_code_generator.py 'Write a Python script that downloads files from URLs'
"""
import sys
import requests
import json

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'

if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} "<prompt>"')
    sys.exit(1)

response = requests.post(API_URL, json={"prompt": sys.argv[1]})
print(response.json().get('code', 'Error generating code'))
