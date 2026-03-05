#!/usr/bin/env python3

"""
Bold-Phoenix Code Review CLI Tool

A command-line tool that uses the Bold-Phoenix API to review code files.
Provides instant AI-powered code reviews for any programming language.

Usage: python code_review_cli.py <file_path> [--pro]

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import argparse
import requests
import sys
import os

API_BASE = "https://upgrades-approx-gadgets-hit.trycloudflare.com"

def get_code_review(code_content, use_pro=False):
    """Get code review from Bold-Phoenix API"""
    endpoint = "/code-review-pro" if use_pro else "/code-review"
    url = f"{API_BASE}{endpoint}"
    
    payload = {
        "code": code_content,
        "language": "auto"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["review"]
    except Exception as e:
        return f"Error getting code review: {e}"

def main():
    parser = argparse.ArgumentParser(description="Bold-Phoenix Code Review CLI")
    parser.add_argument("file_path", help="Path to the code file to review")
    parser.add_argument("--pro", action="store_true", help="Use GPT-4o Pro service")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: File '{args.file_path}' not found")
        sys.exit(1)
    
    try:
        with open(args.file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"🔍 Reviewing {args.file_path} with Bold-Phoenix {'Pro' if args.pro else 'Standard'} API...")
    print("-" * 60)
    
    review = get_code_review(code_content, args.pro)
    
    print(review)
    print("-" * 60)
    print(f"✅ Review complete! Powered by Bold-Phoenix AI")
    print(f"🌐 API: {API_BASE}")

if __name__ == "__main__":
    main()