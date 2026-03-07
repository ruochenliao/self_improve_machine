#!/usr/bin/env python3
"""
CLI tool to generate code using Swift-Flux API

Usage:
$ python code_generator.py 'write a function to calculate factorial'
"""
import sys, requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'

if len(sys.argv) < 2:
    print('Error: Provide a prompt')
    sys.exit(1)

response = requests.post(API_URL, json={'prompt': sys.argv[1]})
print(response.json()['code'])