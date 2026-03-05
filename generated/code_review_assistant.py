#!/usr/bin/env python3

"""
Keen-Vortex: Code Review Assistant
This script provides automated code review for Python files using the Keen-Vortex API.
It analyzes code quality, identifies bugs, suggests improvements, and provides detailed feedback.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import sys
import os
from pathlib import Path

def main():
    """Main function to handle command line interface."""
    if len(sys.argv) != 2:
        print("Usage: python code_review_assistant.py <python_file>")
        print("Example: python code_review_assistant.py my_script.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    if not file_path.endswith('.py'):
        print("Warning: This tool is optimized for Python files")
    
    # Read the file content
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    print(f"🔍 Analyzing {file_path}...")
    print("-" * 50)
    
    # Use the code-review API endpoint
    api_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/api/code-review"
    
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CODE REVIEW RESULTS")
            print("=" * 50)
            print(result.get('review', 'No review provided'))
            
            # Show cost information
            cost = result.get('cost', 0)
            print(f"\n💡 Cost: ${cost:.4f}")
            
        elif response.status_code == 402:
            print("❌ Payment required. Please visit the playground to test this service.")
            print("Free playground: https://charlotte-fifty-rrp-induced.trycloudflare.com")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()