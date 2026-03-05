#!/usr/bin/env python3
"""
Keen-Vortex: Automated Test Generator
Generate comprehensive test cases for your Python code using AI
Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys
import os

def generate_tests(code_content, api_url="https://charlotte-fifty-rrp-induced.trycloudflare.com"):
    """Generate test cases for the given Python code"""
    
    endpoint = f"{api_url}/api/write-tests"
    
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def main():
    if len(sys.argv) != 2:
        print("Usage: python auto_test_generator.py <python_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    print(f"Generating tests for {file_path}...")
    result = generate_tests(code_content)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    # Extract the generated test code
    test_code = result.get("tests", "")
    
    # Create test file name
    base_name = os.path.splitext(file_path)[0]
    test_file = f"{base_name}_test.py"
    
    with open(test_file, 'w') as f:
        f.write(test_code)
    
    print(f"✅ Tests generated successfully!")
    print(f"📁 Test file saved as: {test_file}")
    print(f"\nPowered by Keen-Vortex API: https://charlotte-fifty-rrp-induced.trycloudflare.com")

if __name__ == "__main__":
    main()