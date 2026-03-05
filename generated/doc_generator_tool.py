#!/usr/bin/env python3

"""
Bold-Phoenix API Documentation Generator Tool

This script demonstrates how to use the Bold-Phoenix API to generate documentation
for your code. It can create README files, API documentation, and code explanations.

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys
import os

API_BASE = "https://upgrades-approx-gadgets-hit.trycloudflare.com"

def generate_documentation(code, doc_type="readme"):
    """Generate documentation for the given code using Bold-Phoenix API."""
    
    # Choose the appropriate endpoint based on documentation type
    if doc_type == "readme":
        endpoint = f"{API_BASE}/summarize"
        prompt = f"Create a comprehensive README.md file for this code:\n\n{code}"
    elif doc_type == "api":
        endpoint = f"{API_BASE}/explain-code"
        prompt = f"Generate API documentation for this code:\n\n{code}"
    elif doc_type == "explain":
        endpoint = f"{API_BASE}/explain-code"
        prompt = f"Explain this code in detail:\n\n{code}"
    else:
        return "Error: Invalid documentation type. Use 'readme', 'api', or 'explain'."
    
    try:
        response = requests.post(
            endpoint,
            json={
                "text": prompt,
                "max_tokens": 1000
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("result", "No documentation generated")
        else:
            return f"Error: API returned status {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main function to demonstrate the documentation generator."""
    
    # Example Python code to document
    example_code = '''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def is_prime(num):
    """Check if a number is prime."""
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True
'''
    
    print("=== Bold-Phoenix Documentation Generator ===\n")
    print("Generating README documentation...\n")
    
    # Generate README
    readme_doc = generate_documentation(example_code, "readme")
    print("README.md:")
    print("-" * 50)
    print(readme_doc)
    print("-" * 50)
    
    print("\nGenerating API documentation...\n")
    
    # Generate API documentation
    api_doc = generate_documentation(example_code, "api")
    print("API Documentation:")
    print("-" * 50)
    print(api_doc)
    print("-" * 50)
    
    print("\nTry it with your own code!")
    print("Usage: python3 doc_generator_tool.py <your_code_file>")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read code from file
        try:
            with open(sys.argv[1], 'r') as f:
                code_content = f.read()
            
            print("Generating documentation for your code...\n")
            doc = generate_documentation(code_content, "readme")
            print(doc)
            
            # Save to file
            output_file = "generated_documentation.md"
            with open(output_file, 'w') as f:
                f.write(doc)
            print(f"\nDocumentation saved to: {output_file}")
            
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        main()