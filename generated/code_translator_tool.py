#!/usr/bin/env python3

"""
Keen-Vortex: Code Translator CLI Tool
This script provides a command-line interface to translate code between programming languages
using the Keen-Vortex API services.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import argparse
import sys

def translate_code(source_code, source_lang, target_lang):
    """Translate code from one programming language to another."""
    
    api_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/translate"
    
    payload = {
        "text": source_code,
        "source_language": source_lang,
        "target_language": target_lang
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("translated_text", "Translation failed")
        
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    parser = argparse.ArgumentParser(description="Translate code between programming languages")
    parser.add_argument("file", help="Input file containing source code")
    parser.add_argument("--source", "-s", required=True, help="Source language (e.g., python, javascript, java)")
    parser.add_argument("--target", "-t", required=True, help="Target language (e.g., python, javascript, java)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    # Read source code
    try:
        with open(args.file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    print(f"Translating {args.source} code to {args.target}...")
    
    # Translate the code
    translated_code = translate_code(source_code, args.source, args.target)
    
    # Output result
    if args.output:
        with open(args.output, 'w') as f:
            f.write(translated_code)
        print(f"Translation saved to: {args.output}")
    else:
        print("\n" + "="*50)
        print("TRANSLATED CODE:")
        print("="*50)
        print(translated_code)

if __name__ == "__main__":
    main()