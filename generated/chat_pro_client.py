#!/usr/bin/env python3
"""
Chat-PRO API Client Example

Usage:
python chat_pro_client.py "Your question here"

Requires API key from https://<tunnel-not-configured>.trycloudflare.com
"""
import sys
import requests

url = 'https://<tunnel-not-configured>.trycloudflare.com/chat-pro'

def main():
    if len(sys.argv) < 2:
        print("Usage: python $0 'Your question'")
        sys.exit(1)

    question = ' '.join(sys.argv[1:])
    response = requests.post(url, json={'query': question}).json()
    print(f"\nAnswer:\n{response['answer']}\n")

if __name__ == '__main__':
    main()