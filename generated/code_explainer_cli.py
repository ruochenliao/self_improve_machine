#!/usr/bin/env python3

"""
Keen-Vortex: Code Explainer CLI Tool
This script provides a command-line interface to explain code snippets using the Keen-Vortex API.
"""

import requests
import json
import argparse
import os

# Your Keen-Vortex API endpoint
# IMPORTANT: Replace with your actual public URL
API_BASE_URL = os.environ.get("KEEN_VORTEX_API_URL", "https://charlotte-fifty-rrp-induced.trycloudflare.com")
EXPLAIN_CODE_ENDPOINT = f"{API_BASE_URL}/explain-code"

def explain_code(code_snippet: str) -> str:
    """
    Explains a given code snippet using the Keen-Vortex explain-code API.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_snippet}
    try:
        response = requests.post(EXPLAIN_CODE_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("explanation", "No explanation found.")
    except requests.exceptions.RequestException as e:
        return f"Error explaining code: {e}"

def main():
    parser = argparse.ArgumentParser(description="Explain a code snippet using the Keen-Vortex API.")
    parser.add_argument("-f", "--file", type=str, help="Path to a file containing the code to explain.")
    parser.add_argument("-c", "--code", type=str, help="Code snippet to explain (use with quotes for multi-word snippets).")

    args = parser.parse_args()

    code_to_explain = None
    if args.file:
        try:
            with open(args.file, "r") as f:
                code_to_explain = f.read()
        except FileNotFoundError:
            print(f"Error: File not found at {args.file}")
            return
    elif args.code:
        code_to_explain = args.code
    else:
        print("Please provide either a file path (-f) or a code snippet (-c).")
        return

    if code_to_explain:
        print("Explaining code...")
        explanation = explain_code(code_to_explain)
        print("
--- Code Explanation ---")
        print(explanation)
        print("------------------------")
    else:
        print("No code provided for explanation.")

if __name__ == "__main__":
    main()
