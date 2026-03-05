#!/usr/bin/env python3

"""
Keen-Vortex API Integration Example: Write Tests

This script demonstrates how to use the Keen-Vortex 'write-tests' API
endpoint to generate unit tests for a given Python code snippet.

Usage:
  python3 write_tests_cli.py <code_file_path>

Example:
  python3 write_tests_cli.py my_module.py

API Endpoint: https://charlotte-fifty-rrp-induced.trycloudflare.com/write-tests
"""

import requests
import json
import sys
import os

# Your Keen-Vortex API endpoint (ensure it's the correct one for write-tests)
API_ENDPOINT = "https://charlotte-fifty-rrp-induced.trycloudflare.com/write-tests"

def write_tests(code_content: str) -> str:
    """Sends code to the API to generate tests and returns the generated tests."""
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "code": code_content
    }
    try:
        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json().get("tests", "No tests generated.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the API: {e}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 write_tests_cli.py <code_file_path>")
        sys.exit(1)

    code_file_path = sys.argv[1]

    if not os.path.exists(code_file_path):
        print(f"Error: File not found at '{code_file_path}'")
        sys.exit(1)

    try:
        with open(code_file_path, 'r') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file '{code_file_path}': {e}")
        sys.exit(1)
    
    print(f"\n--- Generating tests for {code_file_path} using Keen-Vortex API ---")
    generated_tests = write_tests(code_content)
    print("\n--- Generated Tests ---")
    print(generated_tests)

    # Optional: Save tests to a file
    output_filename = f"test_{os.path.basename(code_file_path).replace('.py', '')}.py"
    try:
        with open(output_filename, 'w') as f:
            f.write(generated_tests)
        print(f"\nTests saved to {output_filename}")
    except Exception as e:
        print(f"Error saving tests to file: {e}")

if __name__ == "__main__":
    main()