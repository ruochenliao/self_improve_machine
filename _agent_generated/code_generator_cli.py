#!/usr/bin/env python3
"""
Lucid-Helix AI-powered Code Generator CLI Tool

This script provides a command-line interface to interact with the Lucid-Helix
code generation API services. It allows users to generate code snippets,
functions, or even full scripts based on natural language descriptions.

Services Used:
- generate-code (Standard, DeepSeek): For general code generation.
- generate-code-pro (Pro, GPT-4o): For higher quality or more complex code generation.

Usage:
    python3 code_generator_cli.py "Create a Python function to calculate factorial"
    python3 code_generator_cli.py --pro "Generate a React component for a user profile"

Public API URL: https://cet-temporal-therapist-forgot.trycloudflare.com

Dependencies:
    - requests (install with: pip install requests)
"""

import argparse
import requests
import json

API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def generate_code(prompt: str, pro_service: bool = False):
    """
    Generates code using the Lucid-Helix API.

    Args:
        prompt (str): The natural language description of the code to generate.
        pro_service (bool): If True, use the pro (GPT-4o) service.
                            Otherwise, use the standard (DeepSeek) service.

    Returns:
        str: The generated code or an error message.
    """
    service_endpoint = "/generate-code-pro" if pro_service else "/generate-code"
    url = f"{API_BASE_URL}{service_endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("generated_code", "No code generated.")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to API: {e}"
    except json.JSONDecodeError:
        return f"Error decoding JSON response: {response.text}"

def main():
    parser = argparse.ArgumentParser(
        description="Lucid-Helix AI-powered Code Generator CLI Tool"
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="The natural language description of the code to generate.",
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use the Pro (GPT-4o) code generation service for higher quality.",
    )

    args = parser.parse_args()

    print(f"Generating code for: '{args.prompt}' using {'Pro' if args.pro else 'Standard'} service...")
    generated_code = generate_code(args.prompt, args.pro)
    print("\n--- Generated Code ---\n")
    print(generated_code)
    print("\n----------------------\n")
    print(f"Generated via Lucid-Helix API: {API_BASE_URL}")

if __name__ == "__main__":
    main()
