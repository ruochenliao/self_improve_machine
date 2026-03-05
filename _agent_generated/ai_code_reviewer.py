#!/usr/bin/env python3
"""
AI Code Reviewer - A simple script that uses Prime-Zenith's API to review code files

This script demonstrates the power of AI-powered code review using the Prime-Zenith API.
It can review any Python file and provide intelligent feedback on code quality,
best practices, potential bugs, and improvements.

API Service: https://came-surgeons-river-exterior.trycloudflare.com
"""

import requests
import sys
import os

def review_code(file_path):
    """Review a code file using Prime-Zenith's code review API"""
    
    # Read the file content
    try:
        with open(file_path, 'r') as f:
            code_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Prepare the API request
    api_url = "https://came-surgeons-river-exterior.trycloudflare.com/api/code-review"
    
    payload = {
        "code": code_content,
        "language": "python",
        "filename": os.path.basename(file_path)
    }
    
    try:
        print(f"🔍 Reviewing {file_path}...")
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print(f"📝 CODE REVIEW REPORT for {file_path}")
            print("="*60)
            print(f"\n{result.get('review', 'No review available')}")
            print("\n" + "="*60)
            print("💡 Try more AI services at: https://came-surgeons-river-exterior.trycloudflare.com")
            print("="*60)
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error calling API: {e}")
        print("\n💡 Make sure the API server is running at:")
        print("https://came-surgeons-river-exterior.trycloudflare.com")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ai_code_reviewer.py <path_to_python_file>")
        print("\nExample: python ai_code_reviewer.py my_script.py")
        sys.exit(1)
    
    file_to_review = sys.argv[1]
    
    if not file_to_review.endswith('.py'):
        print("⚠️  Warning: This script works best with Python files (.py)")
        
    review_code(file_to_review)