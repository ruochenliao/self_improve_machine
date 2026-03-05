#!/usr/bin/env python3

"""
Bold-Phoenix API Summarizer Tool

This script demonstrates how to use the Bold-Phoenix API to summarize text.
It takes a text file as input, sends it to the /summarize endpoint, and prints the summarized output.

Usage:
  python3 summarizer_tool.py <input_file.txt>

Example:
  echo "This is a long piece of text that needs to be summarized. It contains multiple sentences and provides detailed information on a specific topic." > example.txt
  python3 summarizer_tool.py example.txt
"""

import requests
import json
import sys
import os

# --- Configuration ---
# Replace with your actual API endpoint
API_BASE_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com"
SUMMARIZE_ENDPOINT = f"{API_BASE_URL}/summarize"
# ---------------------

def summarize_text(text: str) -> dict:
    """
    Sends text to the Bold-Phoenix API for summarization.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}
    try:
        response = requests.post(SUMMARIZE_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with the API: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"API Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 summarizer_tool.py <input_file.txt>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content_to_summarize = f.read()
    except IOError as e:
        print(f"Error reading file '{input_file}': {e}", file=sys.stderr)
        sys.exit(1)

    if not content_to_summarize.strip():
        print("Input file is empty or contains only whitespace. Nothing to summarize.", file=sys.stderr)
        sys.exit(0)

    print(f"Sending text from '{input_file}' to Bold-Phoenix API for summarization...", file=sys.stderr)
    result = summarize_text(content_to_summarize)

    if result and result.get("summary"):
        print("\n--- Summarized Text ---")
        print(result["summary"])
    elif result and result.get("error"):
        print(f"API Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Unexpected API response format.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
