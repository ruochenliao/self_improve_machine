#!/usr/bin/env python3
"""
Code Quality Improvement Tool using Silent-Nexus API

This tool demonstrates how to use the Silent-Nexus API to:
1. Review code for improvements
2. Fix bugs automatically
3. Generate tests for your code

API Endpoint: https://<tunnel-not-configured>.trycloudflare.com
"""

import requests
import json
import sys
import os

def read_code_file(filepath):
    """Read code from a file."""
    with open(filepath, 'r') as f:
        return f.read()

def review_code(code, api_url="https://<tunnel-not-configured>.trycloudflare.com"):
    """Send code for review using the API."""
    response = requests.post(f"{api_url}/code-review", 
                           json={"code": code},
                           headers={"Content-Type": "application/json"})
    return response.json()

def fix_bugs(code, api_url="https://<tunnel-not-configured>.trycloudflare.com"):
    """Send code to fix bugs using the API."""
    response = requests.post(f"{api_url}/fix-bug", 
                           json={"code": code},
                           headers={"Content-Type": "application/json"})
    return response.json()

def generate_tests(code, api_url="https://<tunnel-not-configured>.trycloudflare.com"):
    """Generate tests for the code using the API."""
    response = requests.post(f"{api_url}/write-tests", 
                           json={"code": code},
                           headers={"Content-Type": "application/json"})
    return response.json()

def main():
    if len(sys.argv) != 2:
        print("Usage: python code_quality_tool.py <code_file.py>")
        print("Example: python code_quality_tool.py my_script.py")
        sys.exit(1)
    
    code_file = sys.argv[1]
    if not os.path.exists(code_file):
        print(f"Error: File {code_file} not found")
        sys.exit(1)
    
    # Read the code
    code = read_code_file(code_file)
    print(f"Processing {code_file}...\n")
    
    # Code review
    print("1. Getting code review...")
    review_result = review_code(code)
    print(f"Review: {review_result.get('review', 'No review available')}\n")
    
    # Fix bugs
    print("2. Fixing bugs...")
    fixed_result = fix_bugs(code)
    fixed_code = fixed_result.get('fixed_code', code)
    print(f"Fixed code:\n{fixed_code}\n")
    
    # Generate tests
    print("3. Generating tests...")
    tests_result = generate_tests(fixed_code)
    tests = tests_result.get('tests', '# No tests generated')
    print(f"Generated tests:\n{tests}\n")
    
    # Save improved code and tests
    improved_file = f"improved_{os.path.basename(code_file)}"
    with open(improved_file, 'w') as f:
        f.write(fixed_code)
    print(f"Improved code saved to {improved_file}")
    
    test_file = f"test_{os.path.basename(code_file)}"
    with open(test_file, 'w') as f:
        f.write(tests)
    print(f"Tests saved to {test_file}")

if __name__ == "__main__":
    main()