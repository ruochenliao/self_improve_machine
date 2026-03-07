#!/usr/bin/env python3
import requests
import sys

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/chat'

if __name__ == '__main__':
    query = ' '.join(sys.argv[1:])
    response = requests.post(API_URL, json={'query': query}).json()
    print(response['answer'])