#!/usr/bin/env python3

"""
Keen-Vortex: Summarize API Example
This script demonstrates how to use the Keen-Vortex summarize API endpoint.
It takes a text input and returns a summarized version.
"""

import requests
import json
import argparse

# Your Keen-Vortex API endpoint
API_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com/summarize" 

def summarize_text(text: str, api_url: str = API_URL):
    """
    Calls the Keen-Vortex summarize API to get a summary of the given text.

    Args:
        text (str): The text to be summarized.
        api_url (str): The URL of the summarize API endpoint.

    Returns:
        dict: The JSON response from the API, or an error message.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def main():
    parser = argparse.ArgumentParser(description="Summarize text using the Keen-Vortex API.")
    parser.add_argument("text", type=str, help="The text to summarize.")
    parser.add_argument("--api-url", type=str, default=API_URL,
                        help=f"The URL of the summarize API endpoint (default: {API_URL}).")

    args = parser.parse_args()

    print(f"Summarizing text using API: {args.api_url}")
    result = summarize_text(args.text, args.api_url)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("
--- Original Text ---")
        print(args.text)
        print("
--- Summarized Text ---")
        print(result.get("summary", "No summary received."))

if __name__ == "__main__":
    main()
