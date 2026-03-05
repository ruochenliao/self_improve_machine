#!/usr/bin/env python3

"""
Keen-Vortex API Integration Example: Language Translation CLI

This script demonstrates how to use the Keen-Vortex API for language translation.
It takes a text string and a target language as input and returns the translated text.

To run this script:
1. Make sure you have Python 3 installed.
2. Install the 'requests' library: pip install requests
3. Run the script: python translate_cli.py "Hello, world!" es

Your Keen-Vortex API is live at: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys

# Your Keen-Vortex API endpoint
API_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com/translate"

def translate_text(text: str, target_language: str) -> str | None:
    """
    Translates the given text to the target language using the Keen-Vortex API.

    Args:
        text: The text string to translate.
        target_language: The language code to translate to (e.g., "es" for Spanish).

    Returns:
        The translated text as a string, or None if an error occurs.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"text": text, "target_language": target_language}

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()
        return result.get("translated_text")
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON response: {response.text}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python translate_cli.py <text_to_translate> <target_language_code>")
        print("Example: python translate_cli.py "Hello, world!" es")
        sys.exit(1)

    text_to_translate = sys.argv[1]
    target_language = sys.argv[2]

    print(f"Translating '{text_to_translate}' to '{target_language}'...")
    translated_text = translate_text(text_to_translate, target_language)

    if translated_text:
        print(f"Translated Text: {translated_text}")
    else:
        print("Translation failed.")

if __name__ == "__main__":
    main()
