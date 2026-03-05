#!/usr/bin/env python3

"""
Keen-Vortex: Bug Fixer CLI Tool
This script provides a command-line interface to interact with the Keen-Vortex 'fix-bug' API service.
It allows users to submit Python code with a bug, and receive a corrected version from the API.

To run this script:
1. Make sure you have Python 3 installed.
2. Install the 'requests' library: pip install requests
3. Replace 'YOUR_API_BASE_URL' with the actual base URL of the Keen-Vortex API.
   (e.g., https://charlotte-fifty-rrp-induced.trycloudflare.com)
4. Run the script: python bug_fixer_cli.py

Example Usage:
python bug_fixer_cli.py "def add(a, b): return a - b"
"""

import requests
import json
import argparse

# --- Configuration ---
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com" # Replace with your actual API base URL
FIX_BUG_ENDPOINT = f"{API_BASE_URL}/fix-bug"

# --- CLI Argument Parsing ---
parser = argparse.ArgumentParser(
    description="Fix a bug in Python code using the Keen-Vortex API."
)
parser.add_argument(
    "buggy_code",
    type=str,
    help="The Python code containing a bug (e.g., 'def add(a, b): return a - b')",
)
args = parser.parse_args()

# --- API Interaction ---
def fix_code_bug(buggy_code: str) -> dict:
    """
    Sends buggy code to the Keen-Vortex fix-bug API and returns the response.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"code": buggy_code}
    try:
        response = requests.post(FIX_BUG_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return {"error": str(e)}

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Submitting buggy code to Keen-Vortex API for fixing...")
    result = fix_code_bug(args.buggy_code)

    if "fixed_code" in result:
        print("
--- Original Code ---")
        print(args.buggy_code)
        print("
--- Fixed Code ---")
        print(result["fixed_code"])
        if "explanation" in result:
            print("
--- Explanation ---")
            print(result["explanation"])
    elif "error" in result:
        print(f"
Error: {result['error']}")
    else:
        print(f"
Unexpected API response: {result}")
