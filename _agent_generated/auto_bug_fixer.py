#!/usr/bin/env python3
"""
Auto Bug Fixer: A script to automatically fix bugs in code using the Prime-Zenith API.
"""

import argparse
import requests
import json

API_URL = "https://came-surgeons-river-exterior.trycloudflare.com/fix-bug"

def fix_bug(file_path: str):
    """
    Reads a file, sends its content to the Prime-Zenith fix-bug API, and prints the suggested fix.
    """
    try:
        with open(file_path, 'r') as f:
            code_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    headers = {'Content-Type': 'application/json'}
    payload = {'code': code_content}

    print(f"Sending code from {file_path} to Prime-Zenith for bug fixing...")
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes
        
        fixed_code = response.json().get('fixed_code', 'No fix suggested.')
        cost = response.json().get('cost', 'N/A')
        
        print("\n--- Suggested Fix (Cost: ${cost}) ---")
        print(fixed_code)
        print("--------------------------------------")

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with the API: {e}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from the API.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatically fix bugs in a code file using the Prime-Zenith API.")
    parser.add_argument("file", help="Path to the code file to fix.")
    args = parser.parse_args()

    fix_bug(args.file)
