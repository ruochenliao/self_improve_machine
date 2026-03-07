#!/usr/bin/env python3
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com'

# Example: Generate Python code using the API
response = requests.post(f'{API_URL}/generate-code-pro', json={'query': 'Write a script to calculate Fibonacci numbers recursively'})
print(response.json()['code'])