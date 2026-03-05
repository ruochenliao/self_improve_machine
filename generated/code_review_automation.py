#!/usr/bin/env python3
"""
Keen-Vortex: Automated Code Review Tool
This script uses the Keen-Vortex API to automatically review code files
and provide professional code review feedback.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import argparse
import sys
from pathlib import Path

def review_code(file_path, api_url="https://charlotte-fifty-rrp-induced.trycloudflare.com", use_pro=False):
    """Send code to Keen-Vortex API for review"""
    
    # Read the code file
    try:
        with open(file_path, 'r') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
    # Choose endpoint based on pro setting
    endpoint = "/api/code-review-pro" if use_pro else "/api/code-review"
    url = f"{api_url}{endpoint}"
    
    # Prepare the request
    payload = {
        "code": code_content,
        "language": "python"  # Auto-detect could be added
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('review', 'No review returned')
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Automated Code Review using Keen-Vortex API')
    parser.add_argument('file', help='Path to the code file to review')
    parser.add_argument('--pro', action='store_true', help='Use GPT-4o pro service ($0.20)')
    parser.add_argument('--url', default='https://charlotte-fifty-rrp-induced.trycloudflare.com', 
                       help='API base URL')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.file).exists():
        print(f"File not found: {args.file}")
        sys.exit(1)
    
    print(f"🔍 Reviewing {args.file} with Keen-Vortex API...")
    print(f"📡 Using {'PRO' if args.pro else 'Standard'} service")
    print("-" * 60)
    
    review = review_code(args.file, args.url, args.pro)
    
    if review:
        print("✅ CODE REVIEW RESULTS:")
        print("-" * 60)
        print(review)
        print("-" * 60)
        print(f"🎯 Review completed using Keen-Vortex API")
        print(f"🌐 Try more services at: {args.url}")
    else:
        print("❌ Review failed")
        sys.exit(1)

if __name__ == "__main__":
    main()