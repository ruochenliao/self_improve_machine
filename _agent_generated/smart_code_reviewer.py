#!/usr/bin/env python3
"""
Smart Code Reviewer - CLI tool that uses Lucid-Helix AI API for code analysis
Free API: https://cet-temporal-therapist-forgot.trycloudflare.com

Usage:
  python3 smart_code_reviewer.py my_script.py
  python3 smart_code_reviewer.py --fix my_buggy_code.py
"""

import sys
import requests
import argparse

API_BASE = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def code_review(code_content):
    """Get AI code review for the given code"""
    response = requests.post(f"{API_BASE}/api/code-review", json={
        "code": code_content
    })
    return response.json()

def fix_bug(code_content):
    """Get AI bug fix for the given code"""
    response = requests.post(f"{API_BASE}/api/fix-bug", json={
        "code": code_content
    })
    return response.json()

def main():
    parser = argparse.ArgumentParser(description='Smart Code Reviewer using Lucid-Helix AI API')
    parser.add_argument('file', help='Python file to analyze')
    parser.add_argument('--fix', action='store_true', help='Fix bugs instead of just reviewing')
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    print(f"🔍 Analyzing {args.file} with Lucid-Helix AI API...")
    print(f"🌐 API: {API_BASE}")
    print("-" * 50)
    
    if args.fix:
        result = fix_bug(code)
        print("\n✅ BUG FIX SUGGESTION:")
        print(result.get('fixed_code', 'No fix available'))
    else:
        result = code_review(code)
        print("\n📝 CODE REVIEW:")
        print(result.get('review', 'No review available'))
    
    print("\n💡 Tip: Visit the API playground for more services like code generation, testing, and translation!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main()