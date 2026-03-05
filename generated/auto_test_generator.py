#!/usr/bin/env python3
"""
Keen-Vortex Auto Test Generator
A tool that automatically generates unit tests for your Python code using the Keen-Vortex API.

Usage: python auto_test_generator.py your_code.py

Your API endpoint: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import sys
import argparse

API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def generate_tests(code_content):
    """Generate unit tests using the write-tests API endpoint."""
    payload = {
        "code": code_content
    }
    
    try:
        response = requests.post(f"{API_BASE}/write-tests", json=payload)
        response.raise_for_status()
        return response.json()["tests"]
    except Exception as e:
        print(f"Error generating tests: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate unit tests for Python code")
    parser.add_argument("file", help="Python file to generate tests for")
    parser.add_argument("--output", "-o", help="Output file for tests (default: test_<filename>.py)")
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    print(f"Generating tests for {args.file}...")
    tests = generate_tests(code)
    
    if tests:
        output_file = args.output or f"test_{args.file}"
        with open(output_file, 'w') as f:
            f.write(tests)
        print(f"Tests generated successfully! Saved to {output_file}")
        print(f"\nTo run the tests: python -m pytest {output_file}")
    else:
        print("Failed to generate tests")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_test_generator.py your_code.py")
        print("Example: python auto_test_generator.py my_module.py")
        sys.exit(1)
    
    main()