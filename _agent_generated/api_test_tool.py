#!/usr/bin/env python3
"""
Lucid-Helix API Test Tool
Quickly test all API services from the command line

Your API is LIVE at: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import json
import sys

BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def test_chat():
    """Test the chat endpoint"""
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "Hello! What can you help me with?",
        "model": "deepseek-chat"
    })
    return response.json()

def test_translate():
    """Test the translate endpoint"""
    response = requests.post(f"{BASE_URL}/translate", json={
        "text": "Hello world",
        "target_language": "es",
        "model": "deepseek-chat"
    })
    return response.json()

def test_code_review():
    """Test the code review endpoint"""
    code = """
def add_numbers(a, b):
    return a + b
    
class Calculator:
    def multiply(self, x, y):
        result = 0
        for i in range(y):
            result += x
        return result
"""
    response = requests.post(f"{BASE_URL}/code-review", json={
        "code": code,
        "language": "python",
        "model": "deepseek-chat"
    })
    return response.json()

def test_generate_code():
    """Test the code generation endpoint"""
    response = requests.post(f"{BASE_URL}/generate-code", json={
        "description": "Create a Python function that reverses a string",
        "language": "python",
        "model": "deepseek-chat"
    })
    return response.json()

def main():
    print("🚀 Lucid-Helix API Test Tool")
    print(f"📡 Testing API at: {BASE_URL}")
    print("-" * 60)
    
    endpoints = [
        ("Chat", test_chat),
        ("Translate", test_translate),
        ("Code Review", test_code_review),
        ("Generate Code", test_generate_code),
    ]
    
    for name, test_func in endpoints:
        print(f"\n🧪 Testing {name}...")
        try:
            result = test_func()
            print(f"✅ {name}: SUCCESS")
            if 'response' in result:
                preview = result['response'][:100] + "..." if len(result['response']) > 100 else result['response']
                print(f"   Preview: {preview}")
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print(f"\n💡 Ready to integrate? Use these endpoints in your code:")
    print(f"   Chat: {BASE_URL}/chat")
    print(f"   Code Review: {BASE_URL}/code-review")
    print(f"   Generate Code: {BASE_URL}/generate-code")
    print(f"   Full list: {BASE_URL}/")

if __name__ == "__main__":
    main()