#!/usr/bin/env python3

import requests
import json
import argparse

# Your Lucid-Helix API endpoint
# IMPORTANT: Replace with your actual public URL
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com" 

def explain_code(code_content: str) -> str:
    """
    Sends code content to the explain-code API and returns the explanation.
    """
    url = f"{API_BASE_URL}/explain-code"
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_content}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("explanation", "No explanation received.")
    except requests.exceptions.RequestException as e:
        return f"Error explaining code: {e}"

def main():
    parser = argparse.ArgumentParser(description="Explain code using the Lucid-Helix API.")
    parser.add_argument("file_path", help="Path to the code file to explain.")
    
    args = parser.parse_args()
    
    try:
        with open(args.file_path, "r") as f:
            code_content = f.read()
        
        print(f"Explaining code from: {args.file_path}...")
        explanation = explain_code(code_content)
        print("\n--- Code Explanation ---\n")
        print(explanation)
        print("\n------------------------\n")
        print(f"Powered by Lucid-Helix AI: {API_BASE_URL}")
        
    except FileNotFoundError:
        print(f"Error: File not found at {args.file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
