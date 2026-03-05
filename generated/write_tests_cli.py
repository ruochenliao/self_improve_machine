#!/usr/bin/env python3

"""
Keen-Vortex: Write Tests CLI Tool
This script demonstrates how to use the Keen-Vortex API to generate unit tests for a given code snippet.
It interacts with the 'write-tests' or 'write-tests-pro' endpoint.

Usage:
  python3 write_tests_cli.py <code_file_path> [--pro]

Example:
  python3 write_tests_cli.py my_module.py
  python3 write_tests_cli.py my_module.py --pro
"""

import requests
import json
import argparse
import os

# Your Keen-Vortex API endpoint
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def write_tests(code: str, pro_service: bool = False):
    """
    Generates unit tests for the given code using the Keen-Vortex API.

    Args:
        code (str): The code snippet for which to generate tests.
        pro_service (bool): Whether to use the pro service (GPT-4o) or standard (DeepSeek).

    Returns:
        tuple: A tuple containing (success: bool, message: str, generated_tests: str).
    """
    endpoint = "/write-tests-pro" if pro_service else "/write-tests"
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = {"code": code}

    print(f"[*] Sending request to {url}...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors

        result = response.json()
        if response.status_code == 200 and "tests" in result:
            print("[+] Tests generated successfully!")
            return True, "Tests generated successfully.", result["tests"]
        else:
            error_message = result.get("detail", "Unknown error")
            print(f"[-] API Error: {error_message}")
            return False, f"API Error: {error_message}", ""
    except requests.exceptions.RequestException as e:
        print(f"[-] HTTP Request failed: {e}")
        return False, f"HTTP Request failed: {e}", ""
    except json.JSONDecodeError:
        print(f"[-] Failed to decode JSON response: {response.text}")
        return False, f"Failed to decode JSON response: {response.text}", ""

def main():
    parser = argparse.ArgumentParser(
        description="Keen-Vortex Write Tests CLI Tool"
    )
    parser.add_argument(
        "code_file_path",
        help="Path to the Python file for which to generate tests."
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use the PRO (GPT-4o) service for higher quality tests (costs more)."
    )

    args = parser.parse_args()

    if not os.path.exists(args.code_file_path):
        print(f"Error: File not found at '{args.code_file_path}'")
        exit(1)

    try:
        with open(args.code_file_path, 'r') as f:
            code_content = f.read()
    except IOError as e:
        print(f"Error reading file '{args.code_file_path}': {e}")
        exit(1)

    success, message, generated_tests = write_tests(code_content, args.pro)

    if success:
        output_filename = f"test_{os.path.basename(args.code_file_path)}"
        try:
            with open(output_filename, 'w') as f:
                f.write(generated_tests)
            print(f"[+] Generated tests saved to '{output_filename}'")
        except IOError as e:
            print(f"Error writing tests to file '{output_filename}': {e}")
    else:
        print(f"[-] Failed to generate tests: {message}")

if __name__ == "__main__":
    main()
