#!/usr/bin/env python3
"""
Demo: Smart Code Review using Prime-Zenith AI API
Shows how to use my code review service to improve your Python code.

My API is live at: https://came-surgeons-river-exterior.trycloudflare.com
Try it for free!
"""

import requests
import json

def review_code_with_ai(code_snippet, api_key="free"):
    """Review code using my AI API service"""
    
    # My API endpoint
    url = "https://came-surgeons-river-exterior.trycloudflare.com/api/code-review"
    
    payload = {
        "code": code_snippet,
        "language": "python",
        "api_key": api_key
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def demo():
    """Demo the code review service with sample code"""
    
    print("🚀 Prime-Zenith AI Code Review Demo")
    print("=" * 50)
    print("My API: https://came-surgeons-river-exterior.trycloudflare.com")
    print()
    
    # Sample code with issues to review
    sample_code = '''
def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total / len(numbers)

def process_data(data):
    result = []
    for item in data:
        if item > 10:
            result.append(item * 2)
    return result

class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, name, email):
        self.users.append({"name": name, "email": email})
        return True
'''
    
    print("📝 Sample Code to Review:")
    print("-" * 30)
    print(sample_code)
    print()
    
    print("🤖 Sending to AI Code Review Service...")
    result = review_code_with_ai(sample_code)
    
    print("\n✅ AI Code Review Results:")
    print("-" * 30)
    
    if "review" in result:
        print(result["review"])
    elif "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("Unexpected response format")
        print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 50)
    print("💡 Try my full API with your own code!")
    print("🌐 https://came-surgeons-river-exterior.trycloudflare.com")
    print("💰 Free tier available • Pro services from $0.10")
    print("🔧 14 AI services: chat, translate, code generation, bug fixing")

if __name__ == "__main__":
    demo()