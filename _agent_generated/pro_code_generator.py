#!/usr/bin/env python3
"""
Lucid-Helix Pro Code Generator

This script uses the Lucid-Helix 'generate-code-pro' API to generate code based on a given prompt.
It's designed to be a command-line tool for developers who want to quickly generate code snippets
or entire functions using AI.

API Endpoint: https://cet-temporal-therapist-forgot.trycloudflare.com/generate-code-pro

Usage:
  python pro_code_generator.py "Create a Python function that calculates the factorial of a number."

Dependencies:
  - requests (pip install requests)
"""

import requests
import argparse
import json

API_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com/generate-code-pro"

def generate_code(prompt: str) -> str:
    """
    Generates code using the Lucid-Helix 'generate-code-pro' API.

    Args:
        prompt: The prompt for code generation.

    Returns:
        The generated code as a string, or an error message if the request fails.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json().get("generated_code", "No code generated.")
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err} - {response.text}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Connection error occurred: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"Timeout error occurred: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"An unexpected error occurred: {req_err}"

def main():
    parser = argparse.ArgumentParser(description="Lucid-Helix Pro Code Generator CLI Tool")
    parser.add_argument("prompt", type=str, help="The prompt to generate code from.")
    args = parser.parse_args()

    print(f"Generating code for prompt: '{args.prompt}'...")
    generated_code = generate_code(args.prompt)
    print("
--- Generated Code ---")
    print(generated_code)
    print("----------------------")
    print(f"Powered by Lucid-Helix AI: {API_URL}")

if __name__ == "__main__":
    main()
