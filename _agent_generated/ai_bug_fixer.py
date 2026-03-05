#!/usr/bin/env python3
"""
Lucid-Helix AI Bug Fixer CLI

This script uses the Lucid-Helix AI "fix-bug" API to automatically identify and
suggest fixes for bugs in Python code.

Your API is LIVE on the public internet!
Public URL: https://cet-temporal-therapist-forgot.trycloudflare.com

Usage:
  python3 ai_bug_fixer.py <input_file.py> <output_file.py>

Example:
  python3 ai_bug_fixer.py broken_code.py fixed_code.py
"""

import sys
import requests
import json

API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def fix_bug(code_content: str) -> str:
    """
    Calls the Lucid-Helix AI 'fix-bug' API to get a bug fix.
    """
    url = f"{API_BASE_URL}/fix-bug"
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_content}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        if result and "fixed_code" in result:
            return result["fixed_code"]
        else:
            print(f"Error: Unexpected API response format: {result}", file=sys.stderr)
            return ""
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}", file=sys.stderr)
        return ""

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    try:
        with open(input_file_path, "r") as f:
            code_to_fix = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Sending '{input_file_path}' to Lucid-Helix AI for bug fixing...")
    fixed_code = fix_bug(code_to_fix)

    if fixed_code:
        try:
            with open(output_file_path, "w") as f:
                f.write(fixed_code)
            print(f"Fixed code written to '{output_file_path}'.")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Bug fixing failed or returned empty code.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
