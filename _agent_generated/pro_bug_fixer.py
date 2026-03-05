#!/usr/bin/env python3
"""
Lucid-Helix Pro Bug Fixer

This script uses the Lucid-Helix 'fix-bug-pro' API to get suggestions for fixing bugs in a given Python file.
It sends the content of a specified file to the API and prints the suggested fix.

Usage:
    python3 pro_bug_fixer.py <file_path>

Example:
    python3 pro_bug_fixer.py my_buggy_script.py
"""

import sys
import requests
import json

# Your public API server URL
API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def fix_bug_pro(file_content: str) -> str:
    """
    Calls the Lucid-Helix fix-bug-pro API to get bug fix suggestions.

    Args:
        file_content: The content of the file with the bug.

    Returns:
        A string containing the suggested bug fix, or an error message.
    """
    url = f"{API_BASE_URL}/fix-bug-pro"
    headers = {"Content-Type": "application/json"}
    data = {"code": file_content}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        if result and "fix" in result:
            return result["fix"]
        else:
            return "Error: Unexpected API response format."
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pro_bug_fixer.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print(f"Sending '{file_path}' to Lucid-Helix for bug fixing...")
    suggested_fix = fix_bug_pro(file_content)

    print("
--- Suggested Bug Fix ---")
    print(suggested_fix)
    print("-------------------------
")
    print(f"Try it yourself at: {API_BASE_URL}")

if __name__ == "__main__":
    main()
