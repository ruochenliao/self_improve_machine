#!/usr/bin/env python3
import requests
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: {} 'description'".format(sys.argv[0]))
        return
    api_url = 'YOUR_PUBLIC_API_URL/generate-code-pro'
    response = requests.post(api_url, json={'prompt': sys.argv[1]})
    print(response.json().get('code', 'Error'))

if __name__ == '__main__':
    main()