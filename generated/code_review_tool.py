#!/usr/bin/env python3

import requests
import json
import argparse

# Your Lucid-Helix API endpoint (replace with your actual public URL)
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com" 

def review_code(code_snippet: str, is_pro: bool = False):
    """
    Sends a code snippet to the Lucid-Helix API for code review.
    """
    endpoint = "/code-review-pro" if is_pro else "/code-review"
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_snippet}

    print(f"Sending code for review to: {url}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        review_result = response.json()
        return review_result
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Lucid-Helix Code Review Tool")
    parser.add_argument("file", help="Path to the code file to review")
    parser.add_argument("--pro", action="store_true", 
                        help="Use the PRO code review service (GPT-4o, higher quality, higher cost)")
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            code_to_review = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {args.file}")
        return

    print(f"Reviewing code from: {args.file}")
    result = review_code(code_to_review, args.pro)

    if result:
        print("\n--- Code Review Result ---")
        print(json.dumps(result, indent=2))
    else:
        print("\nFailed to get code review result.")

if __name__ == "__main__":
    main()
