#!/usr/bin/env python3

"""
Keen-Vortex Code Review CLI Tool
A simple command-line interface to review code using the Keen-Vortex API.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import argparse
import sys
from pathlib import Path

API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def review_code(code: str, language: str = "python") -> str:
    """Send code to the Keen-Vortex code review API."""
    url = f"{API_BASE}/api/code-review"
    
    payload = {
        "code": code,
        "language": language
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["review"]
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    parser = argparse.ArgumentParser(description="Review code using Keen-Vortex AI")
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
    print("-" * 50)
    
    review = review_code(code, args.language)
    print(review)
    
    print("\n" + "=" * 50)
    print(f"💡 Powered by Keen-Vortex AI")
    print(f"🌐 API: {API_BASE}")

if __name__ == "__main__":
    main()