#!/usr/bin/env python3
import sys
import requests

API_URL = 'YOUR_PUBLIC_URL_PLACEHOLDER/chat'

if __name__ == '__main__':
    query = ' '.join(sys.argv[1:])
    response = requests.post(API_URL, json={'query': query}).json()
    print(f"AI: {response['answer']}")

# Replace YOUR_PUBLIC_URL_PLACEHOLDER with actual endpoint from /tmp/tunnel_url.txt