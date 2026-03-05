#!/usr/bin/env python3
"""
Keen-Vortex: Auto Code Documentation Generator
This script uses the Keen-Vortex API to automatically generate documentation for code files.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import argparse
import os
import sys

API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def generate_documentation(code_content, use_pro=False):
    """Generate documentation for given code using Keen-Vortex API."""
    endpoint = f"{API_BASE}/explain-code"
    if use_pro:
        endpoint = f"{API_BASE}/explain-code-pro"
    
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            return response.json().get('explanation', 'No explanation generated')
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API request failed: {e}"

def main():
    parser = argparse.ArgumentParser(description='Auto-generate code documentation using Keen-Vortex API')
    parser.add_argument('file_path', help='Path to the code file to document')
    parser.add_argument('--pro', action='store_true', help='Use GPT-4o pro service for better quality')
    parser.add_argument('--output', '-o', help='Output file path (default: print to stdout)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: File '{args.file_path}' not found")
        sys.exit(1)
    
    try:
        with open(args.file_path, 'r') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"Generating documentation for {args.file_path}...")
    documentation = generate_documentation(code_content, args.pro)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(documentation)
            print(f"Documentation saved to: {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}")
    else:
        print("\n" + "="*60)
        print("GENERATED DOCUMENTATION:")
        print("="*60)
        print(documentation)
        print("="*60)

if __name__ == "__main__":
    main()