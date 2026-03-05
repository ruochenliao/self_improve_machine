#!/usr/bin/env python3

"""
Bold-Phoenix Code Translator Tool
Translate code between programming languages using the Bold-Phoenix API

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys

def translate_code(source_code, source_lang, target_lang):
    """Translate code from one programming language to another"""
    
    api_url = "https://upgrades-approx-gadgets-hit.trycloudflare.com/translate"
    
    payload = {
        "text": source_code,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get('translated_text', 'Translation failed')
    
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    print("=== Bold-Phoenix Code Translator ===")
    print("Translate code between programming languages")
    print("Supported: Python, JavaScript, Java, C++, Go, Rust, etc.\n")
    
    if len(sys.argv) > 1:
        # File mode
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return
    else:
        # Interactive mode
        print("Enter your source code (Ctrl+D to finish):")
        source_code = sys.stdin.read()
    
    print("\nEnter source language (e.g., python, javascript, java):")
    source_lang = input("> ").strip().lower()
    
    print("Enter target language (e.g., python, javascript, java):")
    target_lang = input("> ").strip().lower()
    
    print("\nTranslating code...")
    
    translated_code = translate_code(source_code, source_lang, target_lang)
    
    print(f"\n=== Translated Code ({target_lang.upper()}) ===")
    print(translated_code)
    
    # Save to file option
    print(f"\nSave to file? (y/n)")
    save_choice = input("> ").strip().lower()
    
    if save_choice == 'y':
        output_file = f"translated_code.{target_lang}"
        with open(output_file, 'w') as f:
            f.write(translated_code)
        print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()