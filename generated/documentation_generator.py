#!/usr/bin/env python3

import requests
import json
import argparse

# Your Keen-Vortex API endpoint
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def generate_documentation(code_snippet: str) -> str:
    """
    Generates documentation for a given code snippet using the Keen-Vortex API's summarize service.
    """
    url = f"{API_BASE_URL}/summarize"
    headers = {"Content-Type": "application/json"}
    payload = {"text": code_snippet, "model": "deepseek-chat"} # Using deepseek-chat for standard service
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        return result.get("summary", "No documentation generated.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the API: {e}"

def main():
    parser = argparse.ArgumentParser(description="Generate documentation for code snippets using Keen-Vortex API.")
    parser.add_argument("file_path", help="Path to the code file to document.")
    
    args = parser.parse_args()

    try:
        with open(args.file_path, 'r') as f:
            code_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {args.file_path}")
        return

    print(f"Generating documentation for {args.file_path}...")
    documentation = generate_documentation(code_content)
    print("
--- Generated Documentation ---")
    print(documentation)
    print("-----------------------------")
    print(f"Powered by Keen-Vortex API: {API_BASE_URL}")

if __name__ == "__main__":
    main()
