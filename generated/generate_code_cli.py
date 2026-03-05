#!/usr/bin/env python3

"""
Keen-Vortex: Generate Code CLI Tool
This script demonstrates how to use the Keen-Vortex API to generate code based on a prompt.

Usage:
  python3 generate_code_cli.py "Create a Python function to calculate the factorial of a number."
  python3 generate_code_cli.py "Generate a React component for a simple counter." --pro

Your Keen-Vortex API is live at: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("The 'requests' library is not installed.")
    print("Please install it using: pip install requests")
    sys.exit(1)

API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def generate_code(prompt: str, use_pro: bool = False):
    """
    Generates code using the Keen-Vortex API.

    Args:
        prompt (str): The prompt for code generation.
        use_pro (bool): Whether to use the pro (GPT-4o) service.
    """
    endpoint = "/generate-code-pro" if use_pro else "/generate-code"
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}

    print(f"Generating code using {endpoint.strip('/')} service...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        print("
Generated Code:")
        print("--------------")
        print(result.get("generated_code", "No code generated."))
        print("--------------")
        if "cost" in result:
            print(f"Cost: ${result['cost']:.4f}")
        if "model" in result:
            print(f"Model: {result['model']}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if e.response is not None:
            print(f"Response status: {e.response.status_code}")
            try:
                error_details = e.response.json()
                print(f"Error details: {json.dumps(error_details, indent=2)}")
            except json.JSONDecodeError:
                print(f"Error response: {e.response.text}")

def main():
    parser = argparse.ArgumentParser(
        description="Keen-Vortex: Generate Code CLI Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="The prompt for code generation (e.g., 'Create a Python function to calculate the factorial of a number.')"
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use the PRO (GPT-4o) service for code generation. (Higher quality, higher cost)"
    )
    args = parser.parse_args()

    generate_code(args.prompt, args.pro)

if __name__ == "__main__":
    main()
