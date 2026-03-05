#!/usr/bin/env python3

"""
Keen-Vortex: Code Review API Example
This script demonstrates how to use the Keen-Vortex API to perform a code review.

Public URL: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import argparse

API_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def code_review(code_content: str, is_pro: bool = False) -> dict:
    """Performs a code review using the Keen-Vortex API.

    Args:
        code_content: The code to be reviewed.
        is_pro: Whether to use the professional (GPT-4o) code review service.

    Returns:
        A dictionary containing the API response.
    """
    endpoint = "/code-review-pro" if is_pro else "/code-review"
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_content}
    try:
        response = requests.post(f"{API_URL}{endpoint}", headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Keen-Vortex Code Review API Example.")
    parser.add_argument("-f", "--file", help="Path to the code file to review.")
    parser.add_argument("-s", "--string", help="Code string to review (alternative to --file).")
    parser.add_argument("--pro", action="store_true", help="Use the PRO (GPT-4o) code review service.")
    args = parser.parse_args()

    code_to_review = ""
    if args.file:
        try:
            with open(args.file, "r") as f:
                code_to_review = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            return
    elif args.string:
        code_to_review = args.string
    else:
        print("Please provide either a file path (--file) or a code string (--string) to review.")
        return

    if not code_to_review.strip():
        print("Error: No code provided for review.")
        return

    print(f"Performing code review using {'PRO' if args.pro else 'Standard'} service...")
    result = code_review(code_to_review, args.pro)

    if "error" in result:
        print(f"API Error: {result['error']}")
    else:
        print("\nCode Review Result:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
