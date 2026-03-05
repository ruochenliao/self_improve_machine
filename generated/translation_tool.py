#!/usr/bin/env python3

"""
Bold-Phoenix API Translation Tool

This script demonstrates how to use the Bold-Phoenix API for text translation.
It sends a translation request to the API and prints the translated text.

Public API Server: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import os

# Your Bold-Phoenix API endpoint for translation
API_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com/translate"

def translate_text(text: str, target_language: str = "en") -> str | None:
    """
    Translates the given text to the target language using the Bold-Phoenix API.

    Args:
        text (str): The text to be translated.
        target_language (str): The language to translate to (e.g., "en", "es", "fr").

    Returns:
        str | None: The translated text if successful, otherwise None.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "text": text,
        "target_language": target_language
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors

        result = response.json()
        if result and "translated_text" in result:
            return result["translated_text"]
        else:
            print(f"Error: Unexpected API response format: {result}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

if __name__ == "__main__":
    print("Bold-Phoenix API Translation Tool")
    print("---------------------------------")

    input_text = input("Enter text to translate: ")
    input_language = input("Enter target language (e.g., 'es' for Spanish, 'fr' for French, 'en' for English): ")

    if not input_text:
        print("Error: Please enter some text to translate.")
    else:
        translated_result = translate_text(input_text, input_language)

        if translated_result:
            print("
--- Translation Result ---")
            print(f"Original Text: {input_text}")
            print(f"Target Language: {input_language}")
            print(f"Translated Text: {translated_result}")
        else:
            print("
Translation failed. Please check your input and try again.")
