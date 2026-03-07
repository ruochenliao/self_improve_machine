#!/usr/bin/env python3
import requests
import sys

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/write-tests'

def generate_tests(code):
    response = requests.post(API_URL, json={'code': code})
    return response.json()['tests']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python write_tests_cli.py [source_file.py]')
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    tests = generate_tests(code)
    print('\nGenerated tests:\n' + '='*40)    
    print(tests)
