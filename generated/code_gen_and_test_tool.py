#!/usr/bin/env python3

"""
Keen-Vortex: Code Generation & Test Writing Tool
This script demonstrates how to use Keen-Vortex's API to generate code and automatically write tests for it.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json

def generate_code(description, language="python"):
    """Generate code from a description using Keen-Vortex API"""
    url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/generate-code"
    
    payload = {
        "description": description,
        "language": language
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()["code"]
    else:
        print(f"Error generating code: {response.text}")
        return None

def write_tests(code, language="python"):
    """Write tests for generated code using Keen-Vortex API"""
    url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/write-tests"
    
    payload = {
        "code": code,
        "language": language
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()["tests"]
    else:
        print(f"Error writing tests: {response.text}")
        return None

def main():
    print("=== Keen-Vortex Code Generation & Testing Tool ===\n")
    
    # Example: Generate a Python function that calculates Fibonacci numbers
    description = "Write a Python function that calculates the nth Fibonacci number using recursion"
    
    print(f"Generating code for: {description}")
    code = generate_code(description)
    
    if code:
        print("\n✅ Generated Code:")
        print("-" * 50)
        print(code)
        print("-" * 50)
        
        # Now write tests for the generated code
        print("\n📝 Writing tests for the generated code...")
        tests = write_tests(code)
        
        if tests:
            print("\n✅ Generated Tests:")
            print("-" * 50)
            print(tests)
            print("-" * 50)
            
            # Save to files
            with open("generated_fibonacci.py", "w") as f:
                f.write(code)
            
            with open("test_fibonacci.py", "w") as f:
                f.write(tests)
            
            print("\n💾 Files saved:")
            print("- generated_fibonacci.py")
            print("- test_fibonacci.py")
            print("\n🚀 Ready to test: python -m pytest test_fibonacci.py")
    
    print("\n🔗 Try more features at: https://charlotte-fifty-rrp-induced.trycloudflare.com")

if __name__ == "__main__":
    main()