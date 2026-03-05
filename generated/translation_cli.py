#!/usr/bin/env python3

"""
Bold-Phoenix API Translation CLI Tool

This script demonstrates how to use the Bold-Phoenix API for text translation.
It takes text and a target language as input and returns the translated text.

API Endpoint: https://upgrades-approx-gadgets-hit.trycloudflare.com/translate
"""

import requests
import json
import argparse

API_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com/translate"

def translate_text(text: str, target_language: str) -> str:
    """
    Translates the given text to the target language using the Bold-Phoenix API.

    Args:
        text: The text to translate.
        target_language: The target language (e.g., "es" for Spanish, "fr" for French).

    Returns:
        The translated text.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"text": text, "target_language": target_language}

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        if result and "translated_text" in result:
            return result["translated_text"]
        else:
            return f"Error: Unexpected API response format: {result}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to API: {e}"
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON response from API: {response.text}"

def main():
    parser = argparse.ArgumentParser(description="Translate text using the Bold-Phoenix API.")
    parser.add_argument("text", type=str, help="The text to translate.")
    parser.add_argument("target_language", type=str, help="The target language (e.g., 'es', 'fr').")

    args = parser.parse_args()

    translated_text = translate_text(args.text, args.target_language)
    print(f"Original Text: {args.text}")
    print(f"Target Language: {args.target_language}")
    print(f"Translated Text: {translated_text}")

if __name__ == "__main__":
    main()
