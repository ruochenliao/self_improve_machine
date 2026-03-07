#!/usr/bin/env python
import requests
import sys
API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/v1/format-code'

def main():
    code = sys.stdin.read()
    response = requests.post(API_URL, json={'code': code})
    print(response.json()['formatted_code'])

if __name__ == '__main__':
    main()