#!/usr/bin/env python3

"""
Keen-Vortex Code Snippet Generator
A CLI tool that generates code snippets using the Keen-Vortex API

Your API endpoint: https://charlotte-fifty-rrp-induced.trycloudflare.com
Free playground available - no API key required!
"""

import requests
import json
import sys

def generate_code_snippet(language, description, complexity="simple"):
    """Generate a code snippet using the Keen-Vortex API"""
    
    api_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/generate-code"
    
    payload = {
        "language": language,
        "description": description,
        "complexity": complexity
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def main():
    print("🔧 Keen-Vortex Code Snippet Generator")
    print("=" * 50)
    
    if len(sys.argv) < 3:
        print("Usage: python code_snippet_generator.py <language> <description> [complexity]")
        print("\nExamples:")
        print("  python code_snippet_generator.py python 'function to calculate factorial'")
        print("  python code_snippet_generator.py javascript 'sort array of objects by property'")
        print("  python code_snippet_generator.py python 'web scraper using requests' complex")
        sys.exit(1)
    
    language = sys.argv[1]
    description = sys.argv[2]
    complexity = sys.argv[3] if len(sys.argv) > 3 else "simple"
    
    print(f"\nGenerating {language} code snippet...")
    print(f"Description: {description}")
    print(f"Complexity: {complexity}")
    
    result = generate_code_snippet(language, description, complexity)
    
    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
    else:
        print("\n✅ Code generated successfully!")
        print("-" * 40)
        
        if "code" in result:
            print(result["code"])
        elif "response" in result:
            print(result["response"])
        else:
            print(json.dumps(result, indent=2))
        
        print("\n💡 Try our other services:")
        print("- Code Review: $0.02 per request")
        print("- Bug Fixing: $0.05 per request") 
        print("- Test Writing: $0.03 per request")
        print("\n🌐 Visit: https://charlotte-fifty-rrp-induced.trycloudflare.com")

if __name__ == "__main__":
    main()