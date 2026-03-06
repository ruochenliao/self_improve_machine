#!/usr/bin/env python3
"""
⚛ AI Code Workflow Automator ⚛
Generate, Review & Test Code in One Command
Usage: python code_workflow_magic.py 'Function description'
Example: python code_workflow_magic.py 'A function to find prime factors of a number'
"""
import sys
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python $0 'Function description'")
        exit(1)

    desc = sys.argv[1]

    # 1. Generate code
    resp = requests.post(f'{API_URL}/generate-code', json={'prompt': desc}).json()
    code = resp['code']
    
    # 2. Auto-review
    review = requests.post(f'{API_URL}/code-review', json={'code': code}).json()['feedback']
    
    # 3. Generate tests
    tests = requests.post(f'{API_URL}/write-tests', json={'code': code}).json()['tests']
    
    print('\n\033[1mGenerated Code:\033[0m\n')
    print(code)
    print('\n\033[1mReview Feedback:\033[0m\n', review)
    print('\n\033[1mTest Cases:\033[0m\n', tests)
