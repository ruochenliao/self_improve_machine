#!/usr/bin/env python3

"""
Bold-Phoenix Code Summarizer Tool
A practical CLI tool that uses the Bold-Phoenix API to generate concise summaries of code files.

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
Free to use - no API key required!

Usage:
    python3 code_summarizer_tool.py <file_path>
    python3 code_summarizer_tool.py --help
"""

import argparse
import requests
import sys
import os

API_BASE = "https://upgrades-approx-gadgets-hit.trycloudflare.com"

def summarize_code(code_content, use_pro=False):
    """Send code to Bold-Phoenix API for summarization."""
    endpoint = "/summarize" if not use_pro else "/summarize-pro"
    url = API_BASE + endpoint
    
    payload = {
        "text": code_content,
        "max_length": 200
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("summary", "No summary generated")
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    parser = argparse.ArgumentParser(description='Summarize code files using Bold-Phoenix AI')
    parser.add_argument('file_path', help='Path to the code file to summarize')
    parser.add_argument('--pro', action='store_true', help='Use GPT-4o pro service (higher quality)')
    
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
    
    print(f"📄 Summarizing: {args.file_path}")
    print(f"🔧 Using: {'GPT-4o Pro' if args.pro else 'Standard'}")
    print("-" * 50)
    
    summary = summarize_code(code_content, args.pro)
    
    print("📋 CODE SUMMARY:")
    print(summary)
    print("-" * 50)
    print(f"💡 Try more services at: {API_BASE}")

if __name__ == "__main__":
    main()