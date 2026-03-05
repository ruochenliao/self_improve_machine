#!/usr/bin/env python3
"""
Code Review CLI Tool - Powered by Lucid-Helix AI API
Get instant code reviews for your Python files using AI.

API URL: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import argparse
import sys
from pathlib import Path

def code_review(file_path, use_pro=False):
    """Send code to Lucid-Helix API for review"""
    
    # Read the file
    try:
        with open(file_path, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return
    
    # Prepare API request
    base_url = "https://cet-temporal-therapist-forgot.trycloudflare.com"
    endpoint = "/code-review-pro" if use_pro else "/code-review"
    url = base_url + endpoint
    
    payload = {
        "code": code,
        "language": "python",
        "filename": Path(file_path).name
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print(f"CODE REVIEW: {Path(file_path).name}")
            print("="*60)
            print(f"\n{result.get('review', 'No review provided')}")
            
            if 'suggestions' in result:
                print("\nSUGGESTIONS:")
                for i, suggestion in enumerate(result['suggestions'], 1):
                    print(f"{i}. {suggestion}")
                    
            if 'score' in result:
                print(f"\nSCORE: {result['score']}/10")
                
        else:
            print(f"Error: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        print(f"Make sure the API is available at: {base_url}")

def main():
    parser = argparse.ArgumentParser(description='AI Code Review Tool')
    parser.add_argument('file', help='Python file to review')
    parser.add_argument('--pro', action='store_true', help='Use GPT-4o Pro service ($0.20)')
    parser.add_argument('--free', action='store_true', help='Use free DeepSeek service ($0.02)')
    
    args = parser.parse_args()
    
    if not Path(args.file).exists():
        print(f"Error: File '{args.file}' does not exist")
        sys.exit(1)
    
    if not args.file.endswith('.py'):
        print("Warning: This tool works best with Python files")
    
    use_pro = args.pro or not args.free
    
    print(f"\nUsing {'GPT-4o Pro' if use_pro else 'DeepSeek Free'} service")
    print(f"Cost: ${'0.20' if use_pro else '0.02'} per review")
    print("Sending code for review...\n")
    
    code_review(args.file, use_pro)

if __name__ == "__main__":
    main()