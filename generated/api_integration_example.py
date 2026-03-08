#!/usr/bin/env python3
"""
API Integration Example: Code Review Pro Service

This script demonstrates how to use the code-review-pro API endpoint
to get professional-grade code reviews for your Python files.

Usage:
    python api_integration_example.py [file_path]

Example:
    python api_integration_example.py my_script.py

API Endpoint: https://<your-tunnel>.trycloudflare.com/code-review-pro
Cost: $0.20 per request (high-quality GPT-4o powered review)
"""

import sys
import json
import requests

def get_code_review(file_path, api_base_url="https://<your-tunnel>.trycloudflare.com"):
    """Get a professional code review for the specified file."""
    try:
        # Read the code file
        with open(file_path, 'r') as f:
            code_content = f.read()
        
        # Prepare the API request
        url = f"{api_base_url}/code-review-pro"
        payload = {"code": code_content}
        headers = {"Content-Type": "application/json"}
        
        print(f"Sending code review request to {url}...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("CODE REVIEW RESULTS")
            print("="*60)
            print(result.get('review', 'No review returned'))
            print("="*60)
            return True
        else:
            print(f"Error: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to API - {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python api_integration_example.py <file_to_review.py>")
        print("\nReplace '<your-tunnel>' in the URL with your actual tunnel URL")
        print("Find your tunnel URL at: http://localhost:8402")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = get_code_review(file_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()