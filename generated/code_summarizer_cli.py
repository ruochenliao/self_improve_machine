#!/usr/bin/env python3
"""
Keen-Vortex: Code Summarizer CLI Tool
This script demonstrates how to use the Keen-Vortex API to summarize code files.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import sys
import os

API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def summarize_code(code_content, use_pro=False):
    """Summarize code using Keen-Vortex API"""
    endpoint = "/summarize" if not use_pro else "/summarize-pro"
    url = f"{API_BASE}{endpoint}"
    
    payload = {
        "code": code_content,
        "language": "python"  # Auto-detection available
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("summary", "No summary generated")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python code_summarizer_cli.py <file_path> [--pro]")
        print("\nExamples:")
        print("  python code_summarizer_cli.py my_script.py")
        print("  python code_summarizer_cli.py complex_module.py --pro")
        sys.exit(1)
    
    file_path = sys.argv[1]
    use_pro = "--pro" in sys.argv
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"Summarizing {file_path}...")
    print("-" * 50)
    
    summary = summarize_code(code_content, use_pro)
    
    print("SUMMARY:")
    print(summary)
    print("-" * 50)
    
    if use_pro:
        print("✓ Used GPT-4o Pro service for enhanced quality")
    else:
        print("✓ Used standard DeepSeek service (cost-effective)")
    
    print(f"\nTry more services at: {API_BASE}")

if __name__ == "__main__":
    main()