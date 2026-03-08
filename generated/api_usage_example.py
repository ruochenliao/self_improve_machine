#!/usr/bin/env python3
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com'

# Example: Generate code
response = requests.post(f'{API_URL}/generate-code-pro', json={'prompt': 'Create a Python script to calculate Fibonacci numbers recursively'})
print(response.json()['code'])