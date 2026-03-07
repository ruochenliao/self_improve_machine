#!/usr/bin/env python3
import requests
import sys

def review_code(code):
    response = requests.post('https://<tunnel-not-configured>.trycloudflare.com/code-review', json={'code': code})
    return response.json()['suggestions']

if __name__ == '__main__':
    code = sys.stdin.read()
    print(review_code(code))