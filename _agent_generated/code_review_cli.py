#!/usr/bin/env python3
"""
Lucid-Helix Code Review CLI
Uses the Lucid-Helix AI API for intelligent code review
API URL: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import argparse
import sys
import os

API_BASE = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def review_code(code_content, pro_version=False):
    """Send code to Lucid-Helix API for review"""
    endpoint = "/api/code-review-pro" if pro_version else "/api/code-review"
    url = API_BASE + endpoint
    
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def main():
    parser = argparse.ArgumentParser(description="Lucid-Helix Code Review CLI")
    parser.add_argument("file", help="Python file to review")
    parser.add_argument("--pro", action="store_true", help="Use GPT-4o pro version ($0.20)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    with open(args.file, 'r') as f:
        code_content = f.read()
    
    print(f"🔍 Reviewing {args.file} with Lucid-Helix AI...")
    print(f"📡 API: {API_BASE}")
    print("-" * 50)
    
    result = review_code(code_content, args.pro)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    
    if "review" in result:
        print("📋 CODE REVIEW RESULTS:")
        print(result["review"])
    else:
        print("✅ Review completed!")
        print(result.get("result", "No detailed feedback available"))

if __name__ == "__main__":
    main()