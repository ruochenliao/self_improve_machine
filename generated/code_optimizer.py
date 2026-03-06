#!/usr/bin/env python3
"""
⚒ CODE OPTIMIZER 
Automatically improve Python code using AI
Usage: python code_optimizer.py your_script.py
"""
import sys
import requests

API_URL = 'https://<YOUR_PUBLIC_URL>/code-review'

if len(sys.argv)!=2:
    exit('Usage: code_optimizer.py [file]')

with open(sys.argv[1]) as f:
    code = f.read()

response = requests.post(API_URL, json={'code': code}).json()

print('\n'.join(response['suggestions']))

confirm = input('\nApply suggested changes? (y/N) ')
if confirm.lower() == 'y':
    with open(sys.argv[1], 'w') as f:
        f.write(response['optimized_code'])
    print(f'\n✅ {sys.argv[1]} optimized!')