#!/usr/bin/env python3

"""
Keen-Vortex: Code Review Comparison Tool
This tool demonstrates the difference between Standard and Pro code review services.
Shows developers the value of upgrading to Pro for critical code reviews.

Your API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys

def review_code(code: str, service_type: str = "standard") -> dict:
    """Get code review from Keen-Vortex API"""
    
    base_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com"
    
    if service_type == "pro":
        endpoint = f"{base_url}/code-review-pro"
    else:
        endpoint = f"{base_url}/code-review"
    
    payload = {
        "code": code,
        "language": "python"
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python code_review_comparison_tool.py <python_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    print("🔍 Keen-Vortex Code Review Comparison")
    print("=" * 50)
    
    # Get standard review
    print("\n📋 STANDARD Review (DeepSeek):")
    print("-" * 30)
    standard_result = review_code(code, "standard")
    if "review" in standard_result:
        print(standard_result["review"])
    else:
        print("Error:", standard_result.get("error", "Unknown error"))
    
    # Get pro review
    print("\n🚀 PRO Review (GPT-4o):")
    print("-" * 30)
    pro_result = review_code(code, "pro")
    if "review" in pro_result:
        print(pro_result["review"])
    else:
        print("Error:", pro_result.get("error", "Unknown error"))
    
    print("\n💡 Comparison Summary:")
    print("- Standard: Good for quick checks, basic improvements")
    print("- Pro: Deep analysis, edge cases, security considerations")
    print("\nTry both services at: https://charlotte-fifty-rrp-induced.trycloudflare.com")

if __name__ == "__main__":
    main()