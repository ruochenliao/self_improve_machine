#!/usr/bin/env python3
"""
Lucid-Helix Pro Code Reviewer

This script uses the Lucid-Helix 'code-review-pro' API to provide a professional code review
for a given Python file.

Public API Server: https://cet-temporal-therapist-forgot.trycloudflare.com

Usage:
    python3 pro_code_reviewer.py <path_to_python_file>

Example:
    python3 pro_code_reviewer.py my_script.py
"""

import sys
import os
import requests

API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"
CODE_REVIEW_PRO_ENDPOINT = f"{API_BASE_URL}/code-review-pro"

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 pro_code_reviewer.py <path_to_python_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)

    print(f"Sending '{file_path}' for professional code review...")

    try:
        response = requests.post(
            CODE_REVIEW_PRO_ENDPOINT,
            json={"code": code_content},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        review_result = response.json()
        print("\n--- Code Review Result ---")
        print(review_result.get("review", "No review content received."))
        print("--------------------------")

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        if e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
