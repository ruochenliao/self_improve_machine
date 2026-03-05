#!/usr/bin/env python3

"""
Bold-Phoenix API Translation Tool

This script demonstrates the translation API service from Bold-Phoenix.
Translate text between multiple languages with a simple command-line interface.

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys

def translate_text(text, target_lang="en", source_lang="auto"):
    """Translate text using Bold-Phoenix API"""
    
    api_url = "https://upgrades-approx-gadgets-hit.trycloudflare.com/translate"
    
    payload = {
        "text": text,
        "target_lang": target_lang,
        "source_lang": source_lang
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("translated_text", "Translation failed")
        
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def main():
    """Main function with command-line interface"""
    
    if len(sys.argv) < 2:
        print("Usage: python translator_tool.py <text> [target_lang] [source_lang]")
        print("Example: python translator_tool.py 'Hello world' es")
        print("Example: python translator_tool.py 'Bonjour' en fr")
        sys.exit(1)
    
    text = sys.argv[1]
    target_lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    source_lang = sys.argv[3] if len(sys.argv) > 3 else "auto"
    
    print(f"Translating: {text}")
    print(f"From: {source_lang} -> To: {target_lang}")
    print("-" * 50)
    
    translated = translate_text(text, target_lang, source_lang)
    print(f"Result: {translated}")

if __name__ == "__main__":
    main()