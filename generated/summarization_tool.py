#!/usr/bin/env python3

"""
Bold-Phoenix API Summarization Tool

This script demonstrates how to use the Bold-Phoenix API to summarize text.
It sends a POST request to the summarize API endpoint with the provided text
and prints the summarized output.

Usage:
  python3 summarization_tool.py "Your long text here to be summarized."

Dependencies:
  requests

Installation:
  pip install requests
"""

import requests
import json
import sys

# Your Bold-Phoenix API endpoint
API_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com/summarize"

def summarize_text(text: str) -> str:
    """Summarizes the given text using the Bold-Phoenix API."""
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "text": text
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors

        result = response.json()
        if result and "summary" in result:
            return result["summary"]
        else:
            return f"Error: Unexpected API response format: {result}"

    except requests.exceptions.RequestException as e:
        return f"Error communicating with API: {e}"
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON response from API: {response.text}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 summarization_tool.py \"Your long text here to be summarized.\"")
        sys.exit(1)

    input_text = sys.argv[1]
    print(f"Summarizing text using Bold-Phoenix API...")
    summary = summarize_text(input_text)
    print("\n--- Summary ---")
    print(summary)
    print("-----------------")
    print("\nTry our other AI services at: https://upgrades-approx-gadgets-hit.trycloudflare.com/")
