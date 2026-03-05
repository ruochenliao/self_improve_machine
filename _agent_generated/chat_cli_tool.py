#!/usr/bin/env python3
"""
Lucid-Helix Chat CLI Tool

This script provides a command-line interface to interact with the Lucid-Helix
chat API service. It allows users to send messages and receive responses
from the AI, demonstrating the basic chat functionality.

API Endpoint: https://cet-temporal-therapist-forgot.trycloudflare.com/chat

Usage:
  python3 chat_cli_tool.py "Hello, how are you?"

Dependencies:
  - requests

Installation:
  pip install requests

"""

import requests
import sys

API_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com/chat"

def chat_with_lucid_helix(message: str):
    """
    Sends a message to the Lucid-Helix chat API and prints the response.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"message": message}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        print(f"Lucid-Helix: {data.get('response', 'No response received.')}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Lucid-Helix API: {e}")
        if e.response:
            print(f"API Error Response: {e.response.text}")
    except ValueError:
        print("Error: Could not parse JSON response from API.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    user_message = " ".join(sys.argv[1:])
    chat_with_lucid_helix(user_message)
