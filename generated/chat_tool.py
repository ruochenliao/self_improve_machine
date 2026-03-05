#!/usr/bin/env python3

"""
Bold-Phoenix API Chat Tool

This script demonstrates how to use the Bold-Phoenix Chat API.
It takes a user message as input and returns a chat response.

To run this script:
1. Make sure you have the 'requests' library installed (`pip install requests`).
2. Replace 'YOUR_API_BASE_URL' with the actual public URL of your Bold-Phoenix API.
   (e.g., https://upgrades-approx-gadgets-hit.trycloudflare.com)
3. Run the script: `python3 generated/chat_tool.py "Hello, how are you?"`
"""

import requests
import json
import sys

# --- Configuration ---
API_BASE_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com" # Replace with your actual API URL
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"
# --- End Configuration ---

def chat_with_api(message: str) -> dict:
    """
    Sends a chat message to the Bold-Phoenix API and returns the response.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"message": message}
    
    try:
        response = requests.post(CHAT_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with the API: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"API Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generated/chat_tool.py "Your chat message here"", file=sys.stderr)
        sys.exit(1)

    user_message = sys.argv[1]
    print(f"Sending message: '{user_message}' to API...")

    response_data = chat_with_api(user_message)

    if response_data and "response" in response_data:
        print("
--- API Response ---")
        print(response_data["response"])
    else:
        print("
--- Unexpected API Response ---")
        print(json.dumps(response_data, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
