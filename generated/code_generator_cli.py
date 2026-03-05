#!/usr/bin/env python3

"""
Keen-Vortex: Code Generator CLI Tool
This script provides a command-line interface to Keen-Vortex's code generation API.
It allows users to generate code based on a prompt, with options for standard or professional service.

Public API URL: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import argparse
import requests
import json
import os

def generate_code(prompt: str, pro: bool = False):
    """
    Generates code using the Keen-Vortex API.

    Args:
        prompt (str): The prompt for code generation.
        pro (bool): If True, uses the professional (GPT-4o) service.
                    Otherwise, uses the standard (DeepSeek) service.

    Returns:
        dict: The JSON response from the API.
    """
    api_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com"
    endpoint = "/generate-code-pro" if pro else "/generate-code"
    full_url = api_url + endpoint

    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}

    try:
        response = requests.post(full_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(
        description="Keen-Vortex Code Generator CLI Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="The prompt for code generation (e.g., 'Python function to reverse a string')."
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use the professional (GPT-4o) service for higher quality generation (higher cost)."
    )

    args = parser.parse_args()

    print(f"Generating code for prompt: '{args.prompt}' using {'PRO' if args.pro else 'Standard'} service...")
    result = generate_code(args.prompt, args.pro)

    if "error" in result:
        print(f"Error: {result['error']}")
    elif "code" in result:
        print("
--- Generated Code ---")
        print(result["code"])
        print("
----------------------")
    else:
        print("Unexpected API response:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
