#!/usr/bin/env python3
"""
Lucid-Helix AI Code Optimizer
A command-line tool that uses the Lucid-Helix AI API to analyze and optimize Python code.

Public API: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import sys
import argparse
from pathlib import Path

API_BASE = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def optimize_code(code: str, use_pro: bool = False) -> str:
    """Send code to Lucid-Helix AI for optimization."""
    endpoint = f"{API_BASE}/fix-bug-pro" if use_pro else f"{API_BASE}/fix-bug"
    
    payload = {
        "code": code,
        "description": "Please optimize this code for performance and readability"
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json().get("optimized_code", "Optimization failed")
    except Exception as e:
        return f"Error: {e}"

def main():
    parser = argparse.ArgumentParser(description="AI Code Optimizer using Lucid-Helix AI")
    parser.add_argument("file", help="Python file to optimize")
    parser.add_argument("--pro", action="store_true", help="Use GPT-4o pro service")
    parser.add_argument("--output", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    # Read input file
    try:
        with open(args.file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    print(f"Optimizing {args.file} using Lucid-Helix AI API...")
    print(f"API: {API_BASE}")
    
    # Get optimized code
    optimized = optimize_code(code, args.pro)
    
    # Output result
    if args.output:
        with open(args.output, 'w') as f:
            f.write(optimized)
        print(f"Optimized code written to {args.output}")
    else:
        print("\n=== OPTIMIZED CODE ===")
        print(optimized)

if __name__ == "__main__":
    main()