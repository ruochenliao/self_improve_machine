#!/usr/bin/env python3
"""
Keen-Vortex Code Snippet Generator
A practical tool that generates code snippets for various programming languages
using the Keen-Vortex API.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import argparse

# Your Keen-Vortex API endpoint
API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def generate_code_snippet(language, description, complexity="simple"):
    """Generate a code snippet using the Keen-Vortex API"""
    
    prompt = f"Generate a {complexity} {language} code snippet that: {description}"
    
    payload = {
        "prompt": prompt,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(f"{API_BASE}/generate-code", json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("code", "Error: No code generated")
        
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    parser = argparse.ArgumentParser(description="Generate code snippets using Keen-Vortex API")
    parser.add_argument("language", help="Programming language (python, javascript, java, etc)")
    parser.add_argument("description", help="Description of what the code should do")
    parser.add_argument("--complexity", choices=["simple", "medium", "complex"], 
                       default="simple", help="Code complexity level")
    
    args = parser.parse_args()
    
    print(f"Generating {args.complexity} {args.language} code snippet...")
    print("-" * 60)
    
    code = generate_code_snippet(args.language, args.description, args.complexity)
    
    print(f"Language: {args.language}")
    print(f"Description: {args.description}")
    print(f"Complexity: {args.complexity}")
    print("-" * 60)
    print("Generated Code:")
    print("-" * 60)
    print(code)
    print("-" * 60)
    print(f"API: {API_BASE}")

if __name__ == "__main__":
    main()