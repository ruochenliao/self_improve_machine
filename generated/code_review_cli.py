#!/usr/bin/env python3
import sys
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/code-review'

def main():
    if len(sys.argv) != 2:
        print('Usage: code-review.py <file_path>')
        return
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    response = requests.post(API_URL, json={'code': code})
    print(response.json()['review'])

if __name__ == '__main__':
    main()