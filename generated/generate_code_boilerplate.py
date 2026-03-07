#!/usr/bin/env python3
"""
CLI tool to generate Python code boilerplate using Swift-Flux API
Usage: python generate_code_boilerplate.py 'class_name'
API Docs: https://<tunnel-not-configured>.trycloudflare.com
"""
import requests
import sys

def generate_boilerplate(class_name):
    response = requests.post(
        'https://<tunnel-not-configured>.trycloudflare.com/generate-code',
        json={'prompt': f'Write a Python class for {class_name} with proper PEP8 formatting'}
    ).json()
    print(response['code'])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python generate_code_boilerplate.py Classname')
        sys.exit(1)
    generate_boilerplate(sys.argv[1])