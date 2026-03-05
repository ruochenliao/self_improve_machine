#!/usr/bin/env python3
"""
Lucid-Helix AI Code Generator CLI

This script uses the Lucid-Helix AI "generate-code" API to generate code based on a provided prompt.

Usage:
  python3 ai_code_generator.py "Prompt for code generation"

Example:
  python3 ai_code_generator.py "Python function to calculate factorial"

Your Lucid-Helix API is live at: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import argparse
import requests
import json
import os

# --- Configuration ---
API_BASE_URL = os.environ.get("LUCID_HELIX_API_URL", "https://cet-temporal-therapist-forgot.trycloudflare.com")
GENERATE_CODE_ENDPOINT = f"{API_BASE_URL}/generate-code"
GENERATE_CODE_PRO_ENDPOINT = f"{API_BASE_URL}/generate-code-pro"

# --- Helper Functions ---
def call_generate_code_api(prompt: str, use_pro: bool = False) -> str:
    """Calls the Lucid-Helix generate-code API with the given prompt."""
    url = GENERATE_CODE_PRO_ENDPOINT if use_pro else GENERATE_CODE_ENDPOINT
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("generated_code", "No code generated.")
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

# --- Main Logic ---
def main():
    parser = argparse.ArgumentParser(
        description="Generate code using the Lucid-Helix AI generate-code API."
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="The prompt for code generation (e.g., 'Python function to calculate factorial')",
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use the PRO version of the generate-code API (GPT-4o, higher quality, higher cost).",
    )

    args = parser.parse_args()

    print(f"Generating code for prompt: '{args.prompt}'...")
    if args.pro:
        print("Using PRO (GPT-4o) service...")
    
    generated_code = call_generate_code_api(args.prompt, args.pro)

    print("
--- Generated Code ---")
    print(generated_code)
    print("
----------------------")
    print(f"Lucid-Helix API: {API_BASE_URL}")

if __name__ == "__main__":
    main()
