
#!/usr/bin/env python3
"""
Lucid-Helix API Translation Example

This script demonstrates how to use the Lucid-Helix translation API service
to translate text from one language to another.

API Endpoint: https://cet-temporal-therapist-forgot.trycloudflare.com/translate
Pricing: $0.01 per request (standard service)

Usage:
    python3 api_translation_example.py "Hello, world!" "en" "fr"

Dependencies:
    - requests (pip install requests)
"""

import requests
import sys

API_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com/translate"

def translate_text(text: str, source_lang: str, target_lang: str) -> str | None:
    """
    Translates text using the Lucid-Helix API.

    Args:
        text: The text to translate.
        source_lang: The source language code (e.g., "en").
        target_lang: The target language code (e.g., "fr").

    Returns:
        The translated text, or None if an error occurs.
    """
    payload = {
        "text": text,
        "source_language": source_lang,
        "target_language": target_lang
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()
        if result and "translated_text" in result:
            return result["translated_text"]
        else:
            print(f"Error: Unexpected API response format: {result}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}", file=sys.stderr)
        return None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python3 {sys.argv[0]} <text_to_translate> <source_language> <target_language>", file=sys.stderr)
        sys.exit(1)

    text_to_translate = sys.argv[1]
    source_language = sys.argv[2]
    target_language = sys.argv[3]

    print(f"Translating '{text_to_translate}' from {source_language} to {target_language}...")
    translated_text = translate_text(text_to_translate, source_language, target_language)

    if translated_text:
        print(f"Translated Text: {translated_text}")
    else:
        print("Translation failed.", file=sys.stderr)
        sys.exit(1)
