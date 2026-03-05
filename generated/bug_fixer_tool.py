#!/usr/bin/env python3

import requests
import json
import argparse

# Your Keen-Vortex API endpoint (replace with your actual public URL)
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def fix_bug(code_snippet: str, error_message: str) -> str:
    """
    Uses the Keen-Vortex API to fix a bug in a given code snippet.

    Args:
        code_snippet (str): The code snippet containing the bug.
        error_message (str): The error message or description of the bug.

    Returns:
        str: The fixed code, or an error message if the API call fails.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {
        'code': code_snippet,
        'error_message': error_message
    }
    try:
        response = requests.post(f"{API_BASE_URL}/fix-bug", headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get('fixed_code', 'No fixed code returned.')
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    parser = argparse.ArgumentParser(description="Keen-Vortex Bug Fixer Tool. Fixes bugs in code using AI.")
    parser.add_argument('--code', type=str, required=True, help='The code snippet containing the bug.')
    parser.add_argument('--error', type=str, required=True, help='The error message or description of the bug.')

    args = parser.parse_args()

    print(f"Attempting to fix bug in code using Keen-Vortex API...")
    fixed_code = fix_bug(args.code, args.error)

    print("
--- Original Code ---")
    print(args.code)
    print("
--- Error Message ---")
    print(args.error)
    print("
--- Fixed Code ---")
    print(fixed_code)

if __name__ == "__main__":
    main()
