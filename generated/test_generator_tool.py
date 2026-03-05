#!/usr/bin/env python3

"""
Bold-Phoenix API Test Generator Tool

This script demonstrates how to use the Bold-Phoenix API to automatically generate
test cases for Python code. It shows the power of AI-assisted testing.

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys

def generate_tests(code_snippet, api_url="https://upgrades-approx-gadgets-hit.trycloudflare.com"):
    """
    Generate test cases for the given Python code using Bold-Phoenix API
    """
    
    # Prepare the request payload
    payload = {
        "code": code_snippet,
        "language": "python"
    }
    
    try:
        # Call the write-tests API endpoint
        response = requests.post(
            f"{api_url}/write-tests",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("tests", "No tests generated")
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"API call failed: {str(e)}"

def main():
    """Main function to demonstrate test generation"""
    
    print("=== Bold-Phoenix Test Generator Tool ===\n")
    
    # Example Python function to test
    sample_code = '''
def calculate_factorial(n):
    """Calculate factorial of a number"""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

class Calculator:
    """Simple calculator class"""
    def __init__(self):
        self.memory = 0
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
    
    def store(self, value):
        self.memory = value
        return self.memory
'''
    
    print("Sample code to test:")
    print(sample_code)
    print("\nGenerating tests using Bold-Phoenix API...\n")
    
    # Generate tests
    tests = generate_tests(sample_code)
    
    print("=== Generated Test Cases ===\n")
    print(tests)
    
    print("\n=== How to Use This Tool ===")
    print("1. Replace the sample_code variable with your own Python code")
    print("2. Run the script to generate comprehensive test cases")
    print("3. Copy the generated tests into your test files")
    print("\nVisit https://upgrades-approx-gadgets-hit.trycloudflare.com for more AI services!")

if __name__ == "__main__":
    main()