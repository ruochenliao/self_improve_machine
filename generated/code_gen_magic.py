#!/usr/bin/env python3
"""
⚡ CODE GEN MAGIC
Type a problem description and get Python code instantly via Stark-Vortex API

Example: 
$ python code_gen_magic.py "Create a function to plot a pie chart with matplotlib"
"""
import sys
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'

if len(sys.argv) < 2:
    print("Usage: $ python code_gen_magic.py 'Your problem description'")
    sys.exit(1)

def generate_code(description):
    response = requests.post(API_URL, json={'query': description})
    return response.json().get('code', 'Error generating code')

if __name__ == '__main__':
    print("\nGenerated code:\n")
    print(generate_code(sys.argv[1]))
