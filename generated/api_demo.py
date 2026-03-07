#!/usr/bin/env python3
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com'

# Example: Get chat response
response = requests.post(f'{API_URL}/chat', json={'query': 'Explain quantum computing'}).json()
print('Chat:', response['answer'])

# Example: Code review
review = requests.post(f'{API_URL}/code-review-pro', files={'file': open('my_script.py', 'rb')}).json()
print('Code review:', review['suggestions'])