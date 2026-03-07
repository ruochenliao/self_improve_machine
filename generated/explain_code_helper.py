#!/usr/bin/env python3
"""
CLI tool to explain code via /explain-code API
Usage: ./explain_code_helper.py 'your_code_here'
"""
import sys, requests

def main():
    if len(sys.argv)!=2:
        print('Error: Provide code as argument')
        return
    code = sys.argv[1]
    response = requests.post('https://<tunnel-not-configured>.trycloudflare.com/api/explain-code', json={'code': code})
    print(response.json().get('explanation', 'Error'))

if __name__ == '__main__':
    main()