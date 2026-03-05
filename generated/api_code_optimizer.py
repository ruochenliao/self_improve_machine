#!/usr/bin/env python3
"""
Keen-Vortex API Code Optimizer
A practical tool that uses the Keen-Vortex API to optimize Python code.

Your API is live at: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys

def optimize_code(code: str, api_url: str = "https://charlotte-fifty-rrp-induced.trycloudflare.com") -> str:
    """Optimize Python code using Keen-Vortex API"""
    
    payload = {
        "code": code,
        "language": "python"
    }
    
    try:
        response = requests.post(
            f"{api_url}/fix-bug",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("optimized_code", result.get("fixed_code", "Optimization failed"))
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"API call failed: {e}"

def main():
    """Main function to demonstrate code optimization"""
    
    # Example inefficient code to optimize
    sample_code = """
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total

def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
"""
    
    print("Original code:")
    print(sample_code)
    print("\n" + "="*50 + "\n")
    
    print("Optimizing code using Keen-Vortex API...")
    optimized = optimize_code(sample_code)
    
    print("Optimized code:")
    print(optimized)

if __name__ == "__main__":
    main()