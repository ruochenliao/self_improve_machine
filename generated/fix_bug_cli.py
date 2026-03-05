#!/usr/bin/env python3

"""
Keen-Vortex: Fix Bug CLI Tool
This script demonstrates how to use the Keen-Vortex API to fix bugs in code.

Public API Server: https://charlotte-fifty-rrp-induced.trycloudflare.com

Usage:
  python3 fix_bug_cli.py <file_path> [--service SERVICE_TYPE]

Arguments:
  <file_path>    Path to the file containing the buggy code.

Options:
  --service SERVICE_TYPE  Specify 'pro' for GPT-4o powered bug fixing (higher quality, higher cost),
                          or 'standard' for DeepSeek (default, lower cost).
                          [default: standard]

Example:
  python3 fix_bug_cli.py my_buggy_script.py
  python3 fix_bug_cli.py another_bug.py --service pro
"""

import requests
import json
import argparse
import os

API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def fix_bug(file_path: str, service_type: str = "standard"):
    """
    Sends code to the Keen-Vortex API to get bug fixes.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, 'r') as f:
        code_content = f.read()

    endpoint = "/fix-bug"
    if service_type == "pro":
        endpoint = "/fix-bug-pro"

    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_content}

    print(f"Sending code to {url} for bug fixing (service: {service_type})...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors

        result = response.json()
        if "fixed_code" in result:
            print("
--- Fixed Code ---")
            print(result["fixed_code"])
            # Optionally, write to a new file
            fixed_file_path = f"{os.path.splitext(file_path)[0]}_fixed{os.path.splitext(file_path)[1]}"
            with open(fixed_file_path, 'w') as f_fixed:
                f_fixed.write(result["fixed_code"])
            print(f"
Fixed code written to: {fixed_file_path}")
        elif "error" in result:
            print(f"
API Error: {result['error']}")
        else:
            print("
Unexpected API response:")
            print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Network or API error: {e}")
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from response: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Keen-Vortex: Fix Bug CLI Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("file_path", help="Path to the file containing the buggy code.")
    parser.add_argument(
        "--service",
        choices=["standard", "pro"],
        default="standard",
        help="Specify 'pro' for GPT-4o powered bug fixing (higher quality, higher cost), "
             "or 'standard' for DeepSeek (default, lower cost)."
    )
    args = parser.parse_args()

    fix_bug(args.file_path, args.service)

if __name__ == "__main__":
    main()
