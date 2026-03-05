#!/usr/bin/env python3

"""
Bold-Phoenix Code Snippet Generator

A command-line tool that generates code snippets using the Bold-Phoenix API.
Perfect for quickly generating boilerplate code, utility functions, or learning examples.

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys

def generate_code_snippet(prompt, language="python", service="generate-code"):
    """Generate a code snippet using the Bold-Phoenix API."""
    
    api_url = "https://upgrades-approx-gadgets-hit.trycloudflare.com"
    
    payload = {
        "prompt": f"Generate {language} code for: {prompt}",
        "language": language
    }
    
    try:
        response = requests.post(f"{api_url}/{service}", json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("code", "Error: No code generated")
        
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    print("=== Bold-Phoenix Code Snippet Generator ===")
    print("Generate code snippets instantly using AI")
    print("Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com\n")
    
    if len(sys.argv) > 1:
        # Command-line mode
        prompt = " ".join(sys.argv[1:])
        code = generate_code_snippet(prompt)
        print(f"\nGenerated code:\n{code}")
    else:
        # Interactive mode
        while True:
            print("What code would you like to generate?")
            print("Examples: 'fibonacci function', 'read CSV file', 'web scraper'")
            print("Type 'quit' to exit\n")
            
            prompt = input("Prompt: ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                break
                
            if not prompt:
                continue
                
            print("\nGenerating code...")
            
            # Ask for language preference
            language = input("Language (python/javascript/java/cpp, default=python): ").strip()
            if not language:
                language = "python"
            
            code = generate_code_snippet(prompt, language)
            
            print(f"\n=== Generated {language.upper()} Code ===")
            print(code)
            print("=" * 50)
            
            # Offer to save to file
            save = input("\nSave to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = input("Filename (e.g., generated_code.py): ").strip()
                if filename:
                    with open(filename, 'w') as f:
                        f.write(code)
                    print(f"Code saved to {filename}")
            
            print()

if __name__ == "__main__":
    main()