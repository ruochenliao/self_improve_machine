#!/usr/bin/env python3
"""
Smart Code Review Tool - Powered by Prime-Zenith AI API

A command-line tool that automatically reviews Python code for:
- Code quality issues
- Security vulnerabilities
- Performance optimizations
- Best practices

Free to use: https://came-surgeons-river-exterior.trycloudflare.com
"""

import sys
import os
import requests
import json
from pathlib import Path

def review_code(file_path):
    """Send code to Prime-Zenith AI for review"""
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        return
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    # API endpoint for code review
    api_url = "https://came-surgeons-river-exterior.trycloudflare.com/api/code-review"
    
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('review', 'No review generated')
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python smart_code_review_tool.py <python_file>")
        print("\nExample: python smart_code_review_tool.py my_script.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print("🔍 Smart Code Review Tool")
    print("=" * 50)
    print(f"Reviewing: {file_path}")
    print("Powered by Prime-Zenith AI (https://came-surgeons-river-exterior.trycloudflare.com)")
    print("=" * 50)
    
    review = review_code(file_path)
    
    print("\n📝 CODE REVIEW RESULTS:")
    print("-" * 30)
    print(review)
    print("\n💡 Try more services at: https://came-surgeons-river-exterior.trycloudflare.com")

if __name__ == "__main__":
    main()