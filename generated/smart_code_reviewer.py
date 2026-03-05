#!/usr/bin/env python3
"""
Smart Code Reviewer - A CLI tool that uses Lucid-Helix AI API to review your code
Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import argparse
import sys
from pathlib import Path

API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def review_code(code: str, language: str = "python") -> str:
    """Send code to Lucid-Helix API for review"""
    url = f"{API_BASE}/api/code-review"
    
    payload = {
        "code": code,
        "language": language
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("review", "No review received")
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Smart Code Reviewer using Lucid-Helix AI")
    parser.add_argument("file", help="Path to the code file to review")
    parser.add_argument("--language", "-l", default="python", 
                       help="Programming language (default: python)")
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    try:
        code = file_path.read_text()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"🔍 Reviewing {file_path.name} ({args.language})...")
    print("-" * 60)
    
    review = review_code(code, args.language)
    
    print("📝 CODE REVIEW RESULTS:")
    print("-" * 60)
    print(review)
    print("-" * 60)
    print(f"💡 Powered by Lucid-Helix AI: {API_BASE}")

if __name__ == "__main__":
    main()