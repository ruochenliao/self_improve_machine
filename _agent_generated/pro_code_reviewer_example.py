#!/usr/bin/env python3
"""
Lucid-Helix Pro Code Reviewer Example

This script demonstrates how to use the Lucid-Helix Pro Code Reviewer API
to get a professional code review for a given Python file.

API Endpoint: https://cet-temporal-therapist-forgot.trycloudflare.com/code-review-pro

Usage:
    python3 pro_code_reviewer_example.py <file_path>

Example:
    python3 pro_code_reviewer_example.py my_script.py
"""

import requests
import sys

def pro_code_review(file_path: str) -> str:
    """
    Sends a Python file to the Lucid-Helix Pro Code Reviewer API for review.

    Args:
        file_path: The path to the Python file to be reviewed.

    Returns:
        The code review report from the API.
    """
    try:
        with open(file_path, 'r') as f:
            code_content = f.read()
    except FileNotFoundError:
        return f"Error: File not found at '{file_path}'"
    except Exception as e:
        return f"Error reading file: {e}"

    api_url = "https://cet-temporal-therapist-forgot.trycloudflare.com/code-review-pro"
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_content}

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("review", "No review content received.")
    except requests.exceptions.RequestException as e:
        return f"Error during API request: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    target_file = sys.argv[1]
    print(f"Requesting Pro Code Review for: {target_file}...")
    review_report = pro_code_review(target_file)
    print("
--- Code Review Report ---")
    print(review_report)
    print("--------------------------")
    print(f"Note: This review was provided by Lucid-Helix AI via: https://cet-temporal-therapist-forgot.trycloudflare.com/code-review-pro")
