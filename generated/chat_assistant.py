#!/usr/bin/env python3
"""
Chat Assistant CLI - Interact with Bold-Helix's chat API

Usage:
$ python chat_assistant.py "What's Pythonic way to loop?"
"""
import sys, requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/chat'

if __name__ == '__main__':
    query = ' '.join(sys.argv[1:])
    response = requests.post(API_URL, json={'query': query}).json()
    print(f'\n💬 Bold-Helix:', response['answer'])
    print('\n💡 Tips:', response['suggestions'])
