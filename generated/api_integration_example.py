#!/usr/bin/env python3

"""
Keen-Vortex: API Integration Example
This script demonstrates how to integrate with the Keen-Vortex API using Python.
It calls the chat, translate, and summarize services.
"""

import requests
import json

# Replace with your actual public URL
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def call_api_service(service_name: str, payload: dict) -> dict:
    """Calls a Keen-Vortex API service and returns the JSON response."""
    url = f"{API_BASE_URL}/{service_name}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling {service_name} service: {e}")
        return {"error": str(e)}

def main():
    print("--- Keen-Vortex API Integration Example ---")

    # 1. Chat Service Example
    print("\n--- Chat Service ---")
    chat_payload = {"prompt": "Hello, how are you today?"}
    chat_response = call_api_service("chat", chat_payload)
    print(f"Chat Response: {chat_response.get('response', chat_response)}")

    # 2. Translate Service Example
    print("\n--- Translate Service ---")
    translate_payload = {"text": "Hello world!", "target_language": "fr"}
    translate_response = call_api_service("translate", translate_payload)
    print(f"Translate Response (to French): {translate_response.get('translated_text', translate_response)}")

    # 3. Summarize Service Example
    print("\n--- Summarize Service ---")
    long_text = "The quick brown fox jumps over the lazy dog. This is a classic pangram, a sentence containing every letter of the alphabet at least once. It is often used for testing typewriters and computer keyboards. It is also a fun sentence to say."
    summarize_payload = {"text": long_text}
    summarize_response = call_api_service("summarize", summarize_payload)
    print(f"Summarize Response: {summarize_response.get('summary', summarize_response)}")

    print("\n--- End of Example ---")

if __name__ == "__main__":
    main()
