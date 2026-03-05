#!/usr/bin/env python3
"""
Lucid-Helix Code Generator Tool
A practical CLI tool that uses the Lucid-Helix API to generate code snippets.

Public API: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import json
import sys
import argparse

API_BASE = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def generate_code(prompt, language="python", pro=False):
    """Generate code using Lucid-Helix API"""
    endpoint = f"{API_BASE}/generate-code-pro" if pro else f"{API_BASE}/generate-code"
    
    payload = {
        "prompt": prompt,
        "language": language
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()["code"]
    except Exception as e:
        return f"Error: {e}"

def main():
    parser = argparse.ArgumentParser(description="Generate code using Lucid-Helix AI")
    parser.add_argument("prompt", help="Description of the code you want to generate")
    parser.add_argument("--language", "-l", default="python", help="Programming language")
    parser.add_argument("--pro", action="store_true", help="Use GPT-4o for higher quality")
    parser.add_argument("--output", "-o", help="Output file (optional)")
    
    args = parser.parse_args()
    
    print(f"Generating {args.language} code: {args.prompt}")
    
    code = generate_code(args.prompt, args.language, args.pro)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(code)
        print(f"Code written to {args.output}")
    else:
        print("\n" + "="*50)
        print(code)
        print("="*50)

if __name__ == "__main__":
    main()