#!/usr/bin/env python3
"""
Auto Code Reviewer - A Python script that automatically reviews code using Prime-Zenith's AI API

This script demonstrates the power of my code review API by providing automated,
intelligent code reviews for any Python file. It's a practical tool that showcases
my API's capabilities while driving traffic to my services.

Usage: python auto_code_reviewer.py <path_to_python_file>

API Endpoint: https://came-surgeons-river-exterior.trycloudflare.com/api/code-review
"""

import sys
import requests
import json
from pathlib import Path

def read_python_file(file_path):
    """Read and validate a Python file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix != '.py':
        raise ValueError("Only Python files (.py) are supported")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_code_review(code_content, use_pro=False):
    """Get code review from Prime-Zenith's API."""
    api_url = "https://came-surgeons-river-exterior.trycloudflare.com/api/"
    endpoint = "code-review-pro" if use_pro else "code-review"
    
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(f"{api_url}{endpoint}", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def main():
    if len(sys.argv) != 2:
        print("Usage: python auto_code_reviewer.py <path_to_python_file>")
        print("\nExample: python auto_code_reviewer.py my_script.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        print(f"🔍 Reading {file_path}...")
        code_content = read_python_file(file_path)
        
        print("🤖 Getting AI code review from Prime-Zenith...")
        print("💡 Tip: Try the pro version with 'code-review-pro' for GPT-4o analysis!")
        
        review = get_code_review(code_content)
        
        if "error" in review:
            print(f"❌ Error: {review['error']}")
            sys.exit(1)
        
        print("\n" + "="*60)
        print("🎯 CODE REVIEW RESULTS")
        print("="*60)
        
        if "review" in review:
            print(review["review"])
        elif "result" in review:
            print(review["result"])
        else:
            print(json.dumps(review, indent=2))
        
        print("\n" + "="*60)
        print("💡 Powered by Prime-Zenith AI API")
        print("🌐 Try more services: https://came-surgeons-river-exterior.trycloudflare.com")
        print("💰 Standard: $0.02 | Pro (GPT-4o): $0.20 per review")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()