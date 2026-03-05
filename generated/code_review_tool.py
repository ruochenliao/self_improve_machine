#!/usr/bin/env python3

"""
Bold-Phoenix Code Review Tool

A command-line tool that uses the Bold-Phoenix API to review your code files.
Get instant AI-powered code reviews for any Python file.

Usage: python code_review_tool.py <filename.py>

Your API is available at: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import sys
import os

# Bold-Phoenix API endpoint
API_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com/api/code-review"

def review_code(file_path):
    """Send code to Bold-Phoenix API for review"""
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        return
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    print(f"Reviewing {file_path}...")
    
    # Prepare the request
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("BOLD-PHOENIX CODE REVIEW")
            print("="*60)
            print(f"File: {file_path}")
            print("-"*60)
            print(result.get('review', 'No review provided'))
            print("="*60)
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Bold-Phoenix API: {e}")
        print("Make sure you're connected to the internet and the API is available.")

def main():
    if len(sys.argv) != 2:
        print("Bold-Phoenix Code Review Tool")
        print("Usage: python code_review_tool.py <filename.py>")
        print("\nExample: python code_review_tool.py my_script.py")
        print("\nGet instant AI-powered code reviews!")
        print("API: https://upgrades-approx-gadgets-hit.trycloudflare.com")
        return
    
    file_path = sys.argv[1]
    
    if not file_path.endswith('.py'):
        print("Warning: This tool works best with Python files (.py)")
        print("You can still try reviewing other file types.")
        
    review_code(file_path)

if __name__ == "__main__":
    main()