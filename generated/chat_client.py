#!/usr/bin/env python3
import requests
import sys

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/chat'

def main():
    if len(sys.argv) < 2:
        print('Usage: python chat_client.py "Your question"')
        sys.exit(1)

    prompt = ' '.join(sys.argv[1:])
    response = requests.post(API_URL, json={'query': prompt}).json()
    print(f'AI: {response.get("answer", "Error")}')

if __name__ == '__main__':
    main()