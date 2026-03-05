#!/usr/bin/env python3

import requests
import json
import argparse

# Your Keen-Vortex API endpoint
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def generate_test_cases(code_snippet: str, language: str, public_url: str):
    """
    Generates test cases for a given code snippet using the Keen-Vortex API.
    """
    url = f"{API_BASE_URL}/write-tests"
    headers = {"Content-Type": "application/json"}
    payload = {
        "code": code_snippet,
        "language": language,
        "public_url": public_url
    }

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        if response is not None:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate test cases for a code snippet using Keen-Vortex API.")
    parser.add_argument("--code", required=True, help="The code snippet to generate tests for.")
    parser.add_argument("--lang", default="python", help="The programming language of the code snippet (default: python).")
    parser.add_argument("--public-url", default=API_BASE_URL, help=f"Your Keen-Vortex public URL (default: {API_BASE_URL}).")

    args = parser.parse_args()

    print("Generating test cases for the provided code snippet...")
    result = generate_test_cases(args.code, args.lang, args.public_url)

    if result and result.get("success"):
        print("
Successfully generated test cases:")
        print(result.get("tests", "No tests returned."))
        print(f"
Cost: ${result.get('cost', 'N/A')}")
    else:
        print("
Failed to generate test cases.")
        if result:
            print(f"Error: {result.get('error', 'Unknown error.')}")

if __name__ == "__main__":
    main()
