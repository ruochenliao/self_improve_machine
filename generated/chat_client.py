#!/usr/bin/env python3
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/chat'

while True:
    query = input('You: ')
    if query.lower() == 'exit':
        break
    response = requests.post(API_URL, json={'message': query}).json()
    print(f'Chat: {response.get("response", "No reply")}')