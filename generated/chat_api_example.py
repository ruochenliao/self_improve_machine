#!/usr/bin/env python3

"""
Keen-Vortex: Chat API Example
This script demonstrates how to use the Keen-Vortex chat API endpoint.
It sends a message to the API and prints the AI's response.
"""

import requests
import json
import os

# --- Configuration ---
# Replace with your actual API server URL.
# You can find it on your Keen-Vortex landing page.
API_SERVER_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com" 

# Your API key (if required by your Keen-Vortex instance).
# For now, most services are open, but this is a placeholder for future authentication.
API_KEY = os.environ.get("KEEN_VORTEX_API_KEY", "YOUR_API_KEY_HERE") 

# --- Chat API Endpoint ---
CHAT_ENDPOINT = f"{API_SERVER_URL}/chat"

def chat_with_keen_vortex(message: str) -> str:
    """
    Sends a message to the Keen-Vortex chat API and returns the AI's response.
    """
    headers = {
        "Content-Type": "application/json",
        # "X-API-KEY": API_KEY # Uncomment if API key is required
    }
    payload = {
        "user_message": message
    }

    try:
        response = requests.post(CHAT_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        result = response.json()
        return result.get("ai_response", "No response from AI.")

    except requests.exceptions.RequestException as e:
        return f"Error communicating with the API: {e}"
    except json.JSONDecodeError:
        return f"Error decoding JSON response: {response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    print("--- Keen-Vortex Chat API Example ---")
    print(f"API Server: {API_SERVER_URL}")
    print("Type 'exit' or 'quit' to end the chat.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat. Goodbye!")
            break
        
        ai_response = chat_with_keen_vortex(user_input)
        print(f"Keen-Vortex: {ai_response}")
