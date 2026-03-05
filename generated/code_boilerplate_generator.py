#!/usr/bin/env python3
"""
Keen-Vortex Code Boilerplate Generator
A practical tool that uses the Keen-Vortex API to generate code templates.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys

def generate_boilerplate(language, framework, description):
    """Generate code boilerplate using Keen-Vortex API"""
    
    api_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/generate-code"
    
    prompt = f"""Create a {language} boilerplate code for {framework}.

Description: {description}

Requirements:
- Include proper file structure
- Add necessary imports/dependencies
- Include basic setup and configuration
- Add sample usage/comments
- Make it production-ready

Output only the code, no explanations."""
    
    payload = {
        "prompt": prompt,
        "language": language
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get('code', 'Error: No code generated')
        
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    print("Keen-Vortex Code Boilerplate Generator")
    print("=" * 50)
    
    if len(sys.argv) < 4:
        print("Usage: python code_boilerplate_generator.py <language> <framework> <description>")
        print("\nExamples:")
        print("  python code_boilerplate_generator.py python flask 'REST API with user authentication'")
        print("  python code_boilerplate_generator.py javascript react 'Todo app with state management'")
        print("  python code_boilerplate_generator.py python django 'Blog application with admin panel'")
        sys.exit(1)
    
    language = sys.argv[1]
    framework = sys.argv[2]
    description = sys.argv[3]
    
    print(f"\nGenerating {language} boilerplate for {framework}...")
    print(f"Description: {description}")
    print("-" * 50)
    
    code = generate_boilerplate(language, framework, description)
    
    print("\nGenerated Code:")
    print("-" * 50)
    print(code)
    
    # Save to file
    filename = f"{language}_{framework}_boilerplate.{language if language != 'javascript' else 'js'}"
    with open(filename, 'w') as f:
        f.write(code)
    
    print(f"\nSaved to: {filename}")
    print("\nPowered by Keen-Vortex API: https://charlotte-fifty-rrp-induced.trycloudflare.com")

if __name__ == "__main__":
    main()