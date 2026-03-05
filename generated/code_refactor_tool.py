#!/usr/bin/env python3
"""
Keen-Vortex Code Refactoring Tool
A command-line tool that uses the Keen-Vortex API to refactor and improve Python code.

Your API endpoint: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import argparse
import sys
from pathlib import Path

# Your Keen-Vortex API endpoint
API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def refactor_code(code: str, description: str = "Improve code quality and readability") -> str:
    """Send code to the refactoring API endpoint."""
    try:
        response = requests.post(
            f"{API_BASE}/api/refactor",
            json={
                "code": code,
                "description": description
            }
        )
        
        if response.status_code == 200:
            return response.json().get("refactored_code", "Error: No refactored code returned")
        else:
            return f"Error: API returned status {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Refactor Python code using Keen-Vortex AI")
    parser.add_argument("file", help="Python file to refactor")
    parser.add_argument("--description", "-d", help="Refactoring description", 
                       default="Improve code quality, readability, and performance")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    # Read input file
    try:
        with open(args.file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    print("Refactoring code...", file=sys.stderr)
    refactored = refactor_code(code, args.description)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(refactored)
        print(f"Refactored code written to: {args.output}", file=sys.stderr)
    else:
        print(refactored)

if __name__ == "__main__":
    main()