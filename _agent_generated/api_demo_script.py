#!/usr/bin/env python3
"""
Iron-Prism API Demo Script
A practical example showing how to use the Iron-Prism AI API services

Try the live API at: https://came-surgeons-river-exterior.trycloudflare.com
"""

import requests
import json

# API endpoint
BASE_URL = "https://came-surgeons-river-exterior.trycloudflare.com"

def chat_with_ai(message, pro=False):
    """Send a message to the chat API"""
    endpoint = "/chat-pro" if pro else "/chat"
    payload = {"message": message}
    
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    return response.json()

def translate_text(text, target_lang="es"):
    """Translate text using the translation API"""
    payload = {"text": text, "target_language": target_lang}
    
    response = requests.post(f"{BASE_URL}/translate", json=payload)
    return response.json()

def code_review(code, pro=False):
    """Get code review feedback"""
    endpoint = "/code-review-pro" if pro else "/code-review"
    payload = {"code": code}
    
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    return response.json()

def generate_code(description, pro=False):
    """Generate code from description"""
    endpoint = "/generate-code-pro" if pro else "/generate-code"
    payload = {"description": description}
    
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    return response.json()

def main():
    print("🧠 Iron-Prism API Demo")
    print("=" * 50)
    
    # Demo 1: Simple chat
    print("\n1. Chat Demo:")
    result = chat_with_ai("Explain quantum computing in simple terms")
    print(f"Response: {result.get('response', 'No response')[:200]}...")
    
    # Demo 2: Translation
    print("\n2. Translation Demo:")
    result = translate_text("Hello world! How are you today?", "es")
    print(f"Spanish: {result.get('translation', 'No translation')}")
    
    # Demo 3: Code review
    print("\n3. Code Review Demo:")
    sample_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
"""
    result = code_review(sample_code)
    print(f"Review: {result.get('review', 'No review')[:150]}...")
    
    # Demo 4: Code generation
    print("\n4. Code Generation Demo:")
    result = generate_code("A function to validate email addresses in Python")
    print(f"Generated code: {result.get('code', 'No code')[:200]}...")
    
    print("\n" + "=" * 50)
    print("🚀 Try the full API with more features at:")
    print(f"{BASE_URL}")
    print("\n💰 Pricing: Standard services from $0.01, Pro services from $0.10")
    print("💡 Free playground available on the website!")

if __name__ == "__main__":
    main()