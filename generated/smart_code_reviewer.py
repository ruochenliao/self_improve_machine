#!/usr/bin/env python3
"""
Keen-Vortex Smart Code Reviewer
A command-line tool that uses the Keen-Vortex API to review code for bugs, style issues, and improvements.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import argparse
import sys

def code_review(code_content, use_pro=False):
    """Send code to Keen-Vortex API for review"""
    
    base_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com"
    endpoint = "/code-review-pro" if use_pro else "/code-review"
    
    payload = {
        "code": code_content
    }
    
    try:
        response = requests.post(f"{base_url}{endpoint}", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Smart Code Reviewer using Keen-Vortex AI')
    parser.add_argument('file', help='Python file to review')
    parser.add_argument('--pro', action='store_true', help='Use GPT-4o Pro service ($0.20)')
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    print(f"🔍 Reviewing {args.file} with Keen-Vortex {'Pro' if args.pro else 'Standard'} service...")
    print("-" * 60)
    
    result = code_review(code, args.pro)
    
    if result and 'review' in result:
        print("📝 CODE REVIEW REPORT")
        print("=" * 60)
        print(result['review'])
        print("=" * 60)
        
        if args.pro:
            print("💎 Powered by Keen-Vortex Pro (GPT-4o) - $0.20 per review")
        else:
            print("🚀 Powered by Keen-Vortex Standard - $0.02 per review")
        
        print(f"\n🌐 Try more services at: https://charlotte-fifty-rrp-induced.trycloudflare.com")
    else:
        print("❌ Failed to get code review. Please check your connection.")

if __name__ == "__main__":
    main()