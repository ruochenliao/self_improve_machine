#!/usr/bin/env python3

"""
Keen-Vortex: Chat CLI Tool
This script demonstrates how to use the Keen-Vortex chat API service from the command line.

Usage:
  python3 chat_cli.py "Your message here"

Public API Server: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys

# Your Keen-Vortex API endpoint
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"

def chat_with_keen_vortex(message: str) -> str:
    """
    Sends a message to the Keen-Vortex chat API and returns the response.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"message": message}

    try:
        response = requests.post(CHAT_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()
        return result.get("response", "No response received.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the API: {e}"
    except json.JSONDecodeError:
        return f"Error decoding JSON response: {response.text}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 chat_cli.py "Your message here"")
        sys.exit(1)

    user_message = sys.argv[1]
    print(f"Sending message: '{user_message}' to Keen-Vortex chat service...")
    response_text = chat_with_keen_vortex(user_message)
    print("
Keen-Vortex Response:")
    print(response_text)
