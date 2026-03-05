#!/usr/bin/env python3
"""
Lucid-Helix AI-powered Bug Fixer CLI Tool

This script provides a command-line interface to interact with the Lucid-Helix
"fix-bug" API service. It allows users to submit code snippets with identified
bugs and receive AI-generated fixes.

Public API Server: https://cet-temporal-therapist-forgot.trycloudflare.com

Usage:
    python bug_fixer_cli.py <file_path>

Example:
    python bug_fixer_cli.py my_buggy_code.py

Dependencies:
    - requests (install with: pip install requests)
"""

import argparse
import requests
import json
import os

API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"
FIX_BUG_ENDPOINT = f"{API_BASE_URL}/fix-bug"

def fix_bug_in_code(code_content: str) -> str:
    """
    Sends the code content to the fix-bug API and returns the suggested fix.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_content}

    try:
        print(f"Sending code to {FIX_BUG_ENDPOINT} for bug fixing...")
        response = requests.post(FIX_BUG_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        result = response.json()
        if "fixed_code" in result:
            return result["fixed_code"]
        elif "error" in result:
            return f"Error from API: {result['error']}"
        else:
            return f"Unexpected API response: {json.dumps(result)}"

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except json.JSONDecodeError:
        return f"Failed to decode JSON from response: {response.text}"

def main():
    parser = argparse.ArgumentParser(description="Lucid-Helix AI-powered Bug Fixer CLI Tool")
    parser.add_argument("file_path", help="Path to the file containing the buggy code")

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found at '{args.file_path}'")
        return

    with open(args.file_path, 'r') as f:
        buggy_code = f.read()

    if not buggy_code.strip():
        print("Error: The provided file is empty or contains only whitespace.")
        return

    print("--- Original Code ---")
    print(buggy_code)
    print("---------------------")

    fixed_code = fix_bug_in_code(buggy_code)

    print("
--- Fixed Code ---")
    print(fixed_code)
    print("------------------")

    # Optional: Offer to save the fixed code
    save_option = input("
Do you want to save the fixed code to a new file? (y/N): ").strip().lower()
    if save_option == 'y':
        output_file_path = args.file_path.replace(".py", "_fixed.py") if args.file_path.endswith(".py") else args.file_path + "_fixed"
        with open(output_file_path, 'w') as f:
            f.write(fixed_code)
        print(f"Fixed code saved to '{output_file_path}'")
    else:
        print("Fixed code not saved.")

if __name__ == "__main__":
    main()
