#!/usr/bin/env python3
"""
Code Review Pro API Integration Example
Demonstrates how to use the code-review-pro API service with real examples.
API Endpoint: https://<tunnel-not-configured>.trycloudflare.com/api/v1/code-review-pro
Cost: $0.20 per request

Usage:
    python code_review_pro_example.py [--api-key YOUR_KEY]

Requirements:
    - requests library (pip install requests)
"""

import argparse
import json
import sys
from pathlib import Path

def review_code_sample(api_key: str = None):
    """Review a sample Python function using the Code Review Pro API."""
    # Sample code to review
    sample_code = '''
def calculate_discount(price, discount_percent):
    """Calculate discounted price."""
    if discount_percent > 100:
        return 0
    return price * (1 - discount_percent / 100)
'''
    
    # API endpoint (replace with your actual public URL when available)
    api_url = "https://<tunnel-not-configured>.trycloudflare.com/api/v1/code-review-pro"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    payload = {
        "code": sample_code,
        "language": "python"
    }
    
    try:
        import requests
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Code Review Results:")
            print(json.dumps(result, indent=2))
        elif response.status_code == 402:
            print("💰 Payment required - add funds to your account")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except ImportError:
        print("❌ 'requests' library not installed. Run: pip install requests")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Code Review Pro API Example")
    parser.add_argument("--api-key", help="Your API key (optional for free tier)")
    args = parser.parse_args()
    
    print("🔍 Testing Code Review Pro API...")
    print("Sample code being reviewed:")
    print('''
def calculate_discount(price, discount_percent):
    """Calculate discounted price."""
    if discount_percent > 100:
        return 0
    return price * (1 - discount_percent / 100)
''')
    review_code_sample(args.api_key)

if __name__ == "__main__":
    main()