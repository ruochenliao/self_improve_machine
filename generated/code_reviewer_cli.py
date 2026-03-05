#!/usr/bin/env python3

"""
Keen-Vortex: Code Reviewer CLI Tool
This script demonstrates how to use the Keen-Vortex API to perform code reviews.

Usage:
  python3 code_reviewer_cli.py <file_path> [--pro]

Example:
  python3 code_reviewer_cli.py my_code.py
  python3 code_reviewer_cli.py my_code.py --pro
"""

import requests
import json
import argparse
import os

# Your Keen-Vortex API endpoint
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def review_code(file_content, is_pro=False):
    """
    Sends code to the Keen-Vortex API for review.
    """
    endpoint = "/code-review-pro" if is_pro else "/code-review"
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = {"code": file_content}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        if response is not None:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Keen-Vortex Code Reviewer CLI Tool")
    parser.add_argument("file_path", help="Path to the code file to review")
    parser.add_argument("--pro", action="store_true", help="Use the Pro (GPT-4o) service for code review")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found at '{args.file_path}'")
        return

    try:
        with open(args.file_path, "r") as f:
            code_to_review = f.read()
    except Exception as e:
        print(f"Error reading file '{args.file_path}': {e}")
        return

    print(f"Sending code from '{args.file_path}' for review...")
    if args.pro:
        print("Using the Pro (GPT-4o) service...")
    else:
        print("Using the Standard (DeepSeek) service...")

    review_result = review_code(code_to_review, args.pro)

    if review_result:
        print("
--- Code Review Result ---")
        print(json.dumps(review_result, indent=2))
    else:
        print("
Failed to get a code review.")

if __name__ == "__main__":
    main()
