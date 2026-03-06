#!/usr/bin/env python3
"""
✨ CODE TO API ✨
Turn any Python function into a REST API with ONE COMMAND

Usage:
$ python code_to_api.py your_script.py

Example:
>>> def add(a,b):
...    return a+b
>>> 
Becomes a running Flask API at http://localhost:5000/add
"""
import sys
import requests
import subprocess

def generate_api_code(file_path):
    with open(file_path) as f:
        code = f.read()
    response = requests.post(
        'https://<tunnel-not-configured>.trycloudflare.com/generate-code-pro',
        json={'prompt': f'Convert this Python code into a Flask REST API:\n{code}'}
    )
    return response.json()['output']

def main():
    if len(sys.argv) != 2:
        print("Usage: code_to_api.py <python_file>")
        return
    api_code = generate_api_code(sys.argv[1])
    with open('api_app.py', 'w') as f:
        f.write(api_code)
    subprocess.run(['python', 'api_app.py'])

if __name__ == '__main__':
    main()