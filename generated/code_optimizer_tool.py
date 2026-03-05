#!/usr/bin/env python3

"""
Keen-Vortex: Code Optimizer Tool
This script uses the Keen-Vortex API to optimize Python code for performance and readability.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys

def optimize_code(code: str, api_url: str = "https://charlotte-fifty-rrp-induced.trycloudflare.com") -> str:
    """Send code to the Keen-Vortex API for optimization."""
    try:
        response = requests.post(
            f"{api_url}/fix-bug",
            json={
                "code": code,
                "language": "python",
                "description": "Optimize this code for performance and readability"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("fixed_code", "Optimization failed: No result returned")
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Request failed: {str(e)}"

def main():
    """Main function to handle command line usage."""
    if len(sys.argv) != 2:
        print("Usage: python code_optimizer_tool.py <filename.py>")
        print("Example: python code_optimizer_tool.py my_script.py")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            original_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    print("Original code:")
    print("=" * 50)
    print(original_code)
    print("=" * 50)
    print("\nOptimizing code via Keen-Vortex API...\n")
    
    optimized_code = optimize_code(original_code)
    
    print("Optimized code:")
    print("=" * 50)
    print(optimized_code)
    print("=" * 50)
    
    # Save optimized version
    output_filename = filename.replace('.py', '_optimized.py')
    with open(output_filename, 'w') as f:
        f.write(optimized_code)
    
    print(f"\nOptimized code saved to: {output_filename}")
    print("\nTry the free playground: https://charlotte-fifty-rrp-induced.trycloudflare.com")

if __name__ == "__main__":
    main()