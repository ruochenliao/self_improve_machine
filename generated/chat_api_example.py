#!/usr/bin/env python
import requests

# Example usage of Bold-Helix Chat API
API_URL = 'https://your-public-url-here/chat'

response = requests.post(API_URL, json={'query': 'How do quantum computers work?'})
print(response.json()['answer'])