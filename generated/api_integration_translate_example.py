#!/usr/bin/env python3

"""
Keen-Vortex API Integration Example: Text Translation

This script demonstrates how to integrate the Keen-Vortex API to translate text.
It sends a POST request to the '/translate' endpoint with the text to be translated
and the target language, then prints the translated output.

Your Keen-Vortex API is live at: https://charlotte-fifty-rrp-induced.trycloudflare.com

To run this script:
1. Make sure you have the 'requests' library installed (`pip install requests`).
2. Replace 'YOUR_API_BASE_URL' with your actual API base URL.
3. Run the script: `python generated/api_integration_translate_example.py`
"""

import requests
import json

# --- Configuration ---
# Replace with your actual Keen-Vortex API base URL
API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com"
TRANSLATE_ENDPOINT = f"{API_BASE_URL}/translate"

# --- Translation Parameters ---
text_to_translate = "Hello, how are you?"
target_language = "fr"  # Translate to French

# --- API Request ---
def translate_text(text: str, target_lang: str):
    """
    Sends a request to the Keen-Vortex /translate API endpoint.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "text": text,
        "target_language": target_lang
    }

    try:
        print(f"Translating: '{text}' to '{target_lang}'...")
        response = requests.post(TRANSLATE_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        result = response.json()
        translated_text = result.get("translated_text")

        if translated_text:
            print(f"Translation successful: {translated_text}")
        else:
            print(f"Translation failed. API response: {result}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    translate_text(text_to_translate, target_language)
