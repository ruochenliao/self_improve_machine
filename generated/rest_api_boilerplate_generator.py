#!/usr/bin/env python3
"""
CLI tool to generate REST API boilerplate code using Swift-Flux AI

Usage:
$ python rest_api_boilerplate_generator.py 'User model with name/email' > app.py
"""
import requests
import sys

endpoint = 'https://<your-public-url>/generate-code'
def main():
    if len(sys.argv) < 2:
        print("Error: Provide API description")
        sys.exit(1)
    prompt = f'Write Flask REST API for: {sys.argv[1]}'
    response = requests.post(endpoint, json={'prompt': prompt})
    print(response.json()['code'])

if __name__ == '__main__':
    main()