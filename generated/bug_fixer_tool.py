#!/usr/bin/env python3

"""
Bold-Phoenix API Bug Fixer Tool

This script demonstrates how to use the Bold-Phoenix API's 'fix-bug' service.
It takes a Python file as input, sends its content to the API for bug fixing,
and then prints the suggested fixed code.

Your Bold-Phoenix API endpoint: https://upgrades-approx-gadgets-hit.trycloudflare.com

Usage:
    python3 bug_fixer_tool.py <path_to_python_file>

Example:
    # Create a file named 'buggy_code.py' with some buggy Python code:
    #
    # def divide(a, b):
    #     return a / c
    #
    # print(divide(10, 2))
    #
    # Then run:
    # python3 bug_fixer_tool.py buggy_code.py
"""

import requests
import json
import sys
import os

API_BASE_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com"
FIX_BUG_ENDPOINT = f"{API_BASE_URL}/fix-bug"

def fix_bug_in_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        sys.exit(1)

    if not file_path.endswith(".py"):
        print(f"Warning: '{file_path}' does not appear to be a Python file.")
        # Continue anyway, the API might still process it, or return a relevant error.

    try:
        with open(file_path, 'r') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)

    print(f"Sending '{file_path}' content to Bold-Phoenix API for bug fixing...")

    headers = {'Content-Type': 'application/json'}
    payload = {'code': code_content}

    try:
        response = requests.post(FIX_BUG_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()

        if response.status_code == 200:
            fixed_code = result.get('fixed_code', 'No fixed code returned.')
            cost = result.get('cost', 'N/A')
            print("
--- Bug Fixer Tool Output ---")
            print(f"API Cost: ${cost}")
            print("
Suggested Fixed Code:
")
            print(fixed_code)
            print("
---------------------------
")
        else:
            error_message = result.get('error', 'Unknown API error.')
            print(f"API Error ({response.status_code}): {error_message}")

    except requests.exceptions.RequestException as e:
        print(f"Network or API request error: {e}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON response from API. Response content: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    target_file = sys.argv[1]
    fix_bug_in_file(target_file)
