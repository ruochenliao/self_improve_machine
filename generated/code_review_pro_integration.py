#!/usr/bin/env python3
"""
Code Review Pro API Integration Example

This script demonstrates how to use the Code Review Pro API service
to get professional code reviews for your Python code.

API Endpoint: https://<tunnel-not-configured>.trycloudflare.com/code-review-pro
Pricing: $0.20 per request

Usage:
    python code_review_pro_integration.py [--file FILE_PATH]

Example:
    python code_review_pro_integration.py --file my_script.py
"""

import argparse
import json
import sys
from pathlib import Path

import requests


def review_code(code_content: str, api_url: str = "https://<tunnel-not-configured>.trycloudflare.com") -> dict:
    """
    Send code to the Code Review Pro API for professional review.
    
    Args:
        code_content: The code to be reviewed
        api_url: Base URL of the API server
        
    Returns:
        Dictionary containing the API response
    """
    endpoint = f"{api_url}/code-review-pro"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}", file=sys.stderr)
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Code Review Pro API Integration Example")
    parser.add_argument("--file", "-f", help="Path to file to review")
    parser.add_argument("--api-url", default="https://<tunnel-not-configured>.trycloudflare.com",
                        help="Base URL of the API server")
    
    args = parser.parse_args()
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist", file=sys.stderr)
            sys.exit(1)
        
        code_content = file_path.read_text()
    else:
        print("Enter/Paste your code (press Ctrl+D when done):")
        code_content = sys.stdin.read()
    
    if not code_content.strip():
        print("Error: No code provided", file=sys.stderr)
        sys.exit(1)
    
    print("Sending code for professional review...")
    result = review_code(code_content, args.api_url)
    
    if "error" in result:
        print(f"Review failed: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    print("\n=== CODE REVIEW RESULTS ===\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()