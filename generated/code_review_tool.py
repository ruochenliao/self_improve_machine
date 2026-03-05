#!/usr/bin/env python3

"""
Keen-Vortex Code Review Tool
Automatically review your code using the Keen-Vortex API
Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys
import os

def review_code(code: str, api_key: str = None) -> str:
    """Send code to Keen-Vortex API for review"""
    
    url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/code-review"
    
    payload = {
        "code": code,
        "language": "python"
    }
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["review"]
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main function - review code from file or stdin"""
    
    if len(sys.argv) > 1:
        # Read from file
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return
    else:
        # Read from stdin
        print("Paste your code (Ctrl+D to finish):")
        code = sys.stdin.read()
    
    if not code.strip():
        print("Error: No code provided")
        return
    
    print("\n" + "="*60)
    print("KEEN-VORTEX CODE REVIEW")
    print("="*60)
    
    # Get API key from environment or prompt
    api_key = os.getenv('KEEN_VORTEX_API_KEY')
    
    print("\nReviewing your code...")
    
    result = review_code(code, api_key)
    
    print("\n" + "-"*60)
    print("REVIEW RESULTS:")
    print("-"*60)
    print(result)
    print("\n" + "="*60)
    print("Review complete! Visit https://charlotte-fifty-rrp-induced.trycloudflare.com")
    print("for more AI-powered developer tools.")
    print("="*60)

if __name__ == "__main__":
    main()