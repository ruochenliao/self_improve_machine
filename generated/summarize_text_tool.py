#!/usr/bin/env python3

"""
Keen-Vortex: Text Summarization CLI Tool
This script provides a command-line interface to summarize text using the Keen-Vortex API.

Usage:
  python3 summarize_text_tool.py "Your long text here to be summarized."

"""

import requests
import json
import sys

# Your Keen-Vortex API endpoint
# IMPORTANT: Replace with your actual public URL
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com" 
SUMMARIZE_ENDPOINT = f"{API_BASE_URL}/summarize"

def summarize_text(text: str) -> dict:
    """
    Summarizes the given text using the Keen-Vortex API.

    Args:
        text: The text to be summarized.

    Returns:
        A dictionary containing the summarized text or an error message.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}
    
    try:
        response = requests.post(SUMMARIZE_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 summarize_text_tool.py "Your long text here to be summarized."")
        sys.exit(1)

    input_text = sys.argv[1]
    print(f"Summarizing text...")
    
    result = summarize_text(input_text)

    if "error" in result:
        print(f"Error: {result['error']}")
    elif "summary" in result:
        print("\n--- Original Text ---")
        print(input_text)
        print("\n--- Summarized Text ---")
        print(result["summary"])
    else:
        print("Unexpected API response:", result)
