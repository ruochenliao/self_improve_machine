#!/usr/bin/env python3

"""
Bold-Phoenix API Code Review Tool

This script demonstrates how to use the Bold-Phoenix API for code review.
It takes a file path as input, reads the code, and sends it to the
code-review or code-review-pro endpoint for review.

Usage:
    python3 code_reviewer_tool.py <file_path> [--pro]

Example:
    python3 code_reviewer_tool.py my_bad_code.py
    python3 code_reviewer_tool.py my_bad_code.py --pro
"""

import requests
import json
import sys
import os

# Your Bold-Phoenix API endpoint
API_BASE_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com"

def review_code(file_path, pro_service=False):
    """
    Sends the code from the given file path to the Bold-Phoenix API for review.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    try:
        with open(file_path, 'r') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return

    endpoint = "/code-review-pro" if pro_service else "/code-review"
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_content}

    print(f"Sending code for review to {url}...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        review_result = response.json()
        print("Code Review Result:")
        print(json.dumps(review_result, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from the API.")
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target_file = sys.argv[1]
    is_pro = "--pro" in sys.argv

    review_code(target_file, is_pro)
