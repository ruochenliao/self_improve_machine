#!/usr/bin/env python3
"""
Lucid-Helix AI-powered Documentation Generator

This CLI tool uses the Lucid-Helix API to generate documentation for Python code.
It leverages the 'explain-code' service to provide clear and concise explanations
of functions, classes, and modules, which can then be used to populate docstrings
or external documentation.

Public API URL: https://cet-temporal-therapist-forgot.trycloudflare.com

Usage:
  python3 doc_generator.py <file_path>

Example:
  python3 doc_generator.py my_module.py
"""

import argparse
import requests
import json
import os

API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def generate_doc_for_code(code_content: str) -> str:
    """
    Generates documentation for the given Python code content using the Lucid-Helix API.

    Args:
        code_content: The Python code as a string.

    Returns:
        A string containing the generated documentation.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/explain-code",
            headers={"Content-Type": "application/json"},
            json={"code": code_content}
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("explanation", "Could not generate explanation.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with API: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation for Python code using Lucid-Helix API."
    )
    parser.add_argument(
        "file_path",
        help="Path to the Python file for which to generate documentation."
    )
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found at '{args.file_path}'")
        return

    try:
        with open(args.file_path, 'r') as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error reading file '{args.file_path}': {e}")
        return

    print(f"Generating documentation for '{args.file_path}' using Lucid-Helix API...")
    documentation = generate_doc_for_code(code_content)
    print("
--- Generated Documentation ---")
    print(documentation)
    print("-----------------------------")
    print(f"For more AI-powered developer tools, visit: {API_BASE_URL}")

if __name__ == "__main__":
    main()
