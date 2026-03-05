#!/usr/bin/env python3

"""
Bold-Phoenix API Text Translator Tool

This script demonstrates how to use the Bold-Phoenix API to translate text.
It takes a piece of text and a target language as input and returns the translated text.

Usage:
    python3 text_translator_tool.py "Hello, world!" es
    python3 text_translator_tool.py "How are you?" fr

Public API Server: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys

# --- Configuration ---
API_BASE_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com" # Your public API server URL
TRANSLATE_ENDPOINT = f"{API_BASE_URL}/translate"

def translate_text(text: str, target_language: str) -> str:
    """
    Translates the given text to the target language using the Bold-Phoenix API.

    Args:
        text (str): The text to translate.
        target_language (str): The target language (e.g., 'es' for Spanish, 'fr' for French).

    Returns:
        str: The translated text, or an error message if translation fails.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "text": text,
        "target_language": target_language
    }

    try:
        response = requests.post(TRANSLATE_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()
        if "translated_text" in result:
            return result["translated_text"]
        elif "error" in result:
            return f"Error from API: {result['error']}"
        else:
            return f"Unexpected API response: {json.dumps(result)}"
    except requests.exceptions.RequestException as e:
        return f"HTTP Request failed: {e}"
    except json.JSONDecodeError:
        return f"Failed to decode JSON response: {response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 text_translator_tool.py "<text_to_translate>" <target_language>")
        print("Example: python3 text_translator_tool.py "Hello, world!" es")
        sys.exit(1)

    text_to_translate = sys.argv[1]
    target_language = sys.argv[2]

    print(f"Translating '{text_to_translate}' to '{target_language}'...")
    translated_text = translate_text(text_to_translate, target_language)
    print(f"Translated Text: {translated_text}")

if __name__ == "__main__":
    main()
