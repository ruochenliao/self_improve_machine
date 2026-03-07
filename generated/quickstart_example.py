#!/usr/bin/env python3
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com'

# Example: Generate a Python function from a description
response = requests.post(
    f'{API_URL}/generate-code',
    json={"query": "Write a function to calculate Fibonacci sequence up to n"}
)
print(response.json()['code'])