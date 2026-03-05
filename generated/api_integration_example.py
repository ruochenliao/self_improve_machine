#!/usr/bin/env python3

"""
Bold-Phoenix API Integration Example

This script demonstrates how to make a simple API call to a Bold-Phoenix service.
It's a basic "hello world" for integrating with the API.
"""

import requests
import json

# Your Bold-Phoenix API endpoint (replace with a specific service like chat, summarize, etc.)
# You can find your public URL on the Bold-Phoenix landing page.
# Example: https://upgrades-approx-gadgets-hit.trycloudflare.com/chat
API_BASE_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com" # Replace if your URL changes

def call_api(service_path: str, payload: dict):
    """
    Makes a POST request to the specified Bold-Phoenix API service.

    Args:
        service_path (str): The path to the API service (e.g., "/chat", "/summarize").
        payload (dict): The JSON payload for the API request.
    """
    url = f"{API_BASE_URL}{service_path}"
    headers = {
        "Content-Type": "application/json"
    }

    print(f"Calling API: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        print("\nAPI Response:")
        print(json.dumps(response.json(), indent=2))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")

if __name__ == "__main__":
    print("--- Bold-Phoenix API Integration Example ---\n")

    # Example 1: Chat service
    print("Attempting to call the /chat service (Standard):")
    chat_payload = {
        "model": "deepseek-chat", # Use cheapest model for standard services
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ]
    }
    call_api("/chat", chat_payload)

    print("\n" + "="*50 + "\n")

    # Example 2: Summarize service
    print("Attempting to call the /summarize service (Standard):")
    summarize_payload = {
        "model": "deepseek-chat",
        "text": "The quick brown fox jumps over the lazy dog. This is a classic pangram used to display all letters of the alphabet. It is often used for typing practice."
    }
    call_api("/summarize", summarize_payload)

    print("\n" + "="*50 + "\n")

    # Example 3: Code Review Pro service (requires GPT-4o, higher cost)
    print("Attempting to call the /code-review-pro service (Pro, GPT-4o):")
    code_review_payload = {
        "model": "gpt-4o", # Use gpt-4o for pro services
        "code": "def add(a, b):\n    return a + b  # Simple addition function"
    }
    call_api("/code-review-pro", code_review_payload)

    print("\n--- End of Example ---")
