#!/usr/bin/env python3
import requests
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: ./chat_example.py "Your question here"')
        sys.exit(1)

    response = requests.post(
        'https://<tunnel-not-configured>.trycloudflare.com/chat',
        json={'query': sys.argv[1]}
    ).json()

    print('\n\n🤖 Response:\n', response['answer'])