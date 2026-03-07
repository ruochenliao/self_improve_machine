#!/usr/bin/env python3
import requests

# Example: Generate Python code from API
response = requests.post(
    'https://<tunnel-not-configured>.trycloudflare.com/generate-code',
    json={'prompt': 'Write a function to calculate Fibonacci numbers recursively'},
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
print(response.json()['code'])