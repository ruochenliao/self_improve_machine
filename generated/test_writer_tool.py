#!/usr/bin/env python3

"""
Bold-Phoenix API Test Writer Tool

This script demonstrates how to use the Bold-Phoenix API to generate unit tests for a given Python code snippet.
It sends a POST request to the 'write-tests' or 'write-tests-pro' endpoint and prints the generated tests.

To run this script:
1. Make sure you have Python 3 installed.
2. Install the 'requests' library: pip install requests
3. Replace `YOUR_API_KEY` with your actual API key (if required by your setup, though for public playground, it might not be strictly needed for basic usage).
4. Replace `YOUR_API_URL` with the public URL of the Bold-Phoenix API server.
5. Modify the `code_to_test` variable with the Python code for which you want to generate tests.
6. Run the script: python generated/test_writer_tool.py
"""

import requests
import json

# --- Configuration ---
YOUR_API_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com" # Replace with your actual API URL
# YOUR_API_KEY = "YOUR_API_KEY" # Uncomment and replace if your API requires an API key

# The Python code for which to generate tests
code_to_test = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""

# Choose which service to use: 'write-tests' (standard) or 'write-tests-pro' (GPT-4o)
# 'write-tests-pro' generally provides higher quality results but costs more.
SERVICE_ENDPOINT = "/write-tests-pro" # or "/write-tests"

# --- API Request ---
def generate_tests(code, service_endpoint):
    headers = {
        "Content-Type": "application/json",
        # "Authorization": f"Bearer {YOUR_API_KEY}" # Uncomment if using an API key
    }
    payload = {
        "code": code,
        "language": "python" # Specify the language of the code
    }

    full_url = f"{YOUR_API_URL}{service_endpoint}"
    print(f"Sending request to: {full_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors

        response_data = response.json()
        return response_data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")
        return None

if __name__ == "__main__":
    print("--- Bold-Phoenix Test Writer Tool ---")
    print("Generating tests for the following code:")
    print(code_to_test)

    result = generate_tests(code_to_test, SERVICE_ENDPOINT)

    if result and result.get("tests"):
        print("\n--- Generated Tests ---")
        print(result["tests"])
    elif result and result.get("error"):
        print("\n--- Error ---")
        print(result["error"])
    else:
        print("\n--- No tests generated or unexpected response ---")
        print(result)
